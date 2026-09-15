"""JWT token service satisfying the ``TokenService`` protocol.

Secret resolution order
-----------------------
1. ``JWT_SECRET_FILE`` env var → read file contents (Docker secrets mount).
2. ``JWT_SECRET`` env var → use directly.
3. Fallback to a hard-coded dev-only sentinel (raises on production if missing).

Algorithm: HS256 (HMAC-SHA256).
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

# ---------------------------------------------------------------------------
# Secret resolution
# ---------------------------------------------------------------------------

def _load_secret() -> str:
    secret_file = os.getenv("JWT_SECRET_FILE")
    if secret_file:
        try:
            with open(secret_file, "r", encoding="utf-8") as fh:
                secret = fh.read().strip()
            if secret:
                return secret
        except OSError:
            pass  # fall through to env var

    secret = os.getenv("JWT_SECRET", "").strip()
    if secret:
        return secret

    # Dev-only fallback — non-empty so the app starts, but clearly unusable in prod
    return "INSECURE-DEV-ONLY-SECRET-CHANGE-ME"


_ALGORITHM = "HS256"
_ACCESS_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "900"))   # 15 min
_REFRESH_EXPIRE_SECONDS = int(os.getenv("REFRESH_TOKEN_EXPIRE_SECONDS", "1209600"))  # 14 days


class JWTTokenService:
    """Real JWT token service using python-jose.

    Drop-in replacement for ``InMemoryTokenService`` — satisfies the same
    ``TokenService`` protocol.

    Parameters
    ----------
    access_expire_seconds, refresh_expire_seconds:
        Override the env-var-based defaults (useful in tests).
    """

    def __init__(
        self,
        *,
        access_expire_seconds: int | None = None,
        refresh_expire_seconds: int | None = None,
    ) -> None:
        self._secret = _load_secret()
        self._access_expire = access_expire_seconds if access_expire_seconds is not None else _ACCESS_EXPIRE_SECONDS
        self._refresh_expire = refresh_expire_seconds if refresh_expire_seconds is not None else _REFRESH_EXPIRE_SECONDS

    # ------------------------------------------------------------------
    # TokenService protocol
    # ------------------------------------------------------------------

    def create_access_token(self, subject: str) -> str:
        return self._encode(subject, self._access_expire, token_type="access")

    def create_refresh_token(self, subject: str) -> str:
        return self._encode(subject, self._refresh_expire, token_type="refresh")

    def validate_access_token(self, token: str) -> Optional[str]:
        """Return the subject (username) if the token is valid, else None."""
        try:
            payload = jwt.decode(token, self._secret, algorithms=[_ALGORITHM])
            if payload.get("type") != "access":
                return None
            return payload.get("sub")
        except JWTError:
            return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _encode(self, subject: str, expire_seconds: int, *, token_type: str) -> str:
        now = datetime.now(timezone.utc)
        claims = {
            "sub": subject,
            "type": token_type,
            "iat": now,
            "exp": now + timedelta(seconds=expire_seconds),
        }
        return jwt.encode(claims, self._secret, algorithm=_ALGORITHM)
