from shops.shop_base import ShopBase


class BestBuy(ShopBase):
    name = "BESTBUY"

    def parse_results(self, response):
        item_url = response.css(".sku-item .sku-header a ::attr(href)").extract_first()
        yield self.get_request(
            url=item_url, callback=self.parse_data, domain_url=response.url
        )

    def parse_data(self, response):
        image_url = response.css(
            ".product-gallery-static img ::attr(src)"
        ).extract_first()
        title = response.css("#sku-title ::text").extract_first()
        description = self.extract_items(
            response.css(".product-description ::text").extract()
        )
        price = response.css(".priceView-hero-price ::text").extract_first()
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
