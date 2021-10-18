import datetime
import json
import time
import uuid

import sqlalchemy as db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import func

from shops.shop_util.extra_function import generate_result_meta
from support import Config, get_logger

logger = get_logger(__name__)

engine = db.create_engine(Config().POSTGRESS_DB_URL, convert_unicode=True,)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def init_db():
    Model.metadata.create_all(bind=engine)


Model = declarative_base(name="Model")
Model.query = db_session.query_property()


class ModelMixin:
    session = db_session

    def commit(self, retry=0):
        try:
            self.session.add(self)
            self.session.flush()
            self.session.commit()
        except Exception as ex:
            logger.warning(ex)
            self.session.rollback()

    def get_item(self, **kwargs):
        return self.query.get(kwargs)

    def update_item(self, **kwargs):
        for k, v in kwargs.items():
            if k == "id":
                continue
            setattr(self, k, v)
        self.commit()


class ShoppedData(Model, ModelMixin):
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
    date_searched = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    def __init__(self, *args, **kwargs):
        self.searched_keyword = kwargs.get("searched_keyword")
        self.image_url = kwargs.get("image_url")
        self.shop_link = kwargs.get("shop_link")
        self.shop_name = kwargs.get("shop_name")
        self.price = kwargs.get("price")
        self.title = kwargs.get("title")
        self.content_description = kwargs.get("content_description")
        self.date_searched = kwargs.get("date_searched")
        self.numeric_price = kwargs.get("numeric_price")

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


class Job(Model, ModelMixin):
    __tablename__ = "job"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = db.Column(db.String, nullable=False)
    search_keyword = db.Column(db.String, nullable=False)
    shop_names_list = db.Column(db.String, nullable=False)
    match_acc = db.Column(db.String, nullable=False)
    meta = db.Column(db.JSON, nullable=False)
    low_to_high = db.Column(db.String, nullable=False)
    high_to_low = db.Column(db.String, nullable=False)
    date_searched = db.Column(
        db.DateTime(timezone=True), default=datetime.datetime.utcnow
    )

    def __init__(self, *args, **kwargs):
        self.status = kwargs.get("status")
        self.search_keyword = kwargs.get("search_keyword")
        self.shop_names_list = kwargs.get("shop_names_list")
        self.match_acc = kwargs.get("match_acc")
        self.low_to_high = kwargs.get("low_to_high")
        self.high_to_low = kwargs.get("high_to_low")
        self.meta = kwargs.get("meta")

    def __repr__(self):
        data_gen = {
            "status": self.status,
            "search_keyword": self.search_keyword,
            "shop_names_list": self.shop_names_list,
            "match_acc": self.match_acc,
            "low_to_high": self.low_to_high,
            "high_to_low": self.high_to_low,
            "meta": self.meta,
            "date_searched": str(self.date_searched),
        }
        return json.dumps(data_gen)
