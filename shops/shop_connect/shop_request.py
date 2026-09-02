from concurrent.futures import ThreadPoolExecutor

import requests
import scrapy
from scrapy.http import TextResponse
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError, TimeoutError
from w3lib.url import safe_url_string

from shops.shop_util.extra_function import prepend_domain
from support import get_logger

logger = get_logger(__name__)

DIRECT_FETCH_TIMEOUT = 20


def direct_fetch(url, domain_url=None, headers=None):
    """Fetch a page via `requests` instead of Scrapy's own (Twisted) downloader.

    Some sites (Amazon, Walmart, Macy's, Nike, ...) return non-200 responses to
    Scrapy's requests specifically - same headers, same IP, same User-Agent - while
    an identical request through `requests` succeeds. That points at connection/TLS
    fingerprinting rather than anything header-level, so for those shops we bypass
    Scrapy's downloader and hand its response back wrapped as a normal scrapy
    TextResponse, so the rest of each spider's parsing code needs no changes.
    """
    if not headers:
        headers = {}
    url = prepend_domain(url, domain_url)
    if url is None:
        return None
    url = safe_url_string(url)
    try:
        resp = requests.get(url, headers=headers, timeout=DIRECT_FETCH_TIMEOUT)
    except requests.RequestException as ex:
        logger.error("direct_fetch failed for %s: %s", url, ex)
        return None
    return TextResponse(
        url=resp.url,
        status=resp.status_code,
        headers=resp.headers.items(),
        body=resp.content,
    )


BROWSER_FETCH_TIMEOUT_MS = 25000
# A spoofed User-Agent isn't enough on its own: Chromium always sends its real
# identity via the sec-ch-ua Client Hints header (e.g. "HeadlessChrome"),
# regardless of what User-Agent string is set - a mismatch some sites (Target)
# check for. Keep both consistent, and use a real Chrome UA/version pair.
_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
_SEC_CH_UA = '"Not=A?Brand";v="99", "Google Chrome";v="130", "Chromium";v="130"'

_playwright_ctx = None
_browser = None
_browser_context = None
# Playwright's sync API asserts it isn't called from a thread driving an asyncio
# event loop - which Scrapy's own reactor is. Routing every call through one
# dedicated thread (started without a loop) keeps the sync API usable, and the
# module-level browser/context are only ever touched from that same thread.
_browser_executor = ThreadPoolExecutor(max_workers=1)


def _get_browser_context():
    global _playwright_ctx, _browser, _browser_context
    if _browser_context is None:
        from playwright.sync_api import sync_playwright

        _playwright_ctx = sync_playwright().start()
        # sync_playwright().start() spawns Playwright's own Node.js driver process
        # immediately, before the browser launch below is even attempted - if that
        # launch (or anything after it) fails, that driver process would otherwise
        # be silently leaked (the module-level _browser_context stays None, so the
        # *next* call just starts another one on top, without ever stopping this
        # one) and every retry compounds it.
        try:
            _browser = _playwright_ctx.chromium.launch(
                channel="chrome",
                args=["--disable-blink-features=AutomationControlled"],
            )
            _browser_context = _browser.new_context(
                user_agent=_BROWSER_UA,
                viewport={"width": 1280, "height": 900},
                locale="en-US",
                extra_http_headers={"sec-ch-ua": _SEC_CH_UA},
            )
            # Sites like Amazon fingerprint headless Chromium via
            # navigator.webdriver - the one flag that reliably distinguishes it
            # from a real browser.
            _browser_context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
        except Exception:
            _close_browser_sync()
            raise
    return _browser_context


def _close_browser_sync():
    global _playwright_ctx, _browser, _browser_context
    if _browser is not None:
        try:
            _browser.close()
        except Exception:
            pass
    if _playwright_ctx is not None:
        try:
            _playwright_ctx.stop()
        except Exception:
            pass
    _browser = None
    _browser_context = None
    _playwright_ctx = None


def close_browser():
    _browser_executor.submit(_close_browser_sync).result()


def _browser_fetch_sync(url, domain_url, headers):
    url = prepend_domain(url, domain_url)
    if url is None:
        return None
    url = safe_url_string(url)
    page = None
    try:
        context = _get_browser_context()
        page = context.new_page()
        response = page.goto(
            url, timeout=BROWSER_FETCH_TIMEOUT_MS, wait_until="domcontentloaded"
        )
        page.wait_for_timeout(2500)
        body = page.content()
        status = response.status if response else 200
        final_url = page.url
    except Exception as ex:
        logger.error("browser_fetch failed for %s: %s", url, ex)
        return None
    finally:
        if page is not None:
            page.close()
    return TextResponse(url=final_url, status=status, body=body.encode("utf-8"))


def browser_fetch(url, domain_url=None, headers=None):
    """Fetch a page with a real (headless) browser via Playwright.

    For sites whose bot detection defeats both Scrapy's downloader and plain HTTP
    clients (`direct_fetch`) - e.g. Amazon's Akamai JS challenge - only an actual
    browser that executes the page's JavaScript gets a real response.
    """
    return _browser_executor.submit(
        _browser_fetch_sync, url, domain_url, headers
    ).result()


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
