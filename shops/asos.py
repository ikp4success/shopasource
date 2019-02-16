from shops.shop_base import ShopBase


class Asos(ShopBase):
    name = "ASOS"

    def parse_results(self, response):
        items = response.css("._2oHs74P")
        if len(items) == 0:
            yield from(self.parse_data(response))
        for item in items:
            item_url = item.css("a._3x-5VWa ::attr(href)").extract_first()
            price = item.css("._342BXW_ ::text").extract_first()
            yield self.get_request(
                url=item_url,
                callback=self.parse_data,
                domain_url=response.url,
                meta={"pc": price}
            )

    def parse_data(self, response):
        image_url = (
            response.css(".amp-frame .fullImageContainer img ::attr(src), .product-carousel img ::attr(src)").extract_first() or
            response.css(".asos-media-players .fullImageContainer .img img ::attr(src)").extract_first()
        )
        title = self.extract_items(response.css(".product-hero h1 ::text").extract())
        description = self.extract_items(response.css(".product-description ::text").extract())
        price = (
            response.xpath("//span[@itemprop='price']").css("::text").extract_first() or
            self.safe_grab(response.meta, ["pc"])
        )
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description
        )
