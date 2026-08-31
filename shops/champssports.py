from shops.shop_base import ShopBase


class Champssports(ShopBase):
    name = "CHAMPSSPORTS"
    use_browser_fetch = True

    def parse_results(self, response):
        items = response.css("div.ProductCard")
        for item in items:
            item_url = item.css(".ProductCard-link ::attr(href)").extract_first()
            item_url = self.prepend_domain(item_url, response.url)
            title = item.css(".ProductName-primary ::text").extract_first()
            price = item.css('[data-testid="ProductPrice"] ::text').extract_first()
            image_url = item.css(
                ".ProductCard-image--primary ::attr(src)"
            ).extract_first()

            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description="",
            )
