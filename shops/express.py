import re

from shops.shop_base import ShopBase


class Express(ShopBase):
    name = "EXPRESS"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        # "Referer": "",
        "DNT": "1",
        "Host": "",
        "Upgrade-Insecure-Requests": "1",
    }

    def start_requests(self):
        api_host_name = "search.unbxdapi.com"
        # url_key = re.search(r'express_com-\"\:\"(.*?)\"', "".join(response.css("script ::text").extract()))
        api_key = "b3094e45838bdcf3acf786d57e4ddd98"
        shop_url = self.shop_url.format(api_key, self._search_keyword, api_key)
        self.headers["Host"] = api_host_name
        self.headers["Accept"] = "*/*"
        self.headers["Referer"] = "https://www.express.com/exp/search?q={}".format(
            self._search_keyword
        )
        yield self.get_request(shop_url, self.parse_data, headers=self.headers)

    def parse_data(self, response):
        json_data = self.safe_json(response.text)
        t_data = self.safe_grab(json_data, ["response", "products"], default=[])
        for item in t_data:
            title = self.safe_grab(item, ["title"])
            image_url = self.safe_grab(item, ["imageUrl"])
            if image_url and len(image_url) > 0:
                image_url = image_url[0]

            colorSwatch = self.safe_grab(item, ["colorSwatch"])
            description = ""
            if colorSwatch:
                colorSwatchli = ""
                for csw in colorSwatch:
                    csw = re.search(r"(.*?)\:", csw)
                    if csw:
                        colorSwatchli += csw.group(1) + ", "
                description = "Available in " + colorSwatchli

            price = self.safe_grab(item, ["displaySalePrice"])
            if price == "$0.00":
                price = self.safe_grab(item, ["displayPrice"])
            url = self.prepend_domain(
                self.safe_grab(item, ["productUrl"]), response.url
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
