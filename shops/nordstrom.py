import re
import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _nordstormurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.shop_utilities.extra_function import generate_result_meta, safe_json, safe_grab


class NordStrom(scrapy.Spider):
    name = find_shop_configuration("NORDSTROM")["name"]
    _search_keyword = None

    nordstrom_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Referer": "shop.nordstrom.com",
        "DNT": "1",
        "Host": "https://shop.nordstrom.com/",
        "Upgrade-Insecure-Requests": "1"
    }

    image_url = "https://n.nordstrommedia.com/ImageGallery/store/product/Zoom{}?h=365&w=240&dpr=2&quality=45&fit=fill&fm=jpg"

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _nordstormurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_api_key)

    def get_api_key(self, response):
        api_host_name = "query.ecommerce.api.nordstrom.com"
        api_key = re.search(r'QueryServiceApiKey\"\:\"(.*?)\"', response.text)
        if api_key:
            api_key = api_key.group(1)
            self.nordstrom_headers["Currency-Code"] = "USD"
            self.nordstrom_headers["Host"] = api_host_name
            self.nordstrom_headers["Accept"] = "*/*"
            self.nordstrom_headers["Authorization"] = "apikey " + api_key
            self.nordstrom_headers["Referer"] = response.url
            self.nordstrom_headers["NordApiVersion"] = "1"
            api_url = "https://query.ecommerce.api.nordstrom.com/api/queryresults/keywordsearch/?top=40&IncludeFacets=false&Keyword={}".format(self._search_keyword)
            yield get_request(api_url, self.parse_data, headers=self.nordstrom_headers)

    def parse_data(self, response):
        json_data = safe_json(response.text)
        t_data = safe_grab(json_data, ["Products"], default=[])
        for item in t_data:
            title = safe_grab(item, ["Name"])
            media = safe_grab(item, ["Media"])
            if media and len(media) > 0:
                image_url = self.image_url.format(safe_grab(media[0], ["Path"]))
            else:
                image_url = None
            description = safe_grab(item, ["BrandLabelName"])
            price = safe_grab(item, ["Price", "CurrentMaxPrice"]) or safe_grab(item, ["Price", "OriginalMaxPrice"])
            url = "https://shop.nordstrom.com/s/" + safe_grab(item, ["PathAlias"]) + "/" + str(safe_grab(item, ["Id"]))
            yield generate_result_meta(shop_link=url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
