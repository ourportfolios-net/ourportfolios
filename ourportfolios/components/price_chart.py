import reflex as rx
import pandas as pd
from typing import List, Dict, Any
from datetime import date
from dateutil.relativedelta import relativedelta
import json

from ..utils.compute_instrument import compute_ma, compute_rsi
from ..utils.database.load_data import load_historical_data


# Price chart State
class PriceChartState(rx.State):
    df: pd.DataFrame = pd.DataFrame()
    selected_interval: str = "1D"
    selected_chart: str = "Candlestick"
    selected_ma_period: Dict[str, bool] = {}
    rsi_line: bool = False

    ma_period: Dict[str, Any] = {
        "5": "#D19DFF",  # purple 11
        "10": "#B661FFC2",  # purple 9
        "20": "#AEFEEDF5",  # mint 10
        "50": "#41FFDF76",  # mint 8
        "100": "#70B8FF",  # blue 11
        "200": "#3094FEB9",  # blue 8
    }

    df_by_interval: Dict[str, Any] = {
        "1D": pd.DataFrame(),
        "1W": pd.DataFrame(),
        "1M": pd.DataFrame(),
    }
    # Date range for each interval
    interval_range: Dict[str, Any] = {
        "1D": date.today() - relativedelta(years=5),
        "1W": date.today(),
        "1M": date.today(),
    }

    rsi_period: int = 14

    @rx.event
    def load_state(self):
        """Initialize chart with default settings"""
        ticker: str = self.ticker

        # Fetch data for each interval. Time ranges are {
        #     1D: 3 years
        #     1W: 5 years (default)
        #     1M: all (default)
        # }
        self.df_by_interval = {
            i_range: load_historical_data(
                symbol=ticker,
                start=(self.interval_range[i_range]).strftime("%Y-%m-%d"),
                end=(date.today() + relativedelta(days=1)).strftime("%Y-%m-%d"),
                interval=i_range,
            )
            for i_range in self.df_by_interval.keys()
        }

        # Default range
        self.df: pd.DataFrame = self.df_by_interval[self.selected_interval]

        # Loads MA options
        self.selected_ma_period = {item: False for item in self.ma_period.keys()}

        # Initialize chart
        yield from self.render_price_chart()

    @rx.event
    def render_price_chart(self):
        yield rx.call_script(
            f"""render_price_chart({self.chart_options}, {self.chart_data})"""
        )

    @rx.event
    def set_interval(self, _range):
        self.selected_interval = _range
        self.df = self.df_by_interval[self.selected_interval]

        yield from self.render_price_chart()

    @rx.event
    def set_selection(self):
        if self.selected_chart == "Candlestick":
            self.selected_chart = "Price"
        else:
            self.selected_chart = "Candlestick"
        yield from self.render_price_chart()

    @rx.event
    def add_ma_period(self, value: bool, period: str):
        self.selected_ma_period[period] = value
        yield from self.render_price_chart()

    @rx.event
    def add_rsi_line(self):
        if not self.rsi_line:
            self.rsi_line = True
        else:
            self.rsi_line = False
        yield from self.render_price_chart()

    @rx.var
    def ohlc_data(self) -> List[Dict[str, Any]]:
        """Return a list of {time, open, high, low, close}"""
        if self.df.empty:
            return []

        df2 = self.df.copy()
        if "time" not in self.df.columns:
            df2 = df2.reset_index()

        df2["time"] = df2["time"].apply(lambda x: x.strftime("%Y-%m-%d"))
        return df2.to_dict("records")

    @rx.var
    def price_data(self) -> List[Dict[str, Any]]:
        """Return a list of {time, value } from 'close'"""
        if (self.df.empty) or (not {"time", "close"}.issubset(self.df.columns)):
            return []

        df2 = self.df[["time", "close"]].rename(columns={"close": "value"})
        df2["time"] = df2["time"].apply(lambda x: x.strftime("%Y-%m-%d"))
        return df2.dropna(how="any", axis=0).to_dict("records")

    @rx.var
    def ma_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """If ma_period > 0, compute MA"""
        if self.df.empty:
            return {}

        df2 = self.df.copy()
        if "time" not in df2.columns:
            df2 = df2.reset_index()

        ma_data = {
            period: compute_ma(df2, ma_period=int(period))
            for period, state in self.selected_ma_period.items()
            if state
        }
        return ma_data

    @rx.var
    def rsi_data(self) -> List[Dict[str, Any]]:
        """If rsi_period > 0, compute RSI"""
        if self.df.empty or not self.rsi_line:
            return []

        df2 = self.df.copy()
        if "time" not in df2.columns:
            df2 = df2.reset_index()
        return compute_rsi(df2, self.rsi_period)

    @rx.var
    def chart_data(self) -> str:
        """Summarize chart data"""
        # Price
        price_data = (
            self.ohlc_data if self.selected_chart == "Candlestick" else self.price_data
        )
        # MA line
        ma_line_data = self.ma_data
        # RSI line
        rsi_line_data = self.rsi_data

        data: Dict[str, Any] = {
            "type": self.selected_chart,
            "price_data": price_data,
            "ma_line_data": ma_line_data,
            "rsi_line_data": rsi_line_data,
        }

        return json.dumps(data)

    # Chart layout
    @rx.var
    def chart_options(self) -> str:
        """Return chart configurations"""
        options: Dict[str, Any] = {}
        # Chart layout
        options["chart_layout"] = {
            "layout": {
                "background": {"type": "solid", "color": "#131722"},
                "textColor": "#FFFFFFED",  # gray 12
            },
            "grid": {
                "horzLines": {"color": "#FFFFFF09"},  # gray 2
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
                "borderColor": "#FFF1E9EC",  # bronze 12
                "rightOffset": 10,
                "minBarSpacing": 3,
                "lockVisibleTimeRangeOnResize": True,
            },
        }
        # Series setting
        if self.selected_chart == "Candlestick":
            options["series_configs"] = {
                "upColor": "#46FEA5D4",  # green 11
                "wickUpColor": "#46FEA5D4",
                "downColor": "#FF6465EB",  # red 10
                "wickDownColor": "#FF6465EB",
                "borderVisible": False,
            }
        else:
            options["series_configs"] = {
                "color": "#3B9EFF",  # blue 10
                "lineWidth": 2,
                "priceLineVisible": False,
                "lastValueVisible": True,
                "crosshairMarkerVisible": True,
                "crosshairMarkerRadius": 4,
                "crosshairMarkerBorderColor": "#3B9EFF",  # blue 10
            }

        # RSI setting
        if self.rsi_line:
            options["rsi_configs"] = {
                "color": "#9176FED7",  # violet 10
                "lineWidth": 2,
                "priceFormat": {
                    "type": "price",
                    "precision": 2,
                },
                "priceScale": "rsi-scale",
            }

        # MA lines
        options["ma_line_configs"] = {
            period: {
                "color": unique_color,
                "lineWidth": 1.5,
                "priceLineVisible": False,
                "lastValueVisible": True,
                "crosshairMarkerVisible": True,
                "crosshairMarkerRadius": 4,
                "crosshairMarkerBorderColor": unique_color,  # blue 10
            }
            for period, unique_color in self.ma_period.items()
            if self.selected_ma_period.get(
                period, None
            )  # Each ma line is binded to its unique color
        }

        return json.dumps(options)
