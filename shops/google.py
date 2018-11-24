import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _googleurl
from shops.shop_utilities.shop_names import ShopNames
from shops.shop_utilities.extra_function import generate_result_meta, prepend_domain, match_sk
# from debug_app.manual_debug_funcs import printHtmlToFile


class Google(scrapy.Spider):
    name = ShopNames.GOOGLE.name
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _googleurl.format(self._search_keyword)
        yield get_request(shop_url, self.parse_data)

    def parse_data(self, response):
        items = response.css(".sh-dlr__list-result")
        for item in items:
            title = item.css(".eIuuYe a ::text").extract_first()
            if match_sk(self._search_keyword, title):
                link = prepend_domain(item.css(".eIuuYe a ::attr(href)").extract_first(), "https://www.google.com/")
                image_url = item.css(".MUQY0 img ::attr(src)").extract_first()
                description = ""
                price = item.css("span.O8U6h ::text").extract_first()
                if price is not None:
                    price = price.replace("used", "")
                yield generate_result_meta(shop_link=link, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)