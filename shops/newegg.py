import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _neweggurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, safe_grab
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
        if "areyouahuman" in response.text.lower():
            yield None
            return
        items = response.css(".item-container")
        for item in items:
            item_text = item.css("a ::text").extract_first()
            item_url = item.css("a ::attr(href)").extract_first()

            if "areyouahuman" in item_url:
                break

            prize = "{}{}".format(item.css(".price-current strong").extract_first(), item.css(".price-current sup").extract_first())
            meta = {
                "p": prize,
                "t": item_text,
                "img": item.css("img ::attr(src)").extract_first()
            }
            yield get_request(url=item_url,
                              callback=self.parse_data,
                              domain_url=response.url, meta=meta)

    def parse_data(self, response):
        price = safe_grab(response.meta, ["p"])
        price = "${}".format(price)
        title = safe_grab(response.meta, ["t"])
        image_url = safe_grab(response.meta, ["img"])
        if "areyouahuman" not in response.url:
            image_url = response.css(".mainSlide img ::attr(src)").extract_first()
            title = extract_items(response.css("#grpDescrip_h ::text").extract()) or title
            description = "{}\n{}".format(extract_items(response.css(".itemDesc ::text").extract()), extract_items(response.css(".itemColumn ::text").extract())).rstrip().strip()

        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
