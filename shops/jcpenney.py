import scrapy
# import uuid

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _jcpenneyurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, match_sk, safe_json, safe_grab


class JcPenney(scrapy.Spider):
    name = find_shop_configuration("JCPENNEY")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _jcpenneyurl.format(self._search_keyword, self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        items = safe_grab(safe_json(response.text), ["organicZoneInfo", "products"])
        for item in items:
            title = safe_grab(item, ["name"])
            if match_sk(self._search_keyword, title):
                item_url = safe_grab(item, ["pdpUrl"])
                price = safe_grab(item, ["fpacPriceMax"])
                yield get_request(url=item_url, callback=self.parse_data, domain_url="https://www.jcpenney.com", meta={"pc": price})

    def parse_data(self, response):
        image_url = response.css("._3JaiK ::attr(src)").extract_first()
        title = extract_items(response.css("._37-TG ::text").extract())
        description = "\n".join(list(set(response.css("#productDescriptionParent .o3cEt ::text").extract())))
        price = safe_grab(response.meta, ["pc"])
        if price:
            price = "${}".format(price)
        else:
            price = None
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
