import os

from shops.scrapy_settings.random_user_agent import get_desktop_user_agent

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
USER_AGENT = get_desktop_user_agent()
# USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
SPIDER_MODULES = ["shops"]
DOWNLOAD_TIMEOUT = 160
RETRY_TIMES = 0
