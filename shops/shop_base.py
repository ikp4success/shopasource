import scrapy

from debug_app.manual_debug_funcs import printHtmlToFile
from project.models import ShoppedData
from shops.scrapy_settings.shop_settings import USER_AGENT
from shops.shop_connect.shop_request import get_request
from shops.shop_util.extra_function import (
    extract_items,
    generate_result_meta,
    prepend_domain,
    safe_grab,
    safe_json,
)
from shops.shop_util.shop_setup_functions import find_shop_configuration
from support import get_logger


class ShopBase(scrapy.Spider):
    name = None
    _search_keyword = None
    shop_url = None
    domain_url = None
    headers = {}
    meta = {}
    user_agent = USER_AGENT
    logger = get_logger(__name__)

    def __init__(self, search_keyword):
        self.name = self.find_shop_configuration()["name"]
        self.shop_url = self.find_shop_configuration()["url"]
        self._search_keyword = search_keyword

    def start_requests(self):
        self.logger.info(f"USER_AGENT: {self.user_agent}")
        self.logger.info(f"Search Keyword: {self._search_keyword}")
        shop_url = self.shop_url.format(keyword=self._search_keyword)
        self.headers["Referer"] = shop_url
        self.headers["USER-AGENT"] = self.user_agent
        yield get_request(
            url=shop_url,
            domain_url=self.domain_url,
            callback=self.parse_results,
            headers=self.headers,
            meta=self.meta,
        )

    def get_request(self, url, callback, domain_url=None, meta=None, headers=None):
        return get_request(
            url=url,
            callback=callback,
            domain_url=domain_url,
            meta=meta,
            headers=headers,
        )

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
        if gen_result:
            shop = ShoppedData(**gen_result[searched_keyword])
            shop.commit()
        return gen_result

    def safe_json(self, data):
        return safe_json(data)

    def safe_grab(self, data, keys, default=None):
        return safe_grab(data, keys, default)

    def prepend_domain(self, url, domain_url, ignore_domain_splice=False):
        return prepend_domain(url, domain_url, ignore_domain_splice)

    def printHtmlToFile(self, html, page_name=None):
        return printHtmlToFile(html, page_name)

    def extract_items(self, items):
        return extract_items(items)
