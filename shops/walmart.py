import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _walmarturl
from shops.shop_utilities.shop_names import ShopNames
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, get_best_item_by_match, safe_grab
# from debug_app.manual_debug_funcs import printHtmlToFile


class Walmart(scrapy.Spider):
    name = ShopNames.WALMART.name
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _walmarturl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        item_urls = response.css("#searchProductResult .search-result-gridview-items li a")
        query = "::attr(href)"
        item_url = get_best_item_by_match(items=item_urls, search_keyword=self._search_keyword, query=query)
        yield get_request(url=safe_grab(item_url, ["url"]), callback=self.parse_data, domain_url=response.url)

    def parse_data(self, response):
        image_url = response.css(".prod-hero-image-image ::attr(src)").extract_first()
        title = response.css(".ProductTitle div ::text").extract_first()
        description = extract_items(response.css(".about-desc ::text").extract())
        price = response.css(".prod-PriceHero .price-characteristic ::text").extract_first() or ""
        price = "${}".format(price)
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
