import importlib
from multiprocessing import Process, Queue
from subprocess import call  # nosec

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


def spider_runner(spider_name, search_keyword, job_id):
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
            runner.crawl(spider_class, search_keyword=search_keyword, job_id=job_id)
            runner.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=crawl, args=(q,))
    p.start()
    p.join()


def launch_spiders(sn, sk, is_async, job_id):
    if sn and sk:
        if is_async:
            # HACK:  scrapy blocks process, so using python subprocess for now.
            call(  # nosec
                [
                    "scrapy",
                    "crawl",
                    f"{sn.upper()}",
                    "-a",
                    f"search_keyword={sk}",
                    "-a",
                    f"job_id={job_id}",
                ]
            )
        else:
            # actual scrapy designed thread runs, this will block.
            # TODO:  this should be its own queue-server.
            spider_runner(sn, sk, job_id)
    else:
        raise Exception("Name and Search_keyword required")
