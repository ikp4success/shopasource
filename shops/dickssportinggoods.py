import re

from shops.shop_base import ShopBase


class Dickssportinggoods(ShopBase):
    name = "DICKSSPORTINGGOODS"

    def parse_results(self, response):
        items = response.css(".product-grid")
        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            price = (
                item.css(".final-price ::text").extract_first()
                or item.css(".was-item-price ::text").extract_first()
            )
            if price:
                price = price.replace("NOW:", "").replace("WAS:", "")
                if "-" in price:
                    try:
                        price = re.search("(.*)-", price).group(1)
                    except Exception:  # nosec
                        continue
            yield self.get_request(
                url=item_url,
                callback=self.parse_data,
                domain_url=response.url,
                meta={"p": price},
            )

    def parse_data(self, response):
        image_url = response.css(
            "#image-viewer-container img ::attr(src)"
        ).extract_first()
        title = self.extract_items(response.css("h1.product-title ::text").extract())
        description = self.extract_items(
            response.css("div[itemprop='description'] ::text").extract()
        )
        price = response.css(
            "span[itemprop='price'] ::text"
        ).extract_first() or self.safe_grab(response.meta, "p")
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
