import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _leviurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items


class LEVI(scrapy.Spider):
    name = find_shop_configuration("LEVI")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _leviurl.format(self._search_keyword)
        yield get_request(shop_url, self.parse_data)

    def parse_data(self, response):
        items = response.css(".product-item")

        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            image_url = item.css("img.responsive-image ::attr(src)").extract_first()
            title = extract_items(item.css(".details .name ::text").extract())
            description = " ".join(item.css(".details .color-name ::text").extract())
            price = item.css(".details .price .hard-sale ::text").extract_first() or \
                item.css(".details .price .soft-sale ::text").extract_first() or \
                item.css(".details .price .regular ::text").extract_first()
            yield generate_result_meta(shop_link=item_url,
                                       image_url=image_url,
                                       shop_name=self.name,
                                       price=price,
                                       title=title,
                                       searched_keyword=self._search_keyword,
                                       content_description=description)
