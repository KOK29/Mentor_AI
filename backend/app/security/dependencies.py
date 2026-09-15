"""FastAPI dependencies for JWT-based authentication.

Usage
-----
    from .security.dependencies import get_current_user

    @app.get("/api/v1/protected")
    async def protected_route(current_user: str = Depends(get_current_user)):
        return {"user": current_user}

The dependency extracts the bearer token from the ``Authorization`` header,
validates it against ``JWTTokenService``, and returns the subject (username).
Raises HTTP 401 if the token is missing, malformed, or expired.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .jwt_token_service import JWTTokenService

_bearer = HTTPBearer(auto_error=False)
_token_service = JWTTokenService()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    """Return the authenticated username, or raise 401.

    Parameters
    ----------
    credentials:
        Extracted by FastAPI's ``HTTPBearer`` scheme from the
        ``Authorization: Bearer <token>`` request header.
        ``auto_error=False`` means FastAPI won't raise automatically —
        we do it ourselves so the error body matches our schema.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = _token_service.validate_access_token(credentials.credentials)
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return subject
