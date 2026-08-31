import requests

from shops.shop_util.shop_setup_functions import find_shop_configuration, get_shops


def smoke_test_all_shops(keyword="test"):
    shops = get_shops(active=True)
    results = {}
    for s in shops:
        conf = find_shop_configuration(s)
        url_template = conf.get("url")
        if not url_template:
            results[s] = {"ok": False, "error": "no url template"}
            continue
        # some shop url templates expect additional placeholders (e.g. uuid)
        try:
            import uuid

            from support import config

            placeholders = {
                "keyword": keyword,
                "uuid": uuid.uuid4(),
                "api_key": getattr(config, "API_KEY", ""),
                "page": 1,
            }
            url = url_template.format(**placeholders)
        except KeyError as e:
            missing = e.args[0]
            results[s] = {"ok": False, "error": f"missing placeholder: {missing}"}
            continue
        try:
            r = requests.get(url, timeout=10)
            results[s] = {"ok": r.status_code == 200, "status_code": r.status_code}
        except Exception as e:
            results[s] = {"ok": False, "error": str(e)}
    return results


if __name__ == "__main__":
    import json

    res = smoke_test_all_shops()
    print(json.dumps(res, indent=2))
