from shops.shop_base import ShopBase


class Amazon(ShopBase):
    name = "AMAZON"
    use_browser_fetch = True

    def parse_results(self, response):
        items = response.css('div[data-component-type="s-search-result"]')

        for item in items:
            item_url = item.css('a[href*="/dp/"] ::attr(href)').extract_first()
            if not item_url:
                # Sponsored placements link through an ad-redirect URL instead of
                # a real /dp/ product link - skip rather than save a dead link.
                continue
            item_url = self.prepend_domain(item_url, response.url)
            title = item.css("img.s-image ::attr(alt)").extract_first()
            price = item.css(".a-price .a-offscreen ::text").extract_first()
            image_url = item.css("img.s-image ::attr(src)").extract_first()

            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description="",
            )
