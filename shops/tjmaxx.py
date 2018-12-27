import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _tjmaxxurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, match_sk
# from debug_app.manual_debug_funcs import printHtmlToFile


class TjMaxx(scrapy.Spider):
    name = find_shop_configuration("TJMAXX")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _tjmaxxurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        items = response.css(".product-inner")
        for item in items:
            item_text = item.css(".product-title ::text").extract_first()
            if match_sk(self._search_keyword, item_text):
                item_url = item.css(".product-image a.product-link ::attr(href)").extract_first()
                yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url)

    def parse_data(self, response):
        image_url = response.css(".main-image ::attr(src), product-image img ::attr(src)").extract_first()
        title = "{} {}".format(response.css(".product-brand ::text").extract_first() or "", response.css(".product-title ::text").extract_first() or "")
        description = extract_items(response.css(".description-list li ::text").extract())
        price = extract_items(response.css(".price .product-price ::text").extract())
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
