from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from msg import Msg

@dataclass
class LLMRequest:
    messages: List[Msg]
    model: str
    temperature: float = 0.7
    max_output_tokens: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)
