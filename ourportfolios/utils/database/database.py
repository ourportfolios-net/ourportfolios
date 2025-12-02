"""Database session configuration for two async databases.

This module creates async SQLAlchemy engines and session makers for two
databases: the PRICE DB (holds price and financial statements) and the
COMPANY DB (holds other company-related data). It exposes async context
managers `get_price_session()` and `get_company_session()` for individual
database access.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from dotenv import load_dotenv

load_dotenv()

PRICE_DB_URI = os.getenv("PRICE_DB_URI")
COMPANY_DB_URI = os.getenv("COMPANY_DB_URI")


def _ensure_async_pg(url: str | None) -> str:
    """Ensure the provided PostgreSQL URL uses asyncpg dialect.

    Accepts both `postgresql://` and `postgresql+psycopg2://` forms and
    returns a URL using `postgresql+asyncpg://`.
    """
    if url is None:
        raise ValueError("Database URL cannot be None. Check environment variables.")
    if "postgresql+asyncpg" in url:
        return url
    if "postgresql+psycopg2" in url:
        return url.replace("postgresql+psycopg2", "postgresql+asyncpg")
    if "postgresql://" in url and "+" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


PRICE_DB_URI_ASYNC = _ensure_async_pg(PRICE_DB_URI)
COMPANY_DB_URI_ASYNC = _ensure_async_pg(COMPANY_DB_URI)

price_engine = create_async_engine(PRICE_DB_URI_ASYNC)
company_engine = create_async_engine(COMPANY_DB_URI_ASYNC)


PriceSession = async_sessionmaker(
    price_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

CompanySession = async_sessionmaker(
    company_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_price_session() -> AsyncIterator[AsyncSession]:
    """Async context manager yielding a price database session.

    Usage:
        async with get_price_session() as session:
            result = await session.execute(...)

    Session is committed if the block exits normally, and rolled back on exception.
    """
    async with PriceSession() as session:
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
    """Async context manager yielding a company database session.

    Usage:
        async with get_company_session() as session:
            result = await session.execute(...)

    Session is committed if the block exits normally, and rolled back on exception.
    """
    async with CompanySession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
