import os
import pytest
import asyncio

@pytest.fixture(autouse=True)
def _fake_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

class _MockResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status
        self.text = ""
    def json(self):
        return self._payload
    def raise_for_status(self):
        if self.status_code >= 400:
            from httpx import HTTPStatusError, Request, Response
            raise HTTPStatusError("error", request=Request("POST","https://x"), response=Response(self.status_code))

@pytest.fixture
def mock_openai_success_payload():
    return {
        "id": "resp_123",
        "output": [
            {
                "id": "msg_1",
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "output_text", "text": "Hello World"}
                ],
            }
        ],
        "usage": {"input_tokens": 5, "output_tokens": 2, "total_tokens": 7},
    }

@pytest.fixture
def patch_openai_post(monkeypatch, mock_openai_success_payload):
    # Returns a function allowing customization per test
    calls = {"count": 0}
    async def _fake_post(path, json, timeout):
        calls["count"] += 1
        return _MockResponse(mock_openai_success_payload)
    from openai_provider import OpenAIProvider
    def _apply(provider: OpenAIProvider):
        monkeypatch.setattr(provider._client, "post", _fake_post)
        return calls
    return _apply

# Optional event loop speed-up for Windows (if needed)
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
