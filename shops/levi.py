from shops.shop_base import ShopBase


class LEVI(ShopBase):
    name = "LEVI"

    def parse_results(self, response):
        items = response.css(".product-item")

        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            image_url = item.css("img.responsive-image ::attr(src)").extract_first()
            title = self.extract_items(item.css(".details .name ::text").extract())
            description = " ".join(item.css(".details .color-name ::text").extract())
            price = item.css(".details .price .hard-sale ::text").extract_first() or \
                item.css(".details .price .soft-sale ::text").extract_first() or \
                item.css(".details .price .regular ::text").extract_first()
            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=description
            )
