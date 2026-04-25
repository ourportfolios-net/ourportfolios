"""Ticker board state for filtering and displaying ticker lists."""

import reflex as rx
from sqlalchemy import and_, func, select

from ourportfolios.utils.database.database import get_company_session
from ourportfolios.utils.database.models import (
    OverviewORM,
    PriceORM,
    ProfileORM,
    StatsORM,
)


class TickerBoardState(rx.State):
    search_query: str = ""

    tickers_data: rx.Field[list[dict[str, object]]] = rx.Field(
        default_factory=list,
    )
    load_error: str = ""

    selected_exchange: rx.Field[set[str]] = rx.Field(default_factory=set)
    selected_industry: rx.Field[set[str]] = rx.Field(default_factory=set)
    selected_technical_metric: rx.Field[dict[str, list[float]]] = rx.Field(
        default_factory=dict,
    )
    selected_fundamental_metric: rx.Field[dict[str, list[float]]] = rx.Field(
        default_factory=dict,
    )

    selected_sort_order: str = "ASC"
    selected_sort_option: str = "symbol"

    @rx.event
    def apply_filters(self, filters: dict[str, object]) -> None:
        exchange = filters.get("exchange")
        if isinstance(exchange, list | set | tuple):
            self.selected_exchange = {str(item) for item in exchange}

        industry = filters.get("industry")
        if isinstance(industry, list | set | tuple):
            self.selected_industry = {str(item) for item in industry}

        fundamental = filters.get("fundamental")
        if isinstance(fundamental, dict):
            self.selected_fundamental_metric = {
                str(key): [float(v) for v in value if isinstance(v, int | float)]
                for key, value in fundamental.items()
                if isinstance(value, list)
            }

        technical = filters.get("technical")
        if isinstance(technical, dict):
            self.selected_technical_metric = {
                str(key): [float(v) for v in value if isinstance(v, int | float)]
                for key, value in technical.items()
                if isinstance(value, list)
            }

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
    async def _fetch_tickers_data() -> list[dict[str, object]]:
        """Execute the full ticker query (with stats) and return rows."""
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
                # Keep price rows visible even when profile/overview lag behind.
                .outerjoin(ProfileORM, PriceORM.symbol == ProfileORM.symbol)
                .outerjoin(OverviewORM, PriceORM.symbol == OverviewORM.symbol)
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

    @staticmethod
    async def _fetch_tickers_data_fallback() -> list[dict[str, object]]:
        """Fallback query that avoids stats table dependencies."""
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
                .outerjoin(ProfileORM, PriceORM.symbol == ProfileORM.symbol)
                .outerjoin(OverviewORM, PriceORM.symbol == OverviewORM.symbol)
                .order_by(PriceORM.accumulated_volume.desc())
            )
            result = await session.execute(stmt)
            return [dict(row) for row in result.mappings().all()]

    @rx.event
    async def load_tickers(self) -> None:
        try:
            rows = await TickerBoardState._fetch_tickers_data()
            self.tickers_data = rows
            self.load_error = ""
        except Exception:  # noqa: BLE001
            try:
                rows = await TickerBoardState._fetch_tickers_data_fallback()
                self.tickers_data = rows
                self.load_error = ""
            except Exception:  # noqa: BLE001
                self.tickers_data = []
                self.load_error = "Failed to load ticker data."

    @rx.event
    def set_sort_option(self, option: str) -> None:
        self.selected_sort_option = option

    @rx.event
    def set_sort_order(self, order: str) -> None:
        self.selected_sort_order = order

    @staticmethod
    def _passes_metric_filters(
        ticker: dict[str, object],
        metrics: dict[str, list[float]],
    ) -> bool:
        """Return True if ticker passes every metric range filter."""
        metric_bounds_count = 2
        for metric, bounds in metrics.items():
            if len(bounds) != metric_bounds_count:
                continue
            lo, hi = bounds[0], bounds[1]
            val = ticker.get(metric)
            if val is None:
                return False
            if not isinstance(val, int | float | str):
                return False
            try:
                if not (lo <= float(val) <= hi):
                    return False
            except (ValueError, TypeError):
                return False
        return True

    @rx.var
    def cache_size(self) -> int:
        return len(self.tickers_data)

    @rx.var
    def cache_error(self) -> str:
        return self.load_error

    @rx.var
    def get_all_tickers(self) -> list[dict[str, object]]:
        if not self.tickers_data:
            return []

        results: list[dict[str, object]] = list(self.tickers_data)

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
