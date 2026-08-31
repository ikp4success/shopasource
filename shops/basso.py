from shops.shop_base import ShopBase


class Basso(ShopBase):
    name = "BASSO"

    def parse_results(self, response):
        items = response.css(".grid-product")
        for item in items:
            item_url = item.css(".grid-product__link ::attr(href)").extract_first()
            item_url = self.prepend_domain(item_url, response.url)
            title = item.css(".grid-product__title ::text").extract_first()
            price = item.css(".grid-product__price .money ::text").extract()
            price = price[-1].strip() if price else None
            bgset = item.css("[data-bgset] ::attr(data-bgset)").extract_first()
            image_url = bgset.split(",")[0].strip().split(" ")[0] if bgset else None
            if image_url and image_url.startswith("//"):
                image_url = "https:" + image_url

            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description="",
            )
