import scrapy
import re

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _dicksportinggoodsurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, safe_grab


class DicksSportingGoods(scrapy.Spider):
    name = find_shop_configuration("DICKSSPORTINGGOODS")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _dicksportinggoodsurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        items = response.css(".product-grid")
        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            price = item.css(".final-price ::text").extract_first() or item.css(".was-item-price ::text").extract_first()
            if price:
                price = price.replace("NOW:", "").replace("WAS:", "")
                if "-" in price:
                    try:
                        price = re.search("(.*)-", price).group(1)
                    except Exception:
                        continue
            yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url, meta={"p": price})

    def parse_data(self, response):
        image_url = response.css("#image-viewer-container img ::attr(src)").extract_first()
        title = extract_items(response.css("h1.product-title ::text").extract())
        description = extract_items(response.css("div[itemprop='description'] ::text").extract())
        price = response.css("span[itemprop='price'] ::text").extract_first() or safe_grab(response.meta, "p")
        yield generate_result_meta(shop_link=response.url,
                                   image_url=image_url,
                                   shop_name=self.name,
                                   price=price,
                                   title=title,
                                   searched_keyword=self._search_keyword,
                                   content_description=description)
