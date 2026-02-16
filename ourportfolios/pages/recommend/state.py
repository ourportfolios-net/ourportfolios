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


# Define proper models for Reflex type safety
class FrameworkModel(rx.Base):
    """Model for framework data"""

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
    """Model for scope data"""

    value: str
    title: str


class CategoryModel(rx.Base):
    """Model for category filter"""

    value: str
    label: str


class TickerModel(rx.Base):
    """Model for ticker cart items"""

    symbol: str
    name: str = ""


class MetricModel(rx.Base):
    """Model for framework metrics"""

    name: str
    category: str
    enabled: bool = True
    order: int = 0


class FrameworkState(SessionIsolatedStateMixin, rx.State):
    active_scope: str = "fundamental"
    active_category: str = "all"
    scopes: list[ScopeModel] = []
    frameworks: list[FrameworkModel] = []
    loading_scopes: bool = False
    loading_frameworks: bool = False
    selected_framework: FrameworkModel = FrameworkModel(
        id=0, title="", description="", author=""
    )
    show_dialog: bool = False
    show_add_dialog: bool = False

    # Search functionality
    search_query: str = ""

    # Ticker cart for comparison
    ticker_cart: list[TickerModel] = []

    # Category filters
    categories: list[CategoryModel] = [
        CategoryModel(value="all", label="All Frameworks"),
        CategoryModel(value="conservative", label="Conservative"),
        CategoryModel(value="growth", label="Aggressive Growth"),
        CategoryModel(value="income", label="Passive Income"),
        CategoryModel(value="speculative", label="Speculative"),
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

    # Metrics management
    form_metrics: list[MetricModel] = []

    # Available metrics by category
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

    # Form field setters
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

    def _apply_filters(self):
        """Internal method to apply filters - called by events"""
        # This runs on the backend where we can use Python string methods
        pass  # Filtering will be done in the component with rx.cond

    @rx.event
    def add_to_cart(self, ticker: TickerModel):
        """Add a ticker to the comparison cart"""
        if not any(t.symbol == ticker.symbol for t in self.ticker_cart):
            self.ticker_cart.append(ticker)

    @rx.event
    def remove_from_cart(self, symbol: str):
        """Remove a ticker from the comparison cart"""
        self.ticker_cart = [t for t in self.ticker_cart if t.symbol != symbol]

    @rx.event
    def navigate_to_compare(self):
        """Navigate to comparison page with selected tickers"""
        return rx.redirect("/select")

    @rx.event
    def add_metric_to_form(self):
        """Add a new metric to the framework's metric list"""
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
        """Remove a metric from the list"""
        self.form_metrics = [m for m in self.form_metrics if m.name != metric_name]
        for i, metric in enumerate(self.form_metrics):
            metric.order = i

    @rx.event
    def toggle_metric_enabled(self, metric_name: str):
        """Toggle whether a metric is enabled"""
        for metric in self.form_metrics:
            if metric.name == metric_name:
                metric.enabled = not metric.enabled
                break

    @rx.event
    def move_metric_up(self, metric_name: str):
        """Move a metric up in the order"""
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
        """Move a metric down in the order"""
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
        """Initialize session when page is mounted - SYNCHRONOUS for instant load."""
        super().on_mount()  # Initialize session synchronously
        return FrameworkState.auto_load_frameworks

    def on_unmount(self):
        """Cleanup when page is unmounted - SYNCHRONOUS for instant navigation."""
        super().on_unmount()

    @rx.event(background=True)
    @session_isolated
    async def auto_load_frameworks(self):
        """Auto-trigger framework loading after page mounts (non-blocking)."""
        async with self:
            if not self.is_mounted():
                return

            # Load scopes and frameworks within the same async context
            await self.load_scopes()

            if not self.is_mounted():
                return

            if self.scopes:
                first_scope = self.scopes[0].value
                self.active_scope = first_scope

            # Load frameworks for the selected scope
            await self.load_frameworks()

    @session_isolated
    async def load_scopes(self):
        """Load available scopes - internal method, assumes state is already mutable"""
        self.loading_scopes = True

        try:
            # Set scopes directly
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
        """Change active scope and load frameworks"""
        async with self:
            self.active_scope = scope
            # Call load_frameworks while state is still mutable
            await self.load_frameworks()

    @session_isolated
    async def load_frameworks(self):
        """Load frameworks for current scope - internal method, assumes state is already mutable"""
        self.loading_frameworks = True
        active_scope = self.active_scope

        try:
            async with get_company_session() as session:
                query = text("""
                    SELECT 
                        f.*,
                        COALESCE(
                            json_agg(
                                json_build_object(
                                    'name', m.metrics,
                                    'type', m.category,
                                    'order', m.display_order
                                ) ORDER BY m.display_order
                            ) FILTER (WHERE m.id IS NOT NULL),
                            '[]'::json
                        ) as metrics
                    FROM frameworks.frameworks_df f
                    LEFT JOIN frameworks.framework_metrics_df m ON f.id = m.framework_id
                    WHERE f.scope = :scope
                    GROUP BY f.id
                    ORDER BY f.title
                """)
                result = await session.execute(query, {"scope": active_scope})
                frameworks = result.mappings().all()

            # Convert to FrameworkModel instances
            self.frameworks = [
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
        except Exception:
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
        self.form_scope = self.active_scope
        self.form_title = ""
        self.form_description = ""
        self.form_author = ""
        self.form_complexity = "beginner-friendly"
        self.form_industry = "general"
        self.form_source_name = ""
        self.form_source_url = ""
        self.form_metrics = []
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
        """Submit new framework to database"""
        async with self:
            if not self.form_title or not self.form_author:
                return

            # Capture form data
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
                        metrics_query = text("""
                            INSERT INTO frameworks.framework_metrics_df 
                            (framework_id, category, metrics, display_order)
                            VALUES (:framework_id, :category, ARRAY[:metric_name], :order)
                        """)
                        for metric in metrics:
                            await session.execute(
                                metrics_query,
                                {
                                    "framework_id": framework_id,
                                    "category": metric.category,
                                    "metric_name": metric.name,
                                    "order": metric.order,
                                },
                            )

                self.show_add_dialog = False

                # Load frameworks while state is still mutable
                await self.load_frameworks()

            except Exception as e:
                print(f"Error: {e}")
                pass

    @rx.event
    @session_isolated
    async def select_and_navigate_framework(self):
        """Select the current framework and navigate to ticker selection."""
        async with self:
            if not self.selected_framework or self.selected_framework.id == 0:
                return

            framework_id = self.selected_framework.id
            self.show_dialog = False

        # Get global state and select framework
        global_state = await self.get_state(GlobalFrameworkState)
        await global_state.select_framework(framework_id)

        return rx.redirect("/select")
