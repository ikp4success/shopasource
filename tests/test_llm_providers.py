import pytest

import webapp.llm_providers as llm_providers_module
from webapp.llm_providers import extraction_failure_status


class _FakeStatusCodeError(Exception):
    def __init__(self, status_code):
        super().__init__("boom")
        self.status_code = status_code


class _FakeCodeError(Exception):
    def __init__(self, code):
        super().__init__("boom")
        self.code = code


def test_extraction_failure_status_reads_status_code_attr():
    # Anthropic/OpenAI/DeepSeek all raise with .status_code.
    assert extraction_failure_status(_FakeStatusCodeError(400)) == 400


def test_extraction_failure_status_reads_code_attr():
    # google-genai raises with .code instead.
    assert extraction_failure_status(_FakeCodeError(429)) == 429


def test_extraction_failure_status_none_without_status():
    # A plain parse failure (model responded, output didn't parse) has no status.
    assert extraction_failure_status(Exception("could not parse response")) is None


def test_extraction_failure_status_ignores_out_of_range_values():
    assert extraction_failure_status(_FakeStatusCodeError(200)) is None


class _FakeGeminiClient:
    """Fails on every model except the given one, tracking call order."""

    def __init__(self, succeeds_on):
        self.succeeds_on = succeeds_on
        self.calls = []

        class _Models:
            def generate_content(_self, model, contents, config):
                self.calls.append(model)
                if model != self.succeeds_on:
                    raise _FakeCodeError(429)

                class _Response:
                    text = '{"ok": true}'

                return _Response()

        self.models = _Models()


def test_extract_gemini_falls_back_through_models_on_quota_exhaustion(monkeypatch):
    third_model = llm_providers_module._GEMINI_FALLBACK_MODELS[2]
    fake_client = _FakeGeminiClient(succeeds_on=third_model)
    monkeypatch.setattr(llm_providers_module, "_gemini_client", fake_client)

    result = llm_providers_module._extract_gemini("system", "wallet", {})

    assert result == {"ok": True}
    assert fake_client.calls == llm_providers_module._GEMINI_FALLBACK_MODELS[:3]


def test_extract_gemini_does_not_cascade_on_non_retryable_error(monkeypatch):
    fake_client = _FakeGeminiClient(succeeds_on="never-matches-anything")
    monkeypatch.setattr(llm_providers_module, "_gemini_client", fake_client)

    def raise_400(model, contents, config):
        raise _FakeStatusCodeError(400)

    fake_client.models.generate_content = raise_400

    with pytest.raises(_FakeStatusCodeError):
        llm_providers_module._extract_gemini("system", "wallet", {})
