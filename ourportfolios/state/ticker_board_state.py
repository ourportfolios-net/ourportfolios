"""Ticker board state for filtering and displaying ticker lists."""

import reflex as rx
from typing import Any
from sqlalchemy import select
from ..utils.database.database import get_company_session
from ..utils.database.models import PriceORM, ProfileORM, OverviewORM


class TickerBoardState(rx.State):
    search_query: str = ""

    _all_tickers_cache: list[dict[str, Any]] = []
    _cache_loaded: bool = False

    selected_exchange: set[str] = set()
    selected_industry: set[str] = set()
    selected_technical_metric: dict[str, list[float]] = {}
    selected_fundamental_metric: dict[str, list[float]] = {}

    selected_sort_order: str = "ASC"
    selected_sort_option: str = "symbol"

    @rx.event
    def apply_filters(self, filters: dict[str, Any]) -> None:
        if "exchange" in filters:
            self.selected_exchange = filters["exchange"]
        if "industry" in filters:
            self.selected_industry = filters["industry"]
        if "fundamental" in filters:
            self.selected_fundamental_metric = filters["fundamental"]
        if "technical" in filters:
            self.selected_technical_metric = filters["technical"]

    @rx.event
    def clear_all_filters(self) -> None:
        self.selected_exchange = set()
        self.selected_industry = set()
        self.selected_technical_metric = {}
        self.selected_fundamental_metric = {}

    @rx.event
    def set_search_query(self, value: str) -> None:
        self.search_query = value

    @rx.event
    async def load_all_tickers_cache(self) -> None:
        if self._cache_loaded:
            return
        try:
            async with get_company_session() as session:
                stmt = (
                    select(
                        PriceORM.symbol,
                        PriceORM.current_price,
                        PriceORM.accumulated_volume,
                        PriceORM.pct_price_change,
                        ProfileORM.company_name,
                        OverviewORM.market_cap,
                        OverviewORM.industry,
                        OverviewORM.exchange,
                    )
                    .join(ProfileORM, PriceORM.symbol == ProfileORM.symbol)
                    .join(OverviewORM, PriceORM.symbol == OverviewORM.symbol)
                    .order_by(PriceORM.accumulated_volume.desc())
                )
                result = await session.execute(stmt)
                self._all_tickers_cache = [dict(row) for row in result.mappings().all()]
                self._cache_loaded = True
        except Exception as e:
            print(
                f"TICKER BOARD ERROR: Failed to load ticker cache: {type(e).__name__}: {e}"
            )

    @rx.event
    def set_sort_option(self, option: str) -> None:
        self.selected_sort_option = option

    @rx.event
    def set_sort_order(self, order: str) -> None:
        self.selected_sort_order = order

    @rx.var(cache=True)
    def get_all_tickers(self) -> list[dict[str, Any]]:
        if not self._cache_loaded or not self._all_tickers_cache:
            return []

        results: list[dict[str, Any]] = list(self._all_tickers_cache)

        if self.search_query:
            search_upper = self.search_query.upper()
            results = [
                t for t in results if str(t.get("symbol", "")).startswith(search_upper)
            ]

        if self.selected_industry:
            results = [
                t for t in results if t.get("industry") in self.selected_industry
            ]

        if self.selected_exchange:
            results = [
                t for t in results if t.get("exchange") in self.selected_exchange
            ]

        if self.selected_sort_option and results:
            reverse = self.selected_sort_order == "DESC"
            results = sorted(
                results,
                key=lambda x: x.get(self.selected_sort_option, 0) or 0,
                reverse=reverse,
            )

        return results
