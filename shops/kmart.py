from shops.shop_base import ShopBase


class Kmart(ShopBase):
    name = "KMART"
    use_browser_fetch = True

    def parse_results(self, response):
        items = response.css("app-product-card")
        for item in items:
            item_url = item.css('a[href*="/p-"] ::attr(href)').extract_first()
            item_url = self.prepend_domain(item_url, response.url)
            title = item.css(".img-fluid-product ::attr(alt)").extract_first()
            price = item.css(".final-price-display ::text").extract_first()
            image_url = item.css(".img-fluid-product ::attr(src)").extract_first()

            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description="",
            )
