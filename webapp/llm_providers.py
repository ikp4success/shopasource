import json

from support import config, get_logger

logger = get_logger(__name__)


class LLMConfigError(Exception):
    pass


def extraction_failure_status(ex):
    """Pull an HTTP status code out of an exception from any of the four SDKs,
    if there is one. Each SDK names the attribute differently: anthropic/openai
    (and DeepSeek, which reuses the openai SDK) use `.status_code`; google-genai
    uses `.code`. A status code present at all means the provider's API itself
    rejected the request (quota/credits/auth/malformed request - each provider
    uses a different code for "insufficient credits", e.g. Anthropic uses 400
    for it where OpenAI/DeepSeek use 402 and Gemini uses 429, so this
    deliberately doesn't filter by which code), as opposed to the model
    responding successfully with output that didn't parse - that case has no
    status code at all and should fall through to the generic message.
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

# Display-friendly labels for the model picker in the UI, in preferred order.
PROVIDER_LABELS = {
    "anthropic": "Claude (Anthropic)",
    "openai": "GPT (OpenAI / Codex)",
    "gemini": "Gemini (Google)",
    "deepseek": "DeepSeek",
}
_PROVIDER_KEYS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
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
        "GEMINI_API_KEY, DEEPSEEK_API_KEY - optionally set LLM_PROVIDER to force a "
        "specific one when more than one key is present."
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
    raise LLMConfigError(
        f"Unknown LLM_PROVIDER '{provider}', expected anthropic, openai, gemini, "
        "or deepseek"
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


def _extract_gemini(system, user_message, schema):
    from google import genai

    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)

    response = _gemini_client.models.generate_content(
        model=config.GEMINI_MODEL or "gemini-3.6-flash",
        contents=user_message,
        config={
            "system_instruction": system,
            "response_mime_type": "application/json",
            "response_json_schema": schema,
        },
    )
    return json.loads(response.text)


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
