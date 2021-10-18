from shops.shop_base import ShopBase


class Stylerunner(ShopBase):
    name = "STYLERUNNER"

    def parse_results(self, response):
        for item in response.css(".facets-item-cell-grid"):
            item_url = self.prepend_domain(
                item.css("a ::attr(href)").extract_first(), response.url
            )
            image_url = item.css(
                ".facets-item-cell-grid-image ::attr(src)"
            ).extract_first()
            title = self.extract_items(
                item.css(".facets-item-cell-grid-title ::text").extract()
            )
            description = title
            price = item.css(".item-views-price-lead ::attr(data-rate)").extract_first()

            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=description,
            )
