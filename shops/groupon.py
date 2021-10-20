from shops.shop_base import ShopBase


class Groupon(ShopBase):
    name = "GROUPON"
    headers = {
        "Host": "www.groupon.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.groupon.com/",
    }

    def parse_results(self, response):
        item_url = None
        items = response.css("#pull-results .card-ui")

        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            yield self.get_request(
                url=item_url, callback=self.parse_data, domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css(".sleepy-load ::attr(src)").extract_first()
        title = self.extract_items(response.css(".deal-page-title ::text").extract())
        description = self.extract_items(response.css(".pitch ::text").extract())
        price = response.css(
            ".price-discount-wrapper ::text, .breakout-option-value ::text"
        ).extract_first()
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
