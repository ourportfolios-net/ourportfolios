"""Shared SQLAlchemy ORM models."""

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class OverviewORM(Base):
    __tablename__ = "overview_df"
    __table_args__ = {"schema": "tickers"}

    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    industry: Mapped[Optional[str]] = mapped_column(String)
    market_cap: Mapped[Optional[float]] = mapped_column(Float)
    exchange: Mapped[Optional[str]] = mapped_column(String)


class PriceORM(Base):
    __tablename__ = "price_df"
    __table_args__ = {"schema": "tickers"}

    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    pct_price_change: Mapped[Optional[float]] = mapped_column(Float)
    accumulated_volume: Mapped[Optional[float]] = mapped_column(Float)
    current_price: Mapped[Optional[float]] = mapped_column(Float)


class ProfileORM(Base):
    __tablename__ = "profile_df"
    __table_args__ = {"schema": "tickers"}

    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    company_name: Mapped[Optional[str]] = mapped_column(String)


class StatsORM(Base):
    __tablename__ = "stats_df"
    __table_args__ = {"schema": "tickers"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    symbol: Mapped[Optional[str]] = mapped_column(String)
    roe: Mapped[Optional[float]] = mapped_column(Float)
    roa: Mapped[Optional[float]] = mapped_column(Float)
    ev_ebitda: Mapped[Optional[float]] = mapped_column(Float)
    dividend_yield: Mapped[Optional[float]] = mapped_column(Float)
    gross_margin: Mapped[Optional[float]] = mapped_column(Float)
    net_margin: Mapped[Optional[float]] = mapped_column(Float)
    doe: Mapped[Optional[float]] = mapped_column(Float)
    alpha: Mapped[Optional[float]] = mapped_column(Float)
    beta: Mapped[Optional[float]] = mapped_column(Float)
    pe: Mapped[Optional[float]] = mapped_column(Float)
    pb: Mapped[Optional[float]] = mapped_column(Float)
    eps: Mapped[Optional[int]] = mapped_column(BigInteger)
    ps: Mapped[Optional[float]] = mapped_column(Float)
    ev: Mapped[Optional[float]] = mapped_column(Float)
    rsi14: Mapped[Optional[float]] = mapped_column(Float)


class VNIndexORM(Base):
    __tablename__ = "vnindex"
    __table_args__ = {"schema": "market"}

    time: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    close: Mapped[Optional[float]] = mapped_column(Float)


class FrameworkORM(Base):
    __tablename__ = "frameworks_df"
    __table_args__ = {"schema": "frameworks"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    author: Mapped[Optional[str]] = mapped_column(Text)
    complexity: Mapped[Optional[str]] = mapped_column(Text)
    scope: Mapped[Optional[str]] = mapped_column(Text)
    source_name: Mapped[Optional[str]] = mapped_column(String(255))
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    metrics: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    framework_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), unique=True, default=uuid.uuid4
    )

    metric_rows: Mapped[list["FrameworkMetricsORM"]] = relationship(
        back_populates="framework",
        primaryjoin="FrameworkORM.framework_id == FrameworkMetricsORM.framework_uuid",
        foreign_keys="[FrameworkMetricsORM.framework_uuid]",
        lazy="selectin",
    )


class FrameworkMetricsORM(Base):
    __tablename__ = "framework_metrics_df"
    __table_args__ = {"schema": "frameworks"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    metrics: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    display_order: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    framework_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("frameworks.frameworks_df.framework_id", ondelete="CASCADE"),
        nullable=False,
    )

    framework: Mapped["FrameworkORM"] = relationship(
        back_populates="metric_rows",
        primaryjoin="FrameworkMetricsORM.framework_uuid == FrameworkORM.framework_id",
        foreign_keys="[FrameworkMetricsORM.framework_uuid]",
    )
