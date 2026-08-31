from shops.shop_base import ShopBase


class Macys(ShopBase):
    name = "MACYS"
    use_direct_fetch = True

    def parse_results(self, response):
        items = response.css("li.sortablegrid-product")

        for item in items:
            item_url = item.css(
                'a[href*="/shop/product/"] ::attr(href)'
            ).extract_first()
            item_url = self.prepend_domain(item_url, response.url)
            title = item.css('a[href*="/shop/product/"] ::attr(title)').extract_first()
            price = item.css(".price-reg ::text").extract_first()
            image_url = item.css("img ::attr(data-src)").extract_first()

            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description="",
            )
