import json
import re
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from threading import Semaphore

from dateutil import parser
from sqlalchemy import or_

from db.models import ShoppedData
from shops.shop_util.extra_function import safe_grab, safe_json, save_job, truncate_data
from shops.shop_util.shop_setup_functions import find_shop, is_shop_active
from support import config, get_logger
from tasks.scrapy_run import import_class, launch_spiders

logger = get_logger(__name__)

config.intialize_sentry()

# use_browser_fetch shops each launch a real headless Chromium instance, which is
# far heavier than the default/direct_fetch tiers - letting all of MAX_CONCURRENT_SHOPS
# be browser shops at once (e.g. a search that happens to hit Amazon, Walmart, ASOS,
# Zara, ... together) can spike memory well past what a small deployment has. This
# is a per-process soft cap (same scope/limitation as MAX_CONCURRENT_SHOPS itself -
# it doesn't coordinate across hypercorn's multiple worker processes).
_browser_fetch_semaphore = Semaphore(config.MAX_CONCURRENT_BROWSER_SHOPS)


def _is_browser_fetch_shop(shop_name):
    try:
        return bool(import_class(shop_name).use_browser_fetch)
    except Exception:
        return False


def _launch_shop(shop_name, search_keyword, is_async, job_id):
    if _is_browser_fetch_shop(shop_name):
        with _browser_fetch_semaphore:
            launch_spiders(shop_name, search_keyword, is_async, job_id)
    else:
        launch_spiders(shop_name, search_keyword, is_async, job_id)


# Filler words common in shopping queries ("wallet for men", "shoes with laces")
# that would otherwise count as a "matched" keyword on their own - e.g. a search
# for "wallet for men" matching a $65 pair of shoes titled "... for Naturalizer"
# purely on the word "for".
STOPWORDS = {"a", "an", "and", "for", "in", "of", "the", "to", "with"}

possible_match_abbrev = {
    "television": ["tv", "televisions"],
    "televisions": ["tv", "television"],
    "tv": ["tv", "television"],
    "computer": ["laptop", "pc", "desktop"],
    "pc": ["laptop", "computer", "desktop"],
    "laptop": ["computer", "pc", "desktop"],
    "desktop": ["laptop", "computer", "pc"],
    "children": ["child", "kid"],
    "drones": ["drone"],
    "drone": ["drones"],
}


def format_shop_names_list(shop_names_list):
    if shop_names_list:
        shop_names_list = shop_names_list.strip()
        if "," in shop_names_list:
            shop_names_list = [
                shn.strip().upper() for shn in shop_names_list.split(",") if shn.strip()
            ]
        else:
            shop_names_list = [shop_names_list.upper()]

    return shop_names_list


class ResultsFactory:
    search_keyword = None
    shop_names_list = None
    match_acc = 0
    low_to_high = True
    high_to_low = False
    is_cache = False
    is_async = True
    job_id = None
    fallback_error = {"error": "Sorry, no products found"}

    def __init__(self, *args, **kwargs):
        self.search_keyword = kwargs.get("search_keyword")
        self.job_id = kwargs.get("job_id")
        self.shop_names_list = self.validate_shop_list(
            format_shop_names_list(kwargs.get("shop_names_list"))
        )
        if not self.shop_names_list:
            raise Exception("Shops are required.")
        self.match_acc = int(kwargs.get("match_acc", 0))
        self.low_to_high = kwargs.get("low_to_high")
        self.high_to_low = kwargs.get("high_to_low")
        self.is_cache = kwargs.get("is_cache")
        self.is_async = kwargs.get("is_async")

    def validate_shop_list(self, shop_names_list):
        valid_shops = []
        for shop_name in shop_names_list:
            if is_shop_active(shop_name):
                valid_shops.append(shop_name)
        return valid_shops

    def match_sk(self, searched_item):
        if self.match_acc == 0:
            return True
        if not self.search_keyword or not searched_item:
            return False
        search_keyword = self.search_keyword.lower()
        searched_item = searched_item.lower()
        sk_abbrev = safe_grab(possible_match_abbrev, [search_keyword], default=[])

        search_keyword_arr = [
            word for word in search_keyword.split(" ") if word not in STOPWORDS
        ] or search_keyword.split(" ")
        search_keyword_arr.extend(sk_abbrev)
        match_count = 0
        for sk in search_keyword_arr:
            # \b word boundaries - a plain substring check would count "for" as
            # matching inside "force", or "men" inside "women", pulling in
            # unrelated items.
            if (
                sk
                and len(sk) > 1
                and re.search(r"\b" + re.escape(sk) + r"\b", searched_item)
            ):
                match_count = match_count + 1

        if match_count > 0:
            percentage_sk_match = (match_count / len(search_keyword_arr)) * 100
            if percentage_sk_match >= self.match_acc:
                return True
        return False

    def run_search(
        self,
    ):
        results = {}
        try:
            if not self.shop_names_list:
                results = {"error": "Shop name is required"}
                return results
            if not find_shop(self.shop_names_list):
                results = {"error": "Invalid shop name present in parameters"}
                return results
            if len(self.shop_names_list) == 1 and not is_shop_active(
                self.shop_names_list[0]
            ):
                results = {"error": "Shop is inactive at the moment, check back again"}
                return results

            if self.search_keyword.strip():
                if len(self.search_keyword) < 2:
                    return self.fallback_error
                self.search_keyword = truncate_data(
                    self.search_keyword, 75, html_escape=True
                )

                results = self.get_json_db_results()
                if not results:
                    results = self.fallback_error
                return results
        except Exception as e:
            logger.warning(e)
            logger.warning(traceback.format_exc())
            return {
                "error": "Sorry, error encountered during search, try again or contact admin if error persist"
            }
        return results

    def start_search(self, shop_names_list=None):
        shop_names_list = shop_names_list or self.shop_names_list
        # Each launch_spiders() call blocks on its own `scrapy crawl` subprocess, so
        # running this as a plain loop means shop 2 doesn't even start until shop 1's
        # crawl fully finishes - a single slow (or hung) shop stalls every shop behind
        # it. A bounded thread pool lets shops scrape concurrently instead, and a
        # per-shop try/except means one shop's failure doesn't stop the others from
        # completing (previously it would propagate and abort the whole search).
        with ThreadPoolExecutor(max_workers=config.MAX_CONCURRENT_SHOPS) as executor:
            futures = {
                executor.submit(
                    _launch_shop,
                    shop_name,
                    self.search_keyword,
                    self.is_async,
                    self.job_id,
                ): shop_name
                for shop_name in shop_names_list
            }
            for future in as_completed(futures):
                shop_name = futures[future]
                try:
                    future.result()
                except Exception:
                    # launch_spiders raising means the crawl subprocess never even
                    # started, so the spider's own error signal handler never ran to
                    # mark this shop "error" - without this, the job would sit at
                    # "in_progress" forever waiting on a shop that never started.
                    logger.exception("launch_spiders failed for %s", shop_name)
                    save_job(shop_name, self.job_id, status="error")

    def get_data_from_db_by_date_asc(self, shop_name=None):
        results_db = []
        if not shop_name:
            results_db.extend(
                ShoppedData.query.filter(
                    ShoppedData.searched_keyword == self.search_keyword
                )
                .order_by(ShoppedData.date_searched.asc())
                .all()
            )
        else:
            results_db.extend(
                ShoppedData.query.filter(
                    ShoppedData.searched_keyword == self.search_keyword,
                    ShoppedData.shop_name == shop_name,
                )
                .order_by(ShoppedData.date_searched.asc())
                .all()
            )
        return self.join_results_db(results_db)

    def get_data_from_db_contains(self):
        results_db = []

        if self.shop_names_list:
            if self.high_to_low:
                results_db.extend(
                    ShoppedData.query.filter(
                        or_(
                            ShoppedData.searched_keyword.contains(self.search_keyword),
                            ShoppedData.content_description.contains(
                                self.search_keyword
                            ),
                        ),
                        ShoppedData.shop_name.in_(self.shop_names_list),
                    )
                    .order_by(ShoppedData.numeric_price.desc())
                    .all()
                )

            elif self.low_to_high:
                results_db.extend(
                    ShoppedData.query.filter(
                        or_(
                            ShoppedData.searched_keyword.contains(self.search_keyword),
                            ShoppedData.content_description.contains(
                                self.search_keyword
                            ),
                        ),
                        ShoppedData.shop_name.in_(self.shop_names_list),
                    )
                    .order_by(ShoppedData.numeric_price.asc())
                    .all()
                )
        else:
            if self.high_to_low:
                results_db.extend(
                    ShoppedData.query.filter(
                        or_(
                            ShoppedData.searched_keyword.contains(self.search_keyword),
                            ShoppedData.content_description.contains(
                                self.search_keyword
                            ),
                        )
                    )
                    .order_by(ShoppedData.numeric_price.desc())
                    .all()
                )
            elif self.low_to_high:
                results_db.extend(
                    ShoppedData.query.filter(
                        or_(
                            ShoppedData.searched_keyword.contains(self.search_keyword),
                            ShoppedData.content_description.contains(
                                self.search_keyword
                            ),
                        )
                    )
                    .order_by(ShoppedData.numeric_price.asc())
                    .all()
                )

        return self.join_results_db(results_db)

    def get_data_from_db(self):
        results_db = []
        if self.shop_names_list:
            if self.high_to_low:
                results_db.extend(
                    ShoppedData.query.filter(
                        ShoppedData.searched_keyword == self.search_keyword,
                        ShoppedData.shop_name.in_(self.shop_names_list),
                    )
                    .order_by(ShoppedData.numeric_price.desc())
                    .all()
                )
            elif self.low_to_high:
                results_db.extend(
                    ShoppedData.query.filter(
                        ShoppedData.searched_keyword == self.search_keyword,
                        ShoppedData.shop_name.in_(self.shop_names_list),
                    )
                    .order_by(ShoppedData.numeric_price.asc())
                    .all()
                )
        else:
            if self.high_to_low:
                results_db.extend(
                    ShoppedData.query.filter(
                        ShoppedData.searched_keyword == self.search_keyword
                    )
                    .order_by(ShoppedData.numeric_price.desc())
                    .all()
                )
            elif self.low_to_high:
                results_db.extend(
                    ShoppedData.query.filter(
                        ShoppedData.searched_keyword == self.search_keyword
                    )
                    .order_by(ShoppedData.numeric_price.asc())
                    .all()
                )

        return self.join_results_db(results_db)

    def match_results_by_sk(self, results):
        mk_results = []
        for item_r in results:
            item_r = safe_json(item_r)
            if self.match_sk(
                safe_grab(item_r, ["title"]),
            ):
                mk_results.append(item_r)
        return mk_results

    def delete_data_by_shop_sk(self, shop_name):
        ShoppedData.query.filter(
            ShoppedData.searched_keyword == self.search_keyword,
            ShoppedData.shop_name == shop_name,
        ).delete()
        ShoppedData().commit()
        return

    def get_shops_without_data(self, results):
        shops_with_data = []
        if results:
            for shop_name in self.shop_names_list:
                for result in results:
                    if result.get("shop_name") == shop_name:
                        if shop_name not in shops_with_data:
                            shops_with_data.append(shop_name)

        return [
            shop_name
            for shop_name in self.shop_names_list
            if shop_name not in shops_with_data
        ]

    def get_json_db_results(self):

        results = self.get_data_from_db()

        if results:
            if not self.is_cache:
                shops_without_data = self.get_shops_without_data(results)
                if shops_without_data:
                    self.start_search(shops_without_data)
                    results = self.get_data_from_db() or results

            new_result = []
            if self.shop_names_list and len(self.shop_names_list) == 1:
                shop_name = self.shop_names_list[0]
                results_by_date = self.get_data_from_db_by_date_asc(shop_name=shop_name)
                if results_by_date and self.is_new_data(results_by_date):
                    new_result.extend(results)
                else:
                    self.delete_data_by_shop_sk(shop_name)
                    if not self.is_cache:
                        self.start_search([shop_name])
            else:
                new_result.extend(results)

            if new_result:
                results = self.match_results_by_sk(new_result)
                return results
            else:
                results = self.get_data_from_db_contains()

                return self.match_results_by_sk(results)
        elif self.is_cache:
            return []
        else:
            self.start_search()
            results = self.get_data_from_db_contains()
            return self.match_results_by_sk(results)
        return results

    def is_new_data(self, results):
        for result in results:
            result = safe_json(result)
            if result and isinstance(result, list) and len(result) > 0:
                result = result[0]
            date_searched = safe_grab(result, ["date_searched"])
            if date_searched:
                date_searched_parse = parser.parse(date_searched)
                dt_time_diff = datetime.now(timezone.utc) - date_searched_parse
                if dt_time_diff.days < config.SHOP_CACHE_MAX_EXPIRY_TIME:
                    return config.SHOP_CACHE_LOOKUP_SET
        return False

    def join_results_db(self, results):
        joined_result = []
        for result in results:
            if isinstance(result, ShoppedData):
                result = json.loads(result.__repr__())
            for _, v in result.items():
                joined_result.append(v)

        return joined_result
