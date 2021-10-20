import re

from shops.shop_base import ShopBase


class Nordstrom(ShopBase):
    name = "NORDSTROM"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Referer": "shop.nordstrom.com",
        "DNT": "1",
        "Host": "https://shop.nordstrom.com/",
        "Upgrade-Insecure-Requests": "1",
    }

    image_url = "https://n.nordstrommedia.com/ImageGallery/store/product/Zoom{}?h=365&w=240&dpr=2&quality=45&fit=fill&fm=jpg"

    def parse_results(self, response):
        api_host_name = "query.ecommerce.api.nordstrom.com"
        api_key = re.search(r"QueryServiceApiKey\"\:\"(.*?)\"", response.text)
        if api_key:
            api_key = api_key.group(1)
            self.nordstrom_headers["Currency-Code"] = "USD"
            self.nordstrom_headers["Host"] = api_host_name
            self.nordstrom_headers["Accept"] = "*/*"
            self.nordstrom_headers["Authorization"] = "apikey " + api_key
            self.nordstrom_headers["Referer"] = response.url
            self.nordstrom_headers["NordApiVersion"] = "1"
            api_url = "https://query.ecommerce.api.nordstrom.com/api/queryresults/keywordsearch/?top=40&IncludeFacets=false&Keyword={}".format(
                self._search_keyword
            )
            yield self.get_request(
                api_url, self.parse_data, headers=self.nordstrom_headers
            )

    def parse_data(self, response):
        json_data = self.safe_json(response.text)
        t_data = self.safe_grab(json_data, ["Products"], default=[])
        for item in t_data:
            title = self.safe_grab(item, ["Name"])
            media = self.safe_grab(item, ["Media"])
            if media and len(media) > 0:
                image_url = self.image_url.format(self.safe_grab(media[0], ["Path"]))
            else:
                image_url = None
            description = self.safe_grab(item, ["BrandLabelName"])
            price = self.safe_grab(
                item, ["Price", "CurrentMaxPrice"]
            ) or self.safe_grab(item, ["Price", "OriginalMaxPrice"])
            url = (
                "https://shop.nordstrom.com/s/"
                + self.safe_grab(item, ["PathAlias"])
                + "/"
                + str(self.safe_grab(item, ["Id"]))
            )
            yield self.generate_result_meta(
                shop_link=url,
                image_url=image_url,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=description,
            )
