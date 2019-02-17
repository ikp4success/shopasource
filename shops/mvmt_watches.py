from shops.shop_base import ShopBase


class MvmtWatches(ShopBase):
    name = "MVMTWATCHES"

    def parse_results(self, response):
        items = response.css(".product-grid .product-grid-item")

        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            yield self.get_request(
                url=item_url,
                callback=self.parse_data,
                domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css(".product-slider-image ::attr(src)").extract_first()
        title = self.extract_items(response.css(".product-name ::text").extract())
        description = self.extract_items(response.css(".related-details ::text").extract())
        price = response.xpath("//meta[@name='twitter:data1']").css("::attr(content)").extract_first()
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description
        )
