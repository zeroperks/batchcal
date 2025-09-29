import pytest
from openai_provider import OpenAIProvider
from msg import Msg
from batchclient import BatchClient

@pytest.mark.asyncio
async def test_validation_failure(patch_openai_post, monkeypatch):
    prov = OpenAIProvider()
    # Patch provider to return non-JSON text
    calls = patch_openai_post(prov)
    def validator(resp):
        import json
        json.loads(resp.content)  # will raise
    client = BatchClient(prov, validate=validator)
    resp = await client.acomplete([Msg.user("Anything")], model="gpt-4.1-mini")
    assert resp.error and "validation_error" in resp.error
    assert calls["count"] == 1
