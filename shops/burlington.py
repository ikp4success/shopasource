from shops.shop_base import ShopBase


class Burlington(ShopBase):
    name = "BURLINGTON"

    def parse_results(self, response):
        items = response.css("#hawkitemlist .row")

        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            yield self.get_request(
                url=item_url,
                callback=self.parse_data,
                domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css("#productMainImage ::attr(src)").extract_first()
        title = self.extract_items(response.css("#LblProductTitle ::text").extract())
        description = self.extract_items(response.css(".product-details-description ::text").extract())
        price = response.css("#ctl03_MainContentArea_ctl00_ctl00_ctl00_ProductDisplay_ProductPricesModule_LblOurPriceSimple ::text").extract_first()
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price, title=title,
            searched_keyword=self._search_keyword,
            content_description=description
        )
