import scrapy

from shops.shop_connect.shop_request import get_request
# from shops.shop_utilities.extra_function import prepend_domain
from shops.shop_connect.shoplinks import _amazonurl
from shops.shop_utilities.shop_names import ShopNames


class Amazon(scrapy.Spider):
    name = ShopNames.AMAZON.name
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _amazonurl.format(self._search_keyword)
        yield get_request(shop_url, self.parse_data)

    def parse_data(self, response):
        result_meta = {
            self._search_keyword: {
                "image_url": "",
                "shop_name": "",
                "price": "$2.00",
                "title": "HP Printer",
                "criteria": "printer",
                "content_descripiton": "This is a nice printer",
                "date_searched": "08/06/2018"
            }
        }
        yield result_meta
