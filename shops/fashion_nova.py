import scrapy
# import uuid

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _fashionnovaurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, safe_json, safe_grab


class FashionNova(scrapy.Spider):
    name = find_shop_configuration("FASHIONNOVA")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        # uuid_v = uuid.uuid4()
        uuid_v = "8fb37bd6-aef1-4d7c-be3f-88bafef01308"
        shop_url = _fashionnovaurl.format(self._search_keyword, uuid_v)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        items = safe_grab(safe_json(response.text), ["items"])

        for item in items:
            item_url = safe_grab(item, ["u"])
            yield get_request(url=item_url, callback=self.parse_data, domain_url="https://www.fashionnova.com/")

    def parse_data(self, response):
        image_url = response.css("#large-thumb ::attr(src)").extract_first()
        title = extract_items(response.css("#product-info .title ::text").extract())
        description = "\n".join(list(set(response.css(".description .group .group-body ul li::text").extract())))
        price = response.css(".deal spanclass ::text").extract_first()
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
