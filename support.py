import datetime
import decimal
import json
import logging
import os
import sys

import coloredlogs

logger = logging.getLogger(__name__)


def get_config(env=None):
    env = env or os.getenv("ENV_CONFIGURATION", "debug")
    with open("configs/{}.json".format(env)) as file:
        return json.load(file)


class Config:
    SKIP_SENTRY = os.environ.get("SKIP_SENTRY", False)
    ENVIRONMENT = os.environ.get("ENVIRONMENT")
    API_KEY = os.environ.get("API_KEY")
    POSTGRESS_DB_URL = os.environ.get("POSTGRESS_DB_URL")
    SENTRY_DSN = os.environ.get("SENTRY_DSN")

    def apply_env_variables(self, config):
        for k, v in config.items():
            setattr(self, k, v)
        if self.ENVIRONMENT == "debug":
            self.POSTGRESS_DB_URL = f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_DOMAIN']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
        elif not self.ENVIRONMENT:
            raise Exception("Environment is required.")
        if not self.POSTGRESS_DB_URL:
            logger.warning("POSTGRESS_DB_URL is required.")
        if not self.SKIP_SENTRY and not self.SENTRY_DSN:
            logger.warning("SENTRY_DSN is not set.")
            self.SKIP_SENTRY = True
        if not self.API_KEY:
            logger.warning("API_KEY is not set.")

    def load_config(self):
        config = get_config()
        self.apply_env_variables(config)

    def __init__(self):
        self.load_config()

    def intialize_sentry(self):
        if not self.SKIP_SENTRY:
            from sentry_sdk import init

            return init(Config().SENTRY_DSN)


def get_logger(name):
    logger = logging.getLogger(name)
    logging.basicConfig()
    if Config().ENVIRONMENT == "debug":
        logging.getLogger().setLevel(logging.DEBUG)
        coloredlogs.install(level="DEBUG")
    else:
        logging.getLogger().setLevel(logging.WARNING)
        coloredlogs.install(level="WARNING")
    return logger


def generate_key():
    import uuid

    return str(uuid.uuid1()).replace("-", "").upper()


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


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        return super(CustomEncoder, self).default(obj)
