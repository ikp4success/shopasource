import scrapy

from shops.shop_connect.shop_request import get_request
# from shops.shop_utilities.extra_function import prepend_domain
from shops.shop_connect.shoplinks import _amazonurl
from shops.shop_utilities.shop_names import ShopNames


class Amazon(scrapy.Spider):
    shop_name = ShopNames.AMAZON
    shop_url = _amazonurl

    def start_request(self):
        import pdb; pdb.set_trace()
        yield get_request(self.shop_url, self.parse_data)

    def parse_data(self):
        result_meta = {
                        "printer": {
                            "image_url": "",
                            "shop_name": "",
                            "price": "$2.00",
                            "title": "HP Printer",
                            "search_keyword": "printer",
                            "content_descripiton": "This is a nice printer",
                            "date_searched": "08/06/2018"
                        }
                }
        yield result_meta
