"""State management for framework recommendation page."""

import reflex as rx
from sqlalchemy import text
from typing import Any, Optional

from ...state import GlobalFrameworkState
from ...utils.database.database import get_company_session
from ...utils.session_manager import (
    SessionIsolatedStateMixin,
    session_isolated,
)


class FrameworkModel(rx.Base):
    id: int
    title: str
    description: str = ""
    author: str = ""
    complexity: str = "beginner-friendly"
    scope: str = "fundamental"
    industry: str = "general"
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    metrics: list[dict[str, Any]] = []


class ScopeModel(rx.Base):
    value: str
    title: str


class CategoryModel(rx.Base):
    value: str
    label: str


class TickerModel(rx.Base):
    symbol: str
    name: str = ""


class MetricModel(rx.Base):
    name: str
    category: str
    enabled: bool = True
    order: int = 0


class FrameworkState(SessionIsolatedStateMixin, rx.State):
    active_scope: str = "fundamental"
    active_category: str = "all"
    scopes: list[ScopeModel] = []

    # All frameworks from DB — never filtered
    _all_frameworks: list[FrameworkModel] = []
    # Displayed frameworks — filtered subset
    frameworks: list[FrameworkModel] = []

    loading_scopes: bool = False
    loading_frameworks: bool = False
    selected_framework: FrameworkModel = FrameworkModel(
        id=0, title="", description="", author=""
    )
    show_dialog: bool = False
    show_add_dialog: bool = False

    search_query: str = ""

    ticker_cart: list[TickerModel] = []

    categories: list[CategoryModel] = [
        CategoryModel(value="all", label="All"),
        CategoryModel(value="fundamental", label="Fundamentals"),
        CategoryModel(value="technical", label="Technical"),
        CategoryModel(value="beginner-friendly", label="Beginner-Friendly"),
        CategoryModel(value="complex", label="Complex"),
    ]

    # Form fields
    form_title: str = ""
    form_description: str = ""
    form_author: str = ""
    form_complexity: str = "beginner-friendly"
    form_scope: str = ""
    form_industry: str = "general"
    form_source_name: str = ""
    form_source_url: str = ""
    form_errors: dict[str, str] = {}

    form_metrics: list[MetricModel] = []

    available_categories: list[str] = [
        "Per Share Value",
        "Growth Rate",
        "Profitability",
        "Valuation",
        "Leverage & Liquidity",
        "Efficiency",
    ]

    per_share_metrics: list[str] = [
        "Earnings",
        "Book Value",
        "Free Cash Flow",
        "Dividend",
        "Revenues",
    ]
    growth_rate_metrics: list[str] = [
        "Revenues YoY",
        "Earnings YoY",
        "Free Cash Flow YoY",
        "Book Value YoY",
    ]
    profitability_metrics: list[str] = [
        "ROE",
        "ROIC",
        "Net Margin",
        "Gross Margin",
        "Operating Margin",
        "EBITDA Margin",
    ]
    valuation_metrics: list[str] = ["P/E", "P/B", "P/S", "EV/EBITDA"]
    leverage_liquidity_metrics: list[str] = [
        "Debt/Equity",
        "Current Ratio",
        "Quick Ratio",
        "Interest Coverage",
        "Cash Ratio",
    ]
    efficiency_metrics: list[str] = ["ROA", "Asset Turnover", "Dividend Payout %"]

    show_add_metric_dialog: bool = False
    new_metric_name: str = ""
    new_metric_category: str = "Per Share Value"

    @rx.var
    def metrics_count(self) -> int:
        return len(self.form_metrics)

    @rx.var
    def ticker_cart_count(self) -> int:
        return len(self.ticker_cart)

    def _apply_filters(self):
        """Filter _all_frameworks by search_query and active_category, store in frameworks."""
        results = self._all_frameworks

        # Search filter — match title or description
        if self.search_query.strip():
            q = self.search_query.strip().lower()
            results = [
                f for f in results if q in f.title.lower() or q in f.description.lower()
            ]

        # Category filter — scope-based or complexity-based
        if self.active_category == "fundamental":
            results = [f for f in results if f.scope == "fundamental"]
        elif self.active_category == "technical":
            results = [f for f in results if f.scope == "technical"]
        elif self.active_category == "beginner-friendly":
            results = [f for f in results if f.complexity == "beginner-friendly"]
        elif self.active_category == "complex":
            results = [f for f in results if f.complexity == "complex"]

        self.frameworks = results

    # --- Setters ---

    @rx.event
    def set_form_title(self, value: str):
        self.form_title = value

    @rx.event
    def set_form_description(self, value: str):
        self.form_description = value

    @rx.event
    def set_form_author(self, value: str):
        self.form_author = value

    @rx.event
    def set_form_complexity(self, value: str):
        self.form_complexity = value

    @rx.event
    def set_form_scope(self, value: str):
        self.form_scope = value

    @rx.event
    def set_form_industry(self, value: str):
        self.form_industry = value

    @rx.event
    def set_form_source_name(self, value: str):
        self.form_source_name = value

    @rx.event
    def set_form_source_url(self, value: str):
        self.form_source_url = value

    @rx.event
    def set_new_metric_name(self, value: str):
        self.new_metric_name = value

    @rx.event
    def set_new_metric_category(self, value: str):
        self.new_metric_category = value

    @rx.event
    def set_active_category(self, category: str):
        self.active_category = category
        self._apply_filters()

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query
        self._apply_filters()

    @rx.event
    def add_to_cart(self, ticker: TickerModel):
        if not any(t.symbol == ticker.symbol for t in self.ticker_cart):
            self.ticker_cart.append(ticker)

    @rx.event
    def remove_from_cart(self, symbol: str):
        self.ticker_cart = [t for t in self.ticker_cart if t.symbol != symbol]

    @rx.event
    def navigate_to_compare(self):
        return rx.redirect("/select")

    @rx.event
    def add_metric_to_form(self):
        if not self.new_metric_name:
            return
        if any(m.name == self.new_metric_name for m in self.form_metrics):
            return
        next_order = len(self.form_metrics)
        self.form_metrics.append(
            MetricModel(
                name=self.new_metric_name,
                category=self.new_metric_category,
                enabled=True,
                order=next_order,
            )
        )
        self.new_metric_name = ""
        self.show_add_metric_dialog = False

    @rx.event
    def remove_metric(self, metric_name: str):
        self.form_metrics = [m for m in self.form_metrics if m.name != metric_name]
        for i, metric in enumerate(self.form_metrics):
            metric.order = i

    @rx.event
    def toggle_metric_enabled(self, metric_name: str):
        for metric in self.form_metrics:
            if metric.name == metric_name:
                metric.enabled = not metric.enabled
                break

    @rx.event
    def move_metric_up(self, metric_name: str):
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
    def move_metric_down(self, metric_name: str):
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
    def open_add_metric_dialog(self):
        self.show_add_metric_dialog = True
        self.new_metric_name = ""

    @rx.event
    def close_add_metric_dialog(self):
        self.show_add_metric_dialog = False

    @rx.event
    def handle_add_metric_dialog_open(self, value: bool):
        if not value:
            self.close_add_metric_dialog()

    def on_mount(self):
        super().on_mount()
        return FrameworkState.auto_load_frameworks

    def on_unmount(self):
        super().on_unmount()

    @rx.event(background=True)
    @session_isolated
    async def auto_load_frameworks(self):
        async with self:
            if not self.is_mounted():
                return
            await self.load_scopes()
            if not self.is_mounted():
                return
            if self.scopes:
                self.active_scope = self.scopes[0].value
            await self.load_frameworks()

    @session_isolated
    async def load_scopes(self):
        self.loading_scopes = True
        try:
            self.scopes = [
                ScopeModel(value="fundamental", title="Fundamental"),
                ScopeModel(value="technical", title="Technical"),
            ]
            if self.scopes and not self.active_scope:
                self.active_scope = self.scopes[0].value
        except Exception:
            self.scopes = [
                ScopeModel(value="fundamental", title="Fundamental"),
                ScopeModel(value="technical", title="Technical"),
            ]
        finally:
            self.loading_scopes = False

    @rx.event
    @session_isolated
    async def change_scope(self, scope: str):
        async with self:
            self.active_scope = scope
            await self.load_frameworks()

    @session_isolated
    async def load_frameworks(self):
        self.loading_frameworks = True
        active_scope = self.active_scope
        try:
            async with get_company_session() as session:
                # Unnest the metrics array so each individual metric name
                # becomes its own row — produces one badge per metric in the dialog.
                query = text("""
                    SELECT
                        f.*,
                        COALESCE(
                            json_agg(
                                json_build_object(
                                    'name', metric_name,
                                    'type', m.category,
                                    'order', m.display_order
                                ) ORDER BY m.display_order
                            ) FILTER (WHERE metric_name IS NOT NULL),
                            '[]'::json
                        ) as metrics
                    FROM frameworks.frameworks_df f
                    LEFT JOIN frameworks.framework_metrics_df m ON f.id = m.framework_id
                    LEFT JOIN LATERAL unnest(m.metrics) AS metric_name ON true
                    WHERE f.scope = :scope
                    GROUP BY f.id
                    ORDER BY f.title
                """)
                result = await session.execute(query, {"scope": active_scope})
                frameworks = result.mappings().all()

            loaded = [
                FrameworkModel(
                    id=row["id"],
                    title=row["title"],
                    description=row.get("description", ""),
                    author=row.get("author", ""),
                    complexity=row.get("complexity", "beginner-friendly"),
                    scope=row.get("scope", "fundamental"),
                    industry=row.get("industry", "general"),
                    source_name=row.get("source_name"),
                    source_url=row.get("source_url"),
                    metrics=row.get("metrics", []),
                )
                for row in frameworks
            ]
            self._all_frameworks = loaded
            self._apply_filters()
        except Exception:
            self._all_frameworks = []
            self.frameworks = []
        finally:
            self.loading_frameworks = False

    @rx.event
    def show_framework_dialog(self, framework: FrameworkModel):
        self.selected_framework = framework
        self.show_dialog = True

    @rx.event
    def close_dialog(self):
        self.show_dialog = False
        self.selected_framework = FrameworkModel(
            id=0, title="", description="", author=""
        )

    @rx.event
    def handle_dialog_open(self, value: bool):
        if not value:
            self.close_dialog()

    @rx.event
    def open_add_dialog(self):
        self.form_scope = self.active_scope if self.active_scope else "fundamental"
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
    def close_add_dialog(self):
        self.show_add_dialog = False

    @rx.event
    def handle_add_dialog_open(self, value: bool):
        if not value:
            self.close_add_dialog()

    @rx.event
    @session_isolated
    async def submit_framework(self):
        async with self:
            errors = {}
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
            source_name = self.form_source_name if self.form_source_name else None
            source_url = self.form_source_url if self.form_source_url else None
            metrics = list(self.form_metrics)

            try:
                async with get_company_session() as session:
                    framework_query = text("""
                        INSERT INTO frameworks.frameworks_df
                        (title, description, author, complexity, scope, industry, source_name, source_url)
                        VALUES (:title, :description, :author, :complexity, :scope, :industry, :source_name, :source_url)
                        RETURNING id
                    """)
                    result = await session.execute(
                        framework_query,
                        {
                            "title": title,
                            "description": description,
                            "author": author,
                            "complexity": complexity,
                            "scope": scope,
                            "industry": industry,
                            "source_name": source_name,
                            "source_url": source_url,
                        },
                    )
                    framework_row = result.first()
                    framework_id = framework_row[0] if framework_row else None

                    if framework_id and metrics:
                        # Pass metrics as a Python list — let the asyncpg driver
                        # handle the Python list -> PostgreSQL array conversion.
                        # ARRAY[:param] inside text() is invalid SQLAlchemy syntax.
                        metrics_query = text("""
                            INSERT INTO frameworks.framework_metrics_df
                            (framework_id, category, metrics, display_order)
                            VALUES (:framework_id, :category, :metrics_array, :order)
                        """)
                        for metric in metrics:
                            await session.execute(
                                metrics_query,
                                {
                                    "framework_id": framework_id,
                                    "category": metric.category,
                                    "metrics_array": [metric.name],
                                    "order": metric.order,
                                },
                            )

                self.show_add_dialog = False
                self.active_scope = scope
                await self.load_frameworks()
                return rx.toast.success(
                    f'Framework "{title}" added successfully.',
                    duration=3000,
                )
            except Exception as e:
                print(f"[submit_framework] Error: {e}")
                return rx.toast.error(
                    f"Failed to add framework: {str(e)}",
                    duration=5000,
                )

    @rx.event
    @session_isolated
    async def select_and_navigate_framework(self):
        async with self:
            if not self.selected_framework or self.selected_framework.id == 0:
                return
            framework_id = self.selected_framework.id
            title = self.selected_framework.title
            self.show_dialog = False

        global_state = await self.get_state(GlobalFrameworkState)
        await global_state.select_framework(framework_id)
        return [
            rx.toast.success(
                f'Framework selected: "{title}"',
                duration=3000,
            ),
            rx.redirect("/home"),
        ]
