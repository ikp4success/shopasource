import sys

from flask_sqlalchemy import SQLAlchemy
from quart import Quart

from sys_settings import configs

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
if sys.argv and len(sys.argv) > 1 and get_sys_args_kwargs()[1].get("debug"):
    app.config["SQLALCHEMY_DATABASE_URI"] = configs["dev_post_gress_db"]
    app.config["DEBUG"] = True
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = configs["prod_post_gress_db"]
    app.config["DEBUG"] = False
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

db = SQLAlchemy(app)
