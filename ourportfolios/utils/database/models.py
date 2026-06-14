"""Shared SQLAlchemy ORM models."""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class OverviewORM(Base):
    __tablename__ = "overview_df"
    __table_args__ = ({"schema": "tickers"},)

    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    industry: Mapped[str | None] = mapped_column(String)
    market_cap: Mapped[float | None] = mapped_column(Float)
    exchange: Mapped[str | None] = mapped_column(String)


class PriceORM(Base):
    __tablename__ = "price_df"
    __table_args__ = ({"schema": "tickers"},)

    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    pct_price_change: Mapped[float | None] = mapped_column(Float)
    accumulated_volume: Mapped[float | None] = mapped_column(Float)
    current_price: Mapped[float | None] = mapped_column(Float)


class ProfileORM(Base):
    __tablename__ = "profile_df"
    __table_args__ = ({"schema": "tickers"},)

    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    company_name: Mapped[str | None] = mapped_column(String)


class StatsORM(Base):
    __tablename__ = "stats_df"
    __table_args__ = ({"schema": "tickers"},)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    symbol: Mapped[str | None] = mapped_column(String)
    roe: Mapped[float | None] = mapped_column(Float)
    roa: Mapped[float | None] = mapped_column(Float)
    ev_ebitda: Mapped[float | None] = mapped_column(Float)
    dividend_yield: Mapped[float | None] = mapped_column(Float)
    gross_margin: Mapped[float | None] = mapped_column(Float)
    net_margin: Mapped[float | None] = mapped_column(Float)
    doe: Mapped[float | None] = mapped_column(Float)
    alpha: Mapped[float | None] = mapped_column(Float)
    beta: Mapped[float | None] = mapped_column(Float)
    pe: Mapped[float | None] = mapped_column(Float)
    pb: Mapped[float | None] = mapped_column(Float)
    eps: Mapped[int | None] = mapped_column(BigInteger)
    ps: Mapped[float | None] = mapped_column(Float)
    ev: Mapped[float | None] = mapped_column(Float)
    rsi14: Mapped[float | None] = mapped_column(Float)


class VNIndexORM(Base):
    __tablename__ = "vnindex"
    __table_args__ = ({"schema": "market"},)

    time: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    close: Mapped[float | None] = mapped_column(Float)


class FrameworkORM(Base):
    __tablename__ = "frameworks_df"
    __table_args__ = ({"schema": "frameworks"},)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(Text)
    complexity: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[str | None] = mapped_column(Text)
    source_name: Mapped[str | None] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(String(100))
    metrics: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    framework_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        default=uuid.uuid4,
    )

    metric_rows: Mapped[list["FrameworkMetricsORM"]] = relationship(
        back_populates="framework",
        primaryjoin="FrameworkORM.framework_id == FrameworkMetricsORM.framework_uuid",
        foreign_keys="[FrameworkMetricsORM.framework_uuid]",
        lazy="selectin",
    )


class FrameworkMetricsORM(Base):
    __tablename__ = "framework_metrics_df"
    __table_args__ = ({"schema": "frameworks"},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    metrics: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    display_order: Mapped[int | None] = mapped_column(Integer, default=0)
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


class ContactSubmissionORM(Base):
    __tablename__ = "contact_submissions"
    __table_args__ = ({"schema": "public"},)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now,
    )
    is_resolved: Mapped[bool] = mapped_column(default=False)
