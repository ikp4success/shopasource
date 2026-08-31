# Architecture

## Components

```mermaid
flowchart TB
    subgraph Client["Browser"]
        UI["Search UI<br/>search bar + model picker"]
    end

    subgraph App["Quart web app (webapp/)"]
        NL["/api/shop/nl_search<br/>natural-language search"]
        SEARCH["/api/shop/search<br/>structured search"]
        RESULT["/api/get_result<br/>job polling"]
        PROVIDERS["webapp/llm_providers.py<br/>provider abstraction"]
    end

    subgraph LLMs["LLM providers (pick one per request)"]
        ANTH["Anthropic<br/>Claude"]
        OAI["OpenAI<br/>GPT / Codex"]
        GEM["Gemini<br/>Google"]
        DS["DeepSeek"]
        NORMAL["Normal Search<br/>no LLM - plain keyword"]
    end

    subgraph Jobs["Async job (tasks/, db/)"]
        FACTORY["ResultsFactory<br/>tasks/results_factory.py"]
        JOBTBL[("Job table<br/>status per shop")]
    end

    subgraph Spiders["Scrapy spiders (shops/), one per shop"]
        DEFAULT["Scrapy's own downloader<br/>(default)"]
        DIRECT["direct_fetch<br/>requests library"]
        BROWSER["browser_fetch<br/>headless Chromium (Playwright)"]
    end

    STORE[("Retail site<br/>e.g. Amazon, Nike, Newegg")]
    DB[("Postgres<br/>ShoppedData, Job, APIUsage")]

    UI -- "free-text query" --> NL
    UI -- "shop/sort/accuracy params" --> SEARCH
    UI -- "poll" --> RESULT

    NL -- "provider id, or auto" --> PROVIDERS
    PROVIDERS --> ANTH & OAI & GEM & DS & NORMAL
    ANTH & OAI & GEM & DS -- "parsed keyword,<br/>shops, sort, accuracy" --> NL
    NORMAL -- "query text as-is,<br/>all active shops" --> NL
    NL --> SEARCH

    SEARCH --> FACTORY
    FACTORY --> JOBTBL
    FACTORY -- "spawns up to<br/>MAX_CONCURRENT_SHOPS shops<br/>at once (bounded pool);<br/>browser_fetch shops<br/>capped separately, smaller" --> Spiders

    DEFAULT -.->|"blocked by<br/>most sites now"| STORE
    DIRECT -->|"bypasses Scrapy/Twisted<br/>fingerprinting"| STORE
    BROWSER -->|"real browser,<br/>fingerprint-matched<br/>sec-ch-ua"| STORE

    Spiders -- "scraped items" --> DB
    RESULT -- "reads" --> DB
```

## Request flow: natural-language search

```mermaid
sequenceDiagram
    participant U as Browser
    participant A as Quart app
    participant L as LLM provider
    participant J as ResultsFactory / Job
    participant S as Scrapy spider
    participant D as Postgres

    U->>A: GET /api/shop/nl_search?q=...&provider=...
    alt provider = normal
        A->>A: use q verbatim as keyword, all active shops
    else provider = anthropic/openai/gemini/deepseek
        A->>L: parse query into JSON schema
        L-->>A: {search_keyword, shops, sort, match_accuracy}
        Note over A,L: any 4xx/5xx from the SDK names the real<br/>cause instead of a generic "could not understand" message
    end
    A->>J: validate_params + start_async_requests
    J->>D: create Job row (status: started)
    par per shop, bounded concurrency
        J->>S: subprocess.call("scrapy crawl <SHOP> ...")
    end
    S->>S: fetch via default / direct_fetch / browser_fetch
    S->>D: save ShoppedData rows, update Job status
    loop client polls
        U->>A: GET /api/get_result?job_id=...
        A->>D: query ShoppedData + Job status
        D-->>A: rows + status
        A-->>U: {status, data}
    end
```

## Why spiders have three transport tiers

Most retail sites now fingerprint scrapers below the HTTP layer, so a single
transport doesn't work everywhere. Each spider in `shops/` opts into whichever
tier it actually needs, in `shop_base.py`:

| Tier | Flag | How | Used for |
|---|---|---|---|
| Default | *(none)* | Scrapy's own (Twisted) downloader | Sites with no meaningful bot detection (e.g. Newegg) |
| Direct | `use_direct_fetch = True` | Python `requests`, bypassing Scrapy/Twisted's network stack | Sites that fingerprint Twisted's connection signature specifically, but not a plain HTTP client (e.g. Macy's, TJ Maxx) |
| Browser | `use_browser_fetch = True` | Headless Chromium via Playwright, real Chrome channel, `sec-ch-ua` matched to the User-Agent | Sites with JS challenges or Client-Hints fingerprinting that block the other two (e.g. Amazon, Walmart, ASOS, Zara) |

Each search runs every active shop's spider concurrently rather than one at a
time (`ResultsFactory.start_search`, bounded by `MAX_CONCURRENT_SHOPS`), with a
separate, smaller cap (`MAX_CONCURRENT_BROWSER_SHOPS`) just for `browser_fetch`
shops - each one launches a real headless Chromium process, so letting all of
the general concurrency budget be browser shops at once can spike memory well
past what a small deployment has. A shop whose launch fails doesn't abort the
rest of the search; it's marked `error` and the others keep going.

A dead shop (its site no longer responding at all, not just blocking scrapers)
gets marked `active: False` in `shops/shop_util/shop_setup.py` rather than left
to time out on every search - see the `CUSHINE` entry there for an example.

## LLM providers

`webapp/llm_providers.py` is a small dispatch layer, not a framework: one
function (`extract_structured`) takes a system prompt, a user message, and a
JSON schema, and returns parsed JSON, regardless of which of the four SDKs
services the call. Adding a fifth provider means adding one `_extract_x`
function and one entry in `PROVIDER_LABELS` - nothing else in the app knows or
cares which provider handled a given request.

`/api/llm-providers.json` reports which providers actually have a key
configured on the running server (plus the always-available `normal`
pseudo-provider), which is what populates the model picker in the UI - so the
set of choices a user sees always matches what will actually work.

## Search relevance

Every search - LLM-parsed or `normal` - is filtered through
`ResultsFactory.match_sk()` with a minimum match-accuracy floor
(`MIN_MATCH_ACCURACY` in `webapp/nl_search.py`), so a search never runs fully
unfiltered. Without it, a shop that doesn't carry the searched item at all
still contributes its unrelated inventory to the results, and the cheapest of
that junk can end up misleadingly badged as "best price" client-side.
Matching itself uses whole-word boundaries and ignores filler words like
"for"/"with" (`STOPWORDS` in `tasks/results_factory.py`), rather than a plain
substring check, which used to false-positive-match "for" inside "force".

## Operational endpoints

`GET /health` is a liveness check (no api key required). `GET /openapi.json`
serves a machine-readable OpenAPI 3.0 description of the JSON API
(`webapp/openapi_spec.py`), maintained by hand alongside `api.md` since Quart
has no built-in OpenAPI generation.
