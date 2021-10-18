from shops.shop_base import ShopBase


class Nordstromrack(ShopBase):
    name = "NORDSTROMRACK"

    def parse_results(self, response):
        json_data = self.safe_json(response.text)
        items = self.safe_grab(
            json_data, ["_embedded", "http://hautelook.com/rels/products"], default=[]
        )
        for item in items:
            item_url = self.safe_grab(item, ["_links", "alternate", "href"]).replace(
                "{?color,size}", ""
            )
            yield self.get_request(
                url=item_url, callback=self.parse_data, domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css(".image-zoom__image ::attr(src)").extract_first()
        brand = self.extract_items(
            response.css(
                ".product-details__brand product-details__brand--link ::text"
            ).extract()
        )
        title = (
            brand
            + " "
            + self.extract_items(
                response.css(".product-details__title-name ::text").extract()
            )
        ).strip()
        description = self.extract_items(
            response.css(".product-details-section__definition ::text").extract()
        )
        price = response.css(".pricing-and-style__sale-price ::text").extract_first()
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
