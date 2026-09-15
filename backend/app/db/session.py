"""Async SQLAlchemy engine, session factory, and FastAPI dependency.

Configuration
-------------
DATABASE_URL env var (default: ``sqlite+aiosqlite:///./mentor_slm.db``).

Usage in route handlers
-----------------------
    async def my_route(db: AsyncSession = Depends(get_db)):
        ...

Startup
-------
Call ``await init_db()`` once on application startup to create all tables.
"""
from __future__ import annotations

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .models import Base

_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./mentor_slm.db",
)

# echo=False in production; set env var SQLALCHEMY_ECHO=1 for debug SQL logging
_echo = os.getenv("SQLALCHEMY_ECHO", "0") == "1"

def _sqlite_connect_args(url: str) -> dict:
    if "sqlite" not in url:
        return {}
    args: dict = {"check_same_thread": False}
    if "uri=true" in url:
        args["uri"] = True
    return args


_engine = create_async_engine(
    _DATABASE_URL,
    echo=_echo,
    connect_args=_sqlite_connect_args(_DATABASE_URL),
)

_async_session_factory = async_sessionmaker(
    _engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Create all tables (idempotent — safe to call on every startup)."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an ``AsyncSession`` per request."""
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the shared session factory (useful for tests that need custom sessions)."""
    return _async_session_factory
