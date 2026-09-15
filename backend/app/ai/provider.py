from __future__ import annotations
from typing import Protocol, Any


class AIProvider(Protocol):
    async def generate(self, prompt: str, *, model: str | None = None) -> Any:
        ...
