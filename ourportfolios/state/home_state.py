import reflex as rx
import asyncio
import pandas as pd
from sqlalchemy import text
from ..utils.session_manager import SessionIsolatedStateMixin
from ..utils.database.database import company_sync_engine


class HomeState(SessionIsolatedStateMixin, rx.State):
    """Homepage state."""

    # Ticker search input
    ticker_search: str = ""

    # Real VNINDEX data
    vnindex_value: str = "Loading..."
    vnindex_change: str = "..."
    vnindex_is_positive: bool = True
    vnindex_chart_data: list[dict] = []

    # Mock data for other indices
    nasdaq_value: str = "14,972.76"
    nasdaq_change: str = "+0.75%"
    gold_value: str = "2,018.30"
    gold_change: str = "-0.12%"
    oil_value: str = "71.45"
    oil_change: str = "+0.44%"

    # Portfolio values (base and target for animation)
    _base_portfolio_value: float = 142590.22
    _target_portfolio_value: float = 148719.73
    _base_portfolio_change: float = 4.8
    _target_portfolio_change: float = 8.1
    _current_portfolio_value: float = 142590.22
    _current_portfolio_change: float = 4.8
    portfolio_value: str = "$142,590.22"
    portfolio_change: str = "+4.8%"
    is_portfolio_hovered: bool = False
    _animation_running: bool = False

    # Framework card hover state
    framework_hover_index: int = 0
    _framework_card_hovered: bool = False

    # Framework stats
    frameworks_count: str = "12"

    # Comparison stats
    active_comparisons: str = "3"

    # Sample comparison data for the preview chart
    comparison_preview_data: list[dict] = [
        {"period": "Jan", "AAPL": 178, "MSFT": 340},
        {"period": "Feb", "AAPL": 182, "MSFT": 345},
        {"period": "Mar", "AAPL": 175, "MSFT": 352},
        {"period": "Apr", "AAPL": 185, "MSFT": 358},
        {"period": "May", "AAPL": 190, "MSFT": 365},
        {"period": "Jun", "AAPL": 188, "MSFT": 372},
        {"period": "Jul", "AAPL": 195, "MSFT": 380},
        {"period": "Aug", "AAPL": 198, "MSFT": 385},
    ]

    @rx.event(background=True)
    async def load_vnindex_data(self):
        """Load VNINDEX data from database."""
        try:
            # Fetch VNINDEX data from database
            df = pd.read_sql(
                text("SELECT * FROM market.vnindex ORDER BY time"), company_sync_engine
            )

            if df.empty:
                async with self:
                    self.vnindex_value = "N/A"
                    self.vnindex_change = "N/A"
                return

            # First row is previous close, last row is current value
            previous_close = df.iloc[0]["close"]
            current_value = df.iloc[-1]["close"]

            # Calculate point change from previous close
            change = current_value - previous_close
            sign = "+" if change >= 0 else ""

            # Prepare chart data (skip first row which is previous close)
            chart_data = []
            df_today = df.iloc[1:]  # Skip the previous close row

            if not df_today.empty:
                # Normalize today's data
                close_values = df_today["close"].values
                min_val = close_values.min()
                max_val = close_values.max()

                for idx, row in df_today.iterrows():
                    normalized = (
                        (row["close"] - min_val) / (max_val - min_val)
                        if max_val > min_val
                        else 0.5
                    )
                    chart_data.append(
                        {
                            "name": row["time"].strftime("%H:%M"),
                            "normalized_close": normalized,
                        }
                    )

            async with self:
                self.vnindex_value = f"{current_value:,.2f}"
                self.vnindex_change = f"{sign}{abs(change):.2f}"
                self.vnindex_is_positive = bool(change >= 0)
                self.vnindex_chart_data = chart_data

        except Exception as e:
            print(f"Error loading VNINDEX data: {e}")
            async with self:
                self.vnindex_value = "N/A"
                self.vnindex_change = "N/A"

    def start_framework_hover(self):
        """Move spotlight to second framework when card is hovered."""
        self._framework_card_hovered = True
        self.framework_hover_index = 1

    def stop_framework_hover(self):
        """Move spotlight back to first framework when mouse leaves."""
        self._framework_card_hovered = False
        self.framework_hover_index = 0

    @rx.event(background=True)
    async def start_portfolio_hover(self):
        """Start the portfolio hover animation with gradual count-up."""
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

        for i in range(steps + 1):
            async with self:
                if not self.is_portfolio_hovered:
                    self._animation_running = False
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

        async with self:
            self._animation_running = False

    @rx.event(background=True)
    async def end_portfolio_hover(self):
        """End the portfolio hover animation with gradual count-down."""
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

        for i in range(steps + 1):
            async with self:
                if self.is_portfolio_hovered:
                    self._animation_running = False
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

        async with self:
            self._animation_running = False

    def on_mount(self):
        super().on_mount()
        return HomeState.load_vnindex_data

    def on_unmount(self):
        super().on_unmount()

    def handle_analyze_ticker(self):
        """Navigate to analyze page with the ticker."""
        if self.ticker_search:
            return rx.redirect(f"/analyze?ticker={self.ticker_search}")

    def handle_compare(self):
        """Navigate to compare page."""
        return rx.redirect("/compare")

    def handle_portfolio(self):
        """Navigate to portfolio/select page."""
        return rx.redirect("/select")
