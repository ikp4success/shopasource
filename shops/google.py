from shops.shop_base import ShopBase


class Google(ShopBase):
    name = "GOOGLE"

    def parse_results(self, response):
        items = response.css(".sh-dlr__list-result, .sh-pr__product-results-grid .sh-dgr__grid-result")
        for item in items:
            title = item.css(".eIuuYe a ::text, .EI11Pd ::text").extract_first()
            link = self.prepend_domain(
                item.css(".eIuuYe a ::attr(href), .EI11Pd ::attr(href)").extract_first(),
                "https://www.google.com/"
            )
            image_url = item.css(".MUQY0 img ::attr(src)").extract_first()
            description = ""
            price = item.css("span.O8U6h ::text").extract_first()
            if price is not None:
                price = price.replace("used", "")
            yield self.generate_result_meta(
                shop_link=link,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=description
            )
