from shops.shop_base import ShopBase


class Target(ShopBase):
    name = "TARGET"

    def parse_results(self, response):
        json_data = self.safe_json(response.text)
        t_data = self.safe_grab(
            json_data, ["data", "search", "products"], default=[]
        )

        for item in t_data:
            title = self.safe_grab(item, ["item", "product_description", "title"])
            image_url = self.safe_grab(item, ["item", "enrichment", "images", "primary_image_url"])
            descriptions = self.safe_grab(item, ["item", "product_description", "bullet_descriptions"])
            description = [descr.replace("<B>", "").replace("</B>", "") for descr in descriptions if descr]
            price = self.safe_grab(
                item, ["price", "current_retail"]
            )
            url = self.safe_grab(item, ["item", "enrichment", "buy_url"])
            yield self.generate_result_meta(
                shop_link=url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description="".join(description),
            )
