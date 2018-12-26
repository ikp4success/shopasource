import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _neweggurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, safe_grab, match_sk
# from debug_app.manual_debug_funcs import printHtmlToFile


class Newegg(scrapy.Spider):
    name = find_shop_configuration("NEWEGG")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _neweggurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        items = response.css(".item-container a")
        for item in items:
            item_text = item.css("::text").extract_first()
            if match_sk(self._search_keyword, item_text):
                item_url = item.css("::attr(href)").extract_first()
                prize = "{}{}".format(response.css(".price-current strong").extract_first(), response.css(".price-current sup").extract_first())
                yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url, meta={"p": prize, "t": item_text})

    def parse_data(self, response):
        image_url = response.css(".mainSlide img ::attr(src)").extract_first()
        title = response.css("#grpDescrip_h ::text").extract_first() or safe_grab(response.meta, ["t"])
        description = "{}\n{}".format(extract_items(response.css(".itemDesc ::text").extract()), extract_items(response.css(".itemColumn ::text").extract())).rstrip().strip()
        price = safe_grab(response.meta, ["p"])
        price = "${}".format(price)
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
