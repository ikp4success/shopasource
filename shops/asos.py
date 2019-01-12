import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _asosurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, safe_grab


class Asos(scrapy.Spider):
    name = find_shop_configuration("ASOS")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _asosurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        items = response.css("._2oHs74P")
        for item in items:
            item_url = item.css("a._3x-5VWa ::attr(href)").extract_first()
            price = item.css("._342BXW_ ::text").extract_first()
            yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url, meta={"pc": price})

    def parse_data(self, response):
        image_url = response.css(".amp-frame .fullImageContainer img ::attr(src), .product-carousel img ::attr(src)").extract_first()
        title = extract_items(response.css(".product-hero h1 ::text").extract())
        description = extract_items(response.css(".product-description ::text").extract())
        price = safe_grab(response.meta, ["pc"])
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
