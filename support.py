import logging
import json
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
