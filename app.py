import time
from flask import render_template
from flask import jsonify
from flask import request
from flask import session

from project import (
    db,
    app,
    app_user_session
)

from tasks import (
    get_active_bg_task,
    api_bg_task
)

from shops.shop_utilities.extra_function import safe_grab


db.create_all()

task_ids_dict = {}


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
        task_ids = safe_grab(task_ids_dict, [app_user_session_sn_sk, "TASK_IDS"], default=[])
        task_id = result_data.task_id
        old_sk = safe_grab(task_ids_dict, [app_user_session_sn_sk, "sk"])
        if sk != old_sk:
            task_ids_dict[app_user_session_sn_sk] = {}
        task_ids_dict[app_user_session_sn_sk]["sk"] = sk
        task_ids.append(task_id)
        task_ids_dict[app_user_session_sn_sk]["TASK_IDS"] = task_ids
        session["task_ids_dict"] = task_ids_dict
        # return get_tasks()
        return (jsonify({"message": "queued"}), 200)
    else:
        return (jsonify({"message": "oops"}), 400)


@app.route("/refresh", methods=['GET'])
def get_tasks():
    task_ids_dict = session["task_ids_dict"]
    print(str(task_ids_dict))
    result_data = []
    shop_name = request.args.get("shops")
    sk = request.args.get("sk")
    if sk and shop_name and len(task_ids_dict.keys()) > 0:
        shop_name = "".join(shop_name)
        app_user_session_sn_sk = "{}-{}-{}".format(app_user_session, shop_name, sk)
        task_ids = safe_grab(task_ids_dict, [app_user_session_sn_sk, "TASK_IDS"], default=[])
        sk = safe_grab(task_ids_dict, [app_user_session_sn_sk, "sk"]) or sk
        print("\nID - {}\nApp_Session_ID - {}\nSk - {}\nTask_ids - {}\n".format(app_user_session_sn_sk, app_user_session, sk, str(task_ids)))
        for task_id in task_ids:
            task_id = api_bg_task.AsyncResult(task_id)
            if task_id.ready():
                if "message" in task_id.result:
                    continue
                result_data.extend(task_id.result)
        if len(result_data) > 0:
            return (jsonify(result_data), 200)
        return (jsonify({"message": "Loading tasks"}), 200)
    return (jsonify({"message": "oops"}), 400)


@app.route("/websearch/shops-active.json", methods=['GET'])
def shop_list_active():
    result_data = get_active_bg_task.delay()
    return jsonify(result_data.wait()), 200


def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(threaded=True)
