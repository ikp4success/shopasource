from shops.shop_base import ShopBase


class Forever21(ShopBase):
    name = "FOREVER21"

    def start_requests(self):
        shop_url = self.shop_url.replace("{SKEY}", self._search_keyword)
        yield self.get_request(shop_url, self.parse_data)

    def parse_data(self, response):
        json_data = self.safe_json(response.text)
        t_data = self.safe_grab(json_data, ["response", "docs"], default=[])

        for item in t_data:
            title = self.safe_grab(item, ["title"])
            image_url = self.safe_grab(item, ["thumb_image"])
            description = title
            price = self.safe_grab(item, ["sale_price"]) or self.safe_grab(item, ["price"])
            url = self.prepend_domain(self.safe_grab(item, ["url"]), "https://www.forever21.com")
            yield self.generate_result_meta(
                shop_link=url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=description
            )
