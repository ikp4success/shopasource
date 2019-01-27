import re
import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _expressurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, safe_json, safe_grab, prepend_domain


class Express(scrapy.Spider):
    name = find_shop_configuration("EXPRESS")["name"]
    _search_keyword = None

    express_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        # "Referer": "",
        "DNT": "1",
        "Host": "",
        "Upgrade-Insecure-Requests": "1"
    }

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        api_host_name = "search.unbxdapi.com"
        # url_key = re.search(r'express_com-\"\:\"(.*?)\"', "".join(response.css("script ::text").extract()))
        api_key = "b3094e45838bdcf3acf786d57e4ddd98"
        shop_url = _expressurl.format(api_key, self._search_keyword, api_key)
        self.express_headers["Host"] = api_host_name
        self.express_headers["Accept"] = "*/*"
        self.express_headers["Referer"] = "https://www.express.com/exp/search?q={}".format(self._search_keyword)
        yield get_request(shop_url, self.parse_data, headers=self.express_headers)

    def parse_data(self, response):
        json_data = safe_json(response.text)
        t_data = safe_grab(json_data, ["response", "products"], default=[])
        for item in t_data:
            title = safe_grab(item, ["title"])
            image_url = safe_grab(item, ["imageUrl"])
            if image_url and len(image_url) > 0:
                image_url = image_url[0]

            colorSwatch = safe_grab(item, ["colorSwatch"])
            description = ""
            if colorSwatch:
                colorSwatchli = ""
                for csw in colorSwatch:
                    csw = re.search("(.*?)\:", csw)
                    if csw:
                        colorSwatchli += csw.group(1) + ", "
                description = "Available in " + colorSwatchli

            price = safe_grab(item, ["displaySalePrice"])
            if price == "$0.00":
                price = safe_grab(item, ["displayPrice"])
            url = prepend_domain(safe_grab(item, ["productUrl"]), response.url)
            yield generate_result_meta(shop_link=url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
