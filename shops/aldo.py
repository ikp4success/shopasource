import re

from shops.shop_base import ShopBase


class ALDO(ShopBase):
    name = "ALDO"
    headers = {
        "Host": "www.aldoshoes.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.aldoshoes.com/us/en_US/",
        "TE": "Trailers",
        "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0",
    }

    def start_requests(self):
        shop_url = "https://www.aldoshoes.com/us/en_US/"
        yield self.get_request(
            shop_url, callback=self.get_products, headers=self.headers
        )

    def get_products(self, response):
        yield self.get_request(self.shop_url, callback=self.get_best_link)

    def get_best_link(self, response):
        items = "".join(response.css("script ::text").extract())
        items = re.search("__INITIAL_STATE__ =(.*)", items)
        if items:
            items = self.safe_grab(
                self.safe_json(items.group(1)), ["products"], default=[]
            )
            products = self.safe_grab(items, ["byCode"], default={})
            for _, v in products.items():
                item_url = "https://www.aldoshoes.com/us/en_US/" + self.safe_grab(
                    v, ["url"], default=""
                )
                yield self.get_request(
                    url=item_url,
                    callback=self.parse_data,
                    domain_url=response.url,
                    headers=self.aldo_headers,
                    meta={"dont_redirect": "True"},
                )

    def parse_data(self, response):
        image_url = response.css(
            ".c-carousel-product-overview img ::attr(src)"
        ).extract_first()
        title = self.extract_items(
            response.css(
                ".c-product-detail__info .c-heading__dash-wrap .c-markdown ::text"
            ).extract()
        )
        description = self.extract_items(
            response.css(".c-product-detail__info ::text").extract()
        )
        price = response.css(".c-product-price__formatted-price ::text").extract_first()
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
