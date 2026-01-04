"""Ticker board state for filtering and displaying ticker lists."""

import reflex as rx
from typing import Any
from sqlalchemy import text
from ..utils.database.database import get_company_session


class TickerBoardState(rx.State):
    """State for managing ticker board filters, sorts, and display."""

    search_query: str = ""

    # Cache all tickers in memory for instant filtering
    _all_tickers_cache: list[dict[str, Any]] = []
    _cache_loaded: bool = False

    # Filters
    selected_exchange: set[str] = set()
    selected_industry: set[str] = set()
    selected_technical_metric: dict[str, list[float]] = {}
    selected_fundamental_metric: dict[str, list[float]] = {}

    # Sorts
    selected_sort_order: str = "ASC"
    selected_sort_option: str = "symbol"

    @rx.event
    def apply_filters(self, filters: dict[str, Any]):
        """Apply multiple filters at once."""
        if "exchange" in filters.keys():
            self.selected_exchange = filters["exchange"]
        if "industry" in filters.keys():
            self.selected_industry = filters["industry"]
        if "fundamental" in filters.keys():
            self.selected_fundamental_metric = filters["fundamental"]
        if "technical" in filters.keys():
            self.selected_technical_metric = filters["technical"]

    @rx.event
    def clear_all_filters(self):
        """Reset all filters to default state."""
        self.selected_exchange = set()
        self.selected_industry = set()
        self.selected_technical_metric = {}
        self.selected_fundamental_metric = {}

    @rx.event
    def set_search_query(self, value: str):
        """Update search query."""
        self.search_query = value

    async def load_all_tickers_cache(self):
        """Load all tickers into memory once for instant filtering."""
        if self._cache_loaded:
            return

        query = """
            SELECT 
                pb.symbol, pb.current_price, pb.accumulated_volume, 
                pb.pct_price_change, pd.company_name, od.market_cap,
                od.industry, od.exchange
            FROM tickers.price_df AS pb 
            JOIN tickers.profile_df AS pd ON pb.symbol = pd.symbol 
            JOIN tickers.overview_df AS od ON pd.symbol = od.symbol
            ORDER BY pb.accumulated_volume DESC
        """

        try:
            async with get_company_session() as session:
                result = await session.execute(text(query))
                rows = result.mappings().all()
                self._all_tickers_cache = [dict(row) for row in rows]
                self._cache_loaded = True
        except Exception as e:
            print(f"Error loading ticker cache: {e}")

    @rx.event
    def set_sort_option(self, option: str):
        """set column to sort by."""
        self.selected_sort_option = option

    @rx.event
    def set_sort_order(self, order: str):
        """set sort order (ASC/DESC)."""
        self.selected_sort_order = order

    @rx.var(cache=True)
    def get_all_tickers(self) -> list[dict[str, Any]]:
        """Get all tickers matching current filters and search - client-side filtering."""
        if not self._cache_loaded or not self._all_tickers_cache:
            return []

        # Start with all cached tickers
        results = self._all_tickers_cache

        # Filter by search query (client-side)
        if self.search_query:
            search_upper = self.search_query.upper()
            results = [t for t in results if t["symbol"].startswith(search_upper)]

        # Filter by industry
        if self.selected_industry:
            results = [
                t for t in results if t.get("industry") in self.selected_industry
            ]

        # Filter by exchange
        if self.selected_exchange:
            results = [
                t for t in results if t.get("exchange") in self.selected_exchange
            ]

        # Apply sorting
        if self.selected_sort_option and results:
            reverse = self.selected_sort_order == "DESC"
            results = sorted(
                results,
                key=lambda x: x.get(self.selected_sort_option, 0),
                reverse=reverse,
            )

        return results
