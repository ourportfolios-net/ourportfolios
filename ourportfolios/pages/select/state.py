"""State management for the select page."""

import reflex as rx
import asyncio
from typing import Any
from sqlalchemy import select, distinct

from ...state import TickerBoardState
from ...utils.database.database import get_company_session
from ...utils.database.models import OverviewORM
from ...utils.session_manager import SessionIsolatedStateMixin, session_isolated


class State(SessionIsolatedStateMixin, rx.State):
    control: str = "home"
    show_arrow: bool = True
    data: list[dict] = []

    search_query: str = ""
    display_suggestions: bool = False
    ticker_suggestions_list: list[dict[str, Any]] = []

    _data_loaded: bool = False

    def on_mount(self):
        old_session = getattr(self, "_session_id", None)
        super().on_mount()
        new_session = getattr(self, "_session_id", None)
        if old_session != new_session:
            self._data_loaded = False
        return State.auto_load_data

    def on_unmount(self):
        super().on_unmount()

    @rx.event(background=True)
    @session_isolated
    async def auto_load_data(self) -> None:
        async with self:
            if self._data_loaded or not self.is_mounted():
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
    def set_control(self, value: str | list[str]) -> None:
        if isinstance(value, list):
            self.control = value[0] if value else "home"
        else:
            self.control = value

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

    selected_sort_order: str = "ASC"
    selected_sort_option: str = "A-Z"

    sort_orders: list[str] = ["ASC", "DESC"]
    sort_options: dict[str, str] = {
        "A-Z": "symbol",
        "Market Cap": "market_cap",
        "% Change": "pct_price_change",
        "Volume": "accumulated_volume",
    }

    selected_exchange: set[str] = set()
    selected_industry: set[str] = set()
    selected_technical_metric: set[str] = set()
    selected_fundamental_metric: set[str] = set()

    exchange_filter: dict[str, bool] = {}
    industry_filter: dict[str, bool] = {}
    technicals_current_value: dict[str, list[float]] = {}
    fundamentals_current_value: dict[str, list[float]] = {}

    def update_arrow(self, scroll_position: int, max_scroll: int) -> None:
        self.show_arrow = scroll_position < max_scroll - 10

    @rx.var
    def has_filter(self) -> bool:
        return bool(
            self.selected_industry
            or self.selected_exchange
            or self.selected_fundamental_metric
            or self.selected_technical_metric
        )

    @rx.event(background=True)
    @session_isolated
    async def apply_filters(self) -> None:
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

    @rx.event
    @session_isolated
    async def get_all_industries(self) -> None:
        try:
            async with get_company_session() as session:
                stmt = select(distinct(OverviewORM.industry))
                result = await session.execute(stmt)
                industries = [row[0] for row in result.all() if row[0] is not None]
                self.industry_filter = {item: False for item in industries}
        except Exception as e:
            print(
                f"SELECT PAGE ERROR: Failed to load industries: {type(e).__name__}: {e}"
            )
            self.industry_filter = {}

    @rx.event
    @session_isolated
    async def get_all_exchanges(self) -> None:
        try:
            async with get_company_session() as session:
                stmt = select(distinct(OverviewORM.exchange))
                result = await session.execute(stmt)
                exchanges = [row[0] for row in result.all() if row[0] is not None]
                self.exchange_filter = {item: False for item in exchanges}
        except Exception as e:
            print(
                f"SELECT PAGE ERROR: Failed to load exchanges: {type(e).__name__}: {e}"
            )
            self.exchange_filter = {}

    @rx.event
    def get_fundamentals_default_value(self) -> None:
        self.fundamentals_current_value = {
            key: [0.00, 0.00] for key in self.fundamentals_default_value
        }

    @rx.event
    def get_technicals_default_value(self) -> None:
        self.technicals_current_value = {
            key: [0.00, 0.00] for key in self.technicals_default_value
        }

    @rx.event
    def show_suggestions(self) -> None:
        self.display_suggestions = True

    @rx.event
    def hide_suggestions(self) -> None:
        self.display_suggestions = False

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value
        return TickerBoardState.set_search_query(value)

    @rx.event(background=True)
    async def set_sort_option(self, option: str) -> None:
        async with self:
            self.selected_sort_option = option
        yield
        async with self:
            ticker_board_state = await self.get_state(TickerBoardState)
            ticker_board_state.set_sort_option(self.sort_options[option])

    @rx.event(background=True)
    async def set_sort_order(self, order: str) -> None:
        async with self:
            self.selected_sort_order = order
        yield
        async with self:
            ticker_board_state = await self.get_state(TickerBoardState)
            ticker_board_state.set_sort_order(order)

    @rx.event(background=True)
    async def set_exchange(self, exchange: str, value: bool) -> None:
        async with self:
            self.exchange_filter[exchange] = value
        yield
        async with self:
            if value:
                self.selected_exchange.add(exchange)
            else:
                self.selected_exchange.discard(exchange)

    @rx.event(background=True)
    async def set_industry(self, industry: str, value: bool) -> None:
        async with self:
            self.industry_filter[industry] = value
        yield
        async with self:
            if value:
                self.selected_industry.add(industry)
            else:
                self.selected_industry.discard(industry)

    @rx.event(background=True)
    async def set_fundamental_metric(self, metric: str, value: list[float]) -> None:
        async with self:
            self.fundamentals_current_value[metric] = value
        yield
        async with self:
            upper = self.fundamentals_default_value[metric][1]
            if sum(value) > 0 and sum(value) < upper:
                self.selected_fundamental_metric.add(metric)
            else:
                self.selected_fundamental_metric.discard(metric)

    @rx.event(background=True)
    async def set_technical_metric(self, metric: str, value: list[float]) -> None:
        async with self:
            self.technicals_current_value[metric] = value
        yield
        async with self:
            upper = self.technicals_default_value[metric][1]
            if sum(value) > 0 and sum(value) < upper:
                self.selected_technical_metric.add(metric)
            else:
                self.selected_technical_metric.discard(metric)

    @rx.event(background=True)
    async def clear_all_filters(self) -> None:
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
