from shops.shop_base import ShopBase


class Sixpm(ShopBase):
    name = "SIXPM"

    def parse_results(self, response):
        items = response.css(".searchPage article")

        for item in items:
            # title = extract_items(item.css("._2jktc ::text").extract())
            item_url = item.css("a ::attr(href)").extract_first()
            yield self.get_request(
                url=item_url, callback=self.parse_data, domain_url=response.url
            )

    def parse_data(self, response):
        image_url = response.css("._3lbfA ::attr(src)").extract_first()
        title = self.extract_items(response.css("#overview ::text").extract())
        description = self.extract_items(response.css("._1Srfn ::text").extract())
        price = response.css("._3r_Ou ::text").extract_first()
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
