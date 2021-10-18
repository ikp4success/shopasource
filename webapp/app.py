from quart import Quart, jsonify, render_template, request

from db.models import Model, engine
from shops.shop_util.shop_setup_functions import get_shops
from support import Config, get_logger, CustomEncoder
from webapp.config import configure_app
from webapp.util import (
    get_results,
    start_async_requests,
    start_shop_search,
    validate_params,
)

logger = get_logger(__name__)

Config().intialize_sentry()

app = Quart(__name__, template_folder="web_content")
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.json_encoder = CustomEncoder
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


@app.route("/api/get_result", methods=["GET"])
async def get_result():
    if not request.args.get("job_id"):
        return ({"error": "job_id is required."}, 400)
    return get_results(**request.args), 200


@app.route("/api/shop/search", methods=["GET"])
async def api_search():
    # http://0.0.0.0:5003/api/shop/search?sk=tissue&smatch=0&shl=false&slh=true&shops=TARGET,AMAZON&async=1
    params = validate_params(**{**request.args})
    if not params[1]:
        return (params, 400)

    if params[0]["is_async"]:
        start_data = start_async_requests(**params[0])
        return jsonify({**start_data}), 200
    else:
        return jsonify(start_shop_search(**params[0])), 200


@app.route("/websearch/shops-active.json", methods=["GET"])
async def shop_list_active():
    return jsonify(get_shops(active=True)), 200


async def home():
    return await render_template("home.html")


if __name__ == "__main__":
    app.run(threaded=True)
