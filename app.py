from flask import Flask, render_template, request
from utilities.DefaultResources import _resultRow, _errorMessage

app = Flask(__name__, template_folder='web_content')


@app.route("/", methods=['GET'])
def home_page():
    return home()


@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')


@app.route("/searchresults", methods=['POST'])
def searchresults():
    if request.method == 'POST':
        search_keyword = request.form.get('search')
        return get_search_results(search_keyword)
    else:
        return home()
    return render_template('about.html')


def get_search_results(search_keyword):
    return render_template('searchresults.html')


def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run()
