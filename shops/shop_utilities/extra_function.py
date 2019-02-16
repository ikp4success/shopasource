from urllib import parse as urlparse
import datetime as dt
import re
import json
import html


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


def safe_float(fl_str, safeon=True):
    try:
        return float(fl_str)
    except Exception:
        if safeon:
            return 0
        else:
            return None


def price_round(price_str, round_num):
    try:
        price_str = price_str.replace("$", "").replace("USD", "").replace("US", "").strip()
        price_str = str(round(safe_float(price_str, safeon=False), round_num))
        return format_price(price_str)
    except Exception:
        return format_price(price_str)


def generate_result_meta(
    shop_link,
    searched_keyword,
    image_url,
    shop_name,
    price,
    title,
    content_description,
    date_searched=None
):
    if not validate_data(image_url, price, title):
        return None
    price = str(price)
    numeric_price = re.findall("\d+\.+\d+", price) or re.findall("\d+", price)
    if numeric_price is None or len(numeric_price) == 0:
        return None

    numeric_price = safe_float(numeric_price[0], safeon=False)
    if numeric_price is None:
        return None
    price = price_round(price, 2)
    if price is None:
        return None

    if date_searched is None:
        date_searched = str(dt.datetime.now())

    result_meta = {
        searched_keyword: {
            "image_url": prepend_domain(image_url, shop_link),
            "shop_name": shop_name,
            "shop_link": shop_link,
            "price": price,
            "title": truncate_data(title, 75),
            "searched_keyword": searched_keyword,
            "content_description": truncate_data(content_description, 250),
            "date_searched": date_searched,
            "numeric_price": str(round(numeric_price, 2))
        }
    }
    return result_meta


def extract_items(items):
    item_r = ""
    for item in items:
        item_r += " " + item.rstrip().strip()
    return item_r.strip()


def format_price(price):
    if "$" not in price:
        price = "${}".format(price)
    return price.replace("USD", "").replace("US", "").strip()


def validate_data(image_url, price, title):
    if not price:
        return False
    if not title:
        return False
    return True


def truncate_data(data, length_cont, html_escape=False):
    if not data:
        return data
    data = data.rstrip().strip()
    if len(data) > length_cont:
        try:
            if html_escape:
                return html.escape("{}...".format(data[:length_cont]))
            return "{}...".format(data[:length_cont])
        except Exception:
            return ""  # data is not good
    else:
        return data
