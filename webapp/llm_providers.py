import json

from support import config, get_logger

logger = get_logger(__name__)


class LLMConfigError(Exception):
    pass


def extraction_failure_status(ex):
    """Pull an HTTP status code out of an exception from any of the six SDKs,
    if there is one. Each SDK names the attribute differently: anthropic/openai
    (and DeepSeek/Groq, which reuse the openai SDK) and mistralai use
    `.status_code`; google-genai uses `.code`. A status code present at all
    means the provider's API itself rejected the request (quota/credits/auth/
    malformed request - each provider uses a different code for "insufficient
    credits", e.g. Anthropic uses 400 for it where OpenAI/DeepSeek use 402 and
    Gemini uses 429, so this deliberately doesn't filter by which code), as
    opposed to the model responding successfully with output that didn't
    parse - that case has no status code at all and should fall through to
    the generic message.
    """
    for attr in ("status_code", "code"):
        value = getattr(ex, attr, None)
        if isinstance(value, int) and 400 <= value < 600:
            return value
    return None


_anthropic_client = None
_openai_client = None
_gemini_client = None
_deepseek_client = None
_groq_client = None
_mistral_client = None

# Display-friendly labels for the model picker in the UI, in preferred order.
PROVIDER_LABELS = {
    "anthropic": "Claude (Anthropic)",
    "openai": "GPT (OpenAI / Codex)",
    "gemini": "Gemini (Google)",
    "deepseek": "DeepSeek",
    "groq": "Groq",
    "mistral": "Mistral",
}
_PROVIDER_KEYS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
}


def available_providers():
    """Providers that actually have an API key configured on this server, in
    PROVIDER_LABELS order."""
    return [
        name for name in PROVIDER_LABELS if getattr(config, _PROVIDER_KEYS[name], None)
    ]


def _provider_name(explicit=None):
    explicit = (explicit or config.LLM_PROVIDER or "").strip().lower()
    if explicit:
        if explicit not in _PROVIDER_KEYS:
            raise LLMConfigError(
                f"Unknown provider '{explicit}', expected one of: "
                f"{', '.join(_PROVIDER_KEYS)}"
            )
        if not getattr(config, _PROVIDER_KEYS[explicit], None):
            raise LLMConfigError(
                f"Provider '{explicit}' has no API key configured on this server."
            )
        return explicit
    available = available_providers()
    if available:
        return available[0]
    raise LLMConfigError(
        "No LLM provider configured. Set one of ANTHROPIC_API_KEY, OPENAI_API_KEY, "
        "GEMINI_API_KEY, DEEPSEEK_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY - "
        "optionally set LLM_PROVIDER to force a specific one when more than one "
        "key is present."
    )


def extract_structured(system, user_message, schema, provider=None):
    """Run one structured-extraction call against the given (or auto-detected)
    provider. `provider` lets a caller (e.g. the UI's model picker) override the
    server default for a single request; it must be one with a key configured here.

    Returns the parsed JSON object matching `schema`.
    """
    provider = _provider_name(provider)
    if provider == "anthropic":
        return _extract_anthropic(system, user_message, schema)
    if provider == "openai":
        return _extract_openai(system, user_message, schema)
    if provider == "gemini":
        return _extract_gemini(system, user_message, schema)
    if provider == "deepseek":
        return _extract_deepseek(system, user_message, schema)
    if provider == "groq":
        return _extract_groq(system, user_message, schema)
    if provider == "mistral":
        return _extract_mistral(system, user_message, schema)
    raise LLMConfigError(
        f"Unknown LLM_PROVIDER '{provider}', expected one of: {', '.join(_PROVIDER_KEYS)}"
    )


def _extract_anthropic(system, user_message, schema):
    import anthropic

    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    response = _anthropic_client.messages.create(
        model=config.ANTHROPIC_MODEL or "claude-opus-5",
        max_tokens=1024,
        output_config={
            "effort": "low",
            "format": {"type": "json_schema", "schema": schema},
        },
        system=system,
        messages=[{"role": "user", "content": user_message}],
    )
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def _extract_openai(system, user_message, schema):
    import openai

    global _openai_client
    if _openai_client is None:
        _openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

    response = _openai_client.responses.create(
        model=config.OPENAI_MODEL or "gpt-4o-mini",
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "extraction",
                "schema": schema,
                "strict": True,
            }
        },
    )

    for output in response.output:
        if output.type != "message":
            continue
        for item in output.content:
            if item.type == "refusal":
                raise LLMConfigError(f"OpenAI refused the request: {item.refusal}")
            if item.type == "output_text":
                return json.loads(item.text)
    raise LLMConfigError("OpenAI response contained no output_text block")


# Free-tier flash models, newest/most-capable first. Gemini model availability
# churns often - models get retired (404) or hit their free-tier quota (429) or
# are briefly overloaded (503) - so on any of those we fall through to the next
# model down rather than failing the whole search. Verified working live against
# the real API; gemini-2.5-flash/-lite were dropped from this list after they
# started returning 404 "no longer available to new users".
_GEMINI_FALLBACK_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]
_GEMINI_CASCADE_STATUSES = {404, 429, 503}


def _extract_gemini(system, user_message, schema):
    from google import genai

    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)

    models_to_try = [config.GEMINI_MODEL] if config.GEMINI_MODEL else []
    models_to_try += [m for m in _GEMINI_FALLBACK_MODELS if m not in models_to_try]

    for index, model in enumerate(models_to_try):
        try:
            response = _gemini_client.models.generate_content(
                model=model,
                contents=user_message,
                config={
                    "system_instruction": system,
                    "response_mime_type": "application/json",
                    "response_json_schema": schema,
                },
            )
            return json.loads(response.text)
        except Exception as ex:
            status = extraction_failure_status(ex)
            is_last_model = index == len(models_to_try) - 1
            if status in _GEMINI_CASCADE_STATUSES and not is_last_model:
                logger.warning(
                    "Gemini model %s unavailable (status=%s), falling back to "
                    "the next free-tier model: %s",
                    model,
                    status,
                    ex,
                )
                continue
            raise


def _extract_deepseek(system, user_message, schema):
    import openai

    global _deepseek_client
    if _deepseek_client is None:
        _deepseek_client = openai.OpenAI(
            api_key=config.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com"
        )

    # DeepSeek's JSON mode only accepts {"type": "json_object"} - no schema
    # enforcement - so the schema has to be spelled out in the prompt instead.
    full_system = (
        f"{system}\n\nRespond with a single JSON object only, no other text, "
        f"matching exactly this JSON schema: {json.dumps(schema)}"
    )

    response = _deepseek_client.chat.completions.create(
        model=config.DEEPSEEK_MODEL or "deepseek-v4-flash",
        messages=[
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def _extract_groq(system, user_message, schema):
    import openai

    global _groq_client
    if _groq_client is None:
        _groq_client = openai.OpenAI(
            api_key=config.GROQ_API_KEY, base_url="https://api.groq.com/openai/v1"
        )

    # Groq's endpoint is OpenAI-compatible but, like DeepSeek, its JSON mode only
    # accepts {"type": "json_object"} - no schema enforcement - so the schema has
    # to be spelled out in the prompt instead.
    full_system = (
        f"{system}\n\nRespond with a single JSON object only, no other text, "
        f"matching exactly this JSON schema: {json.dumps(schema)}"
    )

    response = _groq_client.chat.completions.create(
        model=config.GROQ_MODEL or "openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def _extract_mistral(system, user_message, schema):
    # The current mistralai package (2.x) ships as a namespace package with no
    # top-level __init__.py - the documented `from mistralai import Mistral`
    # doesn't work with it; the client class actually lives under .client.
    from mistralai.client import Mistral

    global _mistral_client
    if _mistral_client is None:
        _mistral_client = Mistral(api_key=config.MISTRAL_API_KEY)

    # Mistral's JSON mode is also schema-less {"type": "json_object"} - spell the
    # schema into the prompt, same as DeepSeek/Groq.
    full_system = (
        f"{system}\n\nRespond with a single JSON object only, no other text, "
        f"matching exactly this JSON schema: {json.dumps(schema)}"
    )

    response = _mistral_client.chat.complete(
        model=config.MISTRAL_MODEL or "mistral-small-latest",
        messages=[
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
