
from flask import render_template
from flask import jsonify
from flask import request
from flask import session
from celery.result import AsyncResult

from project import (
    db,
    app
)

from tasks import (
    get_active_bg_task,
    api_bg_task
)


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
    tasks_ids = []
    if len(session.keys()) > 0:
        tasks_ids = session.get("TASK_IDS", [])
    tasks_ids.append(result_data.task_id)
    session["TASK_IDS"] = tasks_ids
    return get_tasks()
    # if(result_data == {"message": "Sorry, no products found"}):
    #     return (result_data.wait(), 404)
    # return (jsonify(result_data.wait()), 200)


@app.route("/refresh", methods=['GET'])
def get_tasks():
    if len(session.keys()) > 0:
        task_ids = session['TASK_IDS']
        for task_id in task_ids:
            task_id = api_bg_task.AsyncResult(task_id)
            if task_id.ready():
                result_data = task_id.result
                if(result_data == {"message": "Sorry, no products found"}):
                    return (result_data, 404)
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
