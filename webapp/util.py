import asyncio
import json
from functools import partial

from project.models import Job
from support import get_logger
from tasks.results_factory import ResultsFactory, format_shop_names_list

logger = get_logger(__name__)


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
        results = [{"message": "Parameters are invalid"}]
        update_status(status="error", job_id=kwargs.get("job_id"))
        return results, False


def start_shop_search(**kwargs):
    res_factory = ResultsFactory(**kwargs, is_cache=False)
    results = res_factory.run_search()

    if not res_factory.is_async:
        if results and len(results) > 0 and results[0] != "null":
            results = results[0]
            update_status(status="done", job_id=kwargs.get("job_id"))
        else:
            results = [{"message": "Sorry, no products found"}]
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
    fallback_error = [{"message": "Sorry, no products found"}]
    results = None

    meta_print = None
    if job_id:
        job = Job().get_item(id=job_id)
        if job:
            status = job.status
            params = json.loads(job.__repr__())
            res_factory = ResultsFactory(**params, is_cache=True)
            results = res_factory.run_search()
            in_progress_shops = []
            if job.meta and status != "done":
                for k, v in job.meta.items():
                    if v != "done":
                        in_progress_shops.append(k)

                status = "done"
                if in_progress_shops:
                    meta_print = f"{in_progress_shops} still in progress."
                    logger.debug(meta_print)
                    status = "in_progress"

        if not results:
            results = fallback_error
    else:
        results = [{"message": "job_id is required"}]

    return {"status": status, "data": results, "meta": meta_print}
