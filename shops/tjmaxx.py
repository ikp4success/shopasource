from shops.shop_base import ShopBase


class Tjmaxx(ShopBase):
    name = "TJMAXX"
    use_browser_fetch = True

    def parse_results(self, response):
        items = response.css(".product-inner")
        for item in items:
            item_url = item.css(
                ".product-image a.product-link ::attr(href)"
            ).extract_first()
            item_url = self.prepend_domain(item_url, response.url)
            title = item.css(".main-image ::attr(alt)").extract_first()
            price = item.css(".product-price ::text").extract_first()
            image_url = item.css(".main-image ::attr(src)").extract_first()
            image_url = self.prepend_domain(image_url, response.url)

            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description="",
            )
