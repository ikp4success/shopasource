from shops.shop_base import ShopBase


class Adidas(ShopBase):
    name = "ADIDAS"

    headers = {
        "Host": "www.adidas.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
        "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0",
    }

    def parse_results(self, response):
        json_data = self.safe_json(response.text)
        items = self.safe_grab(json_data, ["items"], default=[])
        for item in items:
            item_url = self.safe_grab(item, ["link"])
            yield self.get_request(
                url=item_url, callback=self.parse_data, domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css(
            ".item_wrapper___1Tz65 img ::attr(src)"
        ).extract_first()
        brand = self.extract_items(
            response.css("h1[data-auto-id='product-category'] ::text").extract()
        )
        title = (
            brand
            + " "
            + self.extract_items(
                response.css("h1[data-auto-id='product-title'] ::text").extract()
            )
        ).strip()
        description = self.extract_items(
            response.css(".content___3jRA5 p ::text").extract()
        )
        price = response.css(".pricing-and-style__sale-price ::text").extract_first()
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
