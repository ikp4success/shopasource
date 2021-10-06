from shops.shop_base import ShopBase


class Amazon(ShopBase):
    name = "AMAZON"

    def parse_results(self, response):
        item_url = None
        items = response.css(
            "div ul#s-results-list-atf li, .s-result-list .sg-col-inner"
        )

        for item in items:
            if (
                "Sponsored" in item.extract()
                or "Top Rated from Our Brands" in item.extract()
            ):
                continue
            item_url = item.css(".a-link-normal ::attr(href)").extract_first()
            yield self.get_request(
                url=item_url, callback=self.parse_data, domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css(
            "#imgTagWrapperId img ::attr(data-old-hires)"
        ).extract_first()
        if image_url is None or image_url == "":
            image_url = response.css(
                "#imgTagWrapperId img ::attr(data-a-dynamic-image)"
            ).extract_first()
            image_url_json = self.safe_json(image_url)
            if image_url_json is not None:
                image_url_json = list(image_url_json)
                if len(image_url_json) > 0:
                    image_url = image_url_json[0]
        title = response.css("#titleSection #productTitle ::text").extract_first()
        description = self.extract_items(
            response.css(
                "#featurebullets_feature_div #feature-bullets li ::text"
            ).extract()
        )
        price = response.css("#priceblock_ourprice ::text").extract_first()
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
