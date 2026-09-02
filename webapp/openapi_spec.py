"""Machine-readable description of the JSON API documented in api.md.

Kept as a plain dict (rather than generated from the routes) since Quart has no
built-in OpenAPI support and the app is small enough that hand-maintaining this
alongside api.md isn't a burden.
"""

SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Shop A Source API",
        "description": (
            "Natural-language product price comparison across dozens of online "
            "stores. See api.md in the repo for narrative documentation."
        ),
        "version": "1.0.0",
    },
    "servers": [{"url": "/"}],
    "components": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "x-api-key",
            }
        },
        "schemas": {
            "SearchResult": {
                "type": "object",
                "properties": {
                    "shop_name": {"type": "string"},
                    "shop_link": {"type": "string"},
                    "title": {"type": "string"},
                    "price": {"type": "string"},
                    "numeric_price": {"type": "number"},
                    "image_url": {"type": "string"},
                    "content_description": {"type": "string"},
                },
            },
            "JobStarted": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string"},
                    "status": {"type": "string"},
                    "result": {"type": "string"},
                    "interpreted_query": {
                        "type": "object",
                        "description": "Only present on /api/shop/nl_search.",
                    },
                },
            },
            "JobResult": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["started", "in_progress", "done", "job not found"],
                    },
                    "data": {
                        "oneOf": [
                            {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/SearchResult"},
                            },
                            {"type": "object", "description": "{'error': '...'}"},
                        ]
                    },
                    "logs": {
                        "type": "object",
                        "description": "Per-shop status, e.g. {'AMAZON': 'done'}.",
                    },
                },
            },
            "Error": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
    },
    "security": [{"ApiKeyAuth": []}],
    "paths": {
        "/health": {
            "get": {
                "summary": "Liveness check",
                "security": [],
                "responses": {
                    "200": {
                        "description": "Process is up",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"status": {"type": "string"}},
                                }
                            }
                        },
                    }
                },
            }
        },
        "/api/public_api_key": {
            "get": {
                "summary": "Get the public API key to use in x-api-key for every other endpoint",
                "security": [],
                "responses": {
                    "200": {
                        "description": "The key to use",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "public_api_key": {"type": "string"}
                                    },
                                }
                            }
                        },
                    },
                    "429": {
                        "description": "Daily usage limit exceeded for this caller",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            }
        },
        "/api/shop/nl_search": {
            "get": {
                "summary": "Natural-language search - the primary way to search",
                "parameters": [
                    {
                        "name": "q",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Free text query, e.g. 'cheap waterproof hiking boots from target and amazon'.",
                    },
                    {
                        "name": "provider",
                        "in": "query",
                        "required": False,
                        "schema": {
                            "type": "string",
                            "enum": [
                                "anthropic",
                                "openai",
                                "gemini",
                                "deepseek",
                                "groq",
                                "mistral",
                                "normal",
                            ],
                        },
                        "description": (
                            "Overrides the server's default LLM provider for this "
                            "request. Must have a key configured server-side (see "
                            "/api/llm-providers.json). 'normal' skips the LLM and "
                            "searches q as a plain keyword across every active shop."
                        ),
                    },
                    {
                        "name": "async",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "enum": [0, 1], "default": 1},
                        "description": "1 (default) schedules a job and returns a job_id. 0 waits for the result - debug mode only.",
                    },
                ],
                "responses": {
                    "201": {
                        "description": "Search scheduled (or completed, if async=0)",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/JobStarted"}
                            }
                        },
                    },
                    "400": {
                        "description": "Missing/invalid query, or the LLM provider rejected the request",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            }
        },
        "/api/shop/search": {
            "get": {
                "summary": "Structured search, no LLM involved",
                "parameters": [
                    {
                        "name": "sk",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Search keyword.",
                    },
                    {
                        "name": "shops",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Comma-separated shop names, e.g. AMAZON,TARGET.",
                    },
                    {
                        "name": "smatch",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "default": 0},
                        "description": "Match accuracy, 0 (loose) to 10 (exact).",
                    },
                    {
                        "name": "shl",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "boolean"},
                        "description": "Sort high to low.",
                    },
                    {
                        "name": "slh",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "boolean"},
                        "description": "Sort low to high.",
                    },
                    {
                        "name": "async",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "enum": [0, 1], "default": 1},
                    },
                ],
                "responses": {
                    "201": {
                        "description": "Search scheduled (or completed, if async=0)",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/JobStarted"}
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid parameters",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            }
        },
        "/api/get_result": {
            "get": {
                "summary": "Poll for the result of a job started by either search endpoint",
                "parameters": [
                    {
                        "name": "job_id",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Current job status and any results so far",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/JobResult"}
                            }
                        },
                    },
                    "400": {
                        "description": "job_id missing",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            }
        },
        "/api/llm-providers.json": {
            "get": {
                "summary": "Which LLM providers have a key configured on this server",
                "responses": {
                    "200": {
                        "description": "Providers usable right now, in picker order",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "label": {"type": "string"},
                                        },
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
        "/api/shops-active.json": {
            "get": {
                "summary": "List of shops currently searchable",
                "responses": {
                    "200": {
                        "description": "Active shop names",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                }
                            }
                        },
                    }
                },
            }
        },
    },
}
