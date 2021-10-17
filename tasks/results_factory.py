import json
import traceback
from datetime import datetime, timezone

from dateutil import parser
from sqlalchemy import or_

from project.models import ShoppedData
from shops.shop_util.extra_function import safe_grab, safe_json, truncate_data
from shops.shop_util.shop_setup import SHOP_CACHE_LOOKUP_SET, SHOP_CACHE_MAX_EXPIRY_TIME
from shops.shop_util.shop_setup_functions import find_shop, is_shop_active
from support import Config, get_logger
from tasks.scrapy_run import launch_spiders

logger = get_logger(__name__)

Config().intialize_sentry()

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
    is_cache = (False,)
    is_async = (True,)
    job_id = (None,)

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

        search_keyword_arr = search_keyword.split(" ")
        search_keyword_arr.extend(sk_abbrev)
        match_count = 0
        for sk in search_keyword_arr:
            if sk and len(sk) > 1 and sk in searched_item.lower():
                match_count = match_count + 1

        if match_count > 0:
            percentage_sk_match = (match_count / len(search_keyword_arr)) * 100
            if percentage_sk_match >= self.match_acc:
                return True
        return False

    def run_search(self,):
        results = {}
        try:
            if not self.shop_names_list:
                results = {"message": "Shop name is required"}
                return results
            if not find_shop(self.shop_names_list):
                results = {"message": "Invalid shop name present in parameters"}
                return results
            if len(self.shop_names_list) == 1 and not is_shop_active(
                self.shop_names_list[0]
            ):
                results = {
                    "message": "Shop is inactive at the moment, check back again"
                }
                return results

            if self.search_keyword is not None and self.search_keyword.strip() != "":
                if len(self.search_keyword) < 2:
                    results = [{"message": "Sorry, no products found"}]
                    return results
                self.search_keyword = truncate_data(
                    self.search_keyword, 75, html_escape=True
                )

                results = self.get_json_db_results()
                if not results:
                    results = [{"message": "Sorry, no products found"}]
                return results
        except Exception as e:
            results = [
                {
                    "message": "Sorry, error encountered during search, try again or contact admin if error persist"
                }
            ]
            logger.warning(e)
            logger.warning(traceback.format_exc())
            return results
        return results

    def start_search(self, shop_names_list=None):
        shop_names_list = shop_names_list or self.shop_names_list
        for shop_name in shop_names_list:
            launch_spiders(shop_name, self.search_keyword, self.is_async, self.job_id)

    def get_data_from_db_by_date_asc(self, shop_name=None):
        results_db = []
        if not shop_name:
            results_db.append(
                ShoppedData.query.filter(
                    ShoppedData.searched_keyword == self.search_keyword
                )
                .order_by(ShoppedData.date_searched.asc())
                .first()
            )
        results_db.append(
            ShoppedData.query.filter(
                ShoppedData.searched_keyword == self.search_keyword,
                ShoppedData.shop_name == shop_name,
            )
            .order_by(ShoppedData.date_searched.asc())
            .first()
        )
        return [res.__str__() for res in results_db]

    def get_data_from_db_contains(self):
        results_db = []
        results_centre = []
        if self.shop_names_list:
            if self.high_to_low:
                results_db.append(
                    ShoppedData.query.filter(
                        # ShoppedData.searched_keyword.contains(searched_keyword),
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
                results_db.append(
                    ShoppedData.query.filter(
                        # ShoppedData.searched_keyword.contains(searched_keyword),
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
                results_db.append(
                    ShoppedData.query.filter(
                        # ShoppedData.searched_keyword.contains(searched_keyword),
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
                results_db.append(
                    ShoppedData.query.filter(
                        # ShoppedData.searched_keyword.contains(searched_keyword),
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
        for results in results_db:
            if results:
                results_1 = []
                for result in results:
                    result.searched_keyword = self.search_keyword
                    results_1.append(result)
                results_centre = [res.__str__() for res in results_1]
        return results_centre

    def get_data_from_db(self):
        results_db = []
        results_centre = []
        if self.shop_names_list:
            if self.high_to_low:
                results_db.append(
                    ShoppedData.query.filter(
                        ShoppedData.searched_keyword == self.search_keyword,
                        ShoppedData.shop_name.in_(self.shop_names_list),
                    )
                    .order_by(ShoppedData.numeric_price.desc())
                    .all()
                )
            elif self.low_to_high:
                results_db.append(
                    ShoppedData.query.filter(
                        ShoppedData.searched_keyword == self.search_keyword,
                        ShoppedData.shop_name.in_(self.shop_names_list),
                    )
                    .order_by(ShoppedData.numeric_price.asc())
                    .all()
                )
        else:
            if self.high_to_low:
                results_db.append(
                    ShoppedData.query.filter(
                        ShoppedData.searched_keyword == self.search_keyword
                    )
                    .order_by(ShoppedData.numeric_price.desc())
                    .all()
                )
            elif self.low_to_high:
                results_db.append(
                    ShoppedData.query.filter(
                        ShoppedData.searched_keyword == self.search_keyword
                    )
                    .order_by(ShoppedData.numeric_price.asc())
                    .all()
                )

        for results in results_db:
            if results is not None and len(results) > 0:
                results_centre = [res.__str__() for res in results]
        return results_centre

    def match_results_by_sk(self, results):
        mk_results = []
        for item_r in results:
            item_r = safe_json(item_r)
            if self.match_sk(safe_grab(item_r, [self.search_keyword, "title"]),):
                mk_results.append(json.dumps(item_r))
        return mk_results

    def delete_data_by_shop_sk(self, shop_name):
        shop_data = ShoppedData.query.filter(
            ShoppedData.searched_keyword == self.search_keyword,
            ShoppedData.shop_name == shop_name,
        ).delete()
        shop_data.commit()
        return

    def get_json_db_results(self):

        results = self.get_data_from_db()
        if results:
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
            date_searched = safe_grab(result, [self.search_keyword, "date_searched"])
            if date_searched is not None:
                date_searched_parse = parser.parse(date_searched)
                dt_time_diff = datetime.now(timezone.utc) - date_searched_parse
                if dt_time_diff.days < SHOP_CACHE_MAX_EXPIRY_TIME:
                    return SHOP_CACHE_LOOKUP_SET
        return False
