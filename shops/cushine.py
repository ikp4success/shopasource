from shops.shop_base import ShopBase


class Cushine(ShopBase):
    name = "CUSHINE"
    _search_keyword = None

    def parse_results(self, response):
        json_data = self.safe_json(response.text)
        t_data = self.safe_grab(json_data, ["response", "docs"], default=[])

        for item in t_data:
            title = self.safe_grab(item, ["name"])
            image_url = self.safe_grab(item, ["image_varchar"])[0]
            url = self.safe_grab(item, ["url"])
            description = self.safe_grab(item, ["description"])
            price = self.safe_grab(item, ["final_price"])
            yield self.generate_result_meta(
                shop_link=url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=description,
            )
