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
    FACTORY -- "spawns one<br/>scrapy subprocess<br/>per shop" --> Spiders

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
        Note over A,L: on 401/402/403/429 the error names the real<br/>cause instead of a generic "could not understand" message
    end
    A->>J: validate_params + start_async_requests
    J->>D: create Job row (status: started)
    J->>S: subprocess.call("scrapy crawl <SHOP> ...") per shop
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
| Browser | `use_browser_fetch = True` | Headless Chromium via Playwright, real Chrome channel, `sec-ch-ua` matched to the User-Agent | Sites with JS challenges or Client-Hints fingerprinting that block both of the above (e.g. Amazon, Nike) |

A handful of retailers (Walmart, H&M, Target's search API, ...) defeat all three
and need infrastructure this project doesn't have - residential IP rotation, in
Walmart's case, or a still-unidentified signing scheme for Target's API.

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
