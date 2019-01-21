from subprocess import call
from shops.shop_utilities.shop_setup import is_shop_active
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing.pool
import json
from project import db
from dateutil import parser
from datetime import datetime, timezone
import traceback
import random
import os
# import time
import requests

from functools import partial

from utilities.DefaultResources import _resultRow
from utilities.DefaultResources import _errorMessage
from project.models import ShoppedData
from shops.shop_utilities.extra_function import truncate_data, safe_json, safe_grab


possible_match_abbrev = {
    "television": ["tv", "televisions"],
    "televisions": ["tv", "television"],
    "tv": ["tv", "television"],
    "computer": ["laptop", "pc", "desktop"],
    "pc": ["laptop", "computer", "desktop"],
    "laptop": ["computer", "pc", "desktop"],
    "desktop": ["laptop", "computer", "pc"],
    "children": ["child", "kid"],
    "drones": ["drone"],
    "drone": ["drones"]
}


def match_sk(search_keyword, searched_item, match_sk_set):
    if match_sk_set == 0:
        return True
    if search_keyword is None or searched_item is None:
        return False
    search_keyword = search_keyword.lower()
    searched_item = searched_item.lower()
    sk_abbrev = safe_grab(possible_match_abbrev, [search_keyword], default=[])

    search_keyword_arr = search_keyword.split(" ")
    search_keyword_arr.extend(sk_abbrev)
    match_count = 0
    for sk in search_keyword_arr:
        if sk and len(sk) > 1 and sk in searched_item.lower():
            match_count = match_count + 1

    if match_count > 0:
        percentage_sk_match = (match_count / len(search_keyword_arr)) * 100
        if percentage_sk_match >= match_sk_set:
            return True
    return False


def run_api_search(shop_names_list, search_keyword, match_acc, low_to_high, high_to_low):
    results = {}
    try:
        if shop_names_list is None or len(shop_names_list) == 0:
            results = {"message": "Shop name is required"}
            return results
        if search_keyword is not None and search_keyword.strip() != "":
            if len(search_keyword) < 2:
                results = {"message": "Sorry, no products found"}
                return results
            search_keyword = truncate_data(search_keyword, 50)

            results = get_json_db_results(shop_names_list, search_keyword, match_acc, low_to_high, high_to_low)
            if results is None or len(results) == 0:
                results = {"message": "Sorry, no products found"}
            return results
    except Exception as e:
        results = {"message": "Sorry, error encountered during search, try again or contact admin if error persist"}
        print(e)
        print(traceback.format_exc())
        return results
    return results


# def run_web_search(search_keyword, match_acc, low_to_high, high_to_low, shop_list_names):
#     try:
#         if search_keyword is None or search_keyword.strip() == "":
#             update_results_row_error("Search keyword is empty or invalid")
#
#         if len(search_keyword) < 2:
#             update_results_row_error("Sorry, no products found")
#             return
#
#         search_keyword = truncate_data(search_keyword, 50)
#
#         # DEBUG url = "http://127.0.0.1:5000/api/shop/search={}".format(search_keyword)
#         # url = "http://shopasource.herokuapp.com/api/shop/search={}".format(search_keyword)
#         # session = requests.Session()
#         # json_data = session.get(url, timeout=60)
#         # results = safe_json(json_data.text)
#
#         results = web_get_data_from_db(search_keyword, match_acc, low_to_high, high_to_low, shop_list_names)
#
#         if results is None or len(results) == 0:
#             update_results_row_error("Sorry, no products found")
#         else:
#             update_search_view_with_db_results(search_keyword, results)
#         return
#     except Exception as e:
#         update_results_row_error("Sorry, error encountered during search, try again or contact admin if error persist")
#         print(e)
#         print(traceback.format_exc())
#     return


# def web_get_data_from_db(search_keyword, match_acc, low_to_high, high_to_low, shop_names_list):
#     results = get_data_from_db(searched_keyword=search_keyword,
#                                match_acc=match_acc,
#                                low_to_high=low_to_high,
#                                high_to_low=high_to_low,
#                                shop_names_list=shop_names_list)
#     return results


def ignite_thread_timeout(shop_name, search_keyword):
    pool = multiprocessing.pool.ThreadPool(1)
    result = pool.apply_async(partial(start_thread_search, shop_name, search_keyword))
    try:
        result.get(timeout=15)
    except multiprocessing.TimeoutError:
        print("Process timed out")
    pool.terminate()
    print("Pool terminated")


def start_thread_search(shop_name, search_keyword):
    if not is_shop_active(shop_name):
        return
    pool = ThreadPool(1)
    launch_spiders_partial = partial(launch_spiders, sk=search_keyword)
    pool.map(launch_spiders_partial, [shop_name])
    pool.close()
    pool.join()


def launch_spiders(sn, sk):
    name = sn
    search_keyword = sk
    file_name = "json_shop_results/{}_RESULTS.json".format(name)
    open(file_name, 'w+').close()
    call(["scrapy", "crawl", "{}".format(name), "-a", "search_keyword={}".format(search_keyword), "-o", file_name])
    results = None

    with open(file_name, "r") as items_file:
        results = items_file.read()

    if results is not None and results != "":
        results = safe_json(results)
        for result in results:
            execute_add_results_to_db(result, search_keyword)
    return results


def execute_add_results_to_db(result, search_keyword):
    if result is not None:
        result_data = result.get(search_keyword, {})
        if len(result_data) > 0:
            add_results_to_db(result_data)


def build_result_row(result_data):
    _resultRow_res = _resultRow.replace("{PRODUCTIMAGESOURCE}", safe_grab(result_data, ["image_url"], "") or "") \
        .replace("{PRODUCTLINK}", safe_grab(result_data, ["shop_link"], "") or "") \
        .replace("{PRODUCTTITLE}", safe_grab(result_data, ["title"], "") or "") \
        .replace("{PRODUCTDESCRIPTION}", safe_grab(result_data, ["content_description"], "") or "") \
        .replace("{PRODUCTPRICE}", safe_grab(result_data, ["price"], "") or "") \
        .replace("{PRODUCTSHOPNAME}", safe_grab(result_data, ["shop_name"], "") or "")
    return _resultRow_res


def update_search_results(data, key):
    filedata = None
    with open("project/web_content/searchresults_default.html", 'r') as file:
        filedata = file.read()
    if filedata is not None:
        if key == "{REACT_RESULT_ROW}":
            filedata = filedata.replace("{error_message}", "")
        filedata = filedata.replace(key, data)

        with open("project/web_content/searchresults.html", 'w+') as file:
            file.write(filedata)


def update_results_row(data):
    update_search_results(data, "{REACT_RESULT_ROW}")


def update_results_row_error(data):
    update_search_results(_errorMessage.replace("{Message}", data), "{error_message}")


def get_data_from_db(searched_keyword, match_acc=0, low_to_high=False, high_to_low=True, shop_names_list=None):
    results_db = []
    mk_results = []
    if shop_names_list is not None:
        for shop_name_l in shop_names_list:
            if high_to_low:
                results_db.append(ShoppedData.query.filter(
                                  ShoppedData.searched_keyword == searched_keyword,
                                  ShoppedData.shop_name == shop_name_l).order_by(ShoppedData.numeric_price.desc()).all())
            elif low_to_high:
                results_db.append(ShoppedData.query.filter(
                                  ShoppedData.searched_keyword == searched_keyword,
                                  ShoppedData.shop_name == shop_name_l).order_by(ShoppedData.numeric_price.asc()).all())
    else:
        if high_to_low:
            results_db.append(ShoppedData.query.filter(ShoppedData.searched_keyword == searched_keyword).order_by(ShoppedData.numeric_price.desc()).all())
        elif low_to_high:
            results_db.append(ShoppedData.query.filter(ShoppedData.searched_keyword == searched_keyword).order_by(ShoppedData.numeric_price.asc()).all())

    for results in results_db:
        if results is not None and len(results) > 0:
            results = [res.__str__() for res in results]
            for item_r in results:
                item_r = safe_json(item_r)
                if match_sk(searched_keyword, safe_grab(item_r, [searched_keyword, "title"]), match_acc):
                    mk_results.append(json.dumps(item_r))
    return mk_results


def update_db_results(results):
    searched_keyword = results.get("searched_keyword")
    shop_name = results.get("shop_name")
    title = results.get("title")
    result_find = ShoppedData.query.\
        filter(ShoppedData.searched_keyword == searched_keyword, ShoppedData.shop_name == shop_name, ShoppedData.title == title).\
        scalar()
    if result_find is not None:
        ShoppedData.query.\
            filter(ShoppedData.id == result_find.id).\
            update(results)
        return True
    return False


def get_json_db_results(shop_names_list, search_keyword, match_acc, low_to_high, high_to_low):
    results = get_data_from_db(shop_names_list=shop_names_list,
                               searched_keyword=search_keyword,
                               match_acc=match_acc,
                               low_to_high=low_to_high,
                               high_to_low=high_to_low)
    if results:
        if is_new_data(results, search_keyword):
            return results
        else:
            ignite_thread_timeout(shop_names_list[0], search_keyword)
            return get_data_from_db(shop_names_list=shop_names_list,
                                    searched_keyword=search_keyword,
                                    match_acc=match_acc,
                                    low_to_high=low_to_high,
                                    high_to_low=high_to_low)
    else:
        ignite_thread_timeout(shop_names_list[0], search_keyword)
        return get_data_from_db(shop_names_list=shop_names_list,
                                searched_keyword=search_keyword,
                                match_acc=match_acc,
                                low_to_high=low_to_high,
                                high_to_low=high_to_low)
    return results


def update_search_view_with_db_results(search_keyword, results):
    if results:
        output_data = ""
        output_data = update(results, search_keyword)
        if output_data != "":
            update_results_row(output_data.replace("<br>", ""))
            return
    return


def update(results, search_keyword):
    output_data = ""
    for result in results:
        result = safe_json(result)
        result_data = safe_grab(result, [search_keyword], {})
        if result_data == {}:
            continue
        output_data += build_result_row(result_data)
    return output_data


def is_new_data(results, search_keyword):
    for result in results:
        result = safe_json(result)
        if result and isinstance(result, list) and len(result) > 0:
            result = result[0]
        date_searched = safe_grab(result, [search_keyword, "date_searched"])
        if date_searched is not None:
            date_searched_parse = parser.parse(date_searched)
            dt_time_diff = datetime.now(timezone.utc) - date_searched_parse
            if dt_time_diff.days < 7:
                return True
    return False


def add_results_to_db(result):
    if not update_db_results(result):
        shopped_data = wrapshopdata(result)
        db.session.add(shopped_data)
    db.session.commit()


def wrapshopdata(results):
    shopped_data = ShoppedData(
        title=results["title"],
        content_description=results["content_description"],
        image_url=results["image_url"],
        price=results["price"],
        numeric_price=results["numeric_price"],
        searched_keyword=results["searched_keyword"],
        date_searched=results["date_searched"],
        shop_name=results["shop_name"],
        shop_link=results["shop_link"]
    )
    return shopped_data
