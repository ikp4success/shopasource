import os

from support import get_config, get_logger

logger = get_logger(__name__)


class BaseConfig(object):
    CONFIG_PREFIX = "test"
    TEST_MODE = False
    DEVELOPMENT = False


class DebugConfig(BaseConfig):
    CONFIG_PREFIX = "debug"
    DEBUG = True
    DEVELOPMENT = True


class DevelopmentConfig(BaseConfig):
    CONFIG_PREFIX = "dev"
    DEVELOPMENT = True


configs = {
    "debug": "webapp.config.DebugConfig",
    "dev": "webapp.config.DevelopmentConfig",
}


def configure_app(app, config_name=None):
    if not config_name:
        config_name = os.getenv("ENV_CONFIGURATION", "dev")
    app.config.from_object(configs[config_name])
    env = app.config["CONFIG_PREFIX"]
    app.config.update(get_config(env))
    if not os.environ.get("SENTRY_DSN"):
        app.config["SKIP_SENTRY"] = True
