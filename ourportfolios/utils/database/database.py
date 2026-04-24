"""Async/sync SQLAlchemy sessions for PRICE_DB (Neon) and COMPANY_DB (Supabase).

Uses NullPool + retry for serverless-safe connections. COMPANY_DB requires a
Supabase Transaction Pooler URL (port 6543). See also:
https://activeno.de/blog/2025-06/properly-connecting-with-a-database-on-serverless/
"""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

from ..retry import retry_async

load_dotenv()

PRICE_DB_URI = os.getenv("PRICE_DB_URI")
COMPANY_DB_URI = os.getenv("COMPANY_DB_URI")


def _strip_query_params(url: str) -> str:
    """Strip query params from a DB URL (must be passed via connect_args instead)."""
    if "?" in url:
        url = url.split("?")[0]
    return url


def _ensure_async_pg(url: str | None) -> str:
    """Normalise a PostgreSQL URL to use the asyncpg dialect and strip query params."""
    if url is None:
        raise ValueError("Database URL cannot be None. Check environment variables.")
    url = _strip_query_params(url)

    if "postgresql+asyncpg" in url:
        return url
    if "postgresql+psycopg2" in url:
        return url.replace("postgresql+psycopg2", "postgresql+asyncpg")
    if "postgresql://" in url and "+" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


def _clean_sync_pg(url: str | None) -> str:
    """Strip query params from a PostgreSQL URL for psycopg2 (pass via connect_args)."""
    if url is None:
        raise ValueError("Database URL cannot be None. Check environment variables.")
    return _strip_query_params(url)


PRICE_DB_URI_ASYNC = _ensure_async_pg(PRICE_DB_URI)
COMPANY_DB_URI_ASYNC = _ensure_async_pg(COMPANY_DB_URI)

# NullPool: one connection per request; statement_cache_size=0 required for pgbouncer transaction mode
price_engine = create_async_engine(
    PRICE_DB_URI_ASYNC,
    poolclass=NullPool,
    connect_args={
        "server_settings": {"jit": "off"},
        "timeout": 10,
        "command_timeout": 20,
        "statement_cache_size": 0,
    },
)
company_engine = create_async_engine(
    COMPANY_DB_URI_ASYNC,
    poolclass=NullPool,
    connect_args={
        "server_settings": {"jit": "off"},
        "timeout": 10,
        "command_timeout": 20,
        "statement_cache_size": 0,
    },
)

price_sync_engine = create_engine(
    _clean_sync_pg(PRICE_DB_URI),
    poolclass=NullPool,
    connect_args={"sslmode": "require", "connect_timeout": 10},
)
company_sync_engine = create_engine(
    _clean_sync_pg(COMPANY_DB_URI),
    poolclass=NullPool,
    connect_args={"sslmode": "require", "connect_timeout": 10},
)


class RetryingAsyncSession(AsyncSession):
    """Async session with retry wrappers for transient serverless DB failures."""

    async def execute(self, *args, **kwargs):
        return await retry_async(
            lambda: super(RetryingAsyncSession, self).execute(*args, **kwargs)
        )

    async def scalar(self, *args, **kwargs):
        return await retry_async(
            lambda: super(RetryingAsyncSession, self).scalar(*args, **kwargs)
        )

    async def scalars(self, *args, **kwargs):
        return await retry_async(
            lambda: super(RetryingAsyncSession, self).scalars(*args, **kwargs)
        )

    async def commit(self):
        return await retry_async(lambda: super(RetryingAsyncSession, self).commit())


class RetryingAsyncSession(AsyncSession):
    """Async session with retry wrappers for transient serverless DB failures."""

    async def execute(self, *args, **kwargs):
        return await retry_async(
            lambda: super(RetryingAsyncSession, self).execute(*args, **kwargs)
        )

    async def scalar(self, *args, **kwargs):
        return await retry_async(
            lambda: super(RetryingAsyncSession, self).scalar(*args, **kwargs)
        )

    async def scalars(self, *args, **kwargs):
        return await retry_async(
            lambda: super(RetryingAsyncSession, self).scalars(*args, **kwargs)
        )

    async def commit(self):
        return await retry_async(lambda: super(RetryingAsyncSession, self).commit())


PriceSession = async_sessionmaker(
    price_engine,
    class_=RetryingAsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

CompanySession = async_sessionmaker(
    company_engine,
    class_=RetryingAsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_price_session() -> AsyncIterator[AsyncSession]:
    """Yield a price DB session; commits on success, rolls back on error."""

    async def _get_session() -> AsyncSession:
        return PriceSession()

    session = await retry_async(_get_session, max_attempts=5, wait_ms=1000)
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


@asynccontextmanager
async def get_company_session() -> AsyncIterator[AsyncSession]:
    """Yield a company DB session; commits on success, rolls back on error."""

    async def _get_session() -> AsyncSession:
        return CompanySession()

    session = await retry_async(_get_session, max_attempts=5, wait_ms=1000)
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
