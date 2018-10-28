from subprocess import call
from shops.shop_utilities.shop_names import ShopNames
from multiprocessing.dummy import Pool as ThreadPool
from project import db

import json
from functools import partial

from utilities.DefaultResources import _resultRow
from utilities.DefaultResources import _errorMessage
from project.models import ShoppedData
from shops.shop_utilities.extra_function import truncate_data


def run_search(search_keyword):
    if search_keyword is None or search_keyword.strip() == "":
        update_results_row_error("Search keyword is empty or invalid")

    search_keyword = truncate_data(search_keyword, 50)
    results = get_data_from_db(search_keyword)
    if results is not None:
        if update_search_view_with_db_results(results, search_keyword):
            return

    pool = ThreadPool(len(ShopNames))
    launch_spiders_partial = partial(launch_spiders, sk=search_keyword)
    results = pool.map(launch_spiders_partial, ShopNames)
    pool.close()
    pool.join()
    if results is not None and len(results) > 0:
        if results[0] != "":
            update_results_row(results[0]["results_row"])
        else:
            update_results_row_error("Sorry, no products found")
    else:
        update_results_row_error("Sorry, no products found")
    return


def launch_spiders(sn, sk):
    name = sn.name
    search_keyword = sk
    file_name = "{}_RESULTS.json".format(name)
    open(file_name, 'w+').close()
    call(["scrapy", "crawl", "{}".format(name), "-a", "search_keyword={}".format(search_keyword), "-o", file_name])
    results = None
    output_data = ""
    with open(file_name) as items_file:
        results = items_file.read()
    if results is not None and results != "":
        results = _result_handler(results, search_keyword)
        if results is not None:
            _built_result_rows = build_result_row(results)
            output_data += _built_result_rows
            results["results_row"] = output_data
            # update_results_row(output_data)
    return results


def _result_handler(results, search_keyword):
    if results is not None and results != "":
        results = json.loads(results)
        if results is not None:
            results = results[0]
            result_data = results.get(search_keyword, {})
            if len(result_data) > 0:
                add_results_to_db(result_data)
                return result_data
    return None


def build_result_row(result_data):
    _resultRow_res = _resultRow.replace("{PRODUCTIMAGESOURCE}", result_data.get("image_url", "")) \
        .replace("{PRODUCTLINK}", result_data.get("shop_link", "")) \
        .replace("{PRODUCTTITLE}", result_data.get("title", "")) \
        .replace("{PRODUCTDESCRIPTION}", result_data.get("content_description", "")) \
        .replace("{PRODUCTPRICE}", result_data.get("price", "")) \
        .replace("{PRODUCTSHOPNAME}", result_data.get("shop_name", ""))
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
    results = ShoppedData.query.filter(ShoppedData.searched_keyword == searched_keyword).order_by(ShoppedData.numeric_price.asc()).all()
    if results is not None and len(results) > 0:
        results = [res.__str__() for res in results]
    return results


def update_db_results(results):
    searched_keyword = results.get("searched_keyword")
    shop_name = results.get("shop_name")
    result_find = ShoppedData.query.\
        filter(ShoppedData.searched_keyword == searched_keyword, ShoppedData.shop_name == shop_name).\
        scalar()
    if result_find is not None:
        ShoppedData.query.\
            filter(ShoppedData.id == result_find.id).\
            update(results)
        return True
    return False


def update_search_view_with_db_results(results, search_keyword):
    output_data = ""
    for result in results:
        results = json.loads("".join(results))
        result_data = results.get(search_keyword, {})
        output_data += build_result_row(result_data)
    if output_data != "":
        update_results_row(output_data)
        return True
    return False


def add_results_to_db(results):
    if not update_db_results(results):
        shopped_data = wrapshopdata(results)
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
