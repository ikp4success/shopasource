from shops.shop_base import ShopBase


class Macys(ShopBase):
    name = "MACYS"
    headers = {
        "Host": "www.macys.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
        "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
        # "If-None-Match": 'W/"1a0905-84p23IFmm2k/vykK/3NpICzo2N8"',
    }

    def parse_results(self, response):
        items = response.css(".items .productThumbnailItem")

        for item in items:
            item_url = item.css("a.productDescLink ::attr(href)").extract_first()
            price = "".join(item.css(".prices span ::text").extract())
            yield self.get_request(
                url=item_url,
                callback=self.parse_data,
                domain_url=response.url,
                meta={"price": price},
            )

    def parse_data(self, response):
        image_url = response.css(".main-image img ::attr(src)").extract_first()
        title = self.extract_items(
            response.xpath("//div[@data-auto='product-title']").css("::text").extract()
        )
        description = self.extract_items(
            response.xpath("//div[@data-el='product-details']").css("::text").extract()
        )
        price = response.css(".price ::text").extract_first() or self.safe_grab(
            response.meta, ["price"]
        )
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
