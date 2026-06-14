"""State management for framework recommendation page."""

import uuid
from collections.abc import AsyncGenerator

import reflex as rx
from pydantic import BaseModel, Field
from reflex.event import EventSpec
from sqlalchemy import BigInteger, Integer, String, Text, select
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    selectinload,
)

from ourportfolios.state import GlobalFrameworkState
from ourportfolios.utils.database.database import get_company_session
from ourportfolios.utils.session_manager import SessionIsolatedStateMixin


class Base(DeclarativeBase):
    pass


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
        nullable=False,
    )

    framework: Mapped["FrameworkORM"] = relationship(
        back_populates="metric_rows",
        primaryjoin="FrameworkMetricsORM.framework_uuid == FrameworkORM.framework_id",
        foreign_keys="[FrameworkMetricsORM.framework_uuid]",
    )


class FrameworkModel(BaseModel):
    id: int
    title: str
    description: str = ""
    author: str = ""
    complexity: str = "beginner-friendly"
    scope: str = "fundamental"
    industry: str = "general"
    source_name: str | None = None
    source_url: str | None = None
    framework_uuid: str = ""
    metrics: list[dict[str, object]] = Field(default_factory=list)


class ScopeModel(BaseModel):
    value: str
    title: str


class CategoryModel(BaseModel):
    value: str
    label: str


class TickerModel(BaseModel):
    symbol: str
    name: str = ""


class MetricModel(BaseModel):
    name: str
    category: str
    enabled: bool = True
    order: int = 0


def _orm_to_framework_model(row: FrameworkORM) -> FrameworkModel:
    metrics: list[dict[str, object]] = [
        {"name": name, "type": mr.category, "order": mr.display_order}
        for mr in sorted(row.metric_rows or [], key=lambda m: m.display_order or 0)
        for name in mr.metrics
    ]
    return FrameworkModel(
        id=row.id,
        title=row.title or "",
        description=row.description or "",
        author=row.author or "",
        complexity=row.complexity or "beginner-friendly",
        scope=row.scope or "fundamental",
        industry=row.industry or "general",
        source_name=row.source_name,
        source_url=row.source_url,
        framework_uuid=str(row.framework_id) if row.framework_id else "",
        metrics=metrics,
    )


class FrameworkState(SessionIsolatedStateMixin, rx.State):
    active_scope: str = "fundamental"
    active_category: str = "all"
    scopes: rx.Field[list[ScopeModel]] = rx.field(
        default_factory=lambda: [
            ScopeModel(value="fundamental", title="Fundamental"),
            ScopeModel(value="technical", title="Technical"),
        ],
    )

    # Private — not serialized to frontend.

    _all_frameworks: list[FrameworkModel] = Field(default_factory=list)

    frameworks: rx.Field[list[FrameworkModel]] = rx.field(default_factory=list)

    loading_frameworks: rx.Field[bool] = rx.field(default=False)

    selected_framework: rx.Field[FrameworkModel] = rx.field(
        default_factory=lambda: FrameworkModel(
            id=0,
            title="",
            description="",
            author="",
        ),
    )
    show_dialog: rx.Field[bool] = rx.field(default=False)
    show_add_dialog: rx.Field[bool] = rx.field(default=False)

    search_query: rx.Field[str] = rx.field(default="")

    ticker_cart: rx.Field[list[TickerModel]] = rx.field(default_factory=list)

    categories: rx.Field[list[CategoryModel]] = rx.field(
        default_factory=lambda: [
            CategoryModel(value="all", label="All"),
            CategoryModel(value="fundamental", label="Fundamentals"),
            CategoryModel(value="technical", label="Technical"),
            CategoryModel(value="beginner-friendly", label="Beginner-Friendly"),
            CategoryModel(value="complex", label="Complex"),
        ],
    )

    form_title: rx.Field[str] = rx.field(default="")
    form_description: rx.Field[str] = rx.field(default="")
    form_author: rx.Field[str] = rx.field(default="")
    form_complexity: rx.Field[str] = rx.field(default="beginner-friendly")
    form_scope: rx.Field[str] = rx.field(default="fundamental")
    form_industry: rx.Field[str] = rx.field(default="general")
    form_source_name: rx.Field[str] = rx.field(default="")
    form_source_url: rx.Field[str] = rx.field(default="")
    form_errors: rx.Field[dict[str, str]] = rx.field(default_factory=dict)

    form_metrics: rx.Field[list[MetricModel]] = rx.field(default_factory=list)
    hovered_metric_index: rx.Field[int] = rx.field(default=-1)

    available_categories: rx.Field[list[str]] = rx.field(
        default_factory=lambda: [
            "Per Share Value",
            "Growth Rate",
            "Profitability",
            "Valuation",
            "Leverage & Liquidity",
            "Efficiency",
        ],
    )

    per_share_metrics: rx.Field[list[str]] = rx.field(
        default_factory=lambda: [
            "Earnings",
            "Book Value",
            "Free Cash Flow",
            "Dividend",
            "Revenues",
        ],
    )
    growth_rate_metrics: rx.Field[list[str]] = rx.field(
        default_factory=lambda: [
            "Revenues YoY",
            "Earnings YoY",
            "Free Cash Flow YoY",
            "Book Value YoY",
        ],
    )
    profitability_metrics: rx.Field[list[str]] = rx.field(
        default_factory=lambda: [
            "ROE",
            "ROIC",
            "Net Margin",
            "Gross Margin",
            "Operating Margin",
            "EBITDA Margin",
        ],
    )
    valuation_metrics: rx.Field[list[str]] = rx.field(
        default_factory=lambda: ["P/E", "P/B", "P/S", "EV/EBITDA"],
    )
    leverage_liquidity_metrics: rx.Field[list[str]] = rx.field(
        default_factory=lambda: [
            "Debt/Equity",
            "Current Ratio",
            "Quick Ratio",
            "Interest Coverage",
            "Cash Ratio",
        ],
    )
    efficiency_metrics: rx.Field[list[str]] = rx.field(
        default_factory=lambda: ["ROA", "Asset Turnover", "Dividend Payout %"],
    )

    show_add_metric_dialog: rx.Field[bool] = rx.field(default=False)
    new_metric_name: rx.Field[str] = rx.field(default="")
    new_metric_category: rx.Field[str] = rx.field(default="Per Share Value")

    @rx.var
    def metrics_count(self) -> int:
        return len(self.form_metrics)

    @rx.var
    def ticker_cart_count(self) -> int:
        return len(self.ticker_cart)

    @rx.var
    def selected_framework_has_metrics(self) -> bool:
        return len(self.selected_framework.metrics) > 0

    def _apply_filters(self) -> None:
        results = self._all_frameworks
        if self.search_query.strip():
            q = self.search_query.strip().lower()
            results = [
                f for f in results if q in f.title.lower() or q in f.description.lower()
            ]
        if self.active_category == "fundamental":
            results = [f for f in results if f.scope == "fundamental"]
        elif self.active_category == "technical":
            results = [f for f in results if f.scope == "technical"]
        elif self.active_category == "beginner-friendly":
            results = [f for f in results if f.complexity == "beginner-friendly"]
        elif self.active_category == "complex":
            results = [f for f in results if f.complexity == "complex"]
        self.frameworks = results

    # ---------------------------------------------------------------------------
    # Simple setters
    # ---------------------------------------------------------------------------

    @rx.event
    def set_form_title(self, value: str) -> None:
        self.form_title = value

    @rx.event
    def set_form_description(self, value: str) -> None:
        self.form_description = value

    @rx.event
    def set_form_author(self, value: str) -> None:
        self.form_author = value

    @rx.event
    def set_form_complexity(self, value: str) -> None:
        self.form_complexity = value

    @rx.event
    def set_form_scope(self, value: str) -> None:
        self.form_scope = value

    @rx.event
    def set_form_industry(self, value: str) -> None:
        self.form_industry = value

    @rx.event
    def set_form_source_name(self, value: str) -> None:
        self.form_source_name = value

    @rx.event
    def set_form_source_url(self, value: str) -> None:
        self.form_source_url = value

    @rx.event
    def set_new_metric_name(self, value: str) -> None:
        self.new_metric_name = value

    @rx.event
    def set_new_metric_category(self, value: str) -> None:
        self.new_metric_category = value

    @rx.event
    def set_active_category(self, category: str) -> None:
        self.active_category = category
        self._apply_filters()

    @rx.event
    def set_search_query(self, query: str) -> None:
        self.search_query = query
        self._apply_filters()

    @rx.event
    def add_to_cart(self, ticker: TickerModel) -> None:
        if not any(t.symbol == ticker.symbol for t in self.ticker_cart):
            self.ticker_cart.append(ticker)

    @rx.event
    def remove_from_cart(self, symbol: str) -> None:
        self.ticker_cart = [t for t in self.ticker_cart if t.symbol != symbol]

    @rx.event
    def navigate_to_compare(self) -> rx.event.EventSpec:
        return rx.redirect("/select")

    @rx.event
    def add_metric_to_form(self) -> None:
        if not self.new_metric_name:
            return
        if any(m.name == self.new_metric_name for m in self.form_metrics):
            return
        self.form_metrics.append(
            MetricModel(
                name=self.new_metric_name,
                category=self.new_metric_category,
                enabled=True,
                order=len(self.form_metrics),
            ),
        )
        self.new_metric_name = ""
        self.show_add_metric_dialog = False

    @rx.event
    def remove_metric(self, metric_name: str) -> None:
        self.form_metrics = [m for m in self.form_metrics if m.name != metric_name]
        for i, metric in enumerate(self.form_metrics):
            metric.order = i

    @rx.event
    def toggle_metric_enabled(self, metric_name: str) -> None:
        for metric in self.form_metrics:
            if metric.name == metric_name:
                metric.enabled = not metric.enabled
                break

    @rx.event
    def move_metric_up(self, metric_name: str) -> None:
        for i, metric in enumerate(self.form_metrics):
            if metric.name == metric_name and i > 0:
                self.form_metrics[i], self.form_metrics[i - 1] = (
                    self.form_metrics[i - 1],
                    self.form_metrics[i],
                )
                self.form_metrics[i].order = i
                self.form_metrics[i - 1].order = i - 1
                break

    @rx.event
    def move_metric_down(self, metric_name: str) -> None:
        for i, metric in enumerate(self.form_metrics):
            if metric.name == metric_name and i < len(self.form_metrics) - 1:
                self.form_metrics[i], self.form_metrics[i + 1] = (
                    self.form_metrics[i + 1],
                    self.form_metrics[i],
                )
                self.form_metrics[i].order = i
                self.form_metrics[i + 1].order = i + 1
                break

    @rx.event
    def open_add_metric_dialog(self) -> None:
        self.show_add_metric_dialog = True
        self.new_metric_name = ""

    @rx.event
    def close_add_metric_dialog(self) -> None:
        self.show_add_metric_dialog = False

    @rx.event
    def handle_add_metric_dialog_open(self, *, value: bool) -> None:
        if not value:
            self.close_add_metric_dialog()

    @rx.event
    def set_hovered_metric_index(self, i: int) -> None:
        self.hovered_metric_index = i

    # ---------------------------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------------------------

    def on_mount(self) -> EventSpec | None:  # type: ignore[override]
        super().on_mount()
        return FrameworkState.load_all_frameworks  # type: ignore[return-value]

    def on_unmount(self) -> None:
        super().on_unmount()

    # ---------------------------------------------------------------------------
    # Loading — no session_isolated, no is_mounted() gate
    # ---------------------------------------------------------------------------

    async def _fetch_frameworks(self) -> None:
        """Shared DB fetch: load all frameworks and apply current filters."""
        async with get_company_session() as session:
            stmt = (
                select(FrameworkORM)
                .options(selectinload(FrameworkORM.metric_rows))
                .order_by(FrameworkORM.title)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()

        models = [_orm_to_framework_model(r) for r in rows]
        async with self:
            self._all_frameworks = models
            self._apply_filters()

    @rx.event(background=True)
    async def load_all_frameworks(self) -> None:
        """Background event: fetch every framework and apply current filters.

        Loading ALL rows (no scope filter) so client-side category filtering
        works correctly across scopes without re-fetching from the DB.
        """
        async with self:
            self.loading_frameworks = True

        try:
            await self._fetch_frameworks()
        except (SQLAlchemyError, RuntimeError, ValueError):
            async with self:
                self._all_frameworks = []
                self.frameworks = []
        finally:
            async with self:
                self.loading_frameworks = False

    # ---------------------------------------------------------------------------
    # Dialogs
    # ---------------------------------------------------------------------------

    @rx.event
    def show_framework_dialog(self, framework: FrameworkModel) -> None:
        self.selected_framework = framework
        self.show_dialog = True

    @rx.event
    def close_dialog(self) -> None:
        self.show_dialog = False
        self.selected_framework = FrameworkModel(
            id=0,
            title="",
            description="",
            author="",
        )

    @rx.event
    def handle_dialog_open(self, *, value: bool) -> None:
        if not value:
            self.close_dialog()

    @rx.event
    def open_add_dialog(self) -> None:
        self.form_scope = self.active_scope or "fundamental"
        self.form_title = ""
        self.form_description = ""
        self.form_author = ""
        self.form_complexity = "beginner-friendly"
        self.form_industry = "general"
        self.form_source_name = ""
        self.form_source_url = ""
        self.form_metrics = []
        self.form_errors = {}
        self.show_add_dialog = True

    @rx.event
    def close_add_dialog(self) -> None:
        self.show_add_dialog = False

    @rx.event
    def handle_add_dialog_open(self, *, value: bool) -> None:
        if not value:
            self.close_add_dialog()

    # ---------------------------------------------------------------------------
    # Submission
    # ---------------------------------------------------------------------------

    @rx.event(background=True)
    async def submit_framework(self) -> AsyncGenerator[EventSpec]:
        async with self:
            errors: dict[str, str] = {}
            if not self.form_title.strip():
                errors["title"] = "Title is required"
            if not self.form_author.strip():
                errors["author"] = "Author is required"
            if errors:
                self.form_errors = errors
                return
            self.form_errors = {}

            title = self.form_title
            description = self.form_description
            author = self.form_author
            complexity = self.form_complexity
            scope = self.form_scope
            industry = self.form_industry
            source_name = self.form_source_name or None
            source_url = self.form_source_url or None
            metrics = list(self.form_metrics)

        try:
            async with get_company_session() as session:
                new_uuid = uuid.uuid4()
                framework = FrameworkORM(
                    title=title,
                    description=description,
                    author=author,
                    complexity=complexity,
                    scope=scope,
                    industry=industry,
                    source_name=source_name,
                    source_url=source_url,
                    framework_id=new_uuid,
                )
                session.add(framework)
                await session.flush()

                for metric in metrics:
                    session.add(
                        FrameworkMetricsORM(
                            framework_uuid=new_uuid,
                            category=metric.category,
                            metrics=[metric.name],
                            display_order=metric.order,
                        ),
                    )

                await session.commit()

            async with self:
                self.show_add_dialog = False
                self.active_scope = scope

            # Re-fetch everything so the new framework appears immediately.
            await self._fetch_frameworks()

            async with self:
                yield rx.toast.success(
                    f'Framework "{title}" added successfully.',
                    duration=3000,
                )

        except (SQLAlchemyError, RuntimeError, ValueError) as e:
            async with self:
                yield rx.toast.error(
                    f"Failed to add framework: {e!s}",
                    duration=5000,
                )

    @rx.event(background=True)
    async def select_and_navigate_framework(self) -> AsyncGenerator[EventSpec]:
        async with self:
            if not self.selected_framework or self.selected_framework.id == 0:
                return
            framework_id = self.selected_framework.id
            title = self.selected_framework.title
            self.show_dialog = False

        # get_state must be called inside async with self in background tasks.
        async with self:
            global_state = await self.get_state(GlobalFrameworkState)
            await global_state.select_framework(framework_id)
            yield rx.toast.success(f'Framework selected: "{title}"', duration=3000)
            yield rx.redirect("/home")
