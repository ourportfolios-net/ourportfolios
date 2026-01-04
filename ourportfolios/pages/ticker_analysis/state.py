"""State management for the ticker landing page."""

import asyncio
import pandas as pd
import reflex as rx
from typing import Any, List, Dict, Optional

from ...state.framework_state import GlobalFrameworkState
from ...components.price_chart import PriceChartState
from ...utils.database.fetch_data import fetch_company_data, fetch_price_data_async
from ...preprocessing.financial_statements import get_transformed_dataframes
from ...utils.session_manager import (
    SessionIsolatedStateMixin,
    session_isolated,
    SessionCancelledError,
)


class State(SessionIsolatedStateMixin, rx.State):
    switch_value: str = "year"
    company_control: str = "shares"

    @rx.var
    def current_ticker(self) -> str:
        """Get ticker from route parameter."""
        try:
            return self.router.url.params.get("ticker", "")
        except AttributeError:
            return ""

    @rx.event
    def set_company_control(self, value: str | List[str]):
        if isinstance(value, list):
            self.company_control = value[0] if value else "shares"
        else:
            self.company_control = value

    # Change to DataFrames
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
    available_metrics_by_category: Dict[str, List[str]] = {}
    selected_metrics: Dict[str, str] = {}

    selected_metric: str = "P/E"
    available_metrics: List[str] = [
        "P/E",
        "P/B",
        "P/S",
        "P/Cash Flow",
        "ROE (%)",
        "ROA (%)",
        "Debt/Equity",
    ]
    selected_margin_metric: str = "gross_margin"

    # Flag to track if the page is mounted - start as True for initial load
    _is_mounted: bool = True

    _data_loaded: bool = False
    _last_framework_id: Optional[int] = None

    def on_mount(self):
        """Initialize session and trigger background data loading."""
        super().on_mount()
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

    @rx.event(background=True)
    @session_isolated
    async def auto_load_data(self):
        """Load page data in the background after mount.

        Automatically exits if the user navigates away during loading.
        """
        async with self:
            if self._data_loaded:
                return

            if not self.is_mounted():
                return

        await self.load_company_data()

        async with self:
            if not self.is_mounted():
                return

        await self.load_transformed_dataframes()

        async with self:
            if not self.is_mounted():
                return

        yield PriceChartState.load_state

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
            await self.load_transformed_dataframes()

    @rx.event
    @session_isolated
    async def load_company_data(self):
        """Load company metadata and price data from database."""
        async with self:
            ticker = self.current_ticker

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

        except SessionCancelledError:
            return
        except Exception as e:
            print(f"Error loading company data for {ticker}: {e}")
            async with self:
                self.overview_df = pd.DataFrame()
                self.shareholders_df = pd.DataFrame()
                self.events_df = pd.DataFrame()
                self.news_df = pd.DataFrame()
                self.profile_df = pd.DataFrame()
                self.officers_df = pd.DataFrame()
                self.price_data = pd.DataFrame()

    @rx.var(cache=True)
    def overview(self) -> dict:
        """Get overview as dict."""
        if self.overview_df.empty:
            return {}
        return self.overview_df.iloc[0].to_dict()

    @rx.var(cache=True)
    def profile(self) -> dict:
        """Get profile as dict."""
        if self.profile_df.empty:
            return {}
        return self.profile_df.iloc[0].to_dict()

    @rx.var(cache=True)
    def shareholders(self) -> list[dict]:
        """Get shareholders as list of dicts."""
        if self.shareholders_df.empty:
            return []
        return self.shareholders_df.to_dict("records")

    @rx.var(cache=True)
    def events(self) -> list[dict]:
        """Get events as list of dicts."""
        if self.events_df.empty:
            return []
        return self.events_df.to_dict("records")

    @rx.var(cache=True)
    def news(self) -> list[dict]:
        """Get news as list of dicts."""
        if self.news_df.empty:
            return []
        return self.news_df.to_dict("records")

    @rx.var(cache=True)
    def officers(self) -> list[dict]:
        """Get officers as list of dicts."""
        if self.officers_df.empty:
            return []
        return self.officers_df.to_dict("records")

    @rx.event
    @session_isolated
    async def load_financial_ratios(self):
        """Load financial ratios data dynamically from database via transformed_dataframes."""
        # Financial ratios are now loaded via load_transformed_dataframes
        # This method is kept for backward compatibility but delegates to the main loader
        if not self.transformed_dataframes:
            await self.load_transformed_dataframes()

    @rx.event
    @session_isolated
    async def load_transformed_dataframes(self):
        ticker = self.current_ticker

        # CRITICAL: Add await point so task cancellation can take effect
        await asyncio.sleep(0)

        # Check if still mounted before loading
        if not self.is_mounted():
            return

        # Only fetch data if not already loaded
        if not self.transformed_dataframes:
            try:
                result = await get_transformed_dataframes(
                    ticker, period=self.switch_value
                )

                # Check again after async operation
                if not self.is_mounted():
                    return

                # Check if API call returned an error
                async with self:
                    if "error" in result:
                        print(f"API error loading financial data: {result['error']}")
                        # Set empty state but continue - UI will show empty cards gracefully
                        self.transformed_dataframes = result
                        self.income_statement = []
                        self.balance_sheet = []
                        self.cash_flow = []
                        self.available_metrics_by_category = {}
                        self.selected_metrics = {}
                        return
                    else:
                        self.transformed_dataframes = result
                        self.income_statement = result["transformed_income_statement"]
                        self.balance_sheet = result["transformed_balance_sheet"]
                        self.cash_flow = result["transformed_cash_flow"]
            except Exception as e:
                print(f"Error loading transformed dataframes: {e}")
                # Set empty data to allow page to continue loading
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
                return
        else:
            result = self.transformed_dataframes

        # Get current framework state and update state within context manager
        async with self:
            global_state = await self.get_state(GlobalFrameworkState)
            current_framework_id = global_state.selected_framework_id

            # Update tracked framework ID
            self._last_framework_id = current_framework_id

            # Cache framework properties that we'll need later
            has_selected_framework = global_state.has_selected_framework
            framework_metrics = global_state.framework_metrics

        categorized_ratios = result.get("categorized_ratios", {})
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

                # Include ALL categories from the framework, even if they don't have data yet
                for (
                    category,
                    framework_metric_names,
                ) in framework_metrics.items():
                    # Check if category has data in the database
                    if category in all_available_metrics:
                        # Category has data - use the metrics from database
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
                        # Category is in framework but has no data yet - still include it
                        # Use the framework's metric list as available metrics
                        if (
                            isinstance(framework_metric_names, list)
                            and len(framework_metric_names) > 0
                        ):
                            self.available_metrics_by_category[category] = (
                                framework_metric_names
                            )
                            self.selected_metrics[category] = framework_metric_names[0]
                        else:
                            # No metrics defined in framework for this category
                            self.available_metrics_by_category[category] = []

                # DO NOT add categories that aren't in the framework
            else:
                self.available_metrics_by_category = all_available_metrics
                self.selected_metrics = {}

                for category, metrics in all_available_metrics.items():
                    if metrics and len(metrics) > 0:
                        self.selected_metrics[category] = metrics[0]

    @rx.event
    @session_isolated
    async def reload_for_framework_change(self):
        """Force reload when framework changes - call this explicitly when needed"""
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
    def get_chart_data_for_category(self) -> Dict[str, List[Dict[str, Any]]]:
        chart_data = {}
        categorized_ratios = self.transformed_dataframes.get("categorized_ratios", {})

        for category in self.selected_metrics.keys():
            if category not in categorized_ratios:
                chart_data[category] = []
                continue

            data = categorized_ratios[category]
            selected_metric = self.selected_metrics.get(category)

            if not selected_metric or not data or len(data) == 0:
                chart_data[category] = []
                continue

            if data and len(data) > 0 and selected_metric not in data[0]:
                chart_data[category] = []
                continue

            chart_points = []
            # Data comes sorted by year ASC (oldest first) from categorization
            # We want the most recent 8 years in chronological order
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

    def get_chart_data(self, category: str) -> List[Dict[str, Any]]:
        """Get chart data for a specific category"""
        return self.get_chart_data_for_category.get(category, [])

    @rx.var
    def get_categories_list(self) -> List[str]:
        """Get list of available categories"""
        return list(self.available_metrics_by_category.keys())

    @rx.var(cache=True)
    def pie_data(self) -> list[dict[str, object]]:
        palettes = ["accent", "plum", "iris"]
        indices = [6, 7, 8]
        colors = [
            rx.color(palette, idx, True) for palette in palettes for idx in indices
        ]

        pie_data = [
            {
                "name": shareholder["share_holder"],
                "value": shareholder["share_own_percent"],
            }
            for shareholder in self.shareholders
        ]
        for idx, d in enumerate(pie_data):
            d["fill"] = colors[idx % len(colors)]
        return pie_data
