from datetime import timedelta

from quart import Quart, jsonify, render_template, request
from quart_rate_limiter import RateLimiter, rate_limit

from db.models import Model, engine
from shops.shop_util.shop_setup_functions import get_shops
from support import CustomEncoder, config, get_logger
from webapp.config import configure_app
from webapp.decor_util import authorize, docache
from webapp.llm_providers import (
    PROVIDER_LABELS,
    LLMConfigError,
    available_providers,
    extraction_failure_status,
)
from webapp.nl_search import parse_nl_query
from webapp.util import (
    get_api_key,
    get_results,
    start_async_requests,
    start_shop_search,
    validate_params,
)

logger = get_logger(__name__)

config.intialize_sentry()

# Pseudo-provider: skip the LLM entirely and treat the query text as a plain
# keyword, searched across every active shop - the pre-AI search behavior.
# Always offered in the model picker (even the only option, if no LLM key is
# configured at all) so search never fully dead-ends.
NORMAL_SEARCH_PROVIDER = "normal"
NORMAL_SEARCH_LABEL = "Normal Search (no AI)"

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
@rate_limit(1500, timedelta(minutes=2))
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


@app.route("/api/shop/nl_search", methods=["GET"])
@authorize(app)
@rate_limit(30, timedelta(minutes=1))
async def api_nl_search():
    # http://0.0.0.0:5003/api/shop/nl_search?q=cheap+waterproof+hiking+boots+from+target+and+amazon
    query_text = request.args.get("q")
    if not query_text:
        return {"error": "q is required."}, 400

    is_async = int(request.args.get("async", 1)) != 0
    provider = request.args.get("provider") or None

    if provider == NORMAL_SEARCH_PROVIDER:
        nl_params = {
            "sk": query_text,
            "shops": ",".join(get_shops(active=True)),
            "smatch": "0",
            "shl": "false",
            "slh": "true",
            "async": "1" if is_async else "0",
        }
    else:
        try:
            nl_params = parse_nl_query(query_text, is_async=is_async, provider=provider)
        except LLMConfigError as ex:
            return {"error": str(ex)}, 400
        except Exception as ex:
            status = extraction_failure_status(ex)
            if status is not None:
                logger.warning(
                    "LLM provider request failed (status=%s) for query %r: %s",
                    status,
                    query_text,
                    ex,
                )
                return {
                    "error": (
                        "The selected AI model rejected the request "
                        f"(HTTP {status} - likely rate limited, out of quota/credits, "
                        f"or a billing issue on that account). Try "
                        f"'{NORMAL_SEARCH_LABEL}' or a different model from the "
                        "picker, or again shortly."
                    )
                }, 400
            logger.exception("Failed to parse natural language query: %s", query_text)
            return {"error": "Could not understand that search, try rephrasing."}, 400

    params = validate_params(**nl_params)
    if not params[1]:
        return (params, 400)

    if params[0]["is_async"]:
        start_data = start_async_requests(**params[0])
        return jsonify({**start_data, "interpreted_query": nl_params}), 201
    else:
        if config.ENV_CONFIGURATION == "debug":
            return jsonify(start_shop_search(**params[0])), 200
        else:
            return {"error": "sync api search allowed only in debug mode."}, 400


@app.route("/api/llm-providers.json", methods=["GET"])
@docache(hours=1, content_type="json")
@authorize(app)
@rate_limit(5000, timedelta(minutes=2))
async def llm_providers_active():
    providers = available_providers()
    options = [{"id": p, "label": PROVIDER_LABELS[p]} for p in providers]
    options.append({"id": NORMAL_SEARCH_PROVIDER, "label": NORMAL_SEARCH_LABEL})
    return jsonify(options), 200


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
