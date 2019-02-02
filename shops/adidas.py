import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _adidasurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, safe_json, safe_grab


class Adidas(scrapy.Spider):
    name = find_shop_configuration("ADIDAS")["name"]
    _search_keyword = None

    adidas_headers = {
        "Host": "www.adidas.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
        "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
    }

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _adidasurl.format(self._search_keyword, headers=self.adidas_headers)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        json_data = safe_json(response.text)
        items = safe_grab(json_data, ["items"], default=[])
        for item in items:
            item_url = safe_grab(item, ["link"])
            yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url)

    def parse_data(self, response):
        image_url = response.css(".item_wrapper___1Tz65 img ::attr(src)").extract_first()
        brand = extract_items(response.css("h1[data-auto-id='product-category'] ::text").extract())
        title = (brand + " " + extract_items(response.css("h1[data-auto-id='product-title'] ::text").extract())).strip()
        description = extract_items(response.css(".content___3jRA5 p ::text").extract())
        price = response.css(".pricing-and-style__sale-price ::text").extract_first()
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
