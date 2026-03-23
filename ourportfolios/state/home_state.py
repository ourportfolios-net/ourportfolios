"""Home page state management."""

import asyncio
import traceback
import reflex as rx
from sqlalchemy import (
    Table,
    Column,
    String,
    Float,
    MetaData,
    select,
    func,
    desc,
)
from ..utils.database.database import get_company_session
from ..utils.database.models import VNIndexORM, PriceORM, OverviewORM, ProfileORM

_market_meta = MetaData(schema="market")


def _change_table(name: str) -> Table:
    return Table(
        name,
        _market_meta,
        Column("symbol", String),
        Column("pct_change", Float),
        Column("market_cap", Float),
        Column("industry", String),
    )


_CHANGE_TABLES = {
    "1W": _change_table("weekly_changes"),
    "1M": _change_table("monthly_changes"),
    "1Q": _change_table("quarterly_changes"),
    "1Y": _change_table("yearly_changes"),
}

_PERIOD_LABEL = {
    "1D": "Day",
    "1W": "Week",
    "1M": "Month",
    "1Q": "Quarter",
    "1Y": "Year",
}

_profile = ProfileORM.__table__
_price = PriceORM.__table__


class HomeState(rx.State):
    framework_hover_index: int = 0
    _framework_hover_active: bool = False

    is_portfolio_hovered: bool = False
    is_comparison_hovered: bool = False

    comparison_preview_data: list[dict] = [
        {"period": "Q1", "value": 12},
        {"period": "Q2", "value": 15},
        {"period": "Q3", "value": 13},
        {"period": "Q4", "value": 16},
    ]

    vnindex_chart_data: list[dict] = []
    vnindex_value: str = ""
    vnindex_change: str = ""
    vnindex_pct_change: str = ""
    vnindex_is_positive: bool = True

    _base_portfolio_value: float = 142590.22
    _target_portfolio_value: float = 148719.73
    _base_portfolio_change: float = 4.8
    _target_portfolio_change: float = 8.1
    _current_portfolio_value: float = 142590.22
    _current_portfolio_change: float = 4.8
    portfolio_value: str = "$142,590.22"
    portfolio_change: str = "+4.8%"
    _animation_running: bool = False

    ticker_of_day_symbol: str = ""
    ticker_of_day_name: str = ""
    ticker_of_day_industry: str = ""
    ticker_of_day_price: str = ""
    ticker_of_day_change: str = ""
    ticker_period_label: str = "Day"

    @rx.event(background=True)
    async def load_vnindex_data(self) -> None:
        try:
            async with get_company_session() as session:
                stmt = select(VNIndexORM).order_by(VNIndexORM.time)
                result = await session.execute(stmt)
                rows = result.scalars().all()

            if not rows:
                async with self:
                    self.vnindex_value = "N/A"
                    self.vnindex_change = "N/A"
                return

            previous_close: float = rows[0].close or 0.0
            current_value: float = rows[-1].close or 0.0
            change: float = current_value - previous_close
            sign = "+" if change >= 0 else "-"

            chart_data: list[dict] = []
            today_rows = rows[1:]

            if today_rows:
                close_values = [r.close or 0.0 for r in today_rows]
                min_val = min(close_values)
                max_val = max(close_values)

                for row in today_rows:
                    row_close = row.close or 0.0
                    normalized = (
                        (row_close - min_val) / (max_val - min_val)
                        if max_val > min_val
                        else 0.5
                    )
                    chart_data.append(
                        {
                            "name": row.time.strftime("%H:%M"),
                            "normalized_close": normalized,
                        }
                    )

            async with self:
                self.vnindex_value = f"{current_value:,.2f}"
                self.vnindex_change = f"{sign}{abs(change):.2f}"
                pct = (change / previous_close * 100) if previous_close else 0.0
                self.vnindex_pct_change = f"{sign}{abs(pct):.2f}%"
                self.vnindex_is_positive = bool(change >= 0)
                self.vnindex_chart_data = chart_data

        except Exception as e:
            print(f"Error loading VNINDEX data: {e}")
            traceback.print_exc()
            async with self:
                self.vnindex_value = "N/A"
                self.vnindex_change = "N/A"

    @rx.event(background=True)
    async def load_ticker_for_period(self, period: str = "1D") -> None:
        label = _PERIOD_LABEL.get(period, "Day")
        try:
            async with get_company_session() as session:
                if period == "1D":
                    score = (
                        PriceORM.accumulated_volume
                        * func.abs(PriceORM.pct_price_change)
                    ).label("score")
                    stmt = (
                        select(
                            PriceORM.symbol,
                            PriceORM.pct_price_change.label("pct_change"),
                            PriceORM.current_price,
                            OverviewORM.industry,
                            ProfileORM.company_name,
                            score,
                        )
                        .join(OverviewORM, PriceORM.symbol == OverviewORM.symbol)
                        .join(ProfileORM, PriceORM.symbol == ProfileORM.symbol)
                        .where(PriceORM.pct_price_change > 0)
                        .order_by(desc(score))
                        .limit(1)
                    )
                else:
                    ct = _CHANGE_TABLES[period]
                    score = (ct.c.market_cap * func.abs(ct.c.pct_change)).label("score")
                    stmt = (
                        select(
                            ct.c.symbol,
                            ct.c.pct_change,
                            _price.c.current_price,
                            ct.c.industry,
                            _profile.c.company_name,
                            score,
                        )
                        .join(_profile, ct.c.symbol == _profile.c.symbol)
                        .join(_price, ct.c.symbol == _price.c.symbol)
                        .where(ct.c.pct_change > 0)
                        .order_by(desc(score))
                        .limit(1)
                    )

                result = await session.execute(stmt)
                row = result.mappings().first()

            if row is not None:
                price = float(row["current_price"] or 0.0)
                pct = float(row["pct_change"] or 0.0)
                async with self:
                    self.ticker_of_day_symbol = row["symbol"] or ""
                    self.ticker_of_day_name = row["company_name"] or ""
                    self.ticker_of_day_industry = row["industry"] or "N/A"
                    self.ticker_of_day_price = f"{price:,.2f}"
                    self.ticker_of_day_change = f"+{pct:.2f}%"
                    self.ticker_period_label = label
            else:
                async with self:
                    self.ticker_of_day_symbol = "N/A"
                    self.ticker_of_day_name = "No data available"
                    self.ticker_of_day_industry = ""
                    self.ticker_of_day_price = "0.00"
                    self.ticker_of_day_change = "+0.00%"
                    self.ticker_period_label = label

        except Exception as e:
            print(f"Error loading ticker for period {period}: {e}")
            traceback.print_exc()
            async with self:
                self.ticker_of_day_symbol = "N/A"
                self.ticker_of_day_name = "Error loading data"
                self.ticker_of_day_industry = ""
                self.ticker_of_day_price = "0.00"
                self.ticker_of_day_change = "+0.00%"
                self.ticker_period_label = label

    def on_mount(self):
        return [
            HomeState.load_vnindex_data,
            HomeState.load_ticker_for_period("1D"),
        ]

    def on_unmount(self):
        pass

    @rx.event
    def navigate_to_ticker_of_day(self):
        if self.ticker_of_day_symbol and self.ticker_of_day_symbol != "N/A":
            return rx.redirect(f"/tickers/{self.ticker_of_day_symbol}")

    @rx.event
    def start_framework_hover(self) -> None:
        self._framework_hover_active = True
        self.framework_hover_index = 1

    @rx.event
    def stop_framework_hover(self) -> None:
        self._framework_hover_active = False
        self.framework_hover_index = 0

    @rx.event(background=True)
    async def start_portfolio_hover(self) -> None:
        async with self:
            if self._animation_running:
                return
            self.is_portfolio_hovered = True
            self._animation_running = True

        duration = 0.35
        steps = 20
        step_duration = duration / steps
        start_value = self._base_portfolio_value
        end_value = self._target_portfolio_value
        start_change = self._base_portfolio_change
        end_change = self._target_portfolio_change

        try:
            for i in range(steps + 1):
                async with self:
                    if not self.is_portfolio_hovered:
                        return
                    t = i / steps
                    eased_t = 1 - (1 - t) ** 4
                    current_val = start_value + (end_value - start_value) * eased_t
                    current_chg = start_change + (end_change - start_change) * eased_t
                    self._current_portfolio_value = current_val
                    self._current_portfolio_change = current_chg
                    self.portfolio_value = f"${current_val:,.2f}"
                    self.portfolio_change = f"+{current_chg:.1f}%"
                if i < steps:
                    await asyncio.sleep(step_duration)
        except asyncio.CancelledError:
            raise
        finally:
            try:
                async with self:
                    self._animation_running = False
            except Exception:
                pass

    @rx.event(background=True)
    async def end_portfolio_hover(self) -> None:
        async with self:
            if self._animation_running and not self.is_portfolio_hovered:
                return
            self.is_portfolio_hovered = False
            self._animation_running = True

        duration = 0.35
        steps = 20
        step_duration = duration / steps

        async with self:
            start_value = self._current_portfolio_value
            start_change = self._current_portfolio_change
        end_value = self._base_portfolio_value
        end_change = self._base_portfolio_change

        try:
            for i in range(steps + 1):
                async with self:
                    if self.is_portfolio_hovered:
                        return
                    t = i / steps
                    eased_t = 1 - (1 - t) ** 4
                    current_val = start_value + (end_value - start_value) * eased_t
                    current_chg = start_change + (end_change - start_change) * eased_t
                    self._current_portfolio_value = current_val
                    self._current_portfolio_change = current_chg
                    self.portfolio_value = f"${current_val:,.2f}"
                    self.portfolio_change = f"+{current_chg:.1f}%"
                if i < steps:
                    await asyncio.sleep(step_duration)
        except asyncio.CancelledError:
            raise
        finally:
            try:
                async with self:
                    self._animation_running = False
            except Exception:
                pass

    @rx.event
    def start_comparison_hover(self) -> None:
        self.is_comparison_hovered = True

    @rx.event
    def end_comparison_hover(self) -> None:
        self.is_comparison_hovered = False

    @rx.event
    def handle_compare(self):
        return rx.redirect("/tickers")

    @rx.event
    def handle_portfolio(self):
        return rx.redirect("/portfolio")
