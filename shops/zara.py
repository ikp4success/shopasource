from shops.shop_base import ShopBase


class ZARA(ShopBase):
    name = "ZARA"

    def parse_data(self, response):
        json_data = self.safe_json(response.text)
        t_data = self.safe_grab(json_data, ["products"], default=[])
        for item in t_data:
            title = self.safe_grab(item, ["detail", "name"])
            image_url = None
            xmedia = self.safe_grab(item, ["xmedia"])
            if xmedia and len(xmedia) > 0:
                xmedia = xmedia[0]
                path_img = self.safe_grab(xmedia, ["path"])
                image_name = self.safe_grab(xmedia, ["name"])
            image_url = "https://static.zara.net/photos///" + path_img + "/" + image_name + ".jpg"
            description = self.safe_grab(item, ["section"]) + ", " + self.safe_grab(item, ["kind"])
            price = self.safe_grab(item, ["price"])
            if price and len(str(price)) > 2:
                price = str(price)
                lst_2 = price[len(price) - 2] + price[len(price) - 1]
                price = price.replace(lst_2, "." + lst_2)
            url = (
                "https://www.zara.com/us/en/" + title.replace(" ", "-") + "-p" +
                self.safe_grab(item, ["seo", "seoProductId"], default="") + ".html?v1=" +
                self.safe_grab(item, ["seo", "discernProductId"], default="")
            )
            yield self.generate_result_meta(
                shop_link=url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=description
            )
