import asyncio
import json
from functools import partial

from quart import Quart, jsonify, render_template, request

from project.models import Job, Model, engine
from shops.shop_util.shop_setup_functions import get_shops
from support import Config, get_logger
from tasks.results_factory import run_search
from webapp.config import configure_app

logger = get_logger(__name__)

Config().intialize_sentry()

app = Quart(__name__, template_folder="web_content")
configure_app(app)
Model.metadata.create_all(engine)


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
                shn.strip().upper() for shn in shop_list_names.split(",") if shn.strip()
            ]
        else:
            shop_list_names = [shop_list_names.upper()]

    return shop_list_names


def update_status(**kwargs):
    if kwargs.get("guid"):
        job = Job().get_item(id=kwargs.get("guid"))
        if job and kwargs.get("status"):
            job.status = kwargs.get("status")
            job.commit()


@app.route("/api/get_result", methods=["GET"])
async def get_result():
    guid = request.args.get("guid")
    status = "job not found"
    fallback_error = [{"message": "Sorry, no products found"}]
    results = None
    import pdb

    pdb.set_trace()
    if guid:
        job = Job().get_item(id=guid)
        if job:
            status = job.status
            shop_list_names = format_shop(shops=job.shop_list_names)
            match_acc = int(job.smatch or 0)
            low_to_high = json.JSONDecoder().decode(job.slh or "false")
            high_to_low = json.JSONDecoder().decode(job.shl or "false")
            results = run_search(
                shop_list_names,
                job.searched_keyword,
                match_acc,
                low_to_high,
                high_to_low,
                is_cache=True,
                job_id=job.id,
            )
            in_progress_shops = []
            if job.meta and status != "done":
                for k, v in job.meta.items():
                    if v != "done":
                        in_progress_shops.append(k)

                status = "done"
                if in_progress_shops:
                    logger.debug("{in_progress_shops} still in progress.")
                    status = "in_progress"
            elif job.meta:
                for k, _ in job.meta.items():
                    job.meta[k] = "done"
                job.commit()

        if not results:
            results = fallback_error

        output = {"status": status, "data": results}

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

    is_async = True
    if kwargs.get("async") == "0":
        is_async = False

    results = run_search(
        shop_list_names,
        search_keyword,
        match_acc,
        low_to_high,
        high_to_low,
        is_cache=False,
        is_async=is_async,
        job_id=kwargs.get("guid"),
    )

    if results and len(results) > 0 and results[0] != "null":
        results = results[0]
        update_status(status="done", guid=kwargs.get("guid"))
    else:
        results = {"message": "Sorry, no products found"}
        update_status(status="error", guid=kwargs.get("guid"))

    return results


@app.route("/api/shop/search", methods=["GET"])
async def api_search():
    match_acc = 0
    low_to_high = False
    high_to_low = True
    kwargs = {**request.args}

    if int(kwargs.get("async", "0")) == 1:
        shop_list_names = format_shop(**kwargs)
        job = Job(
            status="started",
            searched_keyword=request.args.get("sk"),
            shop_list_names=request.args.get("shops"),
            smatch=request.args.get("smatch") or match_acc,
            slh=request.args.get("slh") or low_to_high,
            shl=request.args.get("shl") or high_to_low,
            meta={shop_list_name: "started" for shop_list_name in shop_list_names},
        )
        job.commit()
        kwargs["guid"] = str(job.id)
        kwargs["result"] = f"/api/get_result?guid={str(job.id)}"
        signature = partial(start_api_search, **kwargs)
        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, signature)
        return {"status": job.status, **kwargs}, 200
    else:
        return jsonify(start_api_search(**kwargs), 200)


@app.route("/websearch/shops-active.json", methods=["GET"])
async def shop_list_active():
    return jsonify(get_shops(active=True)), 200


async def home():
    return await render_template("home.html")


if __name__ == "__main__":
    app.run(threaded=True)
