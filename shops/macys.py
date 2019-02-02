import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _macysurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, extract_items, safe_grab


class Macys(scrapy.Spider):
    name = find_shop_configuration("MACYS")["name"]
    _search_keyword = None
    macys_headers = {
        "Host": "www.macys.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
        "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
        # "If-None-Match": 'W/"1a0905-84p23IFmm2k/vykK/3NpICzo2N8"',
    }

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _macysurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link, headers=self.macys_headers)

    def get_best_link(self, response):
        items = response.css(".items .productThumbnailItem")

        for item in items:
            item_url = item.css("a.productDescLink ::attr(href)").extract_first()
            price = "".join(item.css(".prices span ::text").extract())
            yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url, meta={"price": price})

    def parse_data(self, response):
        image_url = response.css(".main-image img ::attr(src)").extract_first()
        title = extract_items(response.xpath("//div[@data-auto='product-title']").css("::text").extract())
        description = extract_items(response.xpath("//div[@data-el='product-details']").css("::text").extract())
        price = response.css(".price ::text").extract_first() or safe_grab(response.meta, ["price"])
        yield generate_result_meta(shop_link=response.url,
                                   image_url=image_url,
                                   shop_name=self.name,
                                   price=price,
                                   title=title,
                                   searched_keyword=self._search_keyword,
                                   content_description=description)
