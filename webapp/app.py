import json
import asyncio
from functools import partial
from project.models import Job

from quart import jsonify, render_template, request
from sentry_sdk import init

from project import app, db
from shops.shop_utilities.shop_setup_functions import get_shops
from support import Config
from utilities.results_factory import run_api_search
from webapp.config import configure_app

init(Config().SENTRY_DSN)

configure_app(app)
db.create_all()


@app.after_request
async def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response


@app.route("/", methods=["GET"])
async def home_page():
    return await home()


@app.route("/about", methods=["GET"])
async def about():
    return await render_template("about.html")


@app.route("/api", methods=["GET"])
async def api():
    return await render_template("api.html")


@app.route("/robots.txt", methods=["GET"])
async def robots():
    return await render_template("robots.txt")


def format_shop(**kwargs):
    shop_list_names = kwargs.get("shops")
    if shop_list_names:
        shop_list_names = shop_list_names.strip()
        if "," in shop_list_names:
            shop_list_names = [
                shn.strip().upper()
                for shn in shop_list_names.split(",")
                if shn.strip()
            ]
        else:
            shop_list_names = [shop_list_names.upper()]

    return shop_list_names


def update_status(**kwargs):
    if kwargs.get("guid"):
        Job.query.filter(
            Job.id == kwargs.get("guid"),
        ).update({"status": kwargs.get("status")})

        db.session.commit()


@app.route("/api/get_result", methods=["GET"])
async def get_result():
    guid = request.args.get("guid")
    if guid:
        job = Job.query.filter(
            Job.id == guid,
        ).scalar()
        if job:
            shop_list_names = format_shop(shops=job.shop_list_names)
            match_acc = int(job.smatch or 0)
            low_to_high = json.JSONDecoder().decode(job.slh or "false")
            high_to_low = json.JSONDecoder().decode(job.shl or "false")
            results = []
            for shop_list_name in shop_list_names:
                result = {
                    shop_list_name: run_api_search(
                        [], [shop_list_name], job.searched_keyword, match_acc, low_to_high, high_to_low, is_cache=True
                    )
                }
                results.append(result)
            if not results:
                results = {"message": "Sorry, no products found"}
        else:
            results = {"message": "Sorry, no products found"}

        output = {
            "status": job.status,
            "data": results
        }

        return jsonify(output), 200


def start_api_search(**kwargs):
    # http://127.0.0.1:8000/api/shop/search?sk=drones&smatch=50&shl=false&slh=false&shops=TARGET
    shop_list_names = []
    search_keyword = None
    match_acc = 0
    low_to_high = False
    high_to_low = True

    try:
        search_keyword = kwargs.get("sk")
        shop_list_names = format_shop(**kwargs)
        match_acc = int(kwargs.get("smatch") or 0)
        low_to_high = json.JSONDecoder().decode(kwargs.get("slh") or "false")
        high_to_low = json.JSONDecoder().decode(kwargs.get("shl") or "false")

        if not low_to_high:  # fail safe
            high_to_low = True
    except Exception:
        results = {
            "message": "Sorry, error encountered during search, try again or contact admin if error persist"
        }
        update_status(status="error", guid=kwargs.get("guid"))
        return (results, 404)

    results = run_api_search(
        [], shop_list_names, search_keyword, match_acc, low_to_high, high_to_low, is_cache=False
    )
    if results and len(results) > 0 and results[0] != "null":
        results = results[0]
        update_status(status="done", guid=kwargs.get("guid"))
        return results
    results = {"message": "Sorry, no products found"}
    update_status(status="error", guid=kwargs.get("guid"))

    return results


@app.route("/schedule/api/shop/search", methods=["GET"])
async def schedule_api_search():
    match_acc = 0
    low_to_high = False
    high_to_low = True
    kwargs = {**request.args}
    job = Job(
        status="started",
        searched_keyword=request.args.get("sk"),
        shop_list_names=request.args.get("shops"),
        smatch=request.args.get("smatch") or match_acc,
        slh=request.args.get("slh") or low_to_high,
        shl=request.args.get("shl") or high_to_low,
    )
    db.session.add(job)
    db.session.commit()
    kwargs["guid"] = str(job.id)
    kwargs["result"] = f"/api/get_result?guid={str(job.id)}"
    signature = partial(start_api_search, **kwargs)
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, signature)
    return {
        "status": job.status,
        **kwargs
    }, 200


@app.route("/api/shop/search", methods=["GET"])
async def api_search():
    kwargs = {**request.args}
    return jsonify(start_api_search(**kwargs), 200)


@app.route("/websearch/shops-active.json", methods=["GET"])
async def shop_list_active():
    return jsonify(get_shops(active=True)), 200


async def home():
    return await render_template("home.html")


if __name__ == "__main__":
    app.run(threaded=True)
