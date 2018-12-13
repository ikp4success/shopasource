import os
from user_agent import generate_user_agent

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
USER_AGENT = generate_user_agent()  # "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
SPIDER_MODULES = ['shops']
DOWNLOAD_TIMEOUT = 45
