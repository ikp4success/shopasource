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
    try:
        with open("configs/{}.json".format(env)) as file:
            return json.load(file)
    except FileNotFoundError:
        logger.warning(f"{env} Config not found.")
    return {}


class Config:
    SKIP_SENTRY = os.environ.get("SKIP_SENTRY", False)
    ENVIRONMENT = os.environ.get("ENVIRONMENT")
    API_KEY = os.environ.get("API_KEY")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    API_MAX_USAGE = int(os.environ.get("API_MAX_USAGE", 100))
    API_MAX_USAGE_DAYS = int(os.environ.get("API_MAX_USAGE_DAYS", 2))
    SHOP_CACHE_MAX_EXPIRY_TIME = int(os.environ.get("SHOP_CACHE_MAX_EXPIRY_TIME", 3))
    SHOP_CACHE_LOOKUP_SET = os.environ.get("SHOP_CACHE_LOOKUP_SET", True)
    SUPER_USER = os.environ.get("SUPER_USER")

    def apply_env_variables(self, config):
        for k, v in config.items():
            # variables set in config takes precedence over environ variables.
            setattr(self, k, v)

    def apply_fallback(self):
        if self.ENVIRONMENT == "debug":
            if not self.DATABASE_URL:
                self.DATABASE_URL = f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_DOMAIN']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
        elif not self.ENVIRONMENT:
            raise Exception("Environment is required.")
        if not self.DATABASE_URL:
            logger.warning("DATABASE_URL is required.")
        elif self.DATABASE_URL.startswith("postgres://"):
            # https://docs.sqlalchemy.org/en/14/changelog/changelog_14.html#change-3687655465c25a39b968b4f5f6e9170b
            self.DATABASE_URL = self.DATABASE_URL.replace(
                "postgres://", "postgresql://"
            )
        if not self.SKIP_SENTRY and not self.SENTRY_DSN:
            logger.warning("SENTRY_DSN is not set, skipping sentry.")
            self.SKIP_SENTRY = True
        if not self.API_KEY:
            logger.warning("API_KEY is not set, using default.")
        if not self.SUPER_USER:
            logger.warning("SUPER_USER is not set, using default.")
            self.SUPER_USER = "127.0.0.1"

    def load_config(self):
        config = get_config()
        self.apply_env_variables(config)
        self.apply_fallback()

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

    return str(uuid.uuid1()).replace("-", "").lower()


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
