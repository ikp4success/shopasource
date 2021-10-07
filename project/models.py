import json

from sqlalchemy.sql import func

from project import db
from shops.shop_utilities.extra_function import generate_result_meta


class ShoppedData(db.Model):
    __tablename__ = "shopped_data"
    id = db.Column(db.Integer, primary_key=True)
    searched_keyword = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    shop_link = db.Column(db.String, nullable=False)
    shop_name = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    numeric_price = db.Column(db.Numeric, nullable=False)
    title = db.Column(db.String, nullable=False)
    content_description = db.Column(db.String)
    date_searched = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(
        self,
        searched_keyword,
        image_url,
        shop_link,
        shop_name,
        price,
        numeric_price,
        title,
        content_description,
        date_searched,
    ):
        self.searched_keyword = searched_keyword
        self.image_url = image_url
        self.shop_link = shop_link
        self.shop_name = shop_name
        self.price = price
        self.title = title
        self.content_description = content_description
        self.date_searched = date_searched
        self.numeric_price = numeric_price

    def __repr__(self):
        data_gen = generate_result_meta(
            image_url=self.image_url,
            searched_keyword=self.searched_keyword,
            shop_name=self.shop_name,
            shop_link=self.shop_link,
            price=self.price,
            title=self.title,
            content_description=self.content_description,
            date_searched=str(self.date_searched),
        )
        if data_gen is not None:
            data_gen = json.dumps(data_gen)
        return data_gen


class Job(db.Model):
    __tablename__ = "job"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    searched_keyword = db.Column(db.String, nullable=False)
    shop_list_names = db.Column(db.String, nullable=False)
    smatch = db.Column(db.String, nullable=False)
    slh = db.Column(db.String, nullable=False)
    shl = db.Column(db.String, nullable=False)
    date_searched = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, guid, status, searched_keyword, shop_list_names, smatch, slh, shl):
        self.guid = guid
        self.status = status
        self.searched_keyword = searched_keyword
        self.shop_list_names = shop_list_names
        self.smatch = smatch
        self.slh = slh
        self.shl = shl
        self.smatch = smatch
