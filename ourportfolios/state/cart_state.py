"""Cart state management."""

import asyncio

import reflex as rx
from sqlalchemy import select

from ourportfolios.utils.database.database import get_company_session
from ourportfolios.utils.database.models import OverviewORM

_CART_SCROLL_THRESHOLD = 6


async def get_industry(ticker: str) -> str:
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            async with get_company_session() as session:
                stmt = select(OverviewORM.industry).where(OverviewORM.symbol == ticker)
                result = await session.execute(stmt)
                value: str | None = result.scalar_one_or_none()
                return value if value is not None else "Unknown"
        except (ValueError, RuntimeError, KeyError):
            retry_count += 1
            if retry_count >= max_retries:
                # print(f"Error fetching industry for {ticker}: {e}")
                return "Unknown"
            await asyncio.sleep(0.1)
    return "Unknown"


class CartState(rx.State):
    cart_items: list[dict] = rx.Field(default_factory=list)
    is_open: bool = False

    @rx.var
    def should_scroll(self) -> bool:
        return len(self.cart_items) >= _CART_SCROLL_THRESHOLD

    @rx.event
    def toggle_cart(self) -> None:
        self.is_open = not self.is_open

    @rx.event
    def remove_item(self, index: int) -> None:
        self.cart_items.pop(index)

    @rx.event
    async def add_item(self, ticker: str):
        if any(item["name"] == ticker for item in self.cart_items):
            yield rx.toast.error(f"{ticker} already in cart!")
        else:
            industry = await get_industry(ticker)
            self.cart_items.append({"name": ticker, "industry": industry})
            yield rx.toast(f"{ticker} added to cart!")

    @rx.var
    def cart_count_label(self) -> str:
        count = len(self.cart_items)
        if count == 0:
            return "0 ITEMS"
        if count == 1:
            return "1 ITEM"
        return f"{count} ITEMS"

    @rx.event
    def go_to_compare(self):
        return rx.redirect("/compare")
