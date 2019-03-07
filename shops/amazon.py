from shops.shop_base import ShopBase


class Amazon(ShopBase):
    name = "AMAZON"
    amazon_headers = {
        "Host": "www.amazon.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    }

    def parse_results(self, response):
        item_url = None
        items = response.css("div ul#s-results-list-atf li, .s-result-list .sg-col-inner, .s-result-list .s-result-item")

        for item in items:
            if "Sponsored" in item.extract() or "Top Rated from Our Brands" in item.extract():
                continue
            item_url = item.css(".a-link-normal ::attr(href), .a ::attr(href)").extract_first()
            image_url = item.css("img ::attr(src)").extract_first()
            title = self.extract_items(response.css("span.a-text-normal ::text").extract())
            price = "".join(item.css(".a-price ::text").extract())
            if item_url:
                yield self.generate_result_meta(
                    shop_link=item_url,
                    image_url=image_url,
                    price=price,
                    title=title,
                    searched_keyword=self._search_keyword,
                    content_description=""
                )
    #             yield self.get_request(
    #                 url=item_url,
    #                 callback=self.parse_data,
    #                 domain_url=response.url,
    #                 headers=self.amazon_headers
    #             )
    #
    # def parse_data(self, response):
    #     image_url = response.css("#imgTagWrapperId img ::attr(data-old-hires)").extract_first()
    #     if image_url is None or image_url == "":
    #         image_url = response.css("#imgTagWrapperId img ::attr(data-a-dynamic-image)").extract_first()
    #         image_url_json = self.safe_json(image_url)
    #         if image_url_json is not None:
    #             image_url_json = list(image_url_json)
    #             if len(image_url_json) > 0:
    #                 image_url = image_url_json[0]
    #     title = response.css("#titleSection #productTitle ::text").extract_first()
    #     description = self.extract_items(response.css("#featurebullets_feature_div #feature-bullets li ::text").extract())
    #     price = response.css("#priceblock_ourprice ::text").extract_first()
    #     yield self.generate_result_meta(
    #         shop_link=response.url,
    #         image_url=image_url,
    #         price=price,
    #         title=title,
    #         searched_keyword=self._search_keyword,
    #         content_description=description
    #     )
