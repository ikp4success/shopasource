import os

import scrapy
from scrapy import signals

from shops.scrapy_settings.shop_settings import USER_AGENT
from shops.shop_connect.shop_request import (
    browser_fetch,
    close_browser,
    direct_fetch,
    get_request,
    parse_default_errcallback,
)
from shops.shop_util.extra_function import (
    extract_items,
    generate_result_meta,
    prepend_domain,
    safe_grab,
    safe_json,
    save_job,
    save_shop_data,
)
from shops.shop_util.shop_setup_functions import find_shop_configuration
from support import config, get_logger

config.intialize_sentry()


class ShopBase(scrapy.Spider):
    name = None
    _search_keyword = None
    _job_id = None
    shop_url = None
    domain_url = None
    headers = {}
    meta = {}
    user_agent = USER_AGENT
    logger = get_logger(__name__)
    is_error = True
    # Some sites (Amazon, Walmart, Macy's, Nike, ...) block Scrapy's own (Twisted)
    # downloader specifically - same headers/IP/UA succeed via `requests`. Spiders
    # that need this set use_direct_fetch = True.
    use_direct_fetch = False
    # A few sites' bot detection defeats direct_fetch too (e.g. Amazon's Akamai JS
    # challenge) and need an actual browser executing the page's JS.
    use_browser_fetch = False

    def __init__(self, search_keyword, job_id=None):
        self.name = self.find_shop_configuration()["name"]
        self.shop_url = self.find_shop_configuration()["url"]
        self._search_keyword = search_keyword
        self._job_id = job_id

    async def start(self):
        for request in self.start_requests():
            yield request

    def start_requests(self):
        self.logger.info(f"User-Agent: {self.user_agent}")
        self.logger.info(f"Search Keyword: {self._search_keyword}")
        self.logger.info(f"Job ID: {self._job_id}")
        shop_url = self.shop_url.format(keyword=self._search_keyword)
        self.headers["Referer"] = shop_url
        self.headers["user-agent"] = self.user_agent
        self.headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        )
        self.headers.setdefault("Accept-Language", "en-US,en;q=0.9")
        yield from self.get_request(
            url=shop_url,
            domain_url=self.domain_url,
            callback=self.parse_pre_results,
            errcallback=self.parse_errcallback,
            headers=self.headers,
            meta=self.meta,
        )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ShopBase, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_error, signal=signals.spider_error)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info("Spider closed: %s Reason: %s", spider.name, reason)
        if self.use_browser_fetch:
            close_browser()
        save_job(self.name, self._job_id)

    def spider_error(self, failure, response, spider):
        spider.logger.info("Spider error: %s", spider.name)
        save_job(self.name, self._job_id, status="error")
        parse_default_errcallback(failure)

    def parse_pre_results(self, response):
        self.logger.info("Parsing result..")
        yield from self.parse_results(response)

    def parse_errcallback(self, failure):
        self.logger.info("Parse errcallback")
        save_job(self.name, self._job_id, status="error")
        parse_default_errcallback(failure)

    def get_request(
        self, url, callback, errcallback=None, domain_url=None, meta=None, headers=None
    ):
        if self.use_browser_fetch:
            yield from self._fetch_and_callback(
                browser_fetch,
                "browser_fetch",
                url,
                callback,
                errcallback,
                domain_url,
                headers,
            )
        elif self.use_direct_fetch:
            yield from self._fetch_and_callback(
                direct_fetch,
                "direct_fetch",
                url,
                callback,
                errcallback,
                domain_url,
                headers,
            )
        else:
            request = get_request(
                url=url,
                callback=callback,
                errcallback=errcallback,
                domain_url=domain_url,
                meta=meta,
                headers=headers,
            )
            if request is not None:
                yield request

    def _fetch_and_callback(
        self, fetch_fn, fetch_name, url, callback, errcallback, domain_url, headers
    ):
        response = fetch_fn(
            url=url, domain_url=domain_url, headers=headers or self.headers
        )
        if response is None or response.status != 200:
            self.logger.error(
                "%s failed for %s (status=%s)",
                fetch_name,
                url,
                getattr(response, "status", None),
            )
            if errcallback:
                save_job(self.name, self._job_id, status="error")
            return
        yield from callback(response)

    def find_shop_configuration(self):
        return find_shop_configuration(self.name)

    def generate_result_meta(
        self,
        shop_link,
        searched_keyword,
        image_url,
        price,
        title,
        content_description,
        shop_name=None,
        date_searched=None,
    ):
        save_job(self.name, self._job_id, status="in_progress")
        gen_result = generate_result_meta(
            shop_link=shop_link,
            searched_keyword=searched_keyword,
            image_url=image_url,
            shop_name=shop_name or self.name,
            price=price,
            title=title,
            content_description=content_description,
            date_searched=date_searched,
        )
        if gen_result and gen_result.get(searched_keyword):
            save_shop_data(gen_result[searched_keyword])
        return gen_result

    def safe_json(self, data):
        return safe_json(data)

    def safe_grab(self, data, keys, default=None):
        return safe_grab(data, keys, default)

    def prepend_domain(self, url, domain_url, ignore_domain_splice=False):
        return prepend_domain(url, domain_url, ignore_domain_splice)

    def printHtmlToFile(self, html, page_name=None):
        if page_name is None:
            page_name = "spider_test"
        filename = "scraped_sites/spidertest_" + page_name + ".html"
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
            file = open(filename, "w")
            file.write(html)
            file.close()
        else:
            file = open(filename, "w")
            file.write(html)
            file.close()

    def extract_items(self, items):
        return extract_items(items)
