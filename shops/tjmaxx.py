import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _tjmaxxurl
from shops.shop_utilities.shop_names import ShopNames
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, get_best_item_by_match, safe_grab
# from debug_app.manual_debug_funcs import printHtmlToFile


class TjMaxx(scrapy.Spider):
    name = ShopNames.TJMAXX.name
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _tjmaxxurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        item_urls = response.css(".product-inner")
        query = ".product-image a.product-link ::attr(href)"
        alt_query = ".product-title ::text"
        item_url = get_best_item_by_match(items=item_urls, search_keyword=self._search_keyword, query=query, alt_query=alt_query)
        yield get_request(url=safe_grab(item_url, ["url"]), callback=self.parse_data, domain_url=response.url)

    def parse_data(self, response):
        image_url = response.css(".main-image ::attr(src)").extract_first()
        title = "{} {}".format(response.css(".product-brand ::text").extract_first() or "", response.css(".product-title ::text").extract_first() or "")
        description = extract_items(response.css(".description-list li ::text").extract())
        price = extract_items(response.css(".price .product-price ::text").extract())
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
