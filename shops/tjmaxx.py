from shops.shop_base import ShopBase


class TjMaxx(ShopBase):
    name = "TJMAXX"

    def parse_results(self, response):
        items = response.css(".product-inner")
        for item in items:
            item_url = item.css(
                ".product-image a.product-link ::attr(href)"
            ).extract_first()
            yield self.get_request(
                url=item_url, callback=self.parse_data, domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css(
            ".main-image ::attr(src), product-image img ::attr(src)"
        ).extract_first()
        title = "{} {}".format(
            response.css(".product-brand ::text").extract_first() or "",
            response.css(".product-title ::text").extract_first() or "",
        )
        description = self.extract_items(
            response.css(".description-list li ::text").extract()
        )
        price = self.extract_items(
            response.css(".price .product-price ::text").extract()
        )
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
