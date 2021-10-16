import json
import logging
import os
import sys

import coloredlogs


def get_config(env=None):
    env = env or os.getenv("ENV_CONFIGURATION", "debug")
    with open("configs/{}.json".format(env)) as file:
        return json.load(file)


class Config:
    SKIP_SENTRY = os.environ.get("SKIP_SENTRY", False)

    def apply_env_variables(self, config):
        for k, v in config.items():
            setattr(self, k, v)
        if self.ENVIRONMENT == "debug":
            self.POSTGRESS_DB_URL = f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_DOMAIN']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"

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
