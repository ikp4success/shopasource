import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _stylerunnerurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, prepend_domain
# from debug_app.manual_debug_funcs import printHtmlToFile


class StyleRunner(scrapy.Spider):
    name = find_shop_configuration("STYLERUNNER")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _stylerunnerurl.format(self._search_keyword)
        yield get_request(shop_url, self.parse_data)

    def parse_data(self, response):
        for item in response.css(".facets-item-cell-grid"):
            item_url = prepend_domain(item.css("a ::attr(href)").extract_first(), response.url)
            image_url = item.css(".facets-item-cell-grid-image ::attr(src)").extract_first()
            title = extract_items(item.css(".facets-item-cell-grid-title ::text").extract())
            description = title
            price = item.css(".item-views-price-lead ::attr(data-rate)").extract_first()

            yield generate_result_meta(shop_link=item_url,
                                       image_url=image_url,
                                       shop_name=self.name,
                                       price=price,
                                       title=title,
                                       searched_keyword=self._search_keyword,
                                       content_description=description)
