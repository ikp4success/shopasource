from shops.shop_base import ShopBase


class Biink(ShopBase):
    name = "BIINK"

    def parse_data(self, response):
        items = response.css(".product-wrap")

        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            image_url = item.css(".image__container img ::attr(src)").extract_first()
            if image_url:
                image_url = image_url.replace("100x", "900x")
            title = self.extract_items(item.css("span.title ::text").extract())
            description = ""
            price = item.css("span.money ::text").extract_first()
            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=description)
