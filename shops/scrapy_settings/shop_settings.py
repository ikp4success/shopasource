import os
from user_agent import generate_user_agent

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
USER_AGENT = generate_user_agent()
# USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
SPIDER_MODULES = ['shops']
DOWNLOAD_TIMEOUT = 100
SHOP_CACHE_MAX_EXPIRY_TIME = 30
SHOP_CACHE_LOOKUP_SET = True
