import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _grouponurl
from shops.shop_utilities.shop_names import ShopNames
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, match_sk


class GroupOn(scrapy.Spider):
    # name = ShopNames.GROUPON.name
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _grouponurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        item_url = None
        items = response.css("#pull-results .card-ui")

        for item in items:
            item_title = extract_items(item.css(".cui-udc-details .cui-udc-title-with-subtitle ::text").extract())
            if match_sk(self._search_keyword, item_title):
                item_url = item.css("a ::attr(href)").extract_first()
                yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url)

    def parse_data(self, response):
        image_url = response.css(".sleepy-load ::attr(src)").extract_first()
        title = extract_items(response.css(".deal-page-title ::text").extract())
        description = extract_items(response.css(".pitch ::text").extract())
        price = response.css(".price-discount-wrapper ::text, .breakout-option-value ::text").extract_first()
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
