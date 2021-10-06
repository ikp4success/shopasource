import json
import os


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
