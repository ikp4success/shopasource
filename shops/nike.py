from shops.shop_base import ShopBase


class Nike(ShopBase):
    name = "NIKE"
    use_direct_fetch = True

    def parse_results(self, response):
        items = response.css('[data-testid="product-card"]')
        for item in items:
            item_url = item.css(
                'a[data-testid="product-card__link-overlay"] ::attr(href)'
            ).extract_first()
            title = self.extract_items(
                item.css(".product-card__title ::text").extract()
            )
            subtitle = self.extract_items(
                item.css(".product-card__subtitle ::text").extract()
            )
            price = (
                item.css('[data-testid="product-price-reduced"] ::text').extract_first()
                or item.css('[data-testid="product-price"] ::text').extract_first()
            )
            image_url = item.css(
                ".product-card__hero-image ::attr(src)"
            ).extract_first()

            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=subtitle,
            )
