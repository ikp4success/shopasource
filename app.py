from flask import render_template
from flask import jsonify
from flask import request

from utilities.results_factory import run_web_search, run_api_search
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


@app.route("/api/shop/<shop_name>/search=<search_keyword>", methods=['GET'])
def api_search(shop_name, search_keyword):
    results = run_api_search(shop_name, search_keyword)
    results = jsonify(results)
    return (results, 200)


@app.route("/websearch/shops.json", methods=['GET'])
def shop_list():
    return render_template('shops.json')


@app.route("/websearch/shop/search", methods=['GET'])
def web_search():
    search_keyword = request.args.get("sk")
    match_acc = 0
    low_to_high = False
    high_to_low = True
    try:
        match_acc = int(request.args.get("smatch"))
        low_to_high = request.args.get("slh")
        high_to_low = request.args.get("shl")
        if low_to_high == "true":
            high_to_low = False
            low_to_high = True
        elif low_to_high == "false":
            high_to_low = True
            low_to_high = False
        else:
            low_to_high = False
            high_to_low = True

    except Exception:
        match_acc = 0
        low_to_high = False
        high_to_low = True
    return get_search_results(search_keyword, match_acc, low_to_high, high_to_low)


def get_search_results(search_keyword, match_acc, low_to_high, high_to_low):
    run_web_search(search_keyword, match_acc, low_to_high, high_to_low)
    return render_template('searchresults.html')


def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(threaded=True)
