import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _kmarturl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, safe_json, safe_grab
# from debug_app.manual_debug_funcs import printHtmlToFile


class Kmart(scrapy.Spider):
    name = find_shop_configuration("KMART")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _kmarturl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        json_data = safe_json(response.text)
        t_data = safe_grab(json_data, ["data", "products"], default=[])
        for item in t_data:
            item_url = "https://www.kmart.com/content/pdp/config/products/v1/products/{}?site=kmart".format(safe_grab(item, ["sin"]))
            yield get_request(url=item_url, callback=self.parse_data)

    def parse_data(self, response):
        data = safe_grab(safe_json(response.text), ["data"], default={})
        image_url = safe_grab(safe_grab(safe_grab(data, ["product", "assets", "imgs"])[0], ["vals"])[0], ["src"])
        title = safe_grab(data, ["product", "name"])
        description = safe_grab(data, ["product", "seo", "description"])
        price = "${}".format(safe_grab(data, ["offerranking", "totalPrice"]))
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
