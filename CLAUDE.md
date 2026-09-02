# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make .venv                              # create venv, install requirements.txt, install pre-commit hooks
make pre-commit                         # run all pre-commit hooks (black, isort, flake8+bugbear, bandit) against the whole tree
make run                                # run the web app (STAGE=debug by default; STAGE=dev for dev config)
make run_db                             # start a local Postgres container (shopasource-psql)
make load_db                            # open a psql shell against it
make stop_db / make clean_db            # stop / stop+remove the db container
make run_spider SPIDER=AMAZON SEARCH_KEYWORD=shirts   # run one Scrapy spider standalone, writes json_shop_results/<SPIDER>_RESULTS.json
make generate_key                       # print a fresh random API key
```

`make run` invokes `quart run`, which fails here (`shopasource.webapp.app` import error) because of the stray root `__init__.py` — package discovery breaks under Quart's dev runner. Run the ASGI app the way `Procfile` does instead:

```bash
hypercorn -b 0.0.0.0:5003 webapp.app:app
```

with the same env vars `make run` sets (`ENV_CONFIGURATION`, `STAGE`, `DB_USER`/`DB_PASS`/`DB_PORT`/`DB_NAME`/`DB_DOMAIN`, `SAVE_TO_DB`, `SKIP_SENTRY=1`), plus whichever of `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` / `DEEPSEEK_API_KEY` / `GROQ_API_KEY` / `MISTRAL_API_KEY` you want NL search to use.

```bash
API_KEY=testkey ENV_CONFIGURATION=debug SKIP_SENTRY=1 DB_USER=admin DB_PASS=admin DB_PORT=5432 DB_NAME=shopasource DB_DOMAIN=localhost SAVE_TO_DB=0 \
  .venv/bin/pytest -q tests/               # run the test suite (needs a reachable Postgres, e.g. `make run_db`)
```

CI (`.github/workflows/ci.yml`) runs the same `flake8` + `pytest -q tests/` against a Postgres service container on every push/PR to `main`/`master`. `tasks/selector_test.py` is a separate standalone smoke-test script (hits every shop's live URL directly), not part of the pytest suite.

Config: `configs/dev.json.template` documents every key; the real `configs/dev.json` is gitignored and picked by `ENV_CONFIGURATION`. Env vars are the fallback/override layer (`support.Config`) — config file values take precedence over env vars where both are set (`Config.apply_config_variables`).

## Architecture

**Search is a two-stage async job, not a single request.** `POST /api/shop/nl_search` (or `/api/shop/search` for raw keyword+shop params) creates a `Job` row and hands it to `webapp/util.py:start_async_requests`, which runs `start_shop_search` in an executor thread and returns immediately with a `job_id`. The frontend (`webapp/static/js/main_app.js`) polls `/api/get_result?job_id=` every 2s until `status` is `"done"`. `tasks/results_factory.py:ResultsFactory` is the actual search engine underneath both routes: it checks Postgres (`ShoppedData`, keyed by `searched_keyword`) for fresh-enough cached results before triggering `tasks/scrapy_run.py:launch_spiders` for any shop with none. Because `start_shop_search` runs in a fresh executor thread every call, it must call `db_session.remove()` in a `finally` block or the thread-local scoped-session leaks a Postgres connection per search (see `webapp/util.py`).

**LLM provider abstraction (`webapp/llm_providers.py`)**: `extract_structured(system, user_message, schema, provider=None)` is the one entry point `webapp/nl_search.py` calls to turn a free-text query into structured search params. It dispatches to one of six independent per-provider functions (Anthropic, OpenAI, Gemini, DeepSeek, Groq, Mistral), each using that SDK's own structured-output mechanism — they are not interchangeable calls, each has different schema-enforcement semantics (DeepSeek/Groq/Mistral have none; the schema is spelled into the prompt text instead). Groq reuses the `openai` SDK pointed at its OpenAI-compatible endpoint, same as DeepSeek; Mistral's SDK is unusual - `from mistralai import Mistral` doesn't work with the installed 2.x package (it's a namespace package with no top-level `__init__.py`), the real client is `from mistralai.client import Mistral`. `available_providers()` reports whichever have a key configured server-side; the `provider` query param lets the UI's model picker override the server default per-request, but only among configured providers. `extraction_failure_status(ex)` extracts an HTTP status from whichever SDK raised, deliberately without filtering by which code — each provider uses a different status for the same "out of credits" condition (Anthropic 400, OpenAI/DeepSeek 402, Gemini 429), so any 4xx/5xx from the SDK layer is treated as a provider-level rejection and surfaced with a specific error message; anything without a status code (e.g. the model responded but output didn't parse) falls through to a generic message. `provider="normal"` in `/api/shop/nl_search` is a pseudo-provider that skips the LLM entirely and searches all active shops with the raw query text — always offered in the model picker, including when no LLM key is configured at all, so search never fully dead-ends.

Gemini specifically doesn't call just one model - `_extract_gemini` retries down a hardcoded list of free-tier models (`_GEMINI_FALLBACK_MODELS`, newest first) whenever a model comes back 404 (retired), 429 (quota exhausted), or 503 (overloaded), rather than failing the search. Any other status propagates immediately instead of cascading, since a different model wouldn't fix a bad request or an auth failure.

**Spiders use a three-tier transport strategy** (`shops/shop_base.py` + `shops/shop_connect/shop_request.py`), because several target sites block Scrapy's Twisted downloader specifically:
1. Default — Scrapy/Twisted downloader (`get_request`).
2. `use_direct_fetch = True` on a spider — routes through `requests` instead (`direct_fetch`); bypasses Twisted's TLS/connection fingerprint.
3. `use_browser_fetch = True` — routes through a real headless Chromium via Playwright (`browser_fetch`), for sites whose bot detection defeats `direct_fetch` too (e.g. Amazon's Akamai JS challenge).

Playwright's sync API can't run inside Scrapy's asyncio reactor thread, so `browser_fetch` is routed through a dedicated single-thread `ThreadPoolExecutor`. When using `browser_fetch`, `_BROWSER_UA` and `_SEC_CH_UA` in `shop_request.py` must stay consistent with each other — Chromium reveals itself via the `sec-ch-ua` Client Hints header regardless of a spoofed User-Agent string, so a mismatched pair gets caught by bot detection even with `channel="chrome"` set. Scrapy 2.13+ requires `async def start()` rather than sync `start_requests()`; `ShopBase.start()` provides this for every spider by wrapping the (still sync, and still what subclasses override) `start_requests()`.

Per-shop config (URL templates, active/inactive flags) lives in `shops/shop_connect/shoplinks.py` and is looked up via `shops/shop_util/shop_setup_functions.py`.

## Conventions

- Formatting/linting is pre-commit-enforced: black (line-length 88), isort (`profile = black`), flake8 (`extend-ignore = E203, E501, W503, F541`) with flake8-bugbear, bandit. Run `make pre-commit` before considering a change done.
- No comments explaining *what* code does — only non-obvious *why* (a workaround, an invariant, a subtle constraint), matching the existing style in this file's own source (e.g. `use_direct_fetch`/`use_browser_fetch` docstrings, the `db_session.remove()` comment in `webapp/util.py`).
- Keep the LLM integration provider-agnostic: any new AI-assisted feature should go through (or extend) the `webapp/llm_providers.py` dispatch pattern rather than calling one SDK directly, so it keeps working across whichever provider a given deployment has a key for.
