from shops.shop_base import ShopBase


class Walmart(ShopBase):
    name = "WALMART"

    def parse_results(self, response):
        items = response.css(
            "#searchProductResult .search-result-gridview-items a.product-title-link"
        ) or response.css(
            "#searchProductResult .search-result-listview-items a.product-title-link"
        )

        for item in items:
            item_url = item.css("::attr(href)").extract_first()
            yield self.get_request(
                url=item_url, callback=self.parse_data, domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css(".prod-hero-image img ::attr(src)").extract_first()
        title = response.css(".ProductTitle div ::text").extract_first()
        description = self.extract_items(response.css(".about-desc ::text").extract())
        price = (
            response.css(".prod-PriceHero .price-characteristic ::text").extract_first()
            or ""
        )
        price = "${}".format(price)
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
