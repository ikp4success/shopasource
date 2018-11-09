import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _microcenterurl
from shops.shop_utilities.shop_names import ShopNames
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, safe_grab, get_best_item_by_match
# from debug_app.manual_debug_funcs import printHtmlToFile


class MicroCenter(scrapy.Spider):
    name = ShopNames.MICROCENTER.name
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _microcenterurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        item_urls = response.css(".product_wrapper")
        alt_query = "#hypProductH2_0 ::text"
        query = "#hypProductH2_0 ::attr(href)"
        item_url = get_best_item_by_match(items=item_urls, query=query, alt_query=alt_query, search_keyword=self._search_keyword)
        yield get_request(url=safe_grab(item_url, ["url"]), callback=self.parse_data, domain_url=response.url, meta={"ti": safe_grab(item_url, ["alt_item_sk"])})

    def parse_data(self, response):
        image_url = response.css(".image-slide ::attr(src)").extract_first()
        title = safe_grab(response.meta, ["ti"])
        description = "{}\n{}".format(extract_items(response.css(".content-wrapper div.inline ul ::text").extract()), extract_items(response.css(".content-wrapper div.inline p ::text").extract())).rstrip().strip()
        price = extract_items(response.css("#options-pricing #pricing ::text").extract())
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
