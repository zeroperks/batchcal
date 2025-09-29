from __future__ import annotations

import asyncio
import json
from typing import Callable, Dict, List, Optional, Sequence

from provider import Provider
from llm_request import LLMRequest
from llm_response import LLMResponse
from msg import Msg
from backoff import _compute_backoff
from token_bucket import _TokenBucket


class BatchClient:
    def __init__(
        self,
        provider: Provider,
        *,
        max_concurrency: int = 8,
        qps: Optional[float] = None,
        max_retries: int = 3,
        timeout: float = 60.0,
        validate: Optional[Callable[[LLMResponse], None]] = None,
    ):
        self.provider = provider
        self.sema = asyncio.Semaphore(max(1, int(max_concurrency)))
        self.bucket = _TokenBucket(qps) if qps else None
        self.max_retries = max_retries
        self.timeout = timeout
        self.validate = validate

    async def _one(self, req: LLMRequest) -> LLMResponse:
        attempt = 1
        while True:
            try:
                async with self.sema:
                    if self.bucket:
                        await self.bucket.acquire()
                    resp = await self.provider.acomplete(req, timeout=self.timeout)
                if self.validate:
                    try:
                        self.validate(resp)
                    except Exception as e:
                        resp.error = f"validation_error: {e}"
                if not resp.error:
                    return resp
                # if provider returned an error, decide whether to retry
                if attempt > self.max_retries:
                    return resp
            except Exception as e:
                if attempt > self.max_retries:
                    return LLMResponse(provider=self.provider.name, model=req.model, content="", raw={"error": str(e)}, error=str(e))
            # backoff
            await asyncio.sleep(_compute_backoff(attempt))
            attempt += 1

    async def abatch(
        self,
        prompts: Sequence[Sequence[Msg]],
        *,
        model: str,
        temperature: float = 0.7,
        max_output_tokens: Optional[int] = None,
        extra: Optional[Dict[str, any]] = None,
    ) -> List[LLMResponse]:
        extra = extra or {}
        reqs = [
            LLMRequest(messages=list(msgs), model=model, temperature=temperature, max_output_tokens=max_output_tokens, extra=extra)
            for msgs in prompts
        ]
        return await asyncio.gather(*(self._one(r) for r in reqs))

    async def acomplete(self, messages: Sequence[Msg], *, model: str, **kw) -> LLMResponse:
        req = LLMRequest(messages=list(messages), model=model, **kw)
        return await self._one(req)


def run_batch(
    provider: Provider,
    prompts: Sequence[Sequence[Msg]],
    *,
    model: str,
    temperature: float = 0.7,
    max_output_tokens: Optional[int] = None,
    max_concurrency: int = 8,
    qps: Optional[float] = None,
    max_retries: int = 3,
    timeout: float = 60.0,
    extra: Optional[Dict[str, any]] = None,
) -> List[LLMResponse]:
    client = BatchClient(provider, max_concurrency=max_concurrency, qps=qps, max_retries=max_retries, timeout=timeout)
    return asyncio.run(client.abatch(prompts, model=model, temperature=temperature, max_output_tokens=max_output_tokens, extra=extra))


def run_one(provider: Provider, messages: Sequence[Msg], *, model: str, **kw) -> LLMResponse:
    client = BatchClient(provider)
    return asyncio.run(client.acomplete(messages, model=model, **kw))


def require_json(resp: LLMResponse) -> None:
    """Raise if response.content is not valid JSON."""
    try:
        json.loads(resp.content)
    except Exception as e:
        raise ValueError("response is not valid JSON") from e


if __name__ == "__main__":
    from openai_provider import OpenAIProvider

    async def _demo():
        prov = OpenAIProvider()
        client = BatchClient(prov, max_concurrency=5, qps=2.0)
        prompts = [[Msg.user(f"Respond with the number {i} squared only.")] for i in range(5)]
        res = await client.abatch(prompts, model="gpt-4.1-mini")
        for r in res:
            print(r.content)

    asyncio.run(_demo())
            content = "".join(text_parts).strip()

            usage = Usage(
                input_tokens=(data.get("usage", {}) or {}).get("input_tokens"),
                output_tokens=(data.get("usage", {}) or {}).get("output_tokens"),
                total_tokens=(data.get("usage", {}) or {}).get("total_tokens"),
            )
            return LLMResponse(provider=self.name, model=req.model, content=content, raw=data, usage=usage)
        except httpx.HTTPStatusError as e:
            return LLMResponse(provider=self.name, model=req.model, content="", raw={"error": str(e), "body": getattr(e.response, "text", None)}, error=str(e))
        except Exception as e:
            return LLMResponse(provider=self.name, model=req.model, content="", raw={"error": str(e)}, error=str(e))

############################################################
# Retry & rate limit helpers
############################################################

def _compute_backoff(attempt: int, base: float = 0.5, cap: float = 8.0) -> float:
    """Exponential backoff with jitter."""
    exp = min(cap, base * (2 ** (attempt - 1)))
    jitter = random.uniform(0, exp / 2)
    return exp + jitter


class _TokenBucket:
    """Very simple token bucket for QPS limiting (coarse)."""
    def __init__(self, qps: float):
        self.qps = max(0.1, qps)
        self.capacity = 1.0
        self.tokens = self.capacity
        self.last = time.monotonic()

    async def acquire(self):
        while True:
            now = time.monotonic()
            elapsed = now - self.last
            self.last = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.qps)
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return
            # sleep until a token is likely available
            need = (1.0 - self.tokens) / self.qps
            await asyncio.sleep(max(need, 0.001))


############################################################
# Batch client
############################################################

class BatchClient:
    def __init__(
        self,
        provider: Provider,
        *,
        max_concurrency: int = 8,
        qps: Optional[float] = None,
        max_retries: int = 3,
        timeout: float = 60.0,
        validate: Optional[Callable[[LLMResponse], None]] = None,
    ):
        self.provider = provider
        self.sema = asyncio.Semaphore(max(1, int(max_concurrency)))
        self.bucket = _TokenBucket(qps) if qps else None
        self.max_retries = max_retries
        self.timeout = timeout
        self.validate = validate

    async def _one(self, req: LLMRequest) -> LLMResponse:
        attempt = 1
        while True:
            try:
                async with self.sema:
                    if self.bucket:
                        await self.bucket.acquire()
                    resp = await self.provider.acomplete(req, timeout=self.timeout)
                if self.validate:
                    try:
                        self.validate(resp)
                    except Exception as e:
                        resp.error = f"validation_error: {e}"
                if not resp.error:
                    return resp
                # if provider returned an error, decide whether to retry
                if attempt > self.max_retries:
                    return resp
            except Exception as e:
                if attempt > self.max_retries:
                    return LLMResponse(provider=self.provider.name, model=req.model, content="", raw={"error": str(e)}, error=str(e))
            # backoff
            await asyncio.sleep(_compute_backoff(attempt))
            attempt += 1

    async def abatch(
        self,
        prompts: Sequence[Sequence[Msg]],
        *,
        model: str,
        temperature: float = 0.7,
        max_output_tokens: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> List[LLMResponse]:
        extra = extra or {}
        reqs = [
            LLMRequest(messages=list(msgs), model=model, temperature=temperature, max_output_tokens=max_output_tokens, extra=extra)
            for msgs in prompts
        ]
        return await asyncio.gather(*(self._one(r) for r in reqs))

    async def acomplete(self, messages: Sequence[Msg], *, model: str, **kw) -> LLMResponse:
        req = LLMRequest(messages=list(messages), model=model, **kw)
        return await self._one(req)


############################################################
# Convenience sync wrappers
############################################################

def run_batch(
    provider: Provider,
    prompts: Sequence[Sequence[Msg]],
    *,
    model: str,
    temperature: float = 0.7,
    max_output_tokens: Optional[int] = None,
    max_concurrency: int = 8,
    qps: Optional[float] = None,
    max_retries: int = 3,
    timeout: float = 60.0,
    extra: Optional[Dict[str, Any]] = None,
) -> List[LLMResponse]:
    client = BatchClient(provider, max_concurrency=max_concurrency, qps=qps, max_retries=max_retries, timeout=timeout)
    return asyncio.run(client.abatch(prompts, model=model, temperature=temperature, max_output_tokens=max_output_tokens, extra=extra))


def run_one(provider: Provider, messages: Sequence[Msg], *, model: str, **kw) -> LLMResponse:
    client = BatchClient(provider)
    return asyncio.run(client.acomplete(messages, model=model, **kw))


############################################################
# Example validation hook
############################################################

def require_json(resp: LLMResponse) -> None:
    """Raise if response.content is not valid JSON."""
    try:
        json.loads(resp.content)
    except Exception as e:
        raise ValueError("response is not valid JSON") from e


############################################################
# If run directly, do a tiny smoke test (requires OPENAI_API_KEY)
############################################################

if __name__ == "__main__":
    async def _demo():
        prov = OpenAIProvider()
        client = BatchClient(prov, max_concurrency=5, qps=2.0)
        prompts = [[Msg.user(f"Respond with the number {i} squared only.")] for i in range(5)]
        res = await client.abatch(prompts, model="gpt-4.1-mini")
        for r in res:
            print(r.content)
    asyncio.run(_demo())
