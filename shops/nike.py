import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _nikeurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, safe_grab


class Nike(scrapy.Spider):
    name = find_shop_configuration("NIKE")["name"]
    _search_keyword = None

    nike_headers = {
        "Host": "store.nike.com",
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
        shop_url = _nikeurl.format(self._search_keyword, self._search_keyword)
        yield get_request(shop_url, self.get_best_link, headers=self.nike_headers)

    def get_best_link(self, response):
        items = response.css(".grid-item-box")
        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            title = extract_items(response.css(".product-name ::text").extract())
            price = response.css(".product-price span ::text").extract_first()
            meta = {
                "t": title,
                "p": price
            }
            yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url, meta=meta)

    def parse_data(self, response):
        image_url = response.css(".colorway-images .bg-medium-grey ::attr(src)").extract_first()
        if image_url:
            image_url = image_url.replace("144", "1280")
        title = extract_items(response.css(".ncss-base ::text").extract()) or safe_grab(response.meta, ["t"])
        description = extract_items(response.css(".description-preview ::text").extract())
        price = response.css("div[data-test='product-price'] ::text").extract_first() or safe_grab(response.meta, ["p"])
        yield generate_result_meta(shop_link=response.url,
                                   image_url=image_url,
                                   shop_name=self.name,
                                   price=price,
                                   title=title,
                                   searched_keyword=self._search_keyword,
                                   content_description=description)
