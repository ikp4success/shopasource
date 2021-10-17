import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError, TimeoutError
from w3lib.url import safe_url_string

from shops.shop_util.extra_function import prepend_domain
from support import get_logger

logger = get_logger(__name__)


def parse_default_errcallback(failure):
    # logs failures
    logger.error(repr(failure))

    if failure.check(HttpError):
        response = failure.value.response
        logger.error("HttpError occurred on %s", response.url)

    elif failure.check(DNSLookupError):
        request = failure.request
        logger.error("DNSLookupError occurred on %s", request.url)

    elif failure.check(TimeoutError, TCPTimedOutError):
        request = failure.request
        logger.error("TimeoutError occurred on %s", request.url)


def get_request(
    url, callback, errcallback=None, domain_url=None, meta=None, headers=None
):
    if not headers:
        headers = {}
    url = prepend_domain(url, domain_url)
    if url is None:
        return None
    url = safe_url_string(url)
    request = scrapy.Request(
        url,
        callback=callback,
        errback=errcallback or parse_default_errcallback,
        meta=meta,
        headers=headers,
    )
    return request
