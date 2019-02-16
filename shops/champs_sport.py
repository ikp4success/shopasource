from shops.shop_base import ShopBase


class ChampSports(ShopBase):
    name = "CHAMPSPORTS"

    def parse_data(self, response):
        import pdb; pdb.set_trace()
        # json_data = ssafe_json(response.text)
        # t_data = safe_grab(json_data, ["search_response", "items", "Item"], default=[])
        #
        # for item in t_data:
        #     title = safe_grab(item, ["title"])
        #     images = safe_grab(item, ["images"])[0]
        #     base_url = safe_grab(images, ["base_url"])
        #     primary = safe_grab(images, ["primary"])
        #     image_url = "{}{}".format(base_url, primary)
        #     description = safe_grab(item, ["description"])
        #     price = safe_grab(item, ["list_price", "formatted_price"]) or safe_grab(item, ["offer_price", "formatted_price"])
        #     url = prepend_domain(safe_grab(item, ["url"]), "https://www.target.com")
        #     yield generate_result_meta(shop_link=url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
