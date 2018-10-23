from subprocess import call
from shops.shop_utilities.shop_names import ShopNames
import json


def get_results(search_keyword):
    name = ShopNames.AMAZON.name
    file_name = "{}_RESULTS.json".format(name)
    open(file_name, 'w+').close()
    call(["scrapy", "crawl", "{}".format(name), "-a", "search_keyword={}".format(search_keyword), "-o", file_name])
    results = None
    with open(file_name) as items_file:
        results = items_file.read()
    if results is not None:
        results = json.loads(results)[0]
    return results
