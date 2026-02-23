"""State management for ticker analysis page."""

import asyncio
import pandas as pd
import reflex as rx
from typing import Any, Optional, TYPE_CHECKING

from ...state.framework_state import GlobalFrameworkState
from ...components.price_chart import PriceChartState
from ...utils.database.fetch_data import fetch_company_data, fetch_price_data_async
from ...utils.preprocessing.financial_statements import get_transformed_dataframes
from ...utils.session_manager import (
    SessionIsolatedStateMixin,
    session_isolated,
    SessionCancelledError,
)


class State(SessionIsolatedStateMixin, rx.State):
    if TYPE_CHECKING:  # for Pylance
        ticker: str

    switch_value: str = "year"
    company_control: str = "shares"

    # Track which ticker the current data belongs to
    _data_ticker: str = ""

    profile_dialog_open: bool = False
    _is_loading_company: bool = True
    _is_loading_financial: bool = True
    _is_loading_price: bool = True

    error_company: str = ""
    error_financial: str = ""

    _current_ticker: str = ""
    render_key: int = 0

    @rx.event
    def set_company_control(self, value: str | list[str]):
        if isinstance(value, list):
            self.company_control = value[0] if value else "shares"
        else:
            self.company_control = value

    # Data storage
    overview_df: pd.DataFrame = pd.DataFrame()
    profile_df: pd.DataFrame = pd.DataFrame()
    shareholders_df: pd.DataFrame = pd.DataFrame()
    events_df: pd.DataFrame = pd.DataFrame()
    news_df: pd.DataFrame = pd.DataFrame()
    officers_df: pd.DataFrame = pd.DataFrame()
    price_data: pd.DataFrame = pd.DataFrame()

    income_statement: list[dict] = []
    balance_sheet: list[dict] = []
    cash_flow: list[dict] = []
    financial_df: pd.DataFrame = pd.DataFrame()
    transformed_dataframes: dict = {}
    available_metrics_by_category: dict[str, list[str]] = {}
    selected_metrics: dict[str, str] = {}

    selected_metric: str = "P/E"
    available_metrics: list[str] = [
        "P/E",
        "P/B",
        "P/S",
        "P/Cash Flow",
        "ROE (%)",
        "ROA (%)",
        "Debt/Equity",
    ]
    selected_margin_metric: str = "gross_margin"

    # Session isolation flags
    _is_mounted: bool = True
    _data_loaded: bool = False
    _last_framework_id: Optional[int] = None

    # ============================================================================
    # COMPUTED VARS
    # ============================================================================

    @rx.var
    def is_loading_company(self) -> bool:
        if self.ticker != self._data_ticker:
            return True
        return self._is_loading_company

    @rx.var
    def is_loading_financial(self) -> bool:
        if self.ticker != self._data_ticker:
            return True
        return self._is_loading_financial

    @rx.var
    def is_loading_price(self) -> bool:
        if self.ticker != self._data_ticker:
            return True
        return self._is_loading_price

    def on_mount(self):
        """Initialize session and trigger background data loading."""
        super().on_mount()
        # Always force reload on every mount — handles page revisits and refreshes
        self._data_loaded = False
        return State.auto_load_data

    def on_unmount(self):
        """Clean up state when page is unmounted."""
        self._is_mounted = False
        super().on_unmount()

        self.overview_df = pd.DataFrame()
        self.profile_df = pd.DataFrame()
        self.shareholders_df = pd.DataFrame()
        self.events_df = pd.DataFrame()
        self.news_df = pd.DataFrame()
        self.officers_df = pd.DataFrame()
        self.price_data = pd.DataFrame()
        self.transformed_dataframes = {}
        self.financial_df = pd.DataFrame()
        self._data_loaded = False
        self._last_framework_id = None
        self.render_key = 0
        self._data_ticker = ""

        self._is_loading_company = True
        self._is_loading_financial = True
        self._is_loading_price = True
        self.error_company = ""
        self.error_financial = ""

    @rx.event(background=True)
    @session_isolated
    async def auto_load_data(self):
        """Load page data in the background after mount."""
        async with self:
            if not self.is_mounted():
                return

            if not self.ticker:
                self._is_loading_company = False
                self._is_loading_financial = False
                self._is_loading_price = False
                return

            ticker = self.ticker
            ticker_changed = ticker != self._current_ticker

            # Always reset and reload — _data_loaded is set False on every mount
            self._current_ticker = ticker
            self._data_loaded = False
            self._data_ticker = ""

            self.overview_df = pd.DataFrame()
            self.profile_df = pd.DataFrame()
            self.shareholders_df = pd.DataFrame()
            self.events_df = pd.DataFrame()
            self.news_df = pd.DataFrame()
            self.officers_df = pd.DataFrame()
            self.price_data = pd.DataFrame()
            self.transformed_dataframes = {}
            self.income_statement = []
            self.balance_sheet = []
            self.cash_flow = []
            self.available_metrics_by_category = {}
            self.selected_metrics = {}

            self.error_company = ""
            self.error_financial = ""

            self.render_key += 1

            self._is_loading_company = True
            self._is_loading_financial = True
            self._is_loading_price = True

        # Load company + price data
        await self.load_company_data()

        async with self:
            if not self.is_mounted():
                return

        # Load financial data
        await self.load_transformed_dataframes()

        async with self:
            if not self.is_mounted():
                return
            ticker_for_chart = ticker

        # Always yield chart reload — this re-runs the JS initialization
        yield PriceChartState.load_state(ticker_for_chart)

        async with self:
            self._data_loaded = True

    @rx.event
    @session_isolated
    async def toggle_switch(self, value: bool):
        async with self:
            self.switch_value = "year" if value else "quarter"
            self.transformed_dataframes = {}
            self.available_metrics_by_category = {}
            self.selected_metrics = {}
            self.income_statement = []
            self.balance_sheet = []
            self.cash_flow = []
            self._is_loading_financial = True
            self.error_financial = ""
        await self.load_transformed_dataframes()

    @rx.event
    @session_isolated
    async def load_company_data(self):
        """Load company metadata and price data from database."""
        async with self:
            ticker = self.ticker

        if not ticker:
            async with self:
                self._is_loading_company = False
                self._is_loading_price = False
            return

        if not self.is_mounted():
            return

        try:
            await asyncio.sleep(0)

            if not self.is_mounted():
                return

            company_data = fetch_company_data(ticker)

            if not self.is_mounted():
                return

            price_data = await fetch_price_data_async(ticker)

            async with self:
                self.overview_df = company_data.get("overview", pd.DataFrame())
                self.shareholders_df = company_data.get("shareholders", pd.DataFrame())
                self.events_df = company_data.get("events", pd.DataFrame())
                self.news_df = company_data.get("news", pd.DataFrame())
                self.profile_df = company_data.get("profile", pd.DataFrame())
                self.officers_df = company_data.get("officers", pd.DataFrame())
                self.price_data = price_data

                self._data_ticker = ticker
                self._is_loading_company = False
                self._is_loading_price = False
                self.error_company = ""

        except SessionCancelledError:
            return
        except Exception as e:
            async with self:
                self.overview_df = pd.DataFrame()
                self.shareholders_df = pd.DataFrame()
                self.events_df = pd.DataFrame()
                self.news_df = pd.DataFrame()
                self.profile_df = pd.DataFrame()
                self.officers_df = pd.DataFrame()
                self.price_data = pd.DataFrame()
                self._data_ticker = ticker
                self._is_loading_company = False
                self._is_loading_price = False
                self.error_company = str(e)

    @rx.var
    def overview(self) -> dict:
        if self.overview_df.empty:
            return {}
        try:
            return self.overview_df.iloc[0].to_dict()
        except Exception:
            return {}

    @rx.var
    def profile(self) -> dict:
        if self.profile_df.empty:
            return {}
        try:
            return self.profile_df.iloc[0].to_dict()
        except Exception:
            return {}

    @rx.var
    def shareholders(self) -> list[dict]:
        if self.shareholders_df.empty:
            return []
        try:
            return self.shareholders_df.to_dict("records")
        except Exception:
            return []

    @rx.var
    def events(self) -> list[dict]:
        if self.events_df.empty:
            return []
        try:
            return self.events_df.to_dict("records")
        except Exception:
            return []

    @rx.var
    def news(self) -> list[dict]:
        if self.news_df.empty:
            return []
        try:
            return self.news_df.to_dict("records")
        except Exception:
            return []

    @rx.var
    def officers(self) -> list[dict]:
        if self.officers_df.empty:
            return []
        try:
            return self.officers_df.to_dict("records")
        except Exception:
            return []

    @rx.event
    @session_isolated
    async def load_transformed_dataframes(self):
        """Load financial data — always fetches fresh, no cache guard."""
        ticker = self.ticker
        if not self.is_mounted():
            return

        async with self:
            switch_value = self.switch_value

        try:
            result = await get_transformed_dataframes(ticker, period=switch_value)

            if "error" in result:
                async with self:
                    self._is_loading_financial = False
                    self.error_financial = result["error"]
                return

            if not self.is_mounted():
                return

            async with self:
                self.transformed_dataframes = result
                self.income_statement = result.get("transformed_income_statement", [])
                self.balance_sheet = result.get("transformed_balance_sheet", [])
                self.cash_flow = result.get("transformed_cash_flow", [])

        except Exception as e:
            async with self:
                self.transformed_dataframes = {
                    "transformed_income_statement": [],
                    "transformed_balance_sheet": [],
                    "transformed_cash_flow": [],
                    "categorized_ratios": {},
                }
                self.income_statement = []
                self.balance_sheet = []
                self.cash_flow = []
                self.available_metrics_by_category = {}
                self.selected_metrics = {}
                self._is_loading_financial = False
                self.error_financial = str(e)
            return

        # Process categorized ratios with framework awareness
        async with self:
            global_state = await self.get_state(GlobalFrameworkState)
            current_framework_id = global_state.selected_framework_id
            self._last_framework_id = current_framework_id
            has_selected_framework = global_state.has_selected_framework
            framework_metrics = global_state.framework_metrics

        categorized_ratios = self.transformed_dataframes.get("categorized_ratios", {})
        all_available_metrics = {}

        for category, financial_data in categorized_ratios.items():
            if financial_data and len(financial_data) > 0:
                excluded_columns = {"Year", "Quarter", "Date", "Period"}
                metrics = [
                    col for col in financial_data[0] if col not in excluded_columns
                ]
                all_available_metrics[category] = metrics

        async with self:
            if has_selected_framework and framework_metrics:
                self.available_metrics_by_category = {}
                self.selected_metrics = {}

                for category, framework_metric_names in framework_metrics.items():
                    if category in all_available_metrics:
                        self.available_metrics_by_category[category] = (
                            all_available_metrics[category]
                        )
                        if (
                            isinstance(framework_metric_names, list)
                            and len(framework_metric_names) > 0
                        ):
                            first_metric = framework_metric_names[0]
                            if first_metric in all_available_metrics[category]:
                                self.selected_metrics[category] = first_metric
                            else:
                                self.selected_metrics[category] = all_available_metrics[
                                    category
                                ][0]
                        else:
                            self.selected_metrics[category] = all_available_metrics[
                                category
                            ][0]
                    else:
                        if (
                            isinstance(framework_metric_names, list)
                            and len(framework_metric_names) > 0
                        ):
                            self.available_metrics_by_category[category] = (
                                framework_metric_names
                            )
                            self.selected_metrics[category] = framework_metric_names[0]
                        else:
                            self.available_metrics_by_category[category] = []
            else:
                self.available_metrics_by_category = all_available_metrics
                self.selected_metrics = {}

                for category, metrics in all_available_metrics.items():
                    if metrics and len(metrics) > 0:
                        self.selected_metrics[category] = metrics[0]

            self._is_loading_financial = False
            self.error_financial = ""

    @rx.event
    @session_isolated
    async def reload_for_framework_change(self):
        """Force reload when framework changes."""
        async with self:
            self.transformed_dataframes = {}
            self.available_metrics_by_category = {}
            self.selected_metrics = {}
            self._last_framework_id = None
        await self.load_transformed_dataframes()

    @rx.event
    def set_metric_for_category(self, category: str, metric: str):
        self.selected_metrics[category] = metric

    @rx.var(cache=True)
    def get_chart_data_for_category(self) -> dict[str, list[dict[str, Any]]]:
        """Get chart data for all categories."""
        chart_data = {}
        categorized_ratios = self.transformed_dataframes.get("categorized_ratios", {})

        for category in self.selected_metrics.keys():
            if category not in categorized_ratios:
                chart_data[category] = []
                continue

            data = categorized_ratios[category]
            selected_metric = self.selected_metrics.get(category)

            if not selected_metric or not data:
                chart_data[category] = []
                continue

            if data and selected_metric not in data[0]:
                chart_data[category] = []
                continue

            chart_points = []
            for row in data:
                year = row.get("Year", "")
                value = row.get(selected_metric)

                try:
                    if value is not None and str(value).lower() not in [
                        "nan",
                        "none",
                        "",
                    ]:
                        value_float = float(value)
                    else:
                        value_float = 0
                except (ValueError, TypeError):
                    value_float = 0

                chart_points.append({"year": year, "value": value_float})

            chart_data[category] = chart_points[-8:]

        return chart_data

    def get_chart_data(self, category: str) -> list[dict[str, Any]]:
        return self.get_chart_data_for_category.get(category, [])

    @rx.var
    def get_categories_list(self) -> list[str]:
        return list(self.available_metrics_by_category.keys())

    @rx.var
    def pie_data(self) -> list[dict[str, object]]:
        if not self.shareholders:
            return []

        try:
            palettes = ["accent", "plum", "iris"]
            indices = [6, 7, 8]
            colors = [
                rx.color(palette, idx, True) for palette in palettes for idx in indices
            ]

            pie_data = [
                {"name": s["share_holder"], "value": s["share_own_percent"]}
                for s in self.shareholders
            ]
            for idx, d in enumerate(pie_data):
                d["fill"] = colors[idx % len(colors)]
            return pie_data
        except Exception as e:
            print(f"Error: {e}")
            return []

    @rx.event
    def set_profile_dialog_open(self, value: bool):
        self.profile_dialog_open = value
