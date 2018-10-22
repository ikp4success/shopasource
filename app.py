from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from utilities.results_factory import get_results
# from twilio.twiml.messaging_response import MessagingResponse
# from utilities.DefaultResources import _resultRow, _errorMessage
import os

app = Flask(__name__, template_folder='web_content')
# app.secret_key = os.environ["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)


class ShoppedData(db.Model):
    searched_keyword = db.Column(db.String(200), primary_key=True)
    image_url = db.Column(db.String(1999))
    shop_name = db.Column(db.String(50))
    price = db.Column(db.String(10000000))
    title = db.Column(db.String(100))
    content_descripiton = db.Column(db.String(250))
    date_searched = db.Column(db.DateTime(timezone=True), server_default=func.now())

    @property
    def serialize(self):
        return {
            self.searched_keyword: {
                "image_url": self.image_url,
                "shop_name": self.shop_name,
                "price": self.price,
                "title": self.title,
                "criteria": self.searched_keyword,
                "content_descripiton": self.content_description,
                "date_searched": self.date_searched
            }
        }
    db.create_all()


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
    results = get_results(search_keyword)
    if results is not None:
        add_results_to_db(results)
    return render_template('searchresults.html')


def add_results_to_db(results):
    shopped_data = ShoppedData(
            title=results["title"],
            content_descripiton=results["content_descripiton"],
            image_url=results["image_url"],
            price=results["price"],
            criteria=results["searched_keyword"],
            date_searched=results["date_searched"],
            shop_name=results["shop_name"]
    )
    db.session.add(shopped_data)
    db.session.commit()


def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run()
