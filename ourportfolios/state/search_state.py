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

# Module-level dict tracking background load tasks per client token.
# asyncio.Task cannot be stored as a Reflex state field, and self is
# immutable outside `async with self` in background tasks.
_load_tasks: dict[str, asyncio.Task] = {}


class SearchBarState(rx.State):
    search_query: str = ""
    comparison_search_query: str = ""
    display_suggestion: bool = False
    empty_state_display_suggestion: bool = False
    outstanding_tickers: dict[str, Any] = {}
    ticker_list: list[dict[str, Any]] = []
    comparison_suggestions: list[dict[str, Any]] = []
    suggest_tickers: list[dict[str, Any]] = []

    @rx.event
    def set_query(self, text: str = "") -> None:
        self.search_query = text
        return SearchBarState.fetch_suggest_tickers

    @rx.event(background=True)
    async def set_comparison_query(self, text: str = "") -> None:
        async with self:
            self.comparison_search_query = text
        if not text:
            async with self:
                self.comparison_suggestions = list(self.ticker_list[:30])
            return
        result = await self._fetch_by_prefix(text)
        if not result:
            result = await self._fetch_by_permutations(text)
        if not result:
            result = await self._fetch_by_prefix(text[0])
        async with self:
            self.comparison_suggestions = result

    @rx.event
    def focus_comparison_search(self) -> None:
        self.empty_state_display_suggestion = True
        if not self.comparison_search_query:
            self.comparison_suggestions = list(self.ticker_list[:30])

    @rx.event
    def blur_comparison_search(self) -> None:
        yield time.sleep(0.15)
        self.empty_state_display_suggestion = False

    @rx.event
    def clear_comparison_search(self) -> None:
        self.comparison_search_query = ""
        self.empty_state_display_suggestion = False
        self.comparison_suggestions = []

    @rx.event(background=True)
    async def fetch_suggest_tickers(self) -> None:
        async with self:
            if not self.display_suggestion:
                self.suggest_tickers = []
                return
            query = self.search_query
            if not query:
                self.suggest_tickers = list(self.ticker_list)
                return
        result = await self._fetch_by_prefix(query)
        if not result:
            result = await self._fetch_by_permutations(query)
        if not result:
            result = await self._fetch_by_prefix(query[0])
        async with self:
            self.suggest_tickers = result

    @rx.event
    def set_display_suggestions(self, state: bool):
        yield time.sleep(0.2)
        self.display_suggestion = state
        if state:
            return SearchBarState.fetch_suggest_tickers

    @rx.event
    def set_empty_state_display_suggestions(self, state: bool):
        yield time.sleep(0.2)
        self.empty_state_display_suggestion = state

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
        async with self:
            token = self.router.session.client_token

        # Prevent duplicate background loops for this client
        existing = _load_tasks.get(token)
        if existing is not None and not existing.done():
            return

        async def _load_loop() -> None:
            try:
                while True:
                    try:
                        rows = await self._fetch_tickers()
                        async with self:
                            self.ticker_list = rows
                            self.outstanding_tickers = {
                                item["symbol"]: 1 for item in rows[:3]
                            }
                    except asyncio.CancelledError:
                        return
                    except Exception as e:
                        print(f"Error in load_state: {e}")
                    try:
                        await asyncio.sleep(60)
                    except asyncio.CancelledError:
                        return
            finally:
                _load_tasks.pop(token, None)

        _load_tasks[token] = asyncio.create_task(_load_loop())
