"""Search bar state for ticker search and suggestions."""

import reflex as rx
import time
import asyncio
import pandas as pd
import itertools
from sqlalchemy import text
from typing import List, Dict, Any
from ..utils.scheduler import db_settings


class SearchBarState(rx.State):
    """State for managing search bar functionality and suggestions."""

    search_query: str = ""
    display_suggestion: bool = False
    empty_state_display_suggestion: bool = False
    outstanding_tickers: Dict[str, Any] = {}
    ticker_list: List[Dict[str, Any]] = {}

    @rx.event
    def set_query(self, text: str = ""):
        """Set search query text."""
        self.search_query = text if text != "" else text

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
    def get_suggest_ticker(self) -> List[Dict[str, Any]]:
        """Get ticker suggestions based on search query."""
        if not self.display_suggestion and not self.empty_state_display_suggestion:
            return []
        if self.search_query == "":
            return self.ticker_list

        # Try exact match first
        result: pd.DataFrame = self.fetch_ticker(
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
            result: pd.DataFrame = self.fetch_ticker(
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
            result: pd.DataFrame = self.fetch_ticker(
                match_conditions="pb.symbol LIKE :pattern",
                params={"pattern": f"{self.search_query[0]}%"},
            )

        return result.to_dict("records")

    def fetch_ticker(
        self, match_conditions: str = "all", params: Any = None
    ) -> pd.DataFrame:
        """Fetch tickers from database with optional filters."""
        if not db_settings.conn:
            return pd.DataFrame(columns=["symbol", "pct_price_change", "industry"])

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

        try:
            with db_settings.conn.connect() as connection:
                result: pd.DataFrame = pd.read_sql(
                    text(query), connection, params=params
                )
                return result
        except Exception as e:
            print(f"Database error in fetch_ticker: {e}")
            return pd.DataFrame(columns=["symbol", "pct_price_change", "industry"])

    @rx.event(background=True)
    async def load_state(self):
        """Preload tickers and track top trending tickers."""
        while True:
            async with self:
                self.ticker_list = self.fetch_ticker(match_conditions="all").to_dict(
                    "records"
                )
                self.outstanding_tickers: Dict[str, Any] = {
                    item["symbol"]: 1 for item in self.ticker_list[:3]
                }
            await asyncio.sleep(db_settings.interval)
