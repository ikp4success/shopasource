from datetime import datetime, timedelta
from functools import wraps

from quart import make_response, request

from support import get_logger
from webapp.util import get_api_key

logger = get_logger(__name__)


def authorize(app):
    def _authorize(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            headers = request.headers
            headers_lower_case = {}
            for k, v in headers.items():
                k = k.lower()
                headers_lower_case[k] = v
            auth = headers_lower_case.get("x-api-key")
            # check api usage limit
            api_key_info = get_api_key(request)
            if api_key_info.get("error"):
                return api_key_info, 429

            if (
                not api_key_info.get("public_api_key")
                or auth != api_key_info["public_api_key"]
            ):
                logger.error("User could not authenticate!")
                status = {
                    "status": "Unauthorized",
                    "error": "You have failed authentication!",
                }
                return (
                    status,
                    401,
                )
            return await func(*args, **kwargs)

        return wrapper

    return _authorize


def docache(content_type="json", **kwargs):
    # stolen and modified from https://maskaravivek.medium.com/how-to-add-http-cache-control-headers-in-flask-34659ba1efc0
    content_types = {
        "json": "application/json; charset=utf-8",
        "html": "text/html; charset=utf-8",
    }
    max_age_secs = kwargs.get("seconds")
    if kwargs.get("minutes"):
        max_age_secs = kwargs.get("minutes") * 60
    elif kwargs.get("hours"):
        max_age_secs = kwargs.get("hours") * 3600

    """ Flask decorator that allow to set Expire and Cache headers. """

    def fwrap(func):
        @wraps(func)
        async def wrapped_f(*args, **kwargs):
            req = await func(*args, **kwargs)
            then = datetime.now() + timedelta(**kwargs)
            rsp = await make_response(req)
            rsp.headers.add("Content-Type", content_types[content_type])
            rsp.headers.add("Expires", then.strftime("%a, %d %b %Y %H:%M:%S GMT"))
            rsp.headers.add("Cache-Control", f"public,max-age={max_age_secs}")
            return rsp

        return wrapped_f

    return fwrap
