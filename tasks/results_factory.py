import json
import traceback
from multiprocessing import Process
from datetime import datetime, timezone

from dateutil import parser
from sentry_sdk import init
from sqlalchemy import or_

from project.models import ShoppedData
from shops.shop_util.extra_function import safe_grab, safe_json, truncate_data
from shops.shop_util.shop_setup import (
    SHOP_CACHE_LOOKUP_SET,
    SHOP_CACHE_MAX_EXPIRY_TIME,
)
from shops.shop_util.shop_setup_functions import find_shop, is_shop_active
from tasks.scrapy_run import spider_runner
from support import Config, get_logger

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


def run_search(
    shop_names_list,
    search_keyword,
    match_acc,
    low_to_high,
    high_to_low,
    is_cache=False,
):
    results = {}
    try:
        if not shop_names_list:
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


def start_search(shop_names, search_keyword):
    process = []
    for shop_name in shop_names:
        process_func = Process(target=launch_spiders, args=(shop_name, search_keyword))
        process_func.start()
        process.append(process_func)

    for proc in process:
        proc.join()


def launch_spiders(sn, sk):
    if is_shop_active(sn) and sk:
        spider_runner(sn, sk)
    else:
        raise Exception("Name and Search_keyword required")


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
    return [res.__str__() for res in results_db]


def get_data_from_db_contains(
    searched_keyword, low_to_high=False, high_to_low=True, shop_names_list=None
):
    results_db = []
    results_centre = []
    if shop_names_list:
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
    for results in results_db:
        if results:
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
    if shop_names_list:
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


def delete_data_by_shop_sk(shop_name, search_keyword):
    shop_data = ShoppedData.query.filter(
        ShoppedData.searched_keyword == search_keyword,
        ShoppedData.shop_name == shop_name,
    ).delete()
    shop_data.commit()
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
            shop_name = shop_names_list[0]
            results_by_date = get_data_from_db_by_date_asc(
                shop_name=shop_name, searched_keyword=search_keyword
            )
            if results_by_date and is_new_data(results_by_date, search_keyword):
                new_result.extend(results)
            else:
                delete_data_by_shop_sk(shop_name, search_keyword)
                if not is_cache:
                    start_search([shop_name], search_keyword)
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
        start_search(shop_names_list, search_keyword)
        results = get_data_from_db_contains(
            shop_names_list=shop_names_list,
            searched_keyword=search_keyword,
            low_to_high=low_to_high,
            high_to_low=high_to_low,
        )
        return match_results_by_sk(results, search_keyword, match_acc)
    return results


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
