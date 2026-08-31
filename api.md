# API Usage

The web UI (`/`) searches with plain English through `/api/shop/nl_search` - that's the
recommended way to use this API too. `/api/shop/search` (structured keyword/shops/sort
params) still works underneath and remains available directly for programmatic use, but
the UI no longer exposes manual shop-picking or match-accuracy controls - an LLM infers
those from your query text instead.

#### HEADERS ####
* x-api-key: {API_KEY}

#### GET /api/public_api_key ####
* Returns current public api key, and its rate limited.
* Api key and rate limit might change, and it's limited per day(s). e.g 1000 hit per day.
* Rate limit apply to web page https://shopasource.herokuapp.com/ as well.

#### GET /api/shop/nl_search?q={free_text_query}&provider={model}&async=1 ####
* Natural language search - the primary way to search. An LLM parses the free text
  query into a keyword, shop names, sort order and match accuracy, then runs the same
  search as /api/shop/search.
* q - free text query e.g /api/shop/nl_search?q=cheap waterproof hiking boots from target and amazon
* provider - optional; one of `anthropic`, `openai`, `gemini`, `deepseek`, or `normal`.
  Overrides the server's default for this one request. Must be a provider with a key
  configured on the server (see /api/llm-providers.json for which ones are available) or
  the request fails with a 400 naming the problem. `normal` is always available - it
  skips the LLM entirely and searches `q` as a plain keyword across every active shop,
  the pre-AI search behavior; use it if every configured provider is out of quota/credits.
* Async - 1 schedule result and assign to a job id (default). Response includes an
  `interpreted_query` field showing how the query was parsed, for debugging.
* Async - 0 wait for result, not recommended. Great for debugging, debug mode only.
* Requires at least one of ANTHROPIC_API_KEY, OPENAI_API_KEY (also used by Codex),
  GEMINI_API_KEY, or DEEPSEEK_API_KEY to be configured on the server. If more than one
  is set and `provider` isn't given, LLM_PROVIDER (same four values) picks the default -
  see configs/dev.json.template and webapp/llm_providers.py.

#### GET /api/llm-providers.json ####
* Lists which LLM providers are actually usable on this server right now (have an API
  key configured), as `[{"id": "gemini", "label": "Gemini (Google)"}, ...]`. This is what
  populates the model picker in the UI.

#### GET /api/shop/search?sk={keyword}&smatch={match_accuracy}&shl=true&slh=false&shops={shop_name}&async=1 ####
* Structured search, no LLM involved. What /api/shop/nl_search calls internally once it
  has parsed your query - use this directly if you already know exactly which shops and
  parameters you want.
* Match Accuracy - refine results based on keyword
* SHL - High to low
* SLH - Low to High
* Shops - Shop Name, single shops /api/shop/search?sk=wallet&smatch=8&shl=true&slh=false&shops=AMAZON&async=1
* Shops - Shop Name, multiple shops /api/shop/search?sk=wallet&smatch=8&shl=true&slh=false&shops=AMAZON,TARGET&async=1
* Keyword - search keyword
* Async - 1 schedule result and assign to a job id (default).
* Async - 0 wait for result, not recommended. Great for debuging.

#### GET /api/get_result?job_id={job_id} ####
* Job Id - job id from a scheduled search above (either endpoint).

#### GET /api/shops-active.json ####
* Get's list of shops available
