from urllib import parse as urlparse
import datetime as dt
import re
import json


def prepend_domain(url, domain_url):
    if domain_url is None:
        return url
    if url is None or url == "":
        return None
    url = url.strip()
    split_url = urlparse.urlsplit(url)
    if not split_url.scheme:
        if not split_url.netloc:
            split_domain = urlparse.urlsplit(domain_url)
            domain = "{}://{}".format(split_domain.scheme, split_domain.netloc)
            return urlparse.urljoin(domain, url)
        url = "https://{}".format(url.replace("//", ""))
    return url


def safe_grab(data, keys, default=None):
    if data is not None and keys is not None and len(keys) > 0:
        if not isinstance(data, dict):
            return None
        keys_list = keys
        key = keys_list[0]
        data = data.get(key)
        keys_list.pop(0)
    else:
        if data is None and default is not None:
            return default
        return data
    return safe_grab(data, keys, default)


def safe_json(data):
    try:
        if not isinstance(data, str):
            data = json.dumps(data)
        return json.loads(data)
    except Exception:
        return {}
    return {}


def generate_result_meta(shop_link, searched_keyword, image_url, shop_name, price, title, content_description, date_searched=None):
    if not validate_data(image_url, price, title):
        return None

    numeric_price = re.findall("\d+\.+\d+", price) or re.findall("\d+", price)
    if numeric_price is None or len(numeric_price) == 0:
        return None

    if date_searched is None:
        date_searched = str(dt.datetime.now())

    result_meta = {
        searched_keyword: {
            "image_url": prepend_domain(image_url, shop_link),
            "shop_name": shop_name,
            "shop_link": shop_link,
            "price": format_price(price),
            "title": truncate_data(title, 50),
            "searched_keyword": searched_keyword,
            "content_description": truncate_data(content_description, 250),
            "date_searched": date_searched,
            "numeric_price": numeric_price[0]
        }
    }
    return result_meta


def extract_items(items):
    item_r = ""
    for item in items:
        item_r += item.rstrip().strip()
    return item_r


def match_sk(search_keyword, searched_item):
    if search_keyword is None or searched_item is None:
        return False
    search_keyword = search_keyword.lower()
    searched_item = searched_item.lower()
    search_keyword = search_keyword.split(" ")
    match_count = 0
    for sk in search_keyword:
        if len(sk) > 1 and sk in searched_item.lower():
            match_count = match_count + 1

    if match_count > 0:
        percentage_sk_match = (match_count / len(search_keyword)) * 100
        if percentage_sk_match > 55:
            return True
    return False


def format_price(price):
    return price.replace("US", "").strip()


def validate_data(image_url, price, title):
    if price is None or price == "":
        return False
    if image_url is None and title is None:
        return False
    if image_url == "" and title == "":
        return False

    return True


def truncate_data(data, length_cont):
    if not data:
        return data
    data = data.rstrip().strip()
    if len(data) > length_cont:
        try:
            return "{}...".format(data[:length_cont])
        except Exception:
            return ""  # data is not good
    else:
        return data
