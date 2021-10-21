import datetime
import decimal
import json
import logging
import os
import sys
import threading

import coloredlogs

local = threading.local()
logger = logging.getLogger(__name__)


def get_config(env=None):
    env = env or os.getenv("ENV_CONFIGURATION", "debug")
    try:
        with open("configs/{}.json".format(env)) as file:
            return json.load(file)
    except FileNotFoundError:
        logger.warning(f"{env} config not found.")
    return {}


def safe_int(num_str):
    try:
        return int(num_str)
    except Exception:
        return None


class Config:
    SKIP_SENTRY = os.environ.get("SKIP_SENTRY", False)
    ENVIRONMENT = os.environ.get("ENVIRONMENT")
    SET_LOG_LEVEL = os.environ.get("SET_LOG_LEVEL", "WARNING").upper()
    API_KEY = os.environ.get("API_KEY")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    API_MAX_USAGE = int(os.environ.get("API_MAX_USAGE", 100))
    API_MAX_USAGE_DAYS = int(os.environ.get("API_MAX_USAGE_DAYS", 2))
    SHOP_CACHE_MAX_EXPIRY_TIME = int(os.environ.get("SHOP_CACHE_MAX_EXPIRY_TIME", 3))
    SHOP_CACHE_LOOKUP_SET = os.environ.get("SHOP_CACHE_LOOKUP_SET", True)
    SUPER_USER = os.environ.get("SUPER_USER")
    SAVE_TO_DB = os.environ.get("SAVE_TO_DB")
    bool_envs = ["SAVE_TO_DB", "SUPER_USER", "SHOP_CACHE_LOOKUP_SET", "SKIP_SENTRY"]

    def apply_env_variables(self, config):
        for k, v in config.items():
            # variables set in config takes precedence over environ variables.
            setattr(self, k, v)

    def convert_bool_integers_to_bool(self):
        # converts integer used as bool in env variables or config
        for env in self.bool_envs:
            env_v = safe_int(getattr(self, env))  # handle's '1', '0'
            if env_v:
                if env_v == 1:
                    setattr(self, env, True)
                else:
                    setattr(self, env, False)

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

    def config_display(self):
        display = ""
        for k in vars(self).keys():
            display += f"{k}: {getattr(self, k)}\n"
        logger.info(display)

    def load_config(self):
        config = get_config()
        self.apply_env_variables(config)
        self.convert_bool_integers_to_bool()
        self.apply_fallback()
        self.config_display()

    def __init__(self):
        self.load_config()

    def intialize_sentry(self):
        if not self.SKIP_SENTRY:
            from sentry_sdk import init

            return init(config.SENTRY_DSN)


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


try:
    config = local.config
except AttributeError:
    config = Config()
    local.config = config


def get_logger(name):
    logger = logging.getLogger(name)
    logging.basicConfig()
    logging.getLogger().setLevel(getattr(logging, config.SET_LOG_LEVEL))
    coloredlogs.install(level=config.SET_LOG_LEVEL)
    return logger
