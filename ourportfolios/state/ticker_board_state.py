"""Ticker board state for filtering and displaying ticker lists."""

import reflex as rx
from typing import Any
from sqlalchemy import select, func, and_
from ..utils.database.database import get_company_session
from ..utils.database.models import PriceORM, ProfileORM, OverviewORM, StatsORM


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
            self.selected_exchange = set(filters["exchange"])
        if "industry" in filters:
            self.selected_industry = set(filters["industry"])
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

    @staticmethod
    async def _fetch_tickers_data() -> list[dict[str, Any]]:
        """Execute the raw DB query outside any state lock and return the rows."""
        async with get_company_session() as session:
            # Subquery: latest stats row id per symbol
            latest_stats = (
                select(
                    StatsORM.symbol.label("stats_symbol"),
                    func.max(StatsORM.id).label("max_id"),
                )
                .group_by(StatsORM.symbol)
                .subquery()
            )

            # Metric columns derived from the ORM model
            metric_col_names = [
                c.name
                for c in StatsORM.__table__.columns
                if c.name not in ("id", "symbol")
            ]
            stats_columns = [getattr(StatsORM, n) for n in metric_col_names]

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
                    *stats_columns,
                )
                .join(ProfileORM, PriceORM.symbol == ProfileORM.symbol)
                .join(OverviewORM, PriceORM.symbol == OverviewORM.symbol)
                .outerjoin(
                    latest_stats,
                    PriceORM.symbol == latest_stats.c.stats_symbol,
                )
                .outerjoin(
                    StatsORM,
                    and_(
                        StatsORM.symbol == latest_stats.c.stats_symbol,
                        StatsORM.id == latest_stats.c.max_id,
                    ),
                )
                .order_by(PriceORM.accumulated_volume.desc())
            )
            result = await session.execute(stmt)
            return [dict(row) for row in result.mappings().all()]

    @rx.event
    async def load_all_tickers_cache(self) -> None:
        if self._cache_loaded:
            return
        try:
            rows = await TickerBoardState._fetch_tickers_data()
            self._all_tickers_cache = rows
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

    @staticmethod
    def _passes_metric_filters(
        ticker: dict[str, Any], metrics: dict[str, list[float]]
    ) -> bool:
        """Return True if ticker passes every metric range filter."""
        for metric, bounds in metrics.items():
            if len(bounds) != 2:
                continue
            lo, hi = bounds[0], bounds[1]
            val = ticker.get(metric)
            if val is None:
                return False
            try:
                if not (lo <= float(val) <= hi):
                    return False
            except (ValueError, TypeError):
                return False
        return True

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

        if self.selected_fundamental_metric:
            results = [
                t
                for t in results
                if self._passes_metric_filters(t, self.selected_fundamental_metric)
            ]

        if self.selected_technical_metric:
            results = [
                t
                for t in results
                if self._passes_metric_filters(t, self.selected_technical_metric)
            ]

        if self.selected_sort_option and results:
            reverse = self.selected_sort_order == "DESC"
            results = sorted(
                results,
                key=lambda x: x.get(self.selected_sort_option, 0) or 0,
                reverse=reverse,
            )

        return results
