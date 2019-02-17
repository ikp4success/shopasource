from shops.shop_base import ShopBase


class FashionNova(ShopBase):
    name = "FASHIONNOVA"

    def start_requests(self):
        # uuid_v = uuid.uuid4()
        uuid_v = "8fb37bd6-aef1-4d7c-be3f-88bafef01308"
        shop_url = self.shop_url.format(self._search_keyword, uuid_v)
        yield self.get_request(shop_url, self.get_best_link)

    def get_best_link(self, response):
        items = self.safe_grab(self.safe_json(response.text), ["items"])

        for item in items:
            item_url = self.safe_grab(item, ["u"])
            yield self.get_request(
                url=item_url,
                callback=self.parse_data,
                domain_url="https://www.fashionnova.com/"
            )

    def parse_data(self, response):
        image_url = response.css("#large-thumb ::attr(src)").extract_first()
        title = self.extract_items(response.css("#product-info .title ::text").extract())
        description = "\n".join(list(set(response.css(".description .group .group-body ul li::text").extract())))
        price = response.css(".deal spanclass ::text").extract_first()
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description
        )
