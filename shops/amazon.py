import scrapy

from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _amazonurl
from shops.shop_utilities.shop_names import ShopNames
from shops.shop_utilities.extra_function import generate_result_meta, safe_grab, extract_items, safe_json, get_best_item_by_match
# from debug_app.manual_debug_funcs import printHtmlToFile


class Amazon(scrapy.Spider):
    name = ShopNames.AMAZON.name
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _amazonurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        item_urls = response.css("div ul#s-results-list-atf li, .s-result-list .sg-col-inner")
        query = ".a-link-normal ::attr(href), .a-link-normal ::attr(href)"
        item_url = get_best_item_by_match(items=item_urls, search_keyword=self._search_keyword, query=query, keyword_exceptions=["Sponsored", "Top Rated from Our Brands"])
        yield get_request(url=safe_grab(item_url, ["url"]), callback=self.parse_data, domain_url=response.url)

    def parse_data(self, response):
        image_url = response.css("#imgTagWrapperId img ::attr(data-old-hires)").extract_first()
        if image_url is None or image_url == "":
            image_url = response.css("#imgTagWrapperId img ::attr(data-a-dynamic-image)").extract_first()
            image_url_json = safe_json(image_url)
            if image_url_json is not None:
                image_url_json = list(image_url_json)
                if len(image_url_json) > 0:
                    image_url = image_url_json[0]
        title = response.css("#titleSection #productTitle ::text").extract_first()
        description = extract_items(response.css("#featurebullets_feature_div #feature-bullets li ::text").extract())
        price = response.css("#priceblock_ourprice ::text").extract_first()
        yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
