from shops.shop_base import ShopBase


class MicroCenter(ShopBase):
    name = "MICROCENTER"

    def parse_results(self, response):
        items = response.css(".product_wrapper")
        for item in items:
            item_title = self.extract_items(item.css(".pDescription ::text").extract())
            item_url = item.css(".pDescription ::attr(href)").extract_first()
            yield self.get_request(
                url=item_url,
                callback=self.parse_data,
                domain_url=response.url,
                meta={"ti": item_title}
            )

    def parse_data(self, response):
        image_url = response.css(".image-slide ::attr(src)").extract_first()
        title = self.safe_grab(response.meta, ["ti"])
        description = "{}\n{}".format(
            self.extract_items(response.css(".content-wrapper div.inline ul ::text").extract()),
            self.extract_items(response.css(".content-wrapper div.inline p ::text").extract())).rstrip().strip()
        price = self.extract_items(response.css("#options-pricing #pricing ::text").extract())
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description
        )
