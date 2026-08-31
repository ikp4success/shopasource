from shops.shop_base import ShopBase


class Fashionnova(ShopBase):
    name = "FASHIONNOVA"
    use_browser_fetch = True

    def parse_results(self, response):
        items = response.css('[data-testid="product-card"]')
        for item in items:
            item_url = item.css(
                '[data-testid="product-card-link"] ::attr(href)'
            ).extract_first()
            item_url = self.prepend_domain(item_url, response.url)
            title = item.css(
                '[data-testid="product-card-link"] ::attr(aria-label)'
            ).extract_first()
            if title and title.startswith("Go to "):
                title = title[len("Go to ") :]
            price = item.css(
                '[data-testid="product-card-price-regular"] ::text'
            ).extract_first()
            image_url = item.css("img ::attr(src)").extract_first()

            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description="",
            )
