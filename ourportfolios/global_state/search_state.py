"""Search bar state for ticker search and suggestions."""

import reflex as rx
import time
import asyncio
import pandas as pd
import itertools
from sqlalchemy import text
from typing import List, Dict, Any
from ..utils.database.database import get_company_session


class SearchBarState(rx.State):
    """State for managing search bar functionality and suggestions."""

    search_query: str = ""
    comparison_search_query: str = ""
    display_suggestion: bool = False
    empty_state_display_suggestion: bool = False
    outstanding_tickers: Dict[str, Any] = {}
    ticker_list: List[Dict[str, Any]] = {}

    @rx.event
    def set_query(self, text: str = ""):
        """Set search query text."""
        self.search_query = text if text != "" else text

    @rx.event
    def set_comparison_query(self, text: str = ""):
        """Set comparison search query text."""
        self.comparison_search_query = text if text != "" else text

    @rx.event
    def set_display_suggestions(self, state: bool):
        """Toggle suggestion display with a delay."""
        yield time.sleep(0.2)
        self.display_suggestion = state

    @rx.event
    def set_empty_state_display_suggestions(self, state: bool):
        """Toggle empty state suggestion display with a delay."""
        yield time.sleep(0.2)
        self.empty_state_display_suggestion = state

    @rx.var
    async def get_suggest_ticker(self) -> List[Dict[str, Any]]:
        """Get ticker suggestions based on search query (navbar search)."""
        if not self.display_suggestion:
            return []
        if self.search_query == "":
            return self.ticker_list

        # Try exact match first
        result: pd.DataFrame = await self.fetch_ticker(
            match_conditions="pb.symbol LIKE :pattern",
            params={"pattern": f"{self.search_query}%"},
        )

        # Try permutations if no match
        if result.empty:
            combos: List[tuple] = list(
                itertools.permutations(list(self.search_query), len(self.search_query))
            )
            all_combination = {
                f"pattern_{idx}": f"{''.join(combo)}%"
                for idx, combo in enumerate(combos)
            }
            result: pd.DataFrame = await self.fetch_ticker(
                match_conditions=" OR ".join(
                    [
                        f"pb.symbol LIKE :pattern_{i}"
                        for i in range(len(all_combination))
                    ]
                ),
                params=all_combination,
            )

        # Fallback to first letter match
        if result.empty:
            result: pd.DataFrame = await self.fetch_ticker(
                match_conditions="pb.symbol LIKE :pattern",
                params={"pattern": f"{self.search_query[0]}%"},
            )

        return result.to_dict("records")

    @rx.var
    async def get_comparison_suggest_ticker(self) -> List[Dict[str, Any]]:
        """Get ticker suggestions based on comparison search query."""
        if not self.empty_state_display_suggestion:
            return []
        if self.comparison_search_query == "":
            return self.ticker_list

        # Try exact match first
        result: pd.DataFrame = await self.fetch_ticker(
            match_conditions="pb.symbol LIKE :pattern",
            params={"pattern": f"{self.comparison_search_query}%"},
        )

        # Try permutations if no match
        if result.empty:
            combos: List[tuple] = list(
                itertools.permutations(
                    list(self.comparison_search_query),
                    len(self.comparison_search_query),
                )
            )
            all_combination = {
                f"pattern_{idx}": f"{''.join(combo)}%"
                for idx, combo in enumerate(combos)
            }
            result: pd.DataFrame = await self.fetch_ticker(
                match_conditions=" OR ".join(
                    [
                        f"pb.symbol LIKE :pattern_{i}"
                        for i in range(len(all_combination))
                    ]
                ),
                params=all_combination,
            )

        # Fallback to first letter match
        if result.empty:
            result: pd.DataFrame = await self.fetch_ticker(
                match_conditions="pb.symbol LIKE :pattern",
                params={"pattern": f"{self.comparison_search_query[0]}%"},
            )

        return result.to_dict("records")

    async def fetch_ticker(
        self, match_conditions: str = "all", params: Any = None
    ) -> pd.DataFrame:
        """Fetch tickers from database with optional filters."""
        try:
            async with get_company_session() as session:
                query: str = """
                        SELECT
                            pb.symbol,
                            pb.pct_price_change,
                            pb.accumulated_volume,
                            od.industry
                        FROM tickers.price_df AS pb
                        JOIN tickers.overview_df AS od
                            ON pb.symbol = od.symbol
                        """
                if match_conditions != "all":
                    query += f"WHERE {match_conditions}\n"

                query += "ORDER BY pb.accumulated_volume DESC"

                result = await session.execute(text(query), params or {})
                rows = result.mappings().all()
                return pd.DataFrame([dict(row) for row in rows])
        except Exception as e:
            print(f"Database error in fetch_ticker: {e}")
            return pd.DataFrame(columns=["symbol", "pct_price_change", "industry"])

    @rx.event(background=True)
    async def load_state(self):
        """Preload tickers and track top trending tickers."""
        while True:
            async with self:
                result = await self.fetch_ticker(match_conditions="all")
                self.ticker_list = result.to_dict("records")
                self.outstanding_tickers: Dict[str, Any] = {
                    item["symbol"]: 1 for item in self.ticker_list[:3]
                }
            await asyncio.sleep(60)  # Default interval of 60 seconds
