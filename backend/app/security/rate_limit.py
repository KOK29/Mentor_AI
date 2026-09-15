from __future__ import annotations
from collections import defaultdict, deque
from time import time


class InMemoryRateLimiter:
    """Simple in-memory rate limiter for dev and tests. Not a DB-backed solution."""

    def __init__(self, limit_per_minute: int = 60) -> None:
        self.limit_per_minute = limit_per_minute
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time()
        bucket = self._requests[key]
        window_start = now - 60
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= self.limit_per_minute:
            return False
        bucket.append(now)
        return True
