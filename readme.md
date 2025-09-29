batchcal — a tiny wrapper for multi‑provider batch LLM calls

When you have jobs that don't require a real time responses and can use "save token mode" performance, this library can help with reducing token cost and bypass online rate limits and have separate quotas.
eg. nightly jobs, dataset annotation, evals etc.

Features
- Unified request/response dataclasses
- Providers: OpenAI
- Async single + batch with bounded concurrency
- Simple QPS rate limiting
- Retries with exponential backoff + jitter on transient errors
- Per‑request timeouts
- Optional response validation hook
- Pluggable transport (httpx by default)

Install
pip install batchcal
(or clone then: pip install .)

Env Vars
- OPENAI_API_KEY

Usage

Note: you must `pip install httpx` (installed automatically if using pyproject) and have valid API keys.

Example:
```python
from batchcal import BatchClient, OpenAIProvider, Msg

async def main():
    client = BatchClient(OpenAIProvider(), qps=2.0, max_concurrency=5)
    resp = await client.acomplete([Msg.user("Ping")], model="gpt-4.1-mini")
    print(resp.content)
```

With Validation:
```python
from batchcal import BatchClient, OpenAIProvider, Msg, require_json

client = BatchClient(OpenAIProvider(), validate=require_json)

# or custom:
def validate_nonempty(r):
    if not r.content.strip():
        raise ValueError("Empty output")
```

Batch:
```python
prompts = [[Msg.user(f"Item {i}")] for i in range(20)]
resps = await client.abatch(prompts, model="gpt-4.1-mini")
for r in resps:
    print(r.content)
```

Testing
Install dev deps: pip install .[dev]
Run: pytest -q
Tests mock the OpenAI API (no network, no real key needed).

Publishing
1. Update version in pyproject.toml
2. python -m build
3. twine upload dist/*