from shops.shop_base import ShopBase


class Kohls(ShopBase):
    name = "KOHLS"

    def parse_results(self, response):
        items = response.css(".products_grid")

        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            yield self.get_request(
                url=item_url,
                callback=self.parse_data,
                domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css(".pdp-hero-image img ::attr(src)").extract_first()
        title = self.extract_items(response.css(".pdp-product-title ::text").extract())
        description = self.extract_items(response.css(".accordion-segment-content ::text").extract())
        price = response.css(".main-price ::text").extract_first()
        alt_price = response.css(".regorg-small ::text").extract_first()
        if price is None and not alt_price:
            price = alt_price.replace("Regular", "")
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description
        )
