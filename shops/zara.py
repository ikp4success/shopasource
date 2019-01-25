import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _zaraurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, safe_json, safe_grab


class ZARA(scrapy.Spider):
    name = find_shop_configuration("ZARA")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _zaraurl.format(self._search_keyword)
        yield get_request(shop_url, self.parse_data)

    def parse_data(self, response):
        json_data = safe_json(response.text)
        t_data = safe_grab(json_data, ["products"], default=[])
        for item in t_data:
            title = safe_grab(item, ["detail", "name"])
            image_url = None
            xmedia = safe_grab(item, ["xmedia"])
            if xmedia and len(xmedia) > 0:
                xmedia = xmedia[0]
                path_img = safe_grab(xmedia, ["path"])
                image_name = safe_grab(xmedia, ["name"])
            image_url = "https://static.zara.net/photos///" + path_img + "/" + image_name + ".jpg"
            description = safe_grab(item, ["section"]) + ", " + safe_grab(item, ["kind"])
            price = safe_grab(item, ["price"])
            if price and len(str(price)) > 2:
                price = str(price)
                lst_2 = price[len(price) - 2] + price[len(price) - 1]
                price = price.replace(lst_2, "." + lst_2)
            url = "https://www.zara.com/us/en/" + title.replace(" ", "-") + "-p" + safe_grab(item, ["seo", "seoProductId"], default="") + ".html?v1=" + safe_grab(item, ["seo", "discernProductId"], default="")
            yield generate_result_meta(shop_link=url,
                                       image_url=image_url,
                                       shop_name=self.name,
                                       price=price,
                                       title=title,
                                       searched_keyword=self._search_keyword,
                                       content_description=description)
