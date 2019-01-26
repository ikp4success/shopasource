import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _saksfifthavenueurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items


class SaksFifthAvenue(scrapy.Spider):
    name = find_shop_configuration("SAKSFIFTHAVENUE")["name"]
    _search_keyword = None
    headers = {
        "Host": "www.saksfifthavenue.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
        "referer": "https://www.saksfifthavenue.com/Entry.jsp",
        "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
    }

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _saksfifthavenueurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link, headers=self.headers)

    def get_best_link(self, response):
        items = response.css(".pa-product-large")

        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url)

    def parse_data(self, response):
        image_url = response.css(".product__media ::attr(data-image)").extract_first()
        brand = extract_items(response.css("h2.product-overview__brand ::text").extract())
        title = (brand + " " + extract_items(response.css("h1.product-overview__short-description ::text").extract())).strip()
        description = extract_items(response.css(".product-description ::text").extract())
        price = response.css(".product-pricing__price").xpath("//span[@itemprop='price']").css("::attr(content)").extract_first() or \
            response.css(".product-pricing__price").xpath("//span[@itemprop='lowPrice']").css("::attr(content)").extract_first()
        alt_price = extract_items(response.css(".product-pricing__price span::text").extract())
        price = price or alt_price
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
