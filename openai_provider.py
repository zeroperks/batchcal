from __future__ import annotations
import os
from typing import Any, Dict, List, Optional
import httpx
from provider import Provider
from llm_request import LLMRequest
from llm_response import LLMResponse
from usage import Usage

class OpenAIProvider(Provider):
    name = "openai"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=None,
        )

    async def acomplete(self, req: LLMRequest, *, timeout: float = 60.0) -> LLMResponse:
        payload: Dict[str, Any] = {
            "model": req.model,
            "input": [{"role": m.role, "content": m.content} for m in req.messages],
            "temperature": req.temperature,
        }
        if req.max_output_tokens is not None:
            payload["max_output_tokens"] = req.max_output_tokens
        payload.update(req.extra)
        try:
            r = await self._client.post("/responses", json=payload, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            text_parts: List[str] = []
            for out in data.get("output", []):
                if out.get("type") == "message":
                    for c in out["content"]:
                        if c.get("type") == "output_text":
                            text_parts.append(c.get("text", ""))
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
