from shops.shop_connect.shop_request import get_request
from shops.shop_connect.shoplinks import _hautelookurl
from shops.shop_utilities.shop_setup import find_shop_configuration
from shops.nordstrom_rack import NordstromRack


class HauteLook(NordstromRack):
    name = find_shop_configuration("HAUTELOOK")["name"]
    _search_keyword = None

    def __init__(self, search_keyword):
        self._search_keyword = search_keyword

    def start_requests(self):
        shop_url = _hautelookurl.format(self._search_keyword)
        yield get_request(shop_url, self.get_best_link)
