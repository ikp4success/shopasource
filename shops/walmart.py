from shops.shop_base import ShopBase


class Walmart(ShopBase):
    name = "WALMART"
    use_browser_fetch = True

    def parse_results(self, response):
        # PerimeterX was still actively challenging this IP as of the last check,
        # so these selectors are unverified against live markup - re-check against
        # a real render once the block clears (the fetch mechanism itself is
        # confirmed working: it got a real "wallet - Walmart.com" page earlier).
        items = response.css("[data-item-id]")

        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            item_url = self.prepend_domain(item_url, response.url)
            title = item.css(
                '[data-automation-id="product-title"] ::text'
            ).extract_first()
            price = item.css(
                '[data-automation-id="product-price"] ::text'
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
