"""ProgressRepository structural protocol.

Any class with matching method signatures satisfies this protocol —
no inheritance required (duck-typed).
"""
from __future__ import annotations

from typing import Any, Optional, Protocol


class ProgressRepository(Protocol):
    async def record(self, payload: dict) -> dict:
        ...

    async def get_summary(self, user_id: Optional[str] = None) -> dict:
        ...

    async def get_profile(self, user_id: str) -> dict[str, Any]:
        ...
