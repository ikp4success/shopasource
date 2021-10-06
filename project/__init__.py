import sys

from flask_sqlalchemy import SQLAlchemy
from quart import Quart
from utilities.config import Config

app = Quart(__name__, template_folder="web_content")


def get_sys_args_kwargs():
    args_lst = []
    kwargs_dict = {}
    for arg in sys.argv:
        if "=" in arg:
            arg = arg.split("=")
            kwargs_dict[arg[0]] = arg[1]
        else:
            args_lst.append(arg)
    return args_lst, kwargs_dict


app.config["SQLALCHEMY_DATABASE_OPTIONS"] = {
    "connect_args": {
        "ssl": {
            "key": "ssl/mysql/client-key.pem",
            "cert": "/BaltimoreCyberTrustRoot.crt.pem",
        }
    }
}
app.config["SQLALCHEMY_DATABASE_URI"] = Config().POSTGRESS_DB_URL
app.config["DEBUG"] = True if Config().ENVIRONMENT == "debug" else False
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

db = SQLAlchemy(app)
