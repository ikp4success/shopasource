import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _hmurl
from shops.shop_utilities.shop_names import ShopNames
from shops.shop_utilities.extra_function import generate_result_meta, extract_items
# from debug_app.manual_debug_funcs import printHtmlToFile


class HM(scrapy.Spider):
    name = ShopNames.HM.name
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _hmurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        item_url = response.css(".products-listing .product-item a ::attr(href)").extract_first()
        item_urls = response.css(".products-listing .product-item")
        for item in item_urls:
            item_text = item.css(".item-heading a ::text").extract_first() or ""
            if self._search_keyword.lower() in item_text.lower():
                best_item_link = item.css(".item-heading a ::attr(href)").extract_first() or ""
                item_url = best_item_link
                break
        yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url)

    def parse_data(self, response):
        image_url = response.css(".product-detail-main-image-container img ::attr(src)").extract_first()
        title = response.css(".product-item-headline ::text").extract_first()
        description = extract_items(response.css(".pdp-details-content ::text").extract())
        price = response.css(".product-item-price .price-value ::text").extract_first()
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
