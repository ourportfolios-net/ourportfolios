"""State management for the select page."""

import reflex as rx
import asyncio
from typing import Any

from ...state import TickerBoardState
from ...utils.database.database import get_company_session
from ...utils.session_manager import (
    SessionIsolatedStateMixin,
    session_isolated,
)
from sqlalchemy import text


class State(SessionIsolatedStateMixin, rx.State):
    control: str = "home"
    show_arrow: bool = True
    data: list[dict] = []

    # Search bar
    search_query = ""
    display_suggestions: bool = False
    ticker_suggestions_list: list[dict[str, Any]] = []

    _data_loaded: bool = False

    def on_mount(self):
        """Initialize session and trigger background data loading."""
        old_session = getattr(self, "_session_id", None)
        super().on_mount()

        new_session = getattr(self, "_session_id", None)
        if old_session != new_session:
            self._data_loaded = False

        return State.auto_load_data

    def on_unmount(self):
        """Clean up when page is unmounted."""
        super().on_unmount()

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

            await self.get_all_industries()

            if not self.is_mounted():
                return

            await self.get_all_exchanges()

            if not self.is_mounted():
                return

            self.get_fundamentals_default_value()
            self.get_technicals_default_value()
            self.search_query = ""

            ticker_board_state = await self.get_state(TickerBoardState)
            await ticker_board_state.load_all_tickers_cache()

            self._data_loaded = True

    @rx.event
    def set_control(self, value: str | list[str]):
        if isinstance(value, list):
            self.control = value[0] if value else "home"
        else:
            self.control = value

    # Metrics
    fundamentals_default_value: dict[str, list[float]] = {
        "pe": [0.00, 100.00],
        "pb": [0.00, 10.00],
        "roe": [0.00, 100.00],
        "roa": [0.00, 100.00],
        "doe": [0.00, 10.00],
        "eps": [100.00, 10000.00],
        "ps": [0.00, 100.00],
        "gross_margin": [0.00, 200.00],
        "net_margin": [0.00, 200.00],
        "ev": [0.00, 100.00],
        "ev_ebitda": [0.00, 200.00],
        "dividend_yield": [0.00, 100.00],
    }
    technicals_default_value: dict[str, list[float]] = {
        "rsi14": [0.00, 100.00],
        "alpha": [0.00, 5.00],
        "beta": [0.00, 5.00],
    }

    # Sorts
    selected_sort_order: str = "ASC"
    selected_sort_option: str = "A-Z"

    sort_orders: list[str] = ["ASC", "DESC"]
    sort_options: dict[str, str] = {
        "A-Z": "symbol",
        "Market Cap": "market_cap",
        "% Change": "pct_price_change",
        "Volume": "accumulated_volume",
    }

    # Filters
    selected_exchange: set[str] = set()
    selected_industry: set[str] = set()
    selected_technical_metric: set[str] = set()
    selected_fundamental_metric: set[str] = set()

    exchange_filter: dict[str, bool] = {}
    industry_filter: dict[str, bool] = {}
    technicals_current_value: dict[str, list[float]] = {}
    fundamentals_current_value: dict[str, list[float]] = {}

    def update_arrow(self, scroll_position: int, max_scroll: int):
        self.show_arrow = scroll_position < max_scroll - 10

    @rx.var
    def has_filter(self) -> bool:
        if (
            len(self.selected_industry) > 0
            or len(self.selected_exchange) > 0
            or len(self.selected_fundamental_metric) > 0
            or len(self.selected_technical_metric) > 0
        ):
            return True
        return False

    @rx.event(background=True)
    @session_isolated
    async def apply_filters(self):
        async with self:
            ticker_board_state = await self.get_state(TickerBoardState)
            ticker_board_state.apply_filters(
                filters={
                    "industry": self.selected_industry,
                    "exchange": self.selected_exchange,
                    "fundamental": {
                        metric: self.fundamentals_current_value[metric]
                        for metric in self.selected_fundamental_metric
                    },
                    "technical": {
                        metric: self.technicals_current_value[metric]
                        for metric in self.selected_technical_metric
                    },
                }
            )

    # set all metrics/options to their default setting
    @rx.event
    @session_isolated
    async def get_all_industries(self):
        """Load all available industries from database."""
        await asyncio.sleep(0)

        try:
            async with get_company_session() as session:
                result = await session.execute(
                    text("SELECT DISTINCT industry FROM tickers.overview_df")
                )
                industries = [row[0] for row in result.all()]
                self.industry_filter: dict[str, bool] = {
                    item: False for item in industries
                }
        except Exception:
            self.industry_filter: dict[str, bool] = {}

    @rx.event
    @session_isolated
    async def get_all_exchanges(self):
        """Load all available exchanges from database."""
        await asyncio.sleep(0)

        try:
            async with get_company_session() as session:
                result = await session.execute(
                    text("SELECT DISTINCT exchange FROM tickers.overview_df")
                )
                exchanges = [row[0] for row in result.all()]
                self.exchange_filter: dict[str, bool] = {
                    item: False for item in exchanges
                }
        except Exception:
            self.exchange_filter: dict[str, bool] = {}

    @rx.event
    def get_fundamentals_default_value(self):
        self.fundamentals_current_value: dict[str, list[float]] = dict.fromkeys(
            self.fundamentals_default_value, [0.00, 0.00]
        )

    @rx.event
    def get_technicals_default_value(self):
        self.technicals_current_value: dict[str, list[float]] = dict.fromkeys(
            self.technicals_default_value, [0.00, 0.00]
        )

    # Search bar with suggestions
    @rx.event
    def show_suggestions(self):
        """Show suggestion dropdown."""
        self.display_suggestions = True

    @rx.event
    def hide_suggestions(self):
        """Hide suggestion dropdown with a delay."""
        self.display_suggestions = False

    @rx.event
    def set_search_query(self, value: str):
        """Set search query with instant update."""
        self.search_query = value
        return TickerBoardState.set_search_query(value)

    # Filter event handlers

    @rx.event(background=True)
    async def set_sort_option(self, option: str):
        async with self:
            self.selected_sort_option = option

        yield

        async with self:
            ticker_board_state = await self.get_state(TickerBoardState)
            ticker_board_state.set_sort_option(self.sort_options[option])

    @rx.event(background=True)
    async def set_sort_order(self, order: str):
        async with self:
            self.selected_sort_order = order
        yield

        async with self:
            ticker_board_state = await self.get_state(TickerBoardState)
            ticker_board_state.set_sort_order(order)

    @rx.event(background=True)
    async def set_exchange(self, exchange: str, value: bool):
        async with self:
            self.exchange_filter[exchange] = value

        yield

        async with self:
            if value is True:
                self.selected_exchange.add(exchange)
            else:
                self.selected_exchange.discard(exchange)

    @rx.event(background=True)
    async def set_industry(self, industry: str, value: bool):
        async with self:
            self.industry_filter[industry] = value

        yield

        async with self:
            if value is True:
                self.selected_industry.add(industry)
            else:
                self.selected_industry.discard(industry)

    @rx.event(background=True)
    async def set_fundamental_metric(self, metric: str, value: list[float]):
        async with self:
            self.fundamentals_current_value[metric] = value

        yield

        async with self:
            if (
                sum(value) > 0
                and sum(value) < self.fundamentals_default_value[metric][1]
            ):
                self.selected_fundamental_metric.add(metric)
            else:
                self.selected_fundamental_metric.discard(metric)

    @rx.event(background=True)
    async def set_technical_metric(self, metric: str, value: list[float]):
        async with self:
            self.technicals_current_value[metric] = value

        yield

        async with self:
            if sum(value) > 0 and sum(value) < self.technicals_default_value[metric][1]:
                self.selected_technical_metric.add(metric)
            else:
                self.selected_technical_metric.discard(metric)

    # Clear filters

    @rx.event(background=True)
    async def clear_all_filters(self):
        async with self:
            self.selected_technical_metric = set()
            self.selected_fundamental_metric = set()
            self.selected_industry = set()
            self.selected_exchange = set()

        yield

        async with self:
            ticker_board_state = await self.get_state(TickerBoardState)
            tasks = [
                rx.run_in_thread(ticker_board_state.clear_all_filters),
                rx.run_in_thread(self.get_technicals_default_value),
                rx.run_in_thread(self.get_fundamentals_default_value),
                rx.run_in_thread(self.get_all_industries),
                rx.run_in_thread(self.get_all_exchanges),
            ]
            await asyncio.gather(*tasks)
