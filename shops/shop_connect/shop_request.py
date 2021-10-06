import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError, TimeoutError
from w3lib.url import safe_url_string

from shops.shop_utilities.extra_function import prepend_domain


def get_request(url, callback, domain_url=None, meta=None, headers=None):
    if not headers:
        headers = {}
    url = prepend_domain(url, domain_url)
    if url is None:
        return None
    url = safe_url_string(url)
    request = scrapy.Request(
        url, callback=callback, errback=errcallback, meta=meta, headers=headers
    )
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
