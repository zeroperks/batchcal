from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class Usage:
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
