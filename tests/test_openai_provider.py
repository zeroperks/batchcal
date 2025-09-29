import pytest
from openai_provider import OpenAIProvider
from msg import Msg
from batchclient import BatchClient

@pytest.mark.asyncio
async def test_single_completion(patch_openai_post):
    prov = OpenAIProvider()
    patch_openai_post(prov)
    client = BatchClient(prov)
    resp = await client.acomplete([Msg.user("Say hi")], model="gpt-4.1-mini")
    assert resp.error is None
    assert resp.content == "Hello World"
    assert resp.usage.total_tokens == 7

@pytest.mark.asyncio
async def test_batch_completion_counts(patch_openai_post):
    prov = OpenAIProvider()
    calls = patch_openai_post(prov)
    client = BatchClient(prov, max_concurrency=3, qps=100.0)
    prompts = [[Msg.user(f"Item {i}") ] for i in range(5)]
    resps = await client.abatch(prompts, model="gpt-4.1-mini")
    assert len(resps) == 5
    assert all(r.content == "Hello World" for r in resps)
    assert calls["count"] == 5
