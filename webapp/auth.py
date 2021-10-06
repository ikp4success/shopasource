import logging
from functools import wraps

from flask import request

logger = logging.getLogger(__name__)


def authorize(app):
    def _authorize(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            headers = request.headers
            headers_lower_case = {}
            for k, v in headers.items():
                k = k.lower()
                headers_lower_case[k] = v
            auth = headers_lower_case.get("x-api-key")
            api_key = app.config.get("API_KEY")

            if not api_key or auth != api_key:
                logger.error("User could not authenticate!")
                status = {
                    "status": "Unauthorized",
                    "message": "You have failed authentication!",
                }
                return (
                    status,
                    401,
                )
            return func(*args, **kwargs)

        return wrapper

    return _authorize
