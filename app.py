from flask import render_template
from flask import jsonify

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


@app.route("/api/shop/search=<search_keyword>", methods=['GET'])
def api_search(search_keyword):
    results = run_api_search(search_keyword)
    results = jsonify(results)
    return (results, 200)


@app.route("/websearch/shop/search=<search_keyword>", methods=['GET'])
def web_search(search_keyword):
    return get_search_results(search_keyword)


def get_search_results(search_keyword):
    run_web_search(search_keyword)
    return render_template('searchresults.html')


def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run()
