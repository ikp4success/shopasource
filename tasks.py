import json
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool
from utilities.results_factory import run_api_search
from shops.shop_utilities.shop_setup_functions import get_shops
from shops.shop_utilities.extra_function import safe_grab
from project import celery


@celery.task(name="tasks.get_active_bg_task")
def get_active_bg_task():
    return get_shops(active=True)


@celery.task(name="tasks.check_task")
def check_task(sk, task_ids_dict, app_user_session_sn_sk, app_user_session, is_filter=False):
    result_data = []
    print("Task_IDS")
    print(str(task_ids_dict))
    task_ids = safe_grab(task_ids_dict, [app_user_session_sn_sk, "TASK_IDS"], default=[])
    sk = safe_grab(task_ids_dict, [app_user_session_sn_sk, "sk"]) or sk
    print("\nID - {}\nApp_Session_ID - {}\nSk - {}\nTask_ids - {}\n".format(app_user_session_sn_sk, app_user_session, sk, str(task_ids)))
    for task_id in task_ids:
        task_id = api_bg_task.AsyncResult(task_id)
        if task_id.ready():
            if is_filter:
                result_data = task_id.result
                continue
            if task_id.result == {'message': 'Loading tasks'}:
                continue
            if task_id.result and len(task_id.result) > 0 and safe_grab(task_id.result[0], ["message"]):
                result_data.extend([json.dumps(task_id.result[0])])
                continue
            result_data.extend(task_id.result)
    if len(result_data) > 0:
        return result_data
    return {"message": "Loading tasks"}


@celery.task(name="tasks.api_bg_task")
def api_bg_task(request_args):
    # request_args = request.args
    # http://127.0.0.1:8000/api/shop/search?sk=drones&smatch=50&shl=false&slh=false&shops=TARGET
    shop_list_names = []
    search_keyword = None
    match_acc = 0
    low_to_high = False
    high_to_low = True

    try:
        search_keyword = request_args.get("sk")
        shop_list_names = request_args.get("shops")
        if shop_list_names:
            shop_list_names = shop_list_names.strip()
            if "," in shop_list_names:
                shop_list_names = [shn.strip().upper() for shn in shop_list_names.split(",") if shn.strip()]
            else:
                shop_list_names = [shop_list_names.upper()]
        match_acc = int(request_args.get("smatch") or 0)
        low_to_high = json.JSONDecoder().decode(request_args.get("slh") or "false")
        high_to_low = json.JSONDecoder().decode(request_args.get("shl") or "false")

        if not low_to_high:  # fail safe
            high_to_low = True
    except Exception:
        results = {"message": "Sorry, error encountered during search, try again or contact admin if error persist"}
        # return (results, 404)
        return results

    if len(shop_list_names) > 0 and len(shop_list_names) == 1:
        pool = ThreadPool(len(shop_list_names))
        launch_spiders_partial = partial(
            run_api_search,
            shop_names_list=shop_list_names,
            search_keyword=search_keyword,
            match_acc=match_acc,
            low_to_high=low_to_high,
            high_to_low=high_to_low)

        shops_thread_list = shop_list_names
        results = pool.map(launch_spiders_partial, shops_thread_list)
        pool.close()
        pool.join()
        if results and len(results) > 0 and results[0] != "null":
            # results = jsonify(results[0])
            return results[0]
            # return (results, 200)
        results = {"message": "Sorry, no products found"}
        # return (results, 404)
        return results
    else:
        results = run_api_search([], shop_list_names, search_keyword, match_acc, low_to_high, high_to_low)
        if results and len(results) > 0:
            # results = jsonify(results)
            return results
            # return (results, 200)
        else:
            results = {"message": "Sorry, no products found"}
            return results
            # return (results, 404)
