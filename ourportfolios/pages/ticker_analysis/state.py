"""State management for ticker analysis page."""

import asyncio
from typing import TYPE_CHECKING, cast

import pandas as pd
import reflex as rx

from ourportfolios.components.price_chart import PriceChartState
from ourportfolios.state.framework_state import GlobalFrameworkState
from ourportfolios.state.prefs_state import PrefsState
from ourportfolios.utils.database.fetch_data import (
    fetch_company_data,
    fetch_price_data_async,
)
from ourportfolios.utils.preprocessing.financial_statements import (
    get_transformed_dataframes,
)
from ourportfolios.utils.session_manager import (
    SessionIsolatedStateMixin,
    check_session_active,
)

_CATEGORY_DATA_TUPLE_MIN_ITEMS = 2


class State(SessionIsolatedStateMixin, rx.State):
    if TYPE_CHECKING:  # for Pylance
        ticker: str

    switch_value: str = "year"
    company_control: str = "shares"
    selected_tab: str = "performance"

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

    overview_df: pd.DataFrame = pd.DataFrame()
    profile_df: pd.DataFrame = pd.DataFrame()
    shareholders_df: pd.DataFrame = pd.DataFrame()
    events_df: pd.DataFrame = pd.DataFrame()
    news_df: pd.DataFrame = pd.DataFrame()
    officers_df: pd.DataFrame = pd.DataFrame()
    price_data: pd.DataFrame = pd.DataFrame()

    income_statement: rx.Field[list[dict[str, object]]] = rx.Field(
        default_factory=list,
    )
    balance_sheet: rx.Field[list[dict[str, object]]] = rx.Field(
        default_factory=list,
    )
    cash_flow: rx.Field[list[dict[str, object]]] = rx.Field(default_factory=list)
    financial_df: pd.DataFrame = pd.DataFrame()
    transformed_dataframes: dict[str, object] = cast("dict[str, object]", {})
    available_metrics_by_category: dict[str, list[str]] = cast(
        "dict[str, list[str]]",
        {},
    )
    selected_metrics: dict[str, str] = cast("dict[str, str]", {})

    selected_metric: str = "P/E"
    available_metrics: rx.Field[list[str]] = rx.Field(
        default_factory=lambda: [
            "P/E",
            "P/B",
            "P/S",
            "P/Cash Flow",
            "ROE (%)",
            "ROA (%)",
            "Debt/Equity",
        ],
    )
    selected_margin_metric: str = "gross_margin"

    _is_mounted: bool = True
    _data_loaded: bool = False
    _last_framework_id: int | None = None

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
        super().on_mount()
        self._data_loaded = False

    def on_unmount(self):
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

    def _reset_data_state(self, ticker: str) -> None:
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

    # ============================================================================
    # BACKGROUND TASKS
    # Per Reflex docs: state mutations ONLY inside `async with self` blocks.
    # Plain async helpers (_load_financial_data) can be awaited directly from
    # background tasks because they are not event handlers — just coroutines
    # that themselves use `async with self` for every state write.
    # ============================================================================

    async def _await_hydrated_ticker(self) -> str:
        ticker = ""
        for _ in range(20):
            async with self:
                ticker = self.ticker or self.router.page.params.get("ticker", "")
            if ticker:
                return ticker
            await asyncio.sleep(0.1)
        return ""

    async def _apply_company_and_price_data(
        self,
        *,
        ticker: str,
        company_data: dict[str, pd.DataFrame],
        price_data: pd.DataFrame,
    ) -> None:
        async with self:
            if not self._is_mounted:
                return
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

    async def _set_company_and_price_error(
        self,
        *,
        ticker: str,
        error: Exception,
    ) -> None:
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
            self.error_company = str(error)

    @rx.event(background=True)
    async def auto_load_data(self):
        # Wait for ticker to hydrate from the router
        ticker = await self._await_hydrated_ticker()

        async with self:
            if not self._is_mounted:
                return
            if not ticker:
                self._is_loading_company = False
                self._is_loading_financial = False
                self._is_loading_price = False
                return
            self._reset_data_state(ticker)
            prefs = await self.get_state(PrefsState)
            price_chart = await self.get_state(PriceChartState)
            price_chart.selected_interval = prefs.default_chart_period or "1M"

        # ── Company + price data ──────────────────────────────────────────────
        try:
            company_data = fetch_company_data(ticker)
            price_data = await fetch_price_data_async(ticker)
            await self._apply_company_and_price_data(
                ticker=ticker,
                company_data=company_data,
                price_data=price_data,
            )

        except (AttributeError, ValueError, KeyError, RuntimeError) as e:
            await self._set_company_and_price_error(ticker=ticker, error=e)

        async with self:
            if not self._is_mounted:
                return
            switch_value = self.switch_value

        # ── Financial / transformed dataframes ───────────────────────────────
        await self._load_financial_data(ticker, switch_value)

        async with self:
            if not self._is_mounted:
                return

        yield PriceChartState.load_state(ticker)

        async with self:
            self._data_loaded = True

    def set_selected_tab(self, value: str) -> None:
        self.selected_tab = value

    @rx.event(background=True)
    async def toggle_switch(self, value: bool):  # noqa: FBT001
        async with self:
            if not check_session_active(self):
                return
            self.switch_value = "year" if value else "quarter"
            self.transformed_dataframes = {}
            self.available_metrics_by_category = {}
            self.selected_metrics = {}
            self.income_statement = []
            self.balance_sheet = []
            self.cash_flow = []
            self._is_loading_financial = True
            self.error_financial = ""
            ticker = self.ticker
            switch_value = self.switch_value

        await self._load_financial_data(ticker, switch_value)

    @rx.event(background=True)
    async def reload_for_framework_change(self):
        async with self:
            if not check_session_active(self):
                return
            self.transformed_dataframes = {}
            self.available_metrics_by_category = {}
            self.selected_metrics = {}
            self._last_framework_id = None
            ticker = self.ticker
            switch_value = self.switch_value

        await self._load_financial_data(ticker, switch_value)

    async def _load_financial_data(self, ticker: str, switch_value: str) -> None:  # noqa: C901, PLR0912, PLR0915
        """Fetch and process financial data, writing results to state.

        Plain coroutine (no @rx.event) so it can be directly awaited from
        background tasks. All state writes use `async with self`.
        """
        try:
            result = await get_transformed_dataframes(ticker, period=switch_value)

            if "error" in result:
                async with self:
                    self._is_loading_financial = False
                    self.error_financial = result["error"]
                return

            async with self:
                if not self._is_mounted:
                    return
                self.transformed_dataframes = result
                self.income_statement = result.get("transformed_income_statement", [])
                self.balance_sheet = result.get("transformed_balance_sheet", [])
                self.cash_flow = result.get("transformed_cash_flow", [])

        except (ValueError, RuntimeError, KeyError) as e:
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

        # Read what we need under the lock, then process outside it
        async with self:
            global_state = await self.get_state(GlobalFrameworkState)
            has_selected_framework = global_state.has_selected_framework
            framework_metrics = global_state.framework_metrics
            self._last_framework_id = global_state.selected_framework_id
            transformed_dataframes = self.transformed_dataframes

        categorized_ratios = transformed_dataframes.get("categorized_ratios", {})
        all_available_metrics: dict[str, list[str]] = {}

        for category, financial_data in categorized_ratios.items():
            rows = self._extract_category_rows(financial_data)
            if rows:
                excluded_columns = {"Year", "Quarter", "Date", "Period"}
                metrics = [col for col in rows[0] if col not in excluded_columns]
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
                    elif (
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
                    if metrics:
                        self.selected_metrics[category] = metrics[0]

            self._is_loading_financial = False
            self.error_financial = ""

    # ============================================================================
    # REGULAR EVENT HANDLERS
    # ============================================================================

    @rx.event
    def set_metric_for_category(self, category: str, metric: str):
        self.selected_metrics[category] = metric

    @staticmethod
    def _extract_category_rows(financial_data: object) -> list[dict[str, object]]:
        if isinstance(financial_data, list):
            rows = financial_data
        elif (
            isinstance(financial_data, tuple)
            and len(financial_data) >= _CATEGORY_DATA_TUPLE_MIN_ITEMS
            and isinstance(financial_data[1], list)
        ):
            rows = financial_data[1]
        else:
            return []

        return [cast("dict[str, object]", row) for row in rows if isinstance(row, dict)]

    @rx.var(cache=True)
    def get_chart_data_for_category(self) -> dict[str, list[dict[str, object]]]:
        chart_data: dict[str, list[dict[str, object]]] = {}
        categorized_ratios = self.transformed_dataframes.get("categorized_ratios", {})
        if not isinstance(categorized_ratios, dict):
            return chart_data
        categorized_ratios_map = cast("dict[str, object]", categorized_ratios)

        for category, selected_metric in self.selected_metrics.items():
            data = categorized_ratios_map.get(category)
            rows = self._extract_category_rows(data)
            if not rows:
                chart_data[category] = []
                continue
            chart_data[category] = self._chart_points_from_rows(
                cast("list[object]", rows),
                selected_metric,
            )

        return chart_data

    @staticmethod
    def _chart_points_from_rows(
        rows: list[object],
        selected_metric: str,
    ) -> list[dict[str, object]]:
        if not rows:
            return []

        first_row = rows[0]
        if not isinstance(first_row, dict):
            return []

        first_row_map = cast("dict[str, object]", first_row)
        if selected_metric not in first_row_map:
            return []

        chart_points: list[dict[str, object]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_map = cast("dict[str, object]", row)
            year = row_map.get("Year", "")
            value = row_map.get(selected_metric)
            value_str = "" if value is None else str(value).strip()

            try:
                if value_str and value_str.lower() not in ["nan", "none"]:
                    value_float = float(value_str.replace(",", ""))
                else:
                    value_float = 0.0
            except (ValueError, TypeError):
                value_float = 0.0

            chart_points.append({"year": year, "value": value_float})

        return chart_points[-8:]

    def get_chart_data(self, category: str) -> list[dict[str, object]]:
        return self.get_chart_data_for_category.get(category, [])

    @rx.var(cache=True)
    def get_categories_list(self) -> list[str]:
        return list(self.available_metrics_by_category.keys())

    @rx.var
    def pie_data(self) -> list[dict[str, object]]:
        if not self.shareholders:
            return []

        try:
            colors = [
                "var(--violet-7)",
                "var(--indigo-7)",
                "var(--blue-7)",
                "var(--teal-7)",
                "var(--cyan-7)",
                "var(--plum-7)",
                "var(--purple-7)",
                "var(--gray-7)",
                "var(--sage-7)",
            ]

            pie_data = [
                {"name": s["share_holder"], "value": s["share_own_percent"]}
                for s in self.shareholders
            ]
            for idx, d in enumerate(pie_data):
                d["fill"] = colors[idx % len(colors)]
        except (ValueError, KeyError, IndexError):
            return []
        else:
            return pie_data

    @rx.var(cache=True)
    def overview(self) -> dict:
        if self.overview_df.empty:
            return {}
        try:
            return self.overview_df.iloc[0].to_dict()
        except (IndexError, ValueError, KeyError):
            return {}

    @rx.var(cache=True)
    def profile(self) -> dict:
        if self.profile_df.empty:
            return {}
        try:
            return self.profile_df.iloc[0].to_dict()
        except (IndexError, ValueError, KeyError):
            return {}

    @rx.var(cache=True)
    def shareholders(self) -> list[dict]:
        if self.shareholders_df.empty:
            return []
        try:
            return self.shareholders_df.to_dict("records")
        except (ValueError, KeyError, TypeError):
            return []

    @rx.var(cache=True)
    def events(self) -> list[dict]:
        if self.events_df.empty:
            return []
        try:
            return self.events_df.to_dict("records")
        except (ValueError, KeyError, TypeError):
            return []

    @rx.var(cache=True)
    def news(self) -> list[dict]:
        if self.news_df.empty:
            return []
        try:
            return self.news_df.to_dict("records")
        except (ValueError, KeyError, TypeError):
            return []

    @rx.var(cache=True)
    def officers(self) -> list[dict]:
        if self.officers_df.empty:
            return []
        try:
            return self.officers_df.to_dict("records")
        except (ValueError, KeyError, TypeError):
            return []

    @rx.event
    def set_profile_dialog_open(self, value: bool):  # noqa: FBT001
        self.profile_dialog_open = value
