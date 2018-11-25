from subprocess import call
from shops.shop_utilities.shop_names import ShopNames
from multiprocessing.dummy import Pool as ThreadPool
from project import db
from dateutil import parser
from datetime import datetime, timezone
import traceback

from functools import partial

from utilities.DefaultResources import _resultRow
from utilities.DefaultResources import _errorMessage
from project.models import ShoppedData
from shops.shop_utilities.extra_function import truncate_data, safe_json, safe_grab


def run_search(search_keyword):
    try:
        if search_keyword is None or search_keyword.strip() == "":
            update_results_row_error("Search keyword is empty or invalid")

        search_keyword = truncate_data(search_keyword, 50)
        if update_search_view_with_db_results(search_keyword, check=True):
            return

        display_data = None
        pool = ThreadPool(len(ShopNames))
        launch_spiders_partial = partial(launch_spiders, sk=search_keyword)
        display_data = pool.map(launch_spiders_partial, ShopNames)
        pool.close()
        pool.join()

        display_data = [x for x in display_data if x != '']
        if display_data is not None and len(display_data) > 0:
            update_search_view_with_db_results(search_keyword)
        else:
            update_results_row_error("Sorry, no products found")
        return
    except Exception as e:
        update_results_row_error("Sorry, error encountered during search, try again or contact admin if error persist")
        print(e)
        print(traceback.format_exc())
    return


def launch_spiders(sn, sk):
    name = sn.name
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
        print("TEST")
        print(result_data)
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


def get_data_from_db(searched_keyword):
    results = ShoppedData.query.filter(ShoppedData.searched_keyword == searched_keyword).order_by(ShoppedData.numeric_price.desc()).all()
    if results is not None and len(results) > 0:
        results = [res.__str__() for res in results]
    return results


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


def update_search_view_with_db_results(search_keyword, check=False):
    results = get_data_from_db(search_keyword)
    if results is not None:
        output_data = ""
        if check:
            if is_new_data(results, search_keyword):
                output_data = update(results, search_keyword)
        else:
            output_data = update(results, search_keyword)
        if output_data != "":
            update_results_row(output_data.replace("<br>", ""))
            return True
    return False


def update(results, search_keyword):
    output_data = ""
    for result in results:
        result = safe_json(result)
        result_data = safe_grab(result, [search_keyword], {})
        output_data += build_result_row(result_data)
    return output_data


def is_new_data(results, search_keyword):
    for result in results:
        result = safe_json(result)
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
