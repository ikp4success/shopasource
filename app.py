from flask import render_template
from flask import jsonify
from flask import request
from flask import session
from sys import getsizeof
import time

from project import (
    db,
    app,
    app_user_session
)

from tasks import (
    get_active_bg_task,
    api_bg_task,
    check_task
)

from shops.shop_utilities.extra_function import safe_grab


db.create_all()


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.route("/", methods=['GET'])
def home_page():
    return home()


@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')


@app.route("/robots.txt", methods=['GET'])
def robots():
    return render_template('robots.txt')


@app.route("/api/shop/search", methods=['GET'])
def api_search():
    result_data = api_bg_task.delay(request.args)
    if result_data.ready():
        return (jsonify(result_data.result), 200)
    shop_name = request.args.get("shops")
    sk = request.args.get("sk")
    if sk and shop_name:
        shop_name = "".join(shop_name)
        app_user_session_sn_sk = "{}-{}-{}".format(app_user_session, shop_name, sk)
        return queue_task(result_data, app_user_session_sn_sk, sk)
    else:
        return (jsonify({"message": "oops"}), 400)


@app.route("/api/shop/filter", methods=['GET'])
def filter_api_search():
    result_data = api_bg_task.delay(request.args)
    if result_data.ready():
        return (jsonify(result_data.result), 200)
    shop_name = request.args.get("shops")
    sk = request.args.get("sk")
    if sk and shop_name:
        shop_name = "".join(shop_name)
        app_user_session_sn_sk = "filter-{}-{}-{}".format(app_user_session, shop_name, sk)
        return queue_task(result_data, app_user_session_sn_sk, sk)
    else:
        return (jsonify({"message": "oops"}), 400)


def queue_task(result_data, app_user_session_sn_sk, sk):
    task_ids_dict = session["task_ids_dict"]
    task_ids = safe_grab(task_ids_dict, [app_user_session_sn_sk, "TASK_IDS"], default=[])
    if len(task_ids_dict.keys()) > 0 and getsizeof(task_ids) > 4080:
        print("browser limit for cookie session exceeded for {}".format(app_user_session_sn_sk))
        print("resetting queue for {}".format(app_user_session_sn_sk))
        task_ids = {}
        # TODO: need a better a way of handling data between request

    task_id = result_data.task_id
    old_sk = safe_grab(task_ids_dict, [app_user_session_sn_sk, "sk"])
    if sk != old_sk:
        task_ids_dict[app_user_session_sn_sk] = {}
    task_ids_dict[app_user_session_sn_sk]["sk"] = sk
    task_ids.append(task_id)
    task_ids_dict[app_user_session_sn_sk]["TASK_IDS"] = task_ids
    session["task_ids_dict"] = task_ids_dict
    return (jsonify({"message": "queued"}), 201)


@app.route("/refresh", methods=['GET'])
def get_tasks():
    task_ids_dict = session["task_ids_dict"]
    print(str(task_ids_dict))
    shop_name = request.args.get("shops")
    sk = request.args.get("sk")
    import pdb; pdb.set_trace()
    if sk and shop_name and len(task_ids_dict.keys()) > 0:
        app_user_session_sn_sk = "{}-{}-{}".format(app_user_session, shop_name, sk)
        result_task = check_task.delay(sk, task_ids_dict, app_user_session_sn_sk, app_user_session)
        if result_task.ready() and not safe_grab(result_task.result, ["message"]):
            return (jsonify(result_task.result), 200)
        shop_name = "".join(shop_name)
        app_user_session_sn_sk = "{}-{}-{}".format(app_user_session, shop_name, sk)
        return queue_task(result_task, app_user_session_sn_sk, sk)

    return (jsonify({"message": "oops"}), 400)


@app.route("/refresh/filter", methods=['GET'])
def get_filter_task():
    task_ids_dict = session["task_ids_dict"]
    print(str(task_ids_dict))
    shop_name = request.args.get("shops")
    sk = request.args.get("sk")
    if sk and shop_name and len(task_ids_dict.keys()) > 0:
        app_user_session_sn_sk = "filter-{}-{}-{}".format(app_user_session, shop_name, sk)
        result_task = check_task.delay(sk, task_ids_dict, app_user_session_sn_sk, app_user_session, is_filter=True)
        if result_task.ready() and not safe_grab(result_task.result, ["message"]):
            return (jsonify(result_task.result), 200)
        shop_name = "".join(shop_name)
        app_user_session_sn_sk = "filter-{}-{}-{}".format(app_user_session, shop_name, sk)
        return queue_task(result_task, app_user_session_sn_sk, sk)

    return (jsonify({"message": "oops"}), 400)


@app.route("/websearch/shops-active.json", methods=['GET'])
def shop_list_active():
    result_data = get_active_bg_task.delay()
    return jsonify(result_data.wait()), 200


def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(threaded=True)
