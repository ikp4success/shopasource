from subprocess import call
from shops.shop_utilities.shop_names import ShopNames
from multiprocessing.dummy import Pool as ThreadPool
import json
from functools import partial
import os

from utilities.DefaultResources import _resultRow
from utilities.DefaultResources import _errorMessage


def get_results(search_keyword):
    pool = ThreadPool(len(ShopNames))
    launch_spiders_partial = partial(launch_spiders, sk=search_keyword)
    results = pool.map(launch_spiders_partial, ShopNames)
    pool.close()
    pool.join()
    # update_results_row(results[0]["results_row"])
    return results


def launch_spiders(sn, sk):
    name = sn.name
    search_keyword = sk
    file_name = "{}_RESULTS.json".format(name)
    open(file_name, 'w+').close()
    call(["scrapy", "crawl", "{}".format(name), "-a", "search_keyword={}".format(search_keyword), "-o", file_name])
    results = None
    with open(file_name) as items_file:
        results = items_file.read()
    if results is not None and results != "":
        results = json.loads(results)
        if results is not None:
            results = results[0]
            result_data = results.get(search_keyword, {})
            _resultRow_res = _resultRow.replace("{PRODUCTIMAGESOURCE}", result_data.get("image_url", "")) \
                .replace("{PRODUCTLINK}", result_data.get("shop_link", "")) \
                .replace("{PRODUCTTITLE}", result_data.get("title", "")) \
                .replace("{PRODUCTDESCRIPTION}", result_data.get("content_descripition", "")) \
                .replace("{PRODUCTPRICE}", result_data.get("price", "")) \
                .replace("{PRODUCTSHOPNAME}", result_data.get("shop_name", ""))
            results["results_row"] = _resultRow_res
            update_results_row(_resultRow_res)
    else:
        update_results_row_error("Sorry, no products found")
    return results


def update_search_results(data, key):
    filedata = None
    with open("web_content/searchresults_default.html", 'r') as file:
        filedata = file.read()
    if filedata is not None:
        if key == "{REACT_RESULT_ROW}":
            filedata.replace("{error_message}", "")
        filedata = filedata.replace(key, data)

        with open("web_content/searchresults.html", 'w+') as file:
            file.write(filedata)


def update_results_row(data):
    update_search_results(data, "{REACT_RESULT_ROW}")


def update_results_row_error(data):
    update_search_results(_errorMessage.replace("{Message}", data), "{error_message}")
