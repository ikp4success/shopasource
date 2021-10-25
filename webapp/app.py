from datetime import timedelta

from quart import Quart, jsonify, render_template, request
from quart_rate_limiter import RateLimiter, rate_limit

from db.models import Model, engine
from shops.shop_util.shop_setup_functions import get_shops
from support import CustomEncoder, config, get_logger
from webapp.config import configure_app
from webapp.decor_util import authorize, docache
from webapp.util import (
    get_api_key,
    get_results,
    start_async_requests,
    start_shop_search,
    validate_params,
)

logger = get_logger(__name__)

config.intialize_sentry()

app = Quart(__name__, template_folder="web_content")
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.json_encoder = CustomEncoder
configure_app(app)
RateLimiter(app)
Model.metadata.create_all(engine)


@app.after_request
async def add_header(response):
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    return response


@app.route("/", methods=["GET"])
@docache(hours=24, content_type="html")
@rate_limit(1000, timedelta(minutes=1))
async def home_page():
    return await render_template("home.html")


@app.route("/about", methods=["GET"])
@docache(hours=24, content_type="html")
@rate_limit(1000, timedelta(minutes=1))
async def about():
    return await render_template("about.html")


@app.route("/api", methods=["GET"])
@docache(hours=24, content_type="html")
@rate_limit(1000, timedelta(minutes=1))
async def api():
    return await render_template("api.html")


@app.route("/robots.txt", methods=["GET"])
@docache(hours=24, content_type="html")
@rate_limit(1000, timedelta(minutes=1))
async def robots():
    return await render_template("robots.txt")


@app.route("/api/get_result", methods=["GET"])
@authorize(app)
@rate_limit(1000, timedelta(minutes=2))
async def get_result():
    if not request.args.get("job_id"):
        return ({"error": "job_id is required."}, 400)
    return get_results(**request.args), 200


@app.route("/api/shop/search", methods=["GET"])
@authorize(app)
@rate_limit(100, timedelta(minutes=1))
async def api_search():
    # http://0.0.0.0:5003/api/shop/search?sk=tissue&smatch=0&shl=false&slh=true&shops=TARGET,AMAZON&async=1
    params = validate_params(**{**request.args})
    if not params[1]:
        return (params, 400)

    if params[0]["is_async"]:
        start_data = start_async_requests(**params[0])
        return jsonify({**start_data}), 201
    else:
        if config.ENV_CONFIGURATION == "debug":
            return jsonify(start_shop_search(**params[0])), 200
        else:
            return {"error": "sync api search allowed only in debug mode."}, 400


@app.route("/api/shops-active.json", methods=["GET"])
@docache(hours=1, content_type="json")
@authorize(app)
@rate_limit(5000, timedelta(minutes=2))
async def shop_list_active():
    return jsonify(get_shops(active=True)), 200


@app.route("/api/public_api_key", methods=["GET"])
@docache(minutes=5, content_type="json")
@rate_limit(1000, timedelta(minutes=2))
async def get_public_api_key():
    api_key_info = get_api_key(request)
    if api_key_info.get("error"):
        return api_key_info, 429
    return api_key_info, 200


if __name__ == "__main__":
    app.run(threaded=True)
