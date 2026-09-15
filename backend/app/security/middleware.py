from __future__ import annotations
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .rate_limit import InMemoryRateLimiter

rate_limiter = InMemoryRateLimiter(limit_per_minute=120)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "anonymous"
        if not rate_limiter.allow(client_ip):
            return JSONResponse({"detail": "Too many requests"}, status_code=429)
        return await call_next(request)
