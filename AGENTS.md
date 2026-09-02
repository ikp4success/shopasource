# AGENTS.md

This file provides standalone project guidance for Codex.

## Commands

```bash
make .venv
make pre-commit
make run                              # debug config and local Postgres
make run STAGE=dev
make run_db
make load_db
make stop_db
make clean_db
make run_spider SPIDER=AMAZON SEARCH_KEYWORD=shirts
make generate_key
```

`make run` uses Hypercorn because Quart's runner misinterprets the stray root
`__init__.py`. The production entry point is
`hypercorn -b 0.0.0.0:$PORT webapp.app:app`.

Tests require reachable Postgres. CI runs flake8 and pytest against Postgres;
`tasks/selector_test.py` is a separate live-site smoke test. Configuration is
documented by `configs/dev.json.template`; the real `configs/dev.json` is
gitignored. JSON config values override environment variables.

## Deployment

`render.yaml` defines the Render Docker service and Postgres database. Bind to
`0.0.0.0:$PORT`; Render supplies `DATABASE_URL`. Never commit credentials or
API keys. Configure optional LLM keys in Render. `/health` is the health check.
The image installs real Google Chrome because Playwright launches
`channel="chrome"`, not bundled Chromium.

## Architecture

Search is a two-stage async job. Search endpoints create a `Job`, hand work to
`start_async_requests`, and return a `job_id`; the frontend polls
`/api/get_result`. `ResultsFactory` checks cached `ShoppedData` before launching
Scrapy processes. Executor threads must call `db_session.remove()` in `finally`.

All natural-language parsing goes through
`webapp.llm_providers.extract_structured`. Keep features provider-agnostic. The
supported providers are Anthropic, OpenAI, Gemini, DeepSeek, Groq, and Mistral;
`normal` skips AI. Gemini cascades through fallback models on 404, 429, and 503.
The LLM selects plausible shops before per-item relevance filtering, falling
back to all active shops only when it returns none.

Shop fetching has three tiers: Scrapy/Twisted, `use_direct_fetch` via requests,
and `use_browser_fetch` via Playwright. Playwright runs in a dedicated thread;
keep `_BROWSER_UA` and `_SEC_CH_UA` consistent and clean up failed browser
starts. Scrapy 2.13+ uses async `start()`. Shop definitions live under
`shops/shop_connect` and `shops/shop_util`.

## Conventions

- Run `make pre-commit` before completing work.
- Use Black at 88 columns, isort, flake8 with bugbear, and Bandit.
- Comments explain non-obvious reasons or invariants, not straightforward code.
- Preserve unrelated user and agent changes.
- Keep AI features provider-agnostic through `webapp/llm_providers.py`.

After completing and verifying requested changes, automatically commit only the
task's files. Add this trailer to every Codex-authored commit:

`Co-Authored-By: Codex <codex@openai.com>`
