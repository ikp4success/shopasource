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
