"""bcrypt-backed password hasher satisfying the ``PasswordHasher`` protocol.

Uses the ``bcrypt`` package directly (avoids passlib/bcrypt 4.x incompatibility).
Passwords are SHA-256-prehashed before bcrypt so there is no 72-byte truncation.
"""
from __future__ import annotations

import hashlib
import hmac

import bcrypt


def _prehash(password: str) -> bytes:
    """SHA-256 pre-hash so passwords > 72 bytes are handled correctly."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("ascii")


class BcryptPasswordHasher:
    """Production password hasher using bcrypt.

    Drop-in replacement for ``InMemoryPasswordHasher`` — satisfies the same
    ``PasswordHasher`` protocol without any interface changes.
    """

    def hash_password(self, password: str) -> str:
        hashed = bcrypt.hashpw(_prehash(password), bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(_prehash(password), hashed.encode("utf-8"))
        except Exception:
            return False
