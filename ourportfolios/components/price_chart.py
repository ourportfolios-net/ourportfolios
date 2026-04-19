import asyncio
import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import pandas as pd
import reflex as rx
from dateutil.relativedelta import relativedelta

from ourportfolios.utils.compute_instrument import compute_ma, compute_rsi
from ourportfolios.utils.database.fetch_data import load_historical_data


class PriceChartState(rx.State):
    if TYPE_CHECKING:
        ticker: str
    chart_script_loaded: bool = False
    is_loading: bool = True
    _last_ticker: str = ""

    df: pd.DataFrame = pd.DataFrame()
    selected_interval: str = "1D"
    selected_chart: str = "Candlestick"
    selected_ma_period: dict[str, bool] = rx.Field(default_factory=dict)
    rsi_line: bool = False

    ma_period: dict[str, Any] = rx.Field(
        default_factory=lambda: {
            "5": "#D19DFF",
            "10": "#B661FFC2",
            "20": "#AEFEEDF5",
            "50": "#41FFDF76",
            "100": "#70B8FF",
            "200": "#3094FEB9",
        },
    )

    df_daily: pd.DataFrame = pd.DataFrame()
    df_by_interval: dict[str, Any] = rx.Field(
        default_factory=lambda: {
            "1D": pd.DataFrame(),
            "1W": pd.DataFrame(),
            "1M": pd.DataFrame(),
        },
    )
    interval_range: dict[str, Any] = rx.Field(
        default_factory=lambda: {
            "1D": datetime.now(UTC).date() - relativedelta(years=5),
            "1W": datetime.now(UTC).date(),
            "1M": datetime.now(UTC).date(),
        },
    )

    rsi_period: int = 14

    def _resample(self, df: pd.DataFrame, interval: str) -> pd.DataFrame:
        """Resample daily OHLCV DataFrame to weekly or monthly."""
        if df.empty or interval == "1D":
            return df
        rule = "W" if interval == "1W" else "ME"
        df2 = df.copy()
        df2["time"] = pd.to_datetime(df2["time"])
        df2 = df2.set_index("time")
        agg = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
        return df2.resample(rule).agg(agg).dropna(subset=["close"]).reset_index()

    @rx.event(background=True)
    async def load_state(self, ticker: str):
        async with self:
            if ticker == self._last_ticker and not self.df.empty:
                self.is_loading = False
                yield PriceChartState.render_price_chart
                return

            self._last_ticker = ticker
            self.is_loading = True
            start_date = (datetime.now(UTC).date() - relativedelta(years=5)).strftime(
                "%Y-%m-%d",
            )

        try:
            end_date = (datetime.now(UTC).date() + relativedelta(days=1)).strftime(
                "%Y-%m-%d",
            )

            def fetch_daily() -> pd.DataFrame:
                return load_historical_data(
                    symbol=ticker,
                    start=start_date,
                    end=end_date,
                    interval="1D",
                )

            df_daily = await asyncio.get_event_loop().run_in_executor(None, fetch_daily)

            async with self:
                self.df_daily = df_daily
                self.df = self._resample(df_daily, self.selected_interval)
                self.selected_ma_period = dict.fromkeys(self.ma_period.keys(), False)
                self.is_loading = False

            yield PriceChartState.render_price_chart

        except (ValueError, RuntimeError, KeyError):
            # print(f"[PriceChartState] Error loading price chart: {e}")
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def render_price_chart(self):
        async with self:
            yield rx.call_script(
                f"""
                if (typeof render_price_chart === 'function') {{
                    render_price_chart({self.chart_options}, {self.chart_data});
                }} else {{
                    console.warn('render_price_chart not yet loaded, scheduling retry...');
                    setTimeout(() => {{
                        if (typeof render_price_chart === 'function') {{
                            render_price_chart({self.chart_options}, {self.chart_data});
                        }}
                    }}, 100);
                }}
                """,
            )

    @rx.event(background=True)
    async def set_interval(self, _range: str):
        async with self:
            self.selected_interval = _range
            self.df = self._resample(self.df_daily, _range)
        yield PriceChartState.render_price_chart

    @rx.event
    def set_selection(self):
        if self.selected_chart == "Candlestick":
            self.selected_chart = "Price"
        else:
            self.selected_chart = "Candlestick"
        yield PriceChartState.render_price_chart

    @rx.event
    def add_ma_period(self, *, value: bool, period: str) -> None:
        self.selected_ma_period[period] = value
        yield PriceChartState.render_price_chart

    @rx.event
    def add_rsi_line(self):
        self.rsi_line = not self.rsi_line
        yield PriceChartState.render_price_chart

    @rx.event
    def toggle_ma_period(self, period_key: str):
        self.selected_ma_period[period_key] = not self.selected_ma_period.get(
            period_key,
            False,
        )
        yield PriceChartState.render_price_chart

    @rx.event
    def toggle_rsi_line(self):
        self.rsi_line = not self.rsi_line
        yield PriceChartState.render_price_chart

    # ─────────────────────────────────────────────────────────────────────────

    @rx.var
    def ohlc_data(self) -> list[dict[str, Any]]:
        if self.df.empty:
            return []
        df2 = self.df.copy()
        if "time" not in self.df.columns:
            df2 = df2.reset_index()
        df2["time"] = df2["time"].apply(lambda x: x.strftime("%Y-%m-%d"))
        return df2.to_dict("records")

    @rx.var
    def price_data(self) -> list[dict[str, Any]]:
        if (self.df.empty) or (not {"time", "close"}.issubset(self.df.columns)):
            return []
        df2 = self.df[["time", "close"]].rename(columns={"close": "value"})
        df2["time"] = df2["time"].apply(lambda x: x.strftime("%Y-%m-%d"))
        return df2.dropna(how="any", axis=0).to_dict("records")

    @rx.var
    def ma_data(self) -> dict[str, list[dict[str, Any]]]:
        if self.df.empty:
            return {}
        df2 = self.df.copy()
        if "time" not in df2.columns:
            df2 = df2.reset_index()
        return {
            period: compute_ma(df2, ma_period=int(period))
            for period, state in self.selected_ma_period.items()
            if state
        }

    @rx.var
    def rsi_data(self) -> list[dict[str, Any]]:
        if self.df.empty or not self.rsi_line:
            return []
        df2 = self.df.copy()
        if "time" not in df2.columns:
            df2 = df2.reset_index()
        return compute_rsi(df2, self.rsi_period)

    @rx.var
    def chart_data(self) -> str:
        price_data = (
            self.ohlc_data if self.selected_chart == "Candlestick" else self.price_data
        )
        data: dict[str, Any] = {
            "type": self.selected_chart,
            "price_data": price_data,
            "ma_line_data": self.ma_data,
            "rsi_line_data": self.rsi_data,
        }
        return json.dumps(data)

    @rx.var
    def chart_options(self) -> str:
        options: dict[str, Any] = {}
        options["chart_layout"] = {
            "layout": {
                "background": {"type": "solid", "color": "#131722"},
                "textColor": "#FFFFFFED",
            },
            "grid": {
                "horzLines": {"color": "#FFFFFF09"},
                "vertLines": {"color": "#FFFFFF09"},
            },
            "priceScale": {
                "scaleMargins": {"top": 0.1, "bottom": 0.15},
                "borderVisible": False,
            },
            "overlayPriceScales": {
                "scaleMargins": {"top": 0.7, "bottom": 0},
            },
            "timeScale": {
                "borderColor": "#FFF1E9EC",
                "rightOffset": 10,
                "minBarSpacing": 3,
                "lockVisibleTimeRangeOnResize": True,
            },
        }
        if self.selected_chart == "Candlestick":
            options["series_configs"] = {
                "upColor": "#46FEA5D4",
                "wickUpColor": "#46FEA5D4",
                "downColor": "#FF6465EB",
                "wickDownColor": "#FF6465EB",
                "borderVisible": False,
            }
        else:
            options["series_configs"] = {
                "color": "#3B9EFF",
                "lineWidth": 2,
                "priceLineVisible": False,
                "lastValueVisible": True,
                "crosshairMarkerVisible": True,
                "crosshairMarkerRadius": 4,
                "crosshairMarkerBorderColor": "#3B9EFF",
            }
        if self.rsi_line:
            options["rsi_configs"] = {
                "color": "#9176FED7",
                "lineWidth": 2,
                "priceFormat": {"type": "price", "precision": 2},
                "priceScale": "rsi-scale",
            }
        options["ma_line_configs"] = {
            period: {
                "color": unique_color,
                "lineWidth": 1.5,
                "priceLineVisible": False,
                "lastValueVisible": True,
                "crosshairMarkerVisible": True,
                "crosshairMarkerRadius": 4,
                "crosshairMarkerBorderColor": unique_color,
            }
            for period, unique_color in self.ma_period.items()
            if self.selected_ma_period.get(period, None)
        }
        return json.dumps(options)
