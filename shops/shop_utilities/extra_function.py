from urllib import parse as urlparse
import datetime as dt
import re
import json
import html

possible_match_abbrev = {
    "television": "tv",
    "televisions": "tv"
}


def prepend_domain(url, domain_url, ignore_domain_splice=False):
    if domain_url is None:
        return url
    if not url:
        return None
    url = url.strip()
    if url.startswith("www."):
        url = "https://{}".format(url)
        return url
    split_url = urlparse.urlsplit(url)
    if not split_url.scheme:
        if not split_url.netloc:
            if ignore_domain_splice:
                return urlparse.urljoin(domain_url, url)
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
    price = str(price)
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
    sk_abbrev = safe_grab(possible_match_abbrev, [search_keyword])

    search_keyword_arr = search_keyword.split(" ")
    search_keyword_arr.append(sk_abbrev)
    match_count = 0
    for sk in search_keyword_arr:
        if sk and len(sk) > 1 and sk in searched_item.lower():
            match_count = match_count + 1

    if match_count > 0:
        percentage_sk_match = (match_count / len(search_keyword_arr)) * 100
        if percentage_sk_match >= 50:
            return True
    return False


def format_price(price):
    if "$" not in price:
        "${}".format(price)
    return price.replace("USD", "").replace("US", "").strip()


def validate_data(image_url, price, title):
    if not price:
        return False
    if not title:
        return False
    return True


def truncate_data(data, length_cont):
    if not data:
        return data
    data = data.rstrip().strip()
    if len(data) > length_cont:
        try:
            return html.escape("{}...".format(data[:length_cont]))
        except Exception:
            return ""  # data is not good
    else:
        return data
