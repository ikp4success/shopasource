import asyncio
import json
from functools import partial

from project.models import Job
from support import get_logger
from tasks.results_factory import ResultsFactory

logger = get_logger(__name__)


def update_status(**kwargs):
    if kwargs.get("guid"):
        job = Job().get_item(id=kwargs.get("guid"))
        if job and kwargs.get("status"):
            job.status = kwargs.get("status")
            job.commit()


def format_shop_list_names(**kwargs):
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


def validate_params(**kwargs):
    try:
        cleaned = {
            "search_keyword": kwargs["sk"],
            "shop_list_names_str": kwargs["shops"],
            "shop_list_names": format_shop_list_names(**kwargs),
            "match_acc": int(kwargs.get("smatch") or 0),
            "low_to_high": json.JSONDecoder().decode(kwargs.get("slh") or "false"),
            "high_to_low": json.JSONDecoder().decode(kwargs.get("shl") or "false"),
        }

        if not cleaned["low_to_high"]:  # fail safe
            cleaned["high_to_low"] = True
        cleaned["is_async"] = True
        if int(kwargs.get("async", 0)) == 0:
            cleaned["is_async"] = False
        return cleaned
    except Exception:
        results = [{"message": "Parameters are invalid"}]
        update_status(status="error", guid=kwargs.get("guid"))
        return (results, False)


def start_shop_search(**kwargs):
    res_factory = ResultsFactory(**kwargs, is_cache=False)
    results = res_factory.run_search()

    if not res_factory.is_async:
        if results and len(results) > 0 and results[0] != "null":
            results = results[0]
            update_status(status="done", guid=kwargs.get("guid"))
        else:
            results = [{"message": "Sorry, no products found"}]
            update_status(status="error", guid=kwargs.get("guid"))

        return results


def start_async_requests(**kwargs):
    shop_list_names_str = kwargs.get("shop_list_names")
    job = Job(
        status="started",
        shop_list_names=shop_list_names_str,
        meta={
            shop_list_name: "started"
            for shop_list_name in kwargs.get("shop_list_names")
        },
        **kwargs,
    )
    job.commit()
    kwargs["status"] = job.status
    kwargs["guid"] = str(job.id)
    kwargs["result"] = f"/api/get_result?guid={str(job.id)}"
    signature = partial(start_shop_search, **kwargs)
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, signature)
    return kwargs


def get_results(**kwargs):
    guid = kwargs["guid"]
    status = "job not found"
    fallback_error = [{"message": "Sorry, no products found"}]
    results = None

    if guid:
        job = Job().get_item(id=guid)
        if job:
            status = job.status
            params = job.repr()
            params["shop_list_names"] = format_shop_list_names(
                shops=job.shop_list_names
            )
            res_factory = ResultsFactory(**params, is_cache=True)
            results = res_factory.run_search()
            in_progress_shops = []
            meta_print = None
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

        return {"status": status, "data": results, "meta": meta_print}
