"""Home page state management."""

import reflex as rx
import pandas as pd
from sqlalchemy import text
from ..utils.database.database import company_sync_engine


class HomeState(rx.State):
    """State for home page interactions."""

    # Framework card hover
    framework_hover_index: int = 0
    _framework_hover_active: bool = False

    # Portfolio card hover
    is_portfolio_hovered: bool = False

    # Comparison card hover
    is_comparison_hovered: bool = False

    # Sample data for visualizations
    comparison_preview_data: list[dict] = [
        {"period": "Q1", "value": 12},
        {"period": "Q2", "value": 15},
        {"period": "Q3", "value": 13},
        {"period": "Q4", "value": 16},
    ]

    vnindex_chart_data: list[dict] = []
    vnindex_value: str = "Loading..."
    vnindex_change: str = "..."
    vnindex_is_positive: bool = True

    # Portfolio animation values
    _base_portfolio_value: float = 142590.22
    _target_portfolio_value: float = 148719.73
    _base_portfolio_change: float = 4.8
    _target_portfolio_change: float = 8.1
    _current_portfolio_value: float = 142590.22
    _current_portfolio_change: float = 4.8
    portfolio_value: str = "$142,590.22"
    portfolio_change: str = "+4.8%"
    _animation_running: bool = False

    @rx.event(background=True)
    async def load_vnindex_data(self):
        """Load VNINDEX data from database."""
        try:
            # Fetch VNINDEX data from database - ALL historical data
            df = pd.read_sql(
                text("SELECT * FROM market.vnindex ORDER BY time"), company_sync_engine
            )

            if df.empty:
                async with self:
                    self.vnindex_value = "N/A"
                    self.vnindex_change = "N/A"
                return

            # First row is previous close (reference point)
            # Last row is current value
            previous_close = df.iloc[0]["close"]
            current_value = df.iloc[-1]["close"]

            # Calculate point change from previous close
            change = current_value - previous_close
            sign = "+" if change >= 0 else ""

            # Prepare chart data - skip first row (previous close)
            # Only chart today's intraday movement
            chart_data = []
            df_today = df.iloc[1:]  # Skip the previous close row

            if not df_today.empty:
                # Normalize today's data for the chart
                close_values = df_today["close"].values
                min_val = close_values.min()
                max_val = close_values.max()

                for idx, row in df_today.iterrows():
                    # Normalize between 0 and 1 for chart display
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
            import traceback

            traceback.print_exc()
            async with self:
                self.vnindex_value = "N/A"
                self.vnindex_change = "N/A"

    def on_mount(self):
        """Initialize state when page loads."""
        return HomeState.load_vnindex_data

    def on_unmount(self):
        """Cleanup when page unloads."""
        pass

    @rx.event
    def start_framework_hover(self):
        """Start framework card hover animation."""
        self._framework_hover_active = True
        self.framework_hover_index = 1

    @rx.event
    def stop_framework_hover(self):
        """Stop framework card hover animation."""
        self._framework_hover_active = False
        self.framework_hover_index = 0

    @rx.event(background=True)
    async def start_portfolio_hover(self):
        """Start portfolio card hover with count-up animation."""
        import asyncio

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
        """End portfolio card hover with count-down animation."""
        import asyncio

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

    @rx.event
    def start_comparison_hover(self):
        """Start comparison card hover."""
        self.is_comparison_hovered = True

    @rx.event
    def end_comparison_hover(self):
        """End comparison card hover."""
        self.is_comparison_hovered = False

    @rx.event
    def handle_compare(self):
        """Navigate to compare page."""
        return rx.redirect("/analyze/compare")

    @rx.event
    def handle_portfolio(self):
        """Navigate to portfolio page."""
        return rx.redirect("/portfolio")
