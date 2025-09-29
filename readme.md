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

Env Vars
- OPENAI_API_KEY

Usage

Note: you must `pip install httpx` and have valid API keys.

Example:
``` 
from batchai import BatchAI, OpenAIProvider, Request

async def main():
    client = BatchAI(OpenAIProvider(), qps=2.0, concurrency=5)
    res = await client.generate(Request(model="gpt-4.1-mini", input="Ping", max_tokens=8))
    print(res.output_text)

```

With Validation:
```
from batchai import BatchAI, Request, ValidationError, BatchAIError

async def validate_nonempty(res):
    if not res.output_text.strip():
        raise ValidationError("Empty output")

reqs = [Request(model="gpt-4.1-mini", input=f"Item {i}") for i in range(20)]
try:
    out = await client.batch(reqs, validate=validate_nonempty, return_exceptions=True)
    for r in out:
        if isinstance(r, Exception):
            # log and continue
            ...
        else:
            ...
except BatchAIError as e:
    # fatal path
    ...


## Testing
Install dev deps: `pip install pytest`
Run: `pytest -q`
Tests mock the OpenAI API (no network, no real key needed).