"""Cart state management for storing and managing selected tickers."""

import reflex as rx
import asyncio
from sqlalchemy import text
from ..utils.database.database import get_company_session


async def get_industry(ticker: str) -> str:
    """Fetch industry for a given ticker."""
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            async with get_company_session() as session:
                query = text("""
                    SELECT industry
                    FROM tickers.overview_df
                    WHERE symbol = :pattern
                """)
                result = await session.execute(query, {"pattern": ticker})
                row = result.mappings().first()
                if row:
                    return row["industry"]
                return "Unknown"
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Error fetching industry for {ticker}: {e}")
                return "Unknown"
            await asyncio.sleep(0.1)  # Small delay before retry

    return "Unknown"


class CartState(rx.State):
    """Global state for managing the shopping cart of tickers."""

    cart_items: list[dict] = []
    is_open: bool = False

    @rx.var
    def should_scroll(self) -> bool:
        """Determine if cart should have a scrollbar."""
        return len(self.cart_items) >= 6

    @rx.event
    def toggle_cart(self):
        """Toggle cart drawer visibility."""
        self.is_open = not self.is_open

    @rx.event
    def remove_item(self, index: int):
        """Remove item from cart by index."""
        self.cart_items.pop(index)

    @rx.event
    async def add_item(self, ticker: str):
        """Add a ticker to the cart."""
        if any(item["name"] == ticker for item in self.cart_items):
            yield rx.toast.error(f"{ticker} already in cart!")
        else:
            industry = await get_industry(ticker)
            self.cart_items.append({"name": ticker, "industry": industry})
            yield rx.toast(f"{ticker} added to cart!")
