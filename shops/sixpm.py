import re

from shops.shop_base import ShopBase


class Sixpm(ShopBase):
    name = "SIXPM"
    use_browser_fetch = True

    def parse_results(self, response):
        # Product data ships as an embedded JSON state blob, not plain DOM markup -
        # regex out the parallel field lists rather than depend on exact JSON nesting.
        titles = re.findall(r'"productName":"([^"]*)"', response.text)
        prices = re.findall(r'"price":"([^"]*)"', response.text)
        image_ids = re.findall(r'"msaImageId":"([^"]*)"', response.text)
        urls = re.findall(r'"productUrl":"([^"]*)"', response.text)

        for title, price, image_id, url in zip(titles, prices, image_ids, urls):
            item_url = self.prepend_domain(url.replace("\\u002F", "/"), response.url)
            image_url = (
                f"https://m.media-amazon.com/images/I/{image_id}._AC_SR768,1024_.jpg"
                if image_id
                else None
            )
            yield self.generate_result_meta(
                shop_link=item_url,
                image_url=image_url,
                shop_name=self.name,
                price=price,
                title=title,
                searched_keyword=self._search_keyword,
                content_description="",
            )
