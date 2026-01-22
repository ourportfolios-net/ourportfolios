"""Home page state management."""

import reflex as rx
import pandas as pd
from sqlalchemy import text
from ..utils.database.database import get_company_session


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

    # Ticker of the Day state variables
    ticker_of_day_symbol: str = ""
    ticker_of_day_name: str = ""
    ticker_of_day_industry: str = ""
    ticker_of_day_price: str = ""
    ticker_of_day_change: str = ""

    @rx.event(background=True)
    async def load_vnindex_data(self):
        """Load VNINDEX data from database."""
        try:
            async with get_company_session() as session:
                # Fetch VNINDEX data from database - ALL historical data
                query = text("SELECT * FROM market.vnindex ORDER BY time")
                result = await session.execute(query)
                rows = result.mappings().all()
                df = pd.DataFrame([dict(row) for row in rows])

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

    @rx.event(background=True)
    async def load_ticker_of_day(self):
        """Load the ticker of the day - highest volume AND highest % gain."""
        try:
            async with get_company_session() as session:
                # Query to find ticker with highest (volume * price_change_percent)
                # Join all three tables: price_df, overview_df, profile_df
                query = text("""
                    SELECT 
                        pb.symbol,
                        pb.pct_price_change,
                        pb.accumulated_volume,
                        pb.current_price,
                        od.industry,
                        pf.company_name,
                        (pb.accumulated_volume * ABS(pb.pct_price_change)) AS score
                    FROM tickers.price_df AS pb
                    JOIN tickers.overview_df AS od ON pb.symbol = od.symbol
                    JOIN tickers.profile_df AS pf ON pb.symbol = pf.symbol
                    WHERE pb.pct_price_change > 0
                    ORDER BY score DESC
                    LIMIT 1
                """)

                result = await session.execute(query)
                rows = result.mappings().all()
                df = pd.DataFrame([dict(row) for row in rows])

                if not df.empty:
                    ticker_data = df.iloc[0]

                    async with self:
                        self.ticker_of_day_symbol = ticker_data["symbol"]
                        self.ticker_of_day_name = ticker_data["company_name"]
                        self.ticker_of_day_industry = (
                            ticker_data["industry"]
                            if pd.notna(ticker_data["industry"])
                            else "N/A"
                        )
                        self.ticker_of_day_price = (
                            f"{ticker_data['current_price']:,.2f}"
                        )
                        self.ticker_of_day_change = (
                            f"+{ticker_data['pct_price_change']:.2f}%"
                        )
                else:
                    # No data available
                    async with self:
                        self.ticker_of_day_symbol = "N/A"
                        self.ticker_of_day_name = "No data available"
                        self.ticker_of_day_industry = ""
                        self.ticker_of_day_price = "$0.00"
                        self.ticker_of_day_change = "+0.00%"

        except Exception as e:
            print(f"Error loading ticker of the day: {e}")
            import traceback

            traceback.print_exc()
            async with self:
                self.ticker_of_day_symbol = "N/A"
                self.ticker_of_day_name = "Error loading data"
                self.ticker_of_day_industry = ""
                self.ticker_of_day_price = "$0.00"
                self.ticker_of_day_change = "+0.00%"

    def on_mount(self):
        """Initialize state when page loads."""
        return [HomeState.load_vnindex_data, HomeState.load_ticker_of_day]

    def on_unmount(self):
        """Cleanup when page unloads."""
        pass

    @rx.event
    def navigate_to_ticker_of_day(self):
        """Navigate to analyze page for ticker of the day."""
        if self.ticker_of_day_symbol and self.ticker_of_day_symbol != "N/A":
            return rx.redirect(f"/analyze/{self.ticker_of_day_symbol}")

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
