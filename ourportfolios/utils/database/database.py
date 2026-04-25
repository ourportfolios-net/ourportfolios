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

from ourportfolios.utils.retry import retry_async, retry_sync

load_dotenv()

PRICE_DB_URI = os.getenv("PRICE_DB_URI")
COMPANY_DB_URI = os.getenv("COMPANY_DB_URI")


class MissingDatabaseUrlError(ValueError):
    def __init__(self) -> None:
        super().__init__("Database URL cannot be None.")


def _strip_query_params(url: str) -> str:
    return url.split("?", maxsplit=1)[0] if "?" in url else url


def _ensure_async_pg(url: str | None) -> str:
    if url is None:
        raise MissingDatabaseUrlError

    url = _strip_query_params(url)
    if "postgresql+asyncpg" in url:
        return url
    if "postgresql+psycopg2" in url:
        return url.replace("postgresql+psycopg2", "postgresql+asyncpg")
    if "postgresql://" in url and "+" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


def _clean_sync_pg(url: str | None) -> str:
    if url is None:
        raise MissingDatabaseUrlError
    return _strip_query_params(url)


PRICE_DB_URI_ASYNC = _ensure_async_pg(PRICE_DB_URI)
COMPANY_DB_URI_ASYNC = _ensure_async_pg(COMPANY_DB_URI)

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
    async def commit(self) -> None:
        await retry_async(super().commit)


PriceSession = async_sessionmaker(
    price_engine,
    class_=RetryingAsyncSession,
    expire_on_commit=False,
)

CompanySession = async_sessionmaker(
    company_engine,
    class_=RetryingAsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_price_session() -> AsyncIterator[AsyncSession]:
    session = retry_sync(PriceSession, max_attempts=5, wait_ms=1000)
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
    session = retry_sync(CompanySession, max_attempts=5, wait_ms=1000)
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
