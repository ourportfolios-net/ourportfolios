"""State management for the ticker landing page - TRUE independent loading."""

import pandas as pd
import reflex as rx
from typing import Any, List, Dict, Optional

from ...state.framework_state import GlobalFrameworkState
from ...utils.database.fetch_data import fetch_company_data, fetch_price_data_async
from ...preprocessing.financial_statements import get_transformed_dataframes


class State(rx.State):
    switch_value: str = "year"
    company_control: str = "shares"

    is_loading_company: bool = True
    is_loading_financial: bool = True

    error_company: str = ""
    error_financial: str = ""

    _current_ticker: str = ""

    @rx.event
    def set_company_control(self, value: str | List[str]):
        if isinstance(value, list):
            self.company_control = value[0] if value else "shares"
        else:
            self.company_control = value

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

    _last_framework_id: Optional[int] = None

    def _get_ticker(self) -> str:
        """Helper to get ticker from URL."""
        return self.router.url.path.split("/")[-1]

    @rx.event
    def initialize_page_data(self):
        """Initialize loading - triggers independent background tasks."""
        ticker = self._get_ticker()

        if ticker != self._current_ticker:
            print(f"[State] New ticker: {ticker}")
            self._current_ticker = ticker
            self.is_loading_company = True
            self.is_loading_financial = True
            self.error_company = ""
            self.error_financial = ""

            self.overview_df = pd.DataFrame()
            self.profile_df = pd.DataFrame()
            self.shareholders_df = pd.DataFrame()
            self.events_df = pd.DataFrame()
            self.news_df = pd.DataFrame()
            self.officers_df = pd.DataFrame()
            self.transformed_dataframes = {}
            self.available_metrics_by_category = {}
            self.selected_metrics = {}

            return [
                State.load_company_data,
                State.load_transformed_dataframes,
            ]

    @rx.event
    async def on_unmount(self):
        """Called when page is unmounted."""
        self.overview_df = pd.DataFrame()
        self.profile_df = pd.DataFrame()
        self.shareholders_df = pd.DataFrame()
        self.events_df = pd.DataFrame()
        self.news_df = pd.DataFrame()
        self.officers_df = pd.DataFrame()
        self.transformed_dataframes = {}
        self.financial_df = pd.DataFrame()
        self._last_framework_id = None
        self._current_ticker = ""
        self.error_company = ""
        self.error_financial = ""

    @rx.event
    def toggle_switch(self, value: bool):
        self.switch_value = "year" if value else "quarter"
        self.transformed_dataframes = {}
        self.available_metrics_by_category = {}
        self.selected_metrics = {}
        self.is_loading_financial = True
        self.error_financial = ""
        return State.load_transformed_dataframes

    @rx.event(background=True)
    async def load_company_data(self):
        """Load company metadata - runs independently in background."""
        async with self:
            ticker = self._get_ticker()
            print(f"[State] Loading company data for: {ticker}")

        try:
            company_data = fetch_company_data(ticker)
            price_data = await fetch_price_data_async(ticker)

            async with self:
                self.overview_df = company_data.get("overview", pd.DataFrame())
                self.shareholders_df = company_data.get("shareholders", pd.DataFrame())
                self.events_df = company_data.get("events", pd.DataFrame())
                self.news_df = company_data.get("news", pd.DataFrame())
                self.profile_df = company_data.get("profile", pd.DataFrame())
                self.officers_df = company_data.get("officers", pd.DataFrame())
                self.price_data = price_data

                print(f"[State] Company data loaded ✓")
                self.is_loading_company = False
                self.error_company = ""

        except Exception as e:
            error_msg = f"Failed to load company data: {str(e)}"
            print(f"[State] Error: {error_msg}")
            async with self:
                self.is_loading_company = False
                self.error_company = error_msg

    @rx.var
    def overview(self) -> dict:
        if self.overview_df.empty:
            return {}
        return self.overview_df.iloc[0].to_dict()

    @rx.var
    def profile(self) -> dict:
        if self.profile_df.empty:
            return {}
        return self.profile_df.iloc[0].to_dict()

    @rx.var
    def shareholders(self) -> list[dict]:
        if self.shareholders_df.empty:
            return []
        return self.shareholders_df.to_dict("records")

    @rx.var
    def events(self) -> list[dict]:
        if self.events_df.empty:
            return []
        return self.events_df.to_dict("records")

    @rx.var
    def news(self) -> list[dict]:
        if self.news_df.empty:
            return []
        return self.news_df.to_dict("records")

    @rx.var
    def officers(self) -> list[dict]:
        if self.officers_df.empty:
            return []
        return self.officers_df.to_dict("records")

    @rx.event
    def load_financial_ratios(self):
        if not self.transformed_dataframes:
            return State.load_transformed_dataframes

    @rx.event(background=True)
    async def load_transformed_dataframes(self):
        """Load financial data - runs independently in background."""
        async with self:
            ticker = self._get_ticker()
            switch_value = self.switch_value
            print(f"[State] Loading financial data for: {ticker}")

        try:
            result = await get_transformed_dataframes(ticker, period=switch_value)

            if "error" in result:
                error_msg = f"API error: {result['error']}"
                print(f"[State] {error_msg}")
                async with self:
                    self.is_loading_financial = False
                    self.error_financial = error_msg
                return

            # Get global state inside async with self
            async with self:
                global_state = await self.get_state(GlobalFrameworkState)

            # Process metrics outside the lock
            categorized_ratios = result.get("categorized_ratios", {})
            all_available_metrics = {}

            for category, financial_data in categorized_ratios.items():
                if financial_data and len(financial_data) > 0:
                    excluded_columns = {"Year", "Quarter", "Date", "Period"}
                    metrics = [
                        col for col in financial_data[0] if col not in excluded_columns
                    ]
                    all_available_metrics[category] = metrics

            # Prepare final state updates
            final_available_metrics = {}
            final_selected_metrics = {}

            if global_state.has_selected_framework and global_state.framework_metrics:
                for (
                    category,
                    framework_metric_names,
                ) in global_state.framework_metrics.items():
                    if category in all_available_metrics:
                        final_available_metrics[category] = all_available_metrics[
                            category
                        ]

                        if (
                            isinstance(framework_metric_names, list)
                            and len(framework_metric_names) > 0
                        ):
                            first_metric = framework_metric_names[0]
                            if first_metric in all_available_metrics[category]:
                                final_selected_metrics[category] = first_metric
                            else:
                                final_selected_metrics[category] = (
                                    all_available_metrics[category][0]
                                )
                        else:
                            final_selected_metrics[category] = all_available_metrics[
                                category
                            ][0]
                    else:
                        if (
                            isinstance(framework_metric_names, list)
                            and len(framework_metric_names) > 0
                        ):
                            final_available_metrics[category] = framework_metric_names
                            final_selected_metrics[category] = framework_metric_names[0]
                        else:
                            final_available_metrics[category] = []
            else:
                final_available_metrics = all_available_metrics
                for category, metrics in all_available_metrics.items():
                    if metrics and len(metrics) > 0:
                        final_selected_metrics[category] = metrics[0]

            # Single async with self block for all state updates
            async with self:
                self.transformed_dataframes = result
                self.income_statement = result["transformed_income_statement"]
                self.balance_sheet = result["transformed_balance_sheet"]
                self.cash_flow = result["transformed_cash_flow"]
                self.available_metrics_by_category = final_available_metrics
                self.selected_metrics = final_selected_metrics
                self._last_framework_id = global_state.selected_framework_id

                print(f"[State] Financial data loaded ✓")
                self.is_loading_financial = False
                self.error_financial = ""

        except Exception as e:
            error_msg = f"Failed to load financial data: {str(e)}"
            print(f"[State] Error: {error_msg}")
            import traceback

            traceback.print_exc()
            async with self:
                self.is_loading_financial = False
                self.error_financial = error_msg

    @rx.event
    def reload_for_framework_change(self):
        self.transformed_dataframes = {}
        self.available_metrics_by_category = {}
        self.selected_metrics = {}
        self._last_framework_id = None
        return State.load_transformed_dataframes

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
        return self.get_chart_data_for_category.get(category, [])

    @rx.var
    def get_categories_list(self) -> List[str]:
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
