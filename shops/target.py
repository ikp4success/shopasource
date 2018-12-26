import scrapy

from shops.shop_connect.shop_request import get_request, prepend_domain
from shops.shop_connect.shoplinks import _targeturl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, safe_json, safe_grab
# from debug_app.manual_debug_funcs import printHtmlToFile


class Target(scrapy.Spider):
    name = find_shop_configuration("TARGET")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _targeturl.format(self._search_keyword)
        yield get_request(shop_url, self.parse_data)

    def parse_data(self, response):
        json_data = safe_json(response.text)
        t_data = safe_grab(json_data, ["search_response", "items", "Item"], default=[])

        for item in t_data:
            title = safe_grab(item, ["title"])
            images = safe_grab(item, ["images"])[0]
            base_url = safe_grab(images, ["base_url"])
            primary = safe_grab(images, ["primary"])
            image_url = "{}{}".format(base_url, primary)
            description = safe_grab(item, ["description"])
            price = safe_grab(item, ["list_price", "formatted_price"]) or safe_grab(item, ["offer_price", "formatted_price"])
            url = prepend_domain(safe_grab(item, ["url"]), "https://www.target.com")
            yield generate_result_meta(shop_link=url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
