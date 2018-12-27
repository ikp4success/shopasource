import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _cushineurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, safe_json, safe_grab, prepend_domain


class Cushine(scrapy.Spider):
    name = find_shop_configuration("CUSHINE")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _cushineurl.format(self._search_keyword)
        yield get_request(shop_url, self.parse_data)

    def parse_data(self, response):
        import pdb; pdb.set_trace()
        json_data = safe_json(response.text)
        t_data = safe_grab(json_data, ["response", "docs"], default=[])

        for item in t_data:
            title = safe_grab(item, ["name"])
            image_url = safe_grab(item, ["image_varchar"])[0]
            url = safe_grab(item, ["url"])
            description = safe_grab(item, ["description"])
            price = safe_grab(item, ["final_price"])
            yield generate_result_meta(shop_link=url,
                                       image_url=image_url,
                                       shop_name=self.name,
                                       price=price,
                                       title=title,
                                       searched_keyword=self._search_keyword,
                                       content_description=description)
