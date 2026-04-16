"""Database session configuration for two async databases.

This module creates async SQLAlchemy engines and session makers for two
databases: the PRICE DB (holds price and financial statements) and the
COMPANY DB (holds other company-related data). It exposes async context
managers `get_price_session()` and `get_company_session()` for individual
database access.

Configures connection pooling optimized for serverless environments:
- Uses NullPool for async engines (per-request connections)
- Implements connection and statement timeouts
- Wraps sessions with retry logic for transient failures
- Sync engines use minimal pooling with connection recycling

Reference: https://activeno.de/blog/2025-06/properly-connecting-with-a-database-on-serverless/
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

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


def _ensure_async_pg(url: str | None) -> str:
    """Ensure the provided PostgreSQL URL uses asyncpg dialect.

    Accepts both `postgresql://` and `postgresql+psycopg2://` forms and
    returns a URL using `postgresql+asyncpg://`. Also removes query parameters
    like sslmode that should be in connect_args for asyncpg.
    """
    if url is None:
        raise ValueError("Database URL cannot be None. Check environment variables.")
    if "?" in url:
        url = url.split("?")[0]

    if "postgresql+asyncpg" in url:
        return url
    if "postgresql+psycopg2" in url:
        return url.replace("postgresql+psycopg2", "postgresql+asyncpg")
    if "postgresql://" in url and "+" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


def _clean_sync_pg(url: str | None) -> str:
    """Clean PostgreSQL URL for psycopg2 by moving query params to connect_args.

    Removes sslmode and other query params that should be in connect_args.
    """
    if url is None:
        raise ValueError("Database URL cannot be None. Check environment variables.")
    if "?" in url:
        url = url.split("?")[0]
    return url


PRICE_DB_URI_ASYNC = _ensure_async_pg(PRICE_DB_URI)
COMPANY_DB_URI_ASYNC = _ensure_async_pg(COMPANY_DB_URI)

# Async engines with NullPool: per-request connections without pooling
# Prevents exhaustion under serverless traffic bursts
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

# Sync engines with NullPool: one direct connection per unit of work
# This avoids process-level pool accumulation under serverless autoscaling.
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
    """Async context manager yielding a price database session with retry logic.

    Wraps session creation with retry mechanism to handle transient connection
    failures in serverless environments where connection limits may be exceeded
    under traffic bursts.

    Usage:
        async with get_price_session() as session:
            result = await session.execute(...)

    Session is committed if the block exits normally, and rolled back on exception.
    """

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
    """Async context manager yielding a company database session with retry logic.

    Wraps session creation with retry mechanism to handle transient connection
    failures in serverless environments where connection limits may be exceeded
    under traffic bursts.

    Usage:
        async with get_company_session() as session:
            result = await session.execute(...)

    Session is committed if the block exits normally, and rolled back on exception.
    """

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
