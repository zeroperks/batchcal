from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

Role = Literal["system", "user", "assistant"]

@dataclass
class Msg:
    role: Role
    content: str

    @staticmethod
    def system(text: str) -> "Msg":
        return Msg("system", text)

    @staticmethod
    def user(text: str) -> "Msg":
        return Msg("user", text)

    @staticmethod
    def assistant(text: str) -> "Msg":
        return Msg("assistant", text)
