import importlib
from multiprocessing import Process, Queue

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

from support import get_logger

logger = get_logger(__name__)


class SpiderRunner(CrawlerRunner):
    _runner = None

    def __init__(self, settings=None):
        if settings is None:
            settings = get_project_settings()
        super().__init__(settings)

    def run(self):
        d = self.join()
        d.addBoth(lambda _: reactor.stop())
        reactor.run()


def import_class(name):
    name = name.lower()
    module = importlib.import_module(f"shops.{name}")
    return getattr(module, name.title())


def spider_runner(spider_name, search_keyword):
    spider_class = import_class(spider_name)
    logger.debug("Running spider {spider_class.name}")
    scrapy_settings = get_project_settings()
    scrapy_custom_settings = {
        "LOG_FILE": f"logs/{spider_class.name}.log",
    }
    scrapy_settings.update(scrapy_custom_settings)

    def crawl(q):
        try:
            configure_logging()
            runner = SpiderRunner(settings=scrapy_settings)
            runner.crawl(spider_class, search_keyword=search_keyword)
            runner.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=crawl, args=(q,))
    p.start()
    p.join()
