import asyncio
import json
from datetime import datetime, timezone
from functools import partial

from db.models import APIUsage, Job
from support import config, get_logger
from tasks.results_factory import ResultsFactory, format_shop_names_list

logger = get_logger(__name__)

fallback_error = {"error": "Sorry, no products found"}


def update_status(**kwargs):
    if kwargs.get("job_id"):
        job = Job().get_item(id=kwargs.get("job_id"))
        if job and kwargs.get("status"):
            job.status = kwargs.get("status")
            job.commit()


def validate_params(**kwargs):
    try:
        cleaned = {
            "search_keyword": kwargs["sk"],
            "shop_names_list": kwargs["shops"],
            "match_acc": int(kwargs.get("smatch") or 0),
            "low_to_high": json.JSONDecoder().decode(kwargs.get("slh") or "false"),
            "high_to_low": json.JSONDecoder().decode(kwargs.get("shl") or "false"),
        }

        if not cleaned["low_to_high"]:  # fail safe
            cleaned["high_to_low"] = True
        cleaned["is_async"] = True
        if int(kwargs.get("async", 0)) == 0:
            cleaned["is_async"] = False
        return cleaned, True
    except Exception:
        results = {"error": "Parameters are invalid"}
        update_status(status="error", job_id=kwargs.get("job_id"))
        return results, False


def start_shop_search(**kwargs):
    res_factory = ResultsFactory(**kwargs, is_cache=False)
    results = res_factory.run_search()

    if not res_factory.is_async:
        if results and not isinstance(results, dict):
            update_status(status="done", job_id=kwargs.get("job_id"))
        else:
            results = fallback_error
            update_status(status="error", job_id=kwargs.get("job_id"))

        return results


def start_async_requests(**kwargs):
    job = Job(
        status="started",
        meta={
            shop_list_name: "started"
            for shop_list_name in format_shop_names_list(kwargs.get("shop_names_list"))
        },
        **kwargs,
    )
    job.commit()
    kwargs["status"] = job.status
    kwargs["job_id"] = str(job.id)
    kwargs["result"] = f"/api/get_result?job_id={str(job.id)}"
    signature = partial(start_shop_search, **kwargs)
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, signature)
    return kwargs


def get_results(**kwargs):
    job_id = kwargs["job_id"]
    status = "job not found"

    results = None
    logs = {}

    if job_id:
        job = Job().get_item(id=job_id)
        if job:
            status = job.status
            params = json.loads(job.__repr__())
            res_factory = ResultsFactory(**params, is_cache=True)
            results = res_factory.run_search()
            in_progress = False
            if job.meta:
                logs = job.meta
                if status != "done":
                    for _, v in job.meta.items():
                        if v not in ["done", "error"]:
                            in_progress = True
                            break

                status = "in_progress" if in_progress else "done"
        if not results:
            results = fallback_error
    else:
        results = {"error": "job_id is required"}

    return {"status": status, "data": results, "logs": logs}


def get_api_key(request):
    user = get_ip(request)
    api_key = config.API_KEY
    if config.ENV_CONFIGURATION != "debug" and not config.SUPER_USER:
        api = APIUsage().get_item(user=user)
        if api:
            usage_count = api.usage_count
            if usage_count > config.API_MAX_USAGE:
                dt_time_diff = datetime.now(timezone.utc) - api.date_usage
                if dt_time_diff.days > config.API_MAX_USAGE_DAYS:
                    usage_count = 0
                else:
                    return {
                        "error": f"API rate limit is exceeded, try again in {config.API_MAX_USAGE_DAYS} day(s)."
                    }
            api.update_item(usage_count=usage_count + 1)
        else:
            api = APIUsage(user=user, usage_count=1, api_key=api_key,)
            api.commit()

    return {"public_api_key": api_key}


def get_ip(request):
    logger.info(request.headers)
    ip_addr = request.remote_addr
    if request.headers.get("X-Forwarded-For"):
        ip_addr = request.headers["X-Forwarded-For"]
    elif request.headers.getlist("X-Forwarded-For"):
        ip_addr = request.headers.getlist("X-Forwarded-For")[-1]
    return ip_addr
