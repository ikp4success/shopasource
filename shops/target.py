from shops.shop_base import ShopBase


class Target(ShopBase):
    name = "TARGET"

    def parse_results(self, response):
        json_data = self.safe_json(response.text)
        t_data = self.safe_grab(
            json_data, ["search_response", "items", "Item"], default=[]
        )

        for item in t_data:
            title = self.safe_grab(item, ["title"])
            images = self.safe_grab(item, ["images"])[0]
            base_url = self.safe_grab(images, ["base_url"])
            primary = self.safe_grab(images, ["primary"])
            image_url = "{}{}".format(base_url, primary)
            description = self.safe_grab(item, ["description"])
            price = self.safe_grab(
                item, ["list_price", "formatted_price"]
            ) or self.safe_grab(item, ["offer_price", "formatted_price"])
            url = self.prepend_domain(
                self.safe_grab(item, ["url"]), "https://www.target.com"
            )
            yield self.generate_result_meta(
                shop_link=url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=description,
            )
