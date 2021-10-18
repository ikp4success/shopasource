from shops.shop_base import ShopBase


class Saksfifthavenue(ShopBase):
    name = "SAKSFIFTHAVENUE"

    headers = {
        "Host": "www.saksfifthavenue.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
        "referer": "https://www.saksfifthavenue.com/Entry.jsp",
        "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0",
    }

    def parse_results(self, response):
        items = response.css(".pa-product-large")

        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            yield self.get_request(
                url=item_url, callback=self.parse_data, domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css(".product__media ::attr(data-image)").extract_first()
        brand = self.extract_items(
            response.css("h2.product-overview__brand ::text").extract()
        )
        title = (
            brand
            + " "
            + self.extract_items(
                response.css("h1.product-overview__short-description ::text").extract()
            )
        ).strip()
        description = self.extract_items(
            response.css(".product-description ::text").extract()
        )
        price = (
            response.css(".product-pricing__price")
            .xpath("//span[@itemprop='price']")
            .css("::attr(content)")
            .extract_first()
            or response.css(".product-pricing__price")
            .xpath("//span[@itemprop='lowPrice']")
            .css("::attr(content)")
            .extract_first()
        )
        alt_price = self.extract_items(
            response.css(".product-pricing__price span::text").extract()
        )
        price = price or alt_price
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
