import re

from fake_useragent import UserAgent
from user_agent import generate_user_agent

default_user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"


def get_desktop_user_agent():
    try:
        user_agent = other_random_user_agent()
        if user_agent is not None:
            # user_agent = user_agent.upper()
            if (
                "Mobile" not in user_agent
                and "Phone" not in user_agent
                and "Touch" not in user_agent
                and "Trident" not in user_agent
            ):
                alt_user_agent = other_random_user_agent()
                if validate_user_agent(user_agent):
                    return user_agent
                elif validate_user_agent(alt_user_agent):
                    return alt_user_agent
            return get_desktop_user_agent()
    except Exception:
        return default_user_agent


def validate_user_agent(user_agent):
    if "Safari" in user_agent and "Chrome" not in user_agent:
        # print(user_agent)
        browser_version = re.search(r"Version\/(.*?)\.", user_agent)
        if browser_version is not None and int(browser_version.group(1)) >= 10:
            return True
    if "Chrome" in user_agent:
        # print(user_agent)
        browser_version = re.search(r"Chrome\/(.*?)\.", user_agent)
        if browser_version is not None and int(browser_version.group(1)) >= 56:
            return True
    if "Firefox" in user_agent:
        # print(user_agent)
        browser_version = re.search(r"Firefox\/(.*?)\.", user_agent)
        if browser_version is not None and int(browser_version.group(1)) >= 50:
            return True
    if "Edge" in user_agent:
        # print(user_agent)
        browser_version = re.search(r"Edge\/(.*?)\.", user_agent)
        if browser_version is not None and int(browser_version.group(1)) >= 15:
            return True
    if "Opera" in user_agent:
        # print(user_agent)
        browser_version = re.search(r"Opera\/(.*?)\.", user_agent)
        if browser_version is not None and int(browser_version.group(1)) >= 50:
            return True
    return False


def random_user_agent():
    ua = UserAgent(cache=False)
    ua.update()
    user_agent = ua.random
    return user_agent


def other_random_user_agent():
    return generate_user_agent()
