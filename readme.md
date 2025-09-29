"""
py-llm-batch — a tiny, practical wrapper for multi‑provider LLM calls

Features
- Unified request/response dataclasses
- Providers: OpenAI (Responses API), Anthropic
- Async single + batch with bounded concurrency
- Simple QPS rate limiting
- Retries with exponential backoff + jitter on transient errors
- Per‑request timeouts
- Optional response validation hook
- Pluggable transport (httpx by default)

Env Vars
- OPENAI_API_KEY

Usage
>>> import asyncio
>>> from py_llm_batch import BatchClient, OpenAIProvider, AnthropicProvider, Msg
>>> client = BatchClient(
...     provider=OpenAIProvider(),
...     max_concurrency=8,
...     qps=4.0,
... )
>>> prompts = [
...     [Msg.user("Say hi to #"+str(i))] for i in range(10)
... ]
>>> results = asyncio.run(client.abatch(prompts, model="gpt-4.1-mini"))
>>> print(results[0].content)

Note: you must `pip install httpx` and have valid API keys.
"""