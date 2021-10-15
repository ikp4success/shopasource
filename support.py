import json
import logging
import os

import coloredlogs


def get_config(env=None):
    env = env or os.getenv("ENV_CONFIGURATION", "test")
    with open("configs/{}.json".format(env)) as file:
        return json.load(file)


class Config:
    SKIP_SENTRY = os.environ.get("SKIP_SENTRY", False)

    def apply_env_variables(self, config):
        for k, v in config.items():
            setattr(self, k, v)
        if self.ENVIRONMENT == "debug":
            self.POSTGRESS_DB_URL = f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@localhost:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"

    def load_config(self):
        config = get_config()
        self.apply_env_variables(config)

    def __init__(self):
        self.load_config()


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
