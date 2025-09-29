from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from usage import Usage

@dataclass
class LLMResponse:
    provider: str
    model: str
    content: str
    raw: Dict[str, Any]
    usage: Usage = field(default_factory=Usage)
    error: Optional[str] = None
