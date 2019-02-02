import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _shopqueenurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items


class SHOPQUEEN(scrapy.Spider):
    name = find_shop_configuration("SHOPQUEEN")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _shopqueenurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        items = response.css(".ProductItem__Wrapper")

        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url)

    def parse_data(self, response):
        image_url = response.css(".Product__SlideItem img ::attr(src)").extract_first()
        title = extract_items(response.css(".ProductMeta__Title ::text").extract())
        description = extract_items(response.css(".ProductMeta__Description ::text").extract())
        price = response.css(".ProductMeta__PriceList .ProductMeta__Price ::text").extract_first()
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
