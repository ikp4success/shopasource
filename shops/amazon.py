import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_utilities.extra_function import prepend_domain
from shops.shop_connect.shoplinks import _amazonurl
from shops.shop_utilities.shop_names import ShopNames


class Amazon(scrapy.Spider):
    shop_name = ShopNames.AMAZON
    shop_url = _amazonurl

    def get_data(self):
        yield get_request(self.shop_url)
