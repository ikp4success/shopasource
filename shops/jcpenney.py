# import uuid
from shops.shop_base import ShopBase


class Jcpenney(ShopBase):
    name = "JCPENNEY"

    def parse_results(self, response):
        items = self.safe_grab(
            self.safe_json(response.text), ["organicZoneInfo", "products"]
        )
        for item in items:
            item_url = self.safe_grab(item, ["pdpUrl"])
            price = self.safe_grab(item, ["fpacPriceMax"])
            yield self.get_request(
                url=item_url,
                callback=self.parse_data,
                domain_url="https://www.jcpenney.com",
                meta={"pc": price},
            )

    def parse_data(self, response):
        image_url = response.css("._3JaiK ::attr(src)").extract_first()
        title = self.extract_items(response.css("._37-TG ::text").extract())
        description = "\n".join(
            list(set(response.css("#productDescriptionParent .o3cEt ::text").extract()))
        )
        price = self.safe_grab(response.meta, ["pc"])
        if price:
            price = "${}".format(price)
        else:
            price = None
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description,
        )
