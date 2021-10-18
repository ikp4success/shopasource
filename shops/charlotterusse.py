from shops.shop_base import ShopBase


class Charlotterusse(ShopBase):
    name = "CHARLOTTERUSSE"

    def parse_results(self, response):
        items = response.css(".grid-tile")

        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            yield self.get_request(
                url=item_url, callback=self.parse_data, domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css(".product-image img ::attr(src)").extract_first()
        title = self.extract_items(response.css("h1.product-name ::text").extract())
        description = self.extract_items(
            response.css(".product-description ::text").extract()
        )
        salesprice = "".join(
            response.css(".product-info-container .price-sales ::text").extract()
        ).replace("Sales Price", "")
        price = "".join(
            response.css(".product-info-container .price-standard ::text").extract()
        ).replace("Standard Price", "")
        if salesprice.strip():
            price = salesprice
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
