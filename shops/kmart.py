from shops.shop_base import ShopBase


class Kmart(ShopBase):
    name = "KMART"

    def parse_results(self, response):
        json_data = self.safe_json(response.text)
        t_data = self.safe_grab(json_data, ["data", "products"], default=[])
        for item in t_data:
            item_url = "https://www.kmart.com/content/pdp/config/products/v1/products/{}?site=kmart".format(
                self.safe_grab(item, ["sin"])
            )
            yield self.get_request(url=item_url, callback=self.parse_data)

    def parse_data(self, response):
        data = self.safe_grab(self.safe_json(response.text), ["data"], default={})
        image_url = self.safe_grab(
            self.safe_grab(
                self.safe_grab(data, ["product", "assets", "imgs"])[0], ["vals"]
            )[0],
            ["src"],
        )
        title = self.safe_grab(data, ["product", "name"])
        description = self.safe_grab(data, ["product", "seo", "description"])
        price = "${}".format(self.safe_grab(data, ["offerranking", "totalPrice"]))
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
