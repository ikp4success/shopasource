import json
import os
import traceback
from datetime import datetime, timezone
from subprocess import call  # nosec

from dateutil import parser
from sentry_sdk import init
from sqlalchemy import or_

from project import db
from project.models import ShoppedData
from shops.shop_utilities.extra_function import safe_grab, safe_json, truncate_data
from shops.shop_utilities.shop_setup import (
    SHOP_CACHE_LOOKUP_SET,
    SHOP_CACHE_MAX_EXPIRY_TIME,
)
from shops.shop_utilities.shop_setup_functions import find_shop, is_shop_active
from support import Config, get_logger
from utilities.DefaultResources import _errorMessage, _resultRow

logger = get_logger(__name__)

init(Config().SENTRY_DSN)


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
    "drone": ["drones"],
}


def match_sk(search_keyword, searched_item, match_sk_set):
    if match_sk_set == 0:
        return True
    if not search_keyword or not searched_item:
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


def run_api_search(
    shops_thread_list,
    shop_names_list,
    search_keyword,
    match_acc,
    low_to_high,
    high_to_low,
    is_cache=False,
):
    results = {}
    try:
        if shop_names_list is None or len(shop_names_list) == 0:
            results = {"message": "Shop name is required"}
            return results
        if not find_shop(shop_names_list):
            results = {"message": "Invalid shop name present in parameters"}
            return results
        if len(shop_names_list) == 1 and not is_shop_active(shop_names_list[0]):
            results = {"message": "Shop is inactive at the moment, check back again"}
            return results

        if search_keyword is not None and search_keyword.strip() != "":
            if len(search_keyword) < 2:
                results = {"message": "Sorry, no products found"}
                return results
            search_keyword = truncate_data(search_keyword, 75, html_escape=True)

            results = get_json_db_results(
                shop_names_list,
                search_keyword,
                match_acc,
                low_to_high,
                high_to_low,
                is_cache,
            )
            if results is None or len(results) == 0:
                results = {"message": "Sorry, no products found"}
            return results
    except Exception as e:
        results = {
            "message": "Sorry, error encountered during search, try again or contact admin if error persist"
        }
        logger.warning(e)
        logger.warning(traceback.format_exc())
        return results
    return results


def start_thread_search(shop_name, search_keyword):
    if not is_shop_active(shop_name):
        return
    launch_spiders(sk=search_keyword, sn=shop_name)


def launch_spiders(sn, sk):
    name = sn
    search_keyword = sk
    if not os.path.exists("json_shop_results/"):
        os.makedirs("json_shop_results/")
    file_name = "json_shop_results/{}_RESULTS.json".format(name)
    open(file_name, "w+").close()
    call(  # nosec
        [
            "scrapy",
            "crawl",
            "{}".format(name),
            "-a",
            "search_keyword={}".format(search_keyword),
            "-o",
            file_name,
        ]
    )
    return pr_result(search_keyword, file_name)


def pr_result(sk, fname):
    results = None

    with open(fname, "r") as items_file:
        results = items_file.read()

    if results:
        results = safe_json(results)
        for result in results:
            execute_add_results_to_db(result, sk)
    return results


def execute_add_results_to_db(result, search_keyword):
    if result is not None:
        result_data = result.get(search_keyword, {})
        if len(result_data) > 0:
            add_results_to_db(result_data)


def build_result_row(result_data):
    """ this function is deprecated """
    _resultRow_res = (
        _resultRow.replace(
            "{PRODUCTIMAGESOURCE}", safe_grab(result_data, ["image_url"], "") or ""
        )
        .replace("{PRODUCTLINK}", safe_grab(result_data, ["shop_link"], "") or "")
        .replace("{PRODUCTTITLE}", safe_grab(result_data, ["title"], "") or "")
        .replace(
            "{PRODUCTDESCRIPTION}",
            safe_grab(result_data, ["content_description"], "") or "",
        )
        .replace("{PRODUCTPRICE}", safe_grab(result_data, ["price"], "") or "")
        .replace("{PRODUCTSHOPNAME}", safe_grab(result_data, ["shop_name"], "") or "")
    )
    return _resultRow_res


def update_search_results(data, key):
    filedata = None
    with open("project/web_content/searchresults_default.html", "r") as file:
        filedata = file.read()
    if filedata is not None:
        if key == "{REACT_RESULT_ROW}":
            filedata = filedata.replace("{error_message}", "")
        filedata = filedata.replace(key, data)

        with open("project/web_content/searchresults.html", "w+") as file:
            file.write(filedata)


def update_results_row(data):
    update_search_results(data, "{REACT_RESULT_ROW}")


def update_results_row_error(data):
    update_search_results(_errorMessage.replace("{Message}", data), "{error_message}")


def get_data_from_db_by_date_asc(searched_keyword, shop_name=None):
    results_db = []
    if not shop_name:
        results_db.append(
            ShoppedData.query.filter(ShoppedData.searched_keyword == searched_keyword)
            .order_by(ShoppedData.date_searched.asc())
            .first()
        )
    results_db.append(
        ShoppedData.query.filter(
            ShoppedData.searched_keyword == searched_keyword,
            ShoppedData.shop_name == shop_name,
        )
        .order_by(ShoppedData.date_searched.asc())
        .first()
    )
    db.session.commit()
    return [res.__str__() for res in results_db]


def get_data_from_db_contains(
    searched_keyword, low_to_high=False, high_to_low=True, shop_names_list=None
):
    results_db = []
    results_centre = []
    if shop_names_list is not None:
        if high_to_low:
            results_db.append(
                ShoppedData.query.filter(
                    # ShoppedData.searched_keyword.contains(searched_keyword),
                    or_(
                        ShoppedData.searched_keyword.contains(searched_keyword),
                        ShoppedData.content_description.contains(searched_keyword),
                    ),
                    ShoppedData.shop_name.in_(shop_names_list),
                )
                .order_by(ShoppedData.numeric_price.desc())
                .all()
            )

        elif low_to_high:
            results_db.append(
                ShoppedData.query.filter(
                    # ShoppedData.searched_keyword.contains(searched_keyword),
                    or_(
                        ShoppedData.searched_keyword.contains(searched_keyword),
                        ShoppedData.content_description.contains(searched_keyword),
                    ),
                    ShoppedData.shop_name.in_(shop_names_list),
                )
                .order_by(ShoppedData.numeric_price.asc())
                .all()
            )
    else:
        if high_to_low:
            results_db.append(
                ShoppedData.query.filter(
                    # ShoppedData.searched_keyword.contains(searched_keyword),
                    or_(
                        ShoppedData.searched_keyword.contains(searched_keyword),
                        ShoppedData.content_description.contains(searched_keyword),
                    )
                )
                .order_by(ShoppedData.numeric_price.desc())
                .all()
            )
        elif low_to_high:
            results_db.append(
                ShoppedData.query.filter(
                    # ShoppedData.searched_keyword.contains(searched_keyword),
                    or_(
                        ShoppedData.searched_keyword.contains(searched_keyword),
                        ShoppedData.content_description.contains(searched_keyword),
                    )
                )
                .order_by(ShoppedData.numeric_price.asc())
                .all()
            )
    db.session.commit()
    for results in results_db:
        if results is not None and len(results) > 0:
            results_1 = []
            for result in results:
                result.searched_keyword = searched_keyword
                results_1.append(result)
            results_centre = [res.__str__() for res in results_1]
    return results_centre


def get_data_from_db(
    searched_keyword, low_to_high=False, high_to_low=True, shop_names_list=None
):
    results_db = []
    results_centre = []
    if shop_names_list is not None:
        if high_to_low:
            results_db.append(
                ShoppedData.query.filter(
                    ShoppedData.searched_keyword == searched_keyword,
                    ShoppedData.shop_name.in_(shop_names_list),
                )
                .order_by(ShoppedData.numeric_price.desc())
                .all()
            )
        elif low_to_high:
            results_db.append(
                ShoppedData.query.filter(
                    ShoppedData.searched_keyword == searched_keyword,
                    ShoppedData.shop_name.in_(shop_names_list),
                )
                .order_by(ShoppedData.numeric_price.asc())
                .all()
            )
    else:
        if high_to_low:
            results_db.append(
                ShoppedData.query.filter(
                    ShoppedData.searched_keyword == searched_keyword
                )
                .order_by(ShoppedData.numeric_price.desc())
                .all()
            )
        elif low_to_high:
            results_db.append(
                ShoppedData.query.filter(
                    ShoppedData.searched_keyword == searched_keyword
                )
                .order_by(ShoppedData.numeric_price.asc())
                .all()
            )
    db.session.commit()

    for results in results_db:
        if results is not None and len(results) > 0:
            results_centre = [res.__str__() for res in results]
    return results_centre


def match_results_by_sk(results, searched_keyword, match_acc=0):
    mk_results = []
    for item_r in results:
        item_r = safe_json(item_r)
        if match_sk(
            searched_keyword, safe_grab(item_r, [searched_keyword, "title"]), match_acc
        ):
            mk_results.append(json.dumps(item_r))
    return mk_results


def update_db_results(results):
    searched_keyword = results.get("searched_keyword")
    shop_name = results.get("shop_name")
    title = results.get("title")
    result_find = ShoppedData.query.filter(
        ShoppedData.searched_keyword == searched_keyword,
        ShoppedData.shop_name == shop_name,
        ShoppedData.title == title,
    ).scalar()
    if result_find is not None:
        ShoppedData.query.filter(ShoppedData.id == result_find.id).update(results)
        db.session.commit()
        return True
    db.session.commit()
    return False


def delete_data_by_shop_sk(shop_name, search_keyword):
    ShoppedData.query.filter(
        ShoppedData.searched_keyword == search_keyword,
        ShoppedData.shop_name == shop_name,
    ).delete()
    db.session.commit()
    return


def get_json_db_results(
    shop_names_list, search_keyword, match_acc, low_to_high, high_to_low, is_cache
):

    results = get_data_from_db(
        shop_names_list=shop_names_list,
        searched_keyword=search_keyword,
        low_to_high=low_to_high,
        high_to_low=high_to_low,
    )
    if results:
        new_result = []
        if shop_names_list and len(shop_names_list) == 1:
            for shop_name in shop_names_list:
                results_by_date = get_data_from_db_by_date_asc(
                    shop_name=shop_name, searched_keyword=search_keyword
                )
                if results_by_date and is_new_data(results_by_date, search_keyword):
                    new_result.extend(results)
                else:
                    delete_data_by_shop_sk(shop_name, search_keyword)
                    if not is_cache:
                        start_thread_search(shop_name, search_keyword)
        else:
            new_result.extend(results)

        if new_result:
            results = match_results_by_sk(new_result, search_keyword, match_acc)
            return results
        else:
            results = get_data_from_db_contains(
                shop_names_list=shop_names_list,
                searched_keyword=search_keyword,
                low_to_high=low_to_high,
                high_to_low=high_to_low,
            )

            return match_results_by_sk(results, search_keyword, match_acc)
    elif is_cache:
        return []
    else:
        for shop_name in shop_names_list:
            start_thread_search(shop_name, search_keyword)
        results = get_data_from_db_contains(
            shop_names_list=shop_names_list,
            searched_keyword=search_keyword,
            low_to_high=low_to_high,
            high_to_low=high_to_low,
        )
        return match_results_by_sk(results, search_keyword, match_acc)
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
            if dt_time_diff.days < SHOP_CACHE_MAX_EXPIRY_TIME:
                return SHOP_CACHE_LOOKUP_SET
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
        shop_link=results["shop_link"],
    )
    return shopped_data
