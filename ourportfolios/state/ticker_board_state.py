"""Ticker board state for filtering and displaying ticker lists."""

import reflex as rx
from typing import List, Dict, Any, Set
from sqlalchemy import TextClause, text
from ..utils.database.database import get_company_session


class TickerBoardState(rx.State):
    """State for managing ticker board filters, sorts, and display."""

    search_query: str = ""

    # Filters
    selected_exchange: Set[str] = set()
    selected_industry: Set[str] = set()
    selected_technical_metric: Dict[str, List[float]] = {}
    selected_fundamental_metric: Dict[str, List[float]] = {}

    # Sorts
    selected_sort_order: str = "ASC"
    selected_sort_option: str = "symbol"

    @rx.event
    def apply_filters(self, filters: Dict[str, Any]):
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

    @rx.event
    def set_sort_option(self, option: str):
        """Set column to sort by."""
        self.selected_sort_option = option

    @rx.event
    def set_sort_order(self, order: str):
        """Set sort order (ASC/DESC)."""
        self.selected_sort_order = order

    @rx.var
    async def get_all_tickers(self) -> List[Dict[str, Any]]:
        """Get all tickers matching current filters and search."""
        query: List[str] = [
            f"""SELECT 
                pb.symbol, pb.current_price, pb.accumulated_volume, pb.pct_price_change, pd.company_name, od.market_cap
                FROM tickers.price_df AS pb 
                JOIN tickers.profile_df AS pd ON pb.symbol = pd.symbol 
                JOIN tickers.overview_df AS od ON pd.symbol = od.symbol
                {"JOIN tickers.stats_df AS sd ON pd.symbol = sd.symbol" if len(self.selected_fundamental_metric) > 0 or len(self.selected_technical_metric) > 0 else ""}
                WHERE
            """
        ]

        if self.search_query != "":
            from ..utils.generate_query import get_suggest_ticker

            match_query, params = await get_suggest_ticker(
                search_query=self.search_query.upper(), return_type="query"
            )
            query.append(match_query)
        else:
            query.append("1=1")
            params = None

        # Filter by industry
        if len(self.selected_industry) > 0:
            query.append(
                f"AND industry IN ({', '.join(f"'{industry}'" for industry in self.selected_industry)})"
            )

        # Filter by exchange
        if len(self.selected_exchange) > 0:
            query.append(
                f"AND exchange IN ({', '.join(f"'{exchange}'" for exchange in self.selected_exchange)})"
            )

        # Filter by fundamental metrics
        if len(self.selected_fundamental_metric) > 0:
            query.append(
                " ".join(
                    [
                        f"AND {metric} BETWEEN {value_range[0]} AND {value_range[1]}"
                        for metric, value_range in self.selected_fundamental_metric.items()
                    ]
                )
            )

        # Filter by technical metrics
        if len(self.selected_technical_metric) > 0:
            query.append(
                " ".join(
                    [
                        f"AND {metric} BETWEEN {value_range[0]} AND {value_range[1]}"
                        for metric, value_range in self.selected_technical_metric.items()
                    ]
                )
            )

        # Apply sorting
        if self.selected_sort_option:
            query.append(
                f"ORDER BY {self.selected_sort_option} {self.selected_sort_order}"
            )

        full_query: TextClause = text(" ".join(query))

        try:
            async with get_company_session() as session:
                result = await session.execute(full_query, params or {})
                rows = result.mappings().all()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching tickers: {e}")
            return []
