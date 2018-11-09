import scrapy
from w3lib.url import safe_url_string
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from shops.shop_utilities.extra_function import prepend_domain


def get_request(url, callback, domain_url=None, meta=None):
    url = prepend_domain(url, domain_url)
    if url is None:
        return None
    url = safe_url_string(url)
    request = scrapy.Request(url, callback=callback, errback=errcallback, meta=meta)
    return request


def errcallback(failure):
    # logs failures
    print(repr(failure))

    if failure.check(HttpError):
        response = failure.value.response
        print("HttpError occurred on %s", response.url)

    elif failure.check(DNSLookupError):
        request = failure.request
        print("DNSLookupError occurred on %s", request.url)

    elif failure.check(TimeoutError, TCPTimedOutError):
        request = failure.request
        print("TimeoutError occurred on %s", request.url)
