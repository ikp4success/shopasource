import re
import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _aldourl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, safe_json, safe_grab


class ALDO(scrapy.Spider):
    name = find_shop_configuration("ALDO")["name"]
    _search_keyword = None
    aldo_headers = {
        "Host": "www.aldoshoes.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "referrer": "https://www.aldoshoes.com/us/en_US/",
        "TE": "Trailers",
        "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
    }

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = "https://www.aldoshoes.com/us/en_US/"
        yield get_request(shop_url, callback=self.get_products, headers=self.aldo_headers)

    def get_products(self, response):
        shop_url = _aldourl.format(self._search_keyword)
        yield get_request(shop_url, callback=self.get_best_link)

    def get_best_link(self, response):
        items = "".join(response.css("script ::text").extract())
        items = re.search("__INITIAL_STATE__ =(.*)", items)
        if items:
            items = safe_grab(safe_json(items.group(1)), ["products"], default=[])
            products = safe_grab(items, ["byCode"], default={})
            for k, v in products.items():
                item_url = "https://www.aldoshoes.com/us/en_US/" + safe_grab(v, ["url"], default="")
                yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url, headers=self.aldo_headers, meta={"dont_redirect": "True"})

    def parse_data(self, response):
        image_url = response.css(".c-carousel-product-overview img ::attr(src)").extract_first()
        title = extract_items(response.css(".c-product-detail__info .c-heading__dash-wrap .c-markdown ::text").extract())
        description = extract_items(response.css(".c-product-detail__info ::text").extract())
        price = response.css(".c-product-price__formatted-price ::text").extract_first()
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
