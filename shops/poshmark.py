import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _poshmarkurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items


class PostMark(scrapy.Spider):
    name = find_shop_configuration("POSHMARK")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _poshmarkurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        items = response.css("#tiles-con .tile")

        for item in items:
            item_url = item.css("a.covershot-con ::attr(href)").extract_first()
            yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url)

    def parse_data(self, response):
        image_url = response.css(".covershot ::attr(src)").extract_first()
        title = extract_items(response.css(".title ::text").extract())
        description = extract_items(response.css(".description ::text").extract())
        price = response.css(".details .price ::text").extract_first()
        if price:
            price = price.replace("\xa0", "")
        else:
            price = response.css(".orginal ::text").extract_first()
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
