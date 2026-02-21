"""Search bar state for ticker search and suggestions."""

import reflex as rx
import time
import asyncio
import itertools
from collections.abc import Callable
from typing import Any

from sqlalchemy import Select, select, or_
from ..utils.database.database import get_company_session
from ..utils.database.models import PriceORM, OverviewORM

_TickerSelect = Select[tuple[str, float | None, float | None, str | None]]


class SearchBarState(rx.State):
    search_query: str = ""
    comparison_search_query: str = ""
    display_suggestion: bool = False
    empty_state_display_suggestion: bool = False
    outstanding_tickers: dict[str, Any] = {}
    ticker_list: list[dict[str, Any]] = []

    @rx.event
    def set_query(self, text: str = "") -> None:
        self.search_query = text

    @rx.event
    def set_comparison_query(self, text: str = "") -> None:
        self.comparison_search_query = text

    @rx.event
    def set_display_suggestions(self, state: bool):
        yield time.sleep(0.2)
        self.display_suggestion = state

    @rx.event
    def set_empty_state_display_suggestions(self, state: bool):
        yield time.sleep(0.2)
        self.empty_state_display_suggestion = state

    @rx.var
    async def get_suggest_ticker(self) -> list[dict[str, Any]]:
        if not self.display_suggestion:
            return []
        if not self.search_query:
            return self.ticker_list
        result = await self._fetch_by_prefix(self.search_query)
        if not result:
            result = await self._fetch_by_permutations(self.search_query)
        if not result:
            result = await self._fetch_by_prefix(self.search_query[0])
        return result

    @rx.var
    async def get_comparison_suggest_ticker(self) -> list[dict[str, Any]]:
        if not self.empty_state_display_suggestion:
            return []
        if not self.comparison_search_query:
            return self.ticker_list
        result = await self._fetch_by_prefix(self.comparison_search_query)
        if not result:
            result = await self._fetch_by_permutations(self.comparison_search_query)
        if not result:
            result = await self._fetch_by_prefix(self.comparison_search_query[0])
        return result

    async def _fetch_by_prefix(self, prefix: str) -> list[dict[str, Any]]:
        return await self._fetch_tickers(
            lambda q: q.where(PriceORM.symbol.like(f"{prefix}%"))
        )

    async def _fetch_by_permutations(self, query: str) -> list[dict[str, Any]]:
        combos = list(itertools.permutations(list(query), len(query)))
        patterns = list({"".join(c) + "%" for c in combos})
        return await self._fetch_tickers(
            lambda q: q.where(or_(*(PriceORM.symbol.like(p) for p in patterns)))
        )

    async def _fetch_tickers(
        self,
        filter_fn: Callable[[_TickerSelect], _TickerSelect] | None = None,
    ) -> list[dict[str, Any]]:
        try:
            async with get_company_session() as session:
                stmt: _TickerSelect = (
                    select(
                        PriceORM.symbol,
                        PriceORM.pct_price_change,
                        PriceORM.accumulated_volume,
                        OverviewORM.industry,
                    )
                    .join(OverviewORM, PriceORM.symbol == OverviewORM.symbol)
                    .order_by(PriceORM.accumulated_volume.desc())
                )
                if filter_fn is not None:
                    stmt = filter_fn(stmt)
                result = await session.execute(stmt)
                return [dict(row) for row in result.mappings().all()]
        except Exception as e:
            print(f"Database error in _fetch_tickers: {e}")
            return []

    @rx.event(background=True)
    async def load_state(self) -> None:
        while True:
            rows = await self._fetch_tickers()
            async with self:
                self.ticker_list = rows
                self.outstanding_tickers = {item["symbol"]: 1 for item in rows[:3]}
            await asyncio.sleep(60)
