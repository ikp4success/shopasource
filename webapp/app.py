import json
import asyncio
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool
from project.models import Job

from quart import jsonify, render_template, request
from sentry_sdk import init

from project import app, db
from shops.shop_utilities.shop_setup_functions import get_shops
from support import Config, generate_key
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


@app.route("/schedule/api/shop/search", methods=["GET"])
async def schedule_api_search():
    guid = generate_key()
    shop_list_names = []
    match_acc = 0
    low_to_high = False
    high_to_low = True
    kwargs = request.args
    kwargs["guid"] = guid
    job = Job(
        guid=guid,
        status="started",
        searched_keyword=request.args.get("sk"),
        shop_list_names=request.args.get("shops") or shop_list_names,
        smatch=request.args.get("smatch") or match_acc,
        slh=request.args.get("slh") or low_to_high,
        shl=request.args.get("shl") or high_to_low,
    )
    db.session.add(job)
    signature = partial(start_api_search, **kwargs)
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, signature)
    return {
        "guid": guid,
        "status": "success",
        **request.args
    }, 200


async def start_api_search(**kwargs):
    # http://127.0.0.1:8000/api/shop/search?sk=drones&smatch=50&shl=false&slh=false&shops=TARGET
    shop_list_names = []
    search_keyword = None
    match_acc = 0
    low_to_high = False
    high_to_low = True

    try:
        search_keyword = kwargs.get("sk")
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
        match_acc = int(kwargs.get("smatch") or 0)
        low_to_high = json.JSONDecoder().decode(kwargs.get("slh") or "false")
        high_to_low = json.JSONDecoder().decode(kwargs.get("shl") or "false")

        if not low_to_high:  # fail safe
            high_to_low = True
    except Exception:
        results = {
            "message": "Sorry, error encountered during search, try again or contact admin if error persist"
        }
        return (results, 404)

    if len(shop_list_names) > 0:
        pool = ThreadPool(len(shop_list_names))
        launch_spiders_partial = partial(
            run_api_search,
            shop_names_list=shop_list_names,
            search_keyword=search_keyword,
            match_acc=match_acc,
            low_to_high=low_to_high,
            high_to_low=high_to_low,
        )

        shops_thread_list = shop_list_names
        results = pool.map(launch_spiders_partial, shops_thread_list)
        pool.close()
        pool.join()
        if results and len(results) > 0 and results[0] != "null":
            results = jsonify(results[0])
            return (results, 200)
        results = {"message": "Sorry, no products found"}
        return (results, 404)
    else:
        results = run_api_search(
            [], shop_list_names, search_keyword, match_acc, low_to_high, high_to_low
        )
        if results and len(results) > 0:
            results = jsonify(results)
            return (results, 200)
        else:
            results = {"message": "Sorry, no products found"}
            return (results, 404)


@app.route("/api/shop/search", methods=["GET"])
async def api_search():
    return await start_api_search(**request.args)


@app.route("/websearch/shops-active.json", methods=["GET"])
async def shop_list_active():
    return jsonify(get_shops(active=True)), 200


async def home():
    return await render_template("home.html")


if __name__ == "__main__":
    app.run(threaded=True)
