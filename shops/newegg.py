from shops.shop_base import ShopBase


class Newegg(ShopBase):
    name = "NEWEGG"
    # download_delay = 2.5

    def parse_results(self, response):
        if "areyouahuman" in response.text.lower():
            yield None
            return
        items = response.css(".item-container")
        for item in items:
            title = self.extract_items(item.css("a ::text").extract())
            item_url = item.css("a ::attr(href)").extract_first()
            image_url = item.css("img ::attr(src)").extract_first()

            if "areyouahuman" in item_url:
                break

            price = "${}{}".format(item.css(".price-current strong ::text").extract_first(), item.css(".price-current sup ::text").extract_first())

            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=""
            )
    #         meta = {
    #             "p": prize,
    #             "t": item_text,
    #             "img": image_url
    #         }
    #         yield get_request(url=item_url,
    #                           callback=self.parse_data,
    #                           domain_url=response.url, meta=meta)
    #
    # def parse_data(self, response):
    #     price = safe_grab(response.meta, ["p"])
    #     title = safe_grab(response.meta, ["t"])
    #     image_url = safe_grab(response.meta, ["img"])
    #     description = ""
    #     if "areyouahuman" not in response.url:
    #         image_url = response.css(".mainSlide img ::attr(src)").extract_first()
    #         title = extract_items(response.css("#grpDescrip_h ::text").extract()) or title
    #         description = "{}\n{}".format(extract_items(response.css(".itemDesc ::text").extract()), extract_items(response.css(".itemColumn ::text").extract())).rstrip().strip()
    #
    #     yield generate_result_meta(shop_link=response.url, image_url=image_url, shop_name=self.name, price=price, title=title, searched_keyword=self._search_keyword, content_description=description)
