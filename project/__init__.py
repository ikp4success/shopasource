import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sys_settings import (
    dev_post_gress_db,
    prod_post_gress_db
)

app = Flask(__name__, template_folder='web_content')


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


if sys.argv and len(sys.argv) > 1 and get_sys_args_kwargs()[1].get("debug"):
    app.config['SQLALCHEMY_DATABASE_URI'] = dev_post_gress_db
    app.config['DEBUG'] = True
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = prod_post_gress_db
    app.config['DEBUG'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db = SQLAlchemy(app)
