import json
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool

from flask import render_template
from flask import jsonify
from flask import request

from utilities.results_factory import run_api_search
from shops.shop_utilities.shop_setup import get_shops
from project import db, app

db.create_all()


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.route("/", methods=['GET'])
def home_page():
    return home()


@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')


@app.route("/robots.txt", methods=['GET'])
def robots():
    return render_template('robots.txt')


@app.route("/api/shop/search", methods=['GET'])
def api_search():
    # http://127.0.0.1:8000/api/shop/search?sk=drones&smatch=50&shl=false&slh=false&shops=TARGET
    shop_list_names = []
    search_keyword = None
    match_acc = 0
    low_to_high = False
    high_to_low = True

    try:
        search_keyword = request.args.get("sk")
        shop_list_names = request.args.get("shops")
        if shop_list_names:
            shop_list_names = shop_list_names.strip()
            if "," in shop_list_names:
                shop_list_names = [shn.strip().upper() for shn in shop_list_names.split(",") if shn.strip()]
            else:
                shop_list_names = [shop_list_names.upper()]
        match_acc = int(request.args.get("smatch") or 0)
        low_to_high = json.JSONDecoder().decode(request.args.get("slh") or "false")
        high_to_low = json.JSONDecoder().decode(request.args.get("shl") or "false")

        if not low_to_high:  # fail safe
            high_to_low = True
    except Exception:
        results = {"message": "Sorry, error encountered during search, try again or contact admin if error persist"}
        return (results, 404)

    pool = ThreadPool(len(shop_list_names))
    launch_spiders_partial = partial(
        run_api_search,
        shop_names_list=shop_list_names,
        search_keyword=search_keyword,
        match_acc=match_acc,
        low_to_high=low_to_high,
        high_to_low=high_to_low)

    shops_thread_list = shop_list_names
    results = pool.map(launch_spiders_partial, shops_thread_list)
    pool.close()
    pool.join()
    # results = run_api_search(shops_thread_list, shop_list_names, search_keyword, match_acc, low_to_high, high_to_low)
    if len(results) > 0:
        results = jsonify(results[0])
        return (results, 200)
    results = {"message": "Sorry, no products found"}
    return (results, 404)


@app.route("/websearch/shops-active.json", methods=['GET'])
def shop_list_active():
    return jsonify(get_shops(active=True)), 200


def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(threaded=True)
