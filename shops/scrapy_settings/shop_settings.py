import os

from shops.scrapy_settings.random_user_agent import get_random_user_agent

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
USER_AGENT = get_random_user_agent
SPIDER_MODULES = ["shops"]
DOWNLOAD_TIMEOUT = 160
RETRY_TIMES = 2
