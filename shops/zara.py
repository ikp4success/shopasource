from shops.shop_base import ShopBase


class Zara(ShopBase):
    name = "ZARA"
    use_browser_fetch = True

    def parse_results(self, response):
        items = response.css("li.product-grid-product")
        for item in items:
            item_url = item.css(".product-link ::attr(href)").extract_first()
            title = item.css(
                ".product-grid-product-info__name h3 ::text"
            ).extract_first()
            price = item.css(".price-current__amount ::text").extract_first()
            image_url = item.css("img.media-image__image ::attr(src)").extract_first()

            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description="",
            )
