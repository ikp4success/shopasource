import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _nordstormrackurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, safe_json, safe_grab


class NordstromRack(scrapy.Spider):
    name = find_shop_configuration("NORDSTROMRACK")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _nordstormrackurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        json_data = safe_json(response.text)
        items = safe_grab(json_data, ["_embedded", "http://hautelook.com/rels/products"], default=[])
        for item in items:
            item_url = safe_grab(item, ["_links", "alternate", "href"]).replace("{?color,size}", "")
            yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url)

    def parse_data(self, response):
        image_url = response.css(".image-zoom__image ::attr(src)").extract_first()
        brand = extract_items(response.css(".product-details__brand product-details__brand--link ::text").extract())
        title = (brand + " " + extract_items(response.css(".product-details__title-name ::text").extract())).strip()
        description = extract_items(response.css(".product-details-section__definition ::text").extract())
        price = response.css(".pricing-and-style__sale-price ::text").extract_first()
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
