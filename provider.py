from __future__ import annotations
from typing import Protocol
from llm_request import LLMRequest
from llm_response import LLMResponse

class Provider(Protocol):
    name: str
    async def acomplete(self, req: LLMRequest, *, timeout: float = 60.0) -> LLMResponse: ...
