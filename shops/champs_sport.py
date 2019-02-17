from shops.shop_base import ShopBase


class ChampSports(ShopBase):
    name = "CHAMPSSPORTS"
    headers = {
        "Host": "www.champssports.com",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "X-FL-Request-ID": "ef6b7840-3224-11e9-b4b4-35385d7e9887"
    }

    def parse_results(self, response):
        json_data = self.safe_json(response.text)
        t_data = self.safe_grab(json_data, ["products"], default=[])

        for item in t_data:
            title = self.safe_grab(item, ["name"])
            image_url = self.safe_grab(item, ["images"])
            if image_url and len(image_url) > 0:
                image_url = self.safe_grab(image_url[0], ["url"])
            price = (
                self.safe_grab(item, ["price", "formattedValue"]) or
                self.safe_grab(item, ["originalPrice", "formattedValue"])
            )
            url_2nd = title.replace("-", "--").replace(" ", "-").replace("'", "-")
            sku = self.safe_grab(item, ["sku"])
            url_domain = "https://www.champssports.com/product/"
            url = "{}{}/{}.html".format(url_domain, url_2nd, sku)
            yield self.generate_result_meta(
                shop_link=url,
                image_url=image_url,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=""
            )
