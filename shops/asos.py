from shops.shop_base import ShopBase


class Asos(ShopBase):
    name = "ASOS"
    use_browser_fetch = True

    def parse_results(self, response):
        items = response.css('li[id^="product-"]')
        for item in items:
            item_url = item.css("a[aria-label] ::attr(href)").extract_first()
            aria_label = item.css("a[aria-label] ::attr(aria-label)").extract_first()
            title, price = aria_label, None
            if aria_label and ", Price " in aria_label:
                title, price = aria_label.rsplit(", Price ", 1)
            image_url = item.css("img ::attr(src)").extract_first()
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
