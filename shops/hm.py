from shops.shop_base import ShopBase


class Hm(ShopBase):
    name = "HM"

    def parse_results(self, response):
        items = response.css(".products-listing .product-item")

        for item in items:
            item_url = item.css(".item-heading a ::attr(href)").extract_first()
            yield self.get_request(
                url=item_url, callback=self.parse_data, domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css(
            ".product-detail-main-image-container img ::attr(src)"
        ).extract_first()
        title = response.css(".product-item-headline ::text").extract_first()
        description = self.extract_items(
            response.css(".pdp-details-content ::text").extract()
        )
        price = response.css(".product-item-price .price-value ::text").extract_first()
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
