from shops.shop_base import ShopBase


class Nike(ShopBase):
    name = "NIKE"
    # download_delay = 2.5

    headers = {
        "Host": "store.nike.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
        "Referer": "https://www.nike.com",
        "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
    }

    def start_requests(self):
        shop_url = self.shop_url.format(self._search_keyword, self._search_keyword)
        self.nike_headers["Referer"] = shop_url
        yield self.get_request(shop_url, self.get_best_link, headers=self.headers)

    def get_best_link(self, response):
        if "/t/" in response.url:
            yield from self.parse_data(response)
            return
        items = response.css(".grid-item-box")
        for item in items:
            item_url = item.css("a ::attr(href)").extract_first()
            title = self.extract_items(item.css(".product-name ::text").extract())
            price = item.css(".product-price span ::text").extract_first()
            # def_image_url = "https://c.static-nike.com/a/images/t_PDP_1280_v1/f_auto/mnrclursmzg1muwzdgjj/{}.jpg"
            # img_item_url = item_url.replace("https://www.nike.com/t/", "")
            image_url = item.css("a img ::attr(src)").extract_first()
            description = self.extract_items(item.css(".product-subtitle ::text").extract())

            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description=description
            )
            # meta = {
            #     "t": title,
            #     "p": price
            # }
            # yield get_request(url=item_url, callback=self.parse_data, domain_url=response.url, meta=meta)

    def parse_data(self, response):
        image_url = response.css(".colorway-images .bg-medium-grey ::attr(src)").extract_first()
        if image_url:
            image_url = image_url.replace("144", "1280")
        else:
            image_url = response.css("picture #pdp_6up-hero ::attr(src)").extract_first()
        title = self.extract_items(response.css(".ncss-base ::text").extract())  # or safe_grab(response.meta, ["t"])
        description = self.extract_items(response.css(".description-preview ::text").extract())
        price = response.css("div[data-test='product-price'] ::text").extract_first()  # or safe_grab(response.meta, ["p"])
        yield self.generate_result_meta(
            shop_link=response.url,
            image_url=image_url,
            shop_name=self.name,
            price=price,
            title=title,
            searched_keyword=self._search_keyword,
            content_description=description
        )
