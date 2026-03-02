"""State for the combined tickers allrounder page."""

import reflex as rx
import asyncio
from typing import Any
from sqlalchemy import select, distinct
from collections import defaultdict
import pandas as pd

from ...state import TickerBoardState
from ...utils.database.database import get_company_session
from ...utils.database.models import OverviewORM
from ...utils.session_manager import SessionIsolatedStateMixin, session_isolated
from ...state.cart_state import CartState
from ...utils.preprocessing.financial_statements import get_transformed_dataframes
from ...utils.preprocessing.formatters import (
    format_large_number,
    format_percentage,
    format_ratio,
    format_integer,
    format_currency_vnd,
)


class TickersPageState(SessionIsolatedStateMixin, rx.State):
    # ── View mode ─────────────────────────────────────────────────────────────
    view_mode: str = "board"  # "board" | "compare"

    # ── Board / filter state ──────────────────────────────────────────────────
    search_query: str = ""
    _data_loaded: bool = False
    show_arrow: bool = True

    fundamentals_default_value: dict[str, list[float]] = {
        "pe": [0.00, 100.00],
        "pb": [0.00, 10.00],
        "roe": [0.00, 100.00],
        "roa": [0.00, 100.00],
        "doe": [0.00, 10.00],
        "eps": [100.00, 10000.00],
        "ps": [0.00, 100.00],
        "gross_margin": [0.00, 200.00],
        "net_margin": [0.00, 200.00],
        "ev": [0.00, 100.00],
        "ev_ebitda": [0.00, 200.00],
        "dividend_yield": [0.00, 100.00],
    }
    technicals_default_value: dict[str, list[float]] = {
        "rsi14": [0.00, 100.00],
        "alpha": [0.00, 5.00],
        "beta": [0.00, 5.00],
    }

    selected_sort_order: str = "ASC"
    selected_sort_option: str = "A-Z"
    sort_orders: list[str] = ["ASC", "DESC"]
    sort_options: dict[str, str] = {
        "A-Z": "symbol",
        "Market Cap": "market_cap",
        "% Change": "pct_price_change",
        "Volume": "accumulated_volume",
    }

    selected_exchange: set[str] = set()
    selected_industry: set[str] = set()
    selected_technical_metric: set[str] = set()
    selected_fundamental_metric: set[str] = set()

    exchange_filter: dict[str, bool] = {}
    industry_filter: dict[str, bool] = {}
    technicals_current_value: dict[str, list[float]] = {}
    fundamentals_current_value: dict[str, list[float]] = {}
    slider_reset_key: int = 0

    # ── Compare state ─────────────────────────────────────────────────────────
    stocks: list[dict[str, Any]] = []
    compare_list: list[str] = []
    selected_metrics: list[str] = []
    all_metrics: dict[str, list[str]] = {}
    historical_data: dict[str, list[dict[str, Any]]] = {}
    time_period: str = "quarter"
    show_graphs: bool = True
    is_loading_data: bool = False
    is_loading_historical: bool = False
    _data_cache: dict[str, dict[str, Any]] = {}

    # Pending metric buffer — absorbs dialog checkbox changes without touching
    # selected_metrics (and therefore without triggering the heavy compare-table
    # computed vars).  Flushed → selected_metrics only on dialog close.
    pending_metrics: list[str] = []
    metrics_dialog_open: bool = False

    # ── Computed vars ─────────────────────────────────────────────────────────
    @rx.var
    def has_filter(self) -> bool:
        return bool(
            self.selected_industry
            or self.selected_exchange
            or self.selected_fundamental_metric
            or self.selected_technical_metric
        )

    @rx.var
    def is_board_loading(self) -> bool:
        """True while the ticker data cache is still loading."""
        return not self._data_loaded

    @rx.var
    def max_ticker_volume(self) -> float:
        """Max volume across the current ticker list for scaling the volume bar."""
        return 0.0  # Actual max is computed client-side from TickerBoardState.tickers

    @rx.var
    def all_available_metrics(self) -> list[str]:
        metrics: list[str] = []
        for category_metrics in self.all_metrics.values():
            metrics.extend(category_metrics)
        return metrics

    @rx.var
    def metric_labels(self) -> dict[str, str]:
        labels: dict[str, str] = {}
        for metric in self.all_available_metrics:
            clean = metric.replace("(VND)", "").replace("(Bn. VND)", "")
            clean = clean.replace("(Mil. Shares)", "").replace("(%)", "")
            labels[metric] = clean.strip()
        return labels

    @rx.var
    def category_selection_state(self) -> dict[str, bool]:
        state: dict[str, bool] = {}
        for category, metrics in self.all_metrics.items():
            state[category] = bool(metrics) and all(
                m in self.pending_metrics for m in metrics
            )
        return state

    @rx.var
    def metric_selection_state(self) -> dict[str, bool]:
        return {
            metric: metric in self.pending_metrics
            for metric in self.all_available_metrics
        }

    @rx.var
    def latest_values_by_ticker(self) -> dict[str, dict[str, Any]]:
        latest: defaultdict[str, dict[str, Any]] = defaultdict(dict)
        for metric_key, metric_data in self.historical_data.items():
            if metric_data:
                latest_period = metric_data[-1]
                for ticker in self.compare_list:
                    if ticker in latest_period:
                        latest[ticker][metric_key] = latest_period[ticker]
        return dict(latest)

    @rx.var
    def formatted_stocks(self) -> list[dict[str, Any]]:
        formatted: list[dict[str, Any]] = []
        latest_values_by_ticker = self.latest_values_by_ticker
        for stock in self.stocks:
            formatted_stock: dict[str, Any] = {}
            ticker = stock.get("symbol", "")
            formatted_stock["symbol"] = ticker
            formatted_stock["industry"] = stock.get("industry", "Unknown")
            if "market_cap" in stock:
                formatted_stock["market_cap"] = format_large_number(
                    stock["market_cap"], decimals=2
                )
            for metric_name in self.selected_metrics:
                if (
                    ticker in latest_values_by_ticker
                    and metric_name in latest_values_by_ticker[ticker]
                ):
                    value = latest_values_by_ticker[ticker][metric_name]
                    formatted_stock[metric_name] = self._format_value(
                        metric_name, value
                    )
                elif metric_name in stock:
                    formatted_stock[metric_name] = self._format_value(
                        metric_name, stock[metric_name]
                    )
                else:
                    formatted_stock[metric_name] = "N/A"
            formatted.append(formatted_stock)
        return formatted

    @rx.var
    def grouped_stocks(self) -> dict[str, list[dict[str, Any]]]:
        groups: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for stock in self.formatted_stocks:
            groups[stock.get("industry", "Unknown")].append(stock)
        return dict(groups)

    @rx.var
    def industry_best_performers(self) -> dict[str, dict[str, str]]:
        industry_best: dict[str, dict[str, str]] = {}
        latest_values = self.latest_values_by_ticker
        lower_is_better = {
            "P/E",
            "P/B",
            "P/S",
            "Debt/Equity",
            "Days Sales Outstanding",
            "Days Inventory Outstanding",
        }
        for industry, stocks in self.grouped_stocks.items():
            industry_best[industry] = {}
            for metric in self.selected_metrics:
                values: list[tuple[float, str]] = []
                for stock in stocks:
                    ticker = stock.get("symbol", "")
                    if ticker in latest_values and metric in latest_values[ticker]:
                        val = latest_values[ticker][metric]
                        if val is not None and isinstance(val, (int, float)):
                            values.append((float(val), ticker))
                if values:
                    best_ticker = (min if metric in lower_is_better else max)(
                        values, key=lambda x: x[0]
                    )[1]
                    industry_best[industry][metric] = best_ticker
        return industry_best

    @rx.var
    def industry_metric_data_map(self) -> dict[str, dict[str, list[dict[str, Any]]]]:
        result: dict[str, dict[str, list[dict[str, Any]]]] = {}
        for industry, stocks in self.grouped_stocks.items():
            industry_tickers = [s.get("symbol", "") for s in stocks]
            result[industry] = {}
            for metric_key in self.selected_metrics:
                metric_data = self.historical_data.get(metric_key, [])
                result[industry][metric_key] = [
                    entry
                    for entry in metric_data
                    if any(t in entry for t in industry_tickers)
                ]
        return result

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def on_mount(self):
        old_session = getattr(self, "_session_id", None)
        super().on_mount()
        new_session = getattr(self, "_session_id", None)
        if old_session != new_session:
            self._data_loaded = False
        return TickersPageState.auto_load_data

    def on_unmount(self):
        super().on_unmount()

    @rx.event(background=True)
    @session_isolated
    async def auto_load_data(self) -> None:
        async with self:
            if self._data_loaded or not self.is_mounted():
                return
            await self._load_industries()
            if not self.is_mounted():
                return
            await self._load_exchanges()
            if not self.is_mounted():
                return
            await self._discover_metrics()
            if not self.is_mounted():
                return
            self._reset_fundamentals()
            self._reset_technicals()
            self.slider_reset_key += 1
            self.search_query = ""
            ticker_board_state = await self.get_state(TickerBoardState)
            await ticker_board_state.load_all_tickers_cache()
            self._data_loaded = True

    # ── View mode ─────────────────────────────────────────────────────────────
    @rx.event
    def set_view_mode(self, mode: str | list[str]) -> None:
        if isinstance(mode, list):
            self.view_mode = mode[0] if mode else "board"
        else:
            self.view_mode = mode

    # ── Board / filter events ─────────────────────────────────────────────────
    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value
        return TickerBoardState.set_search_query(value)

    @rx.event
    def set_sort_option(self, option: str):
        self.selected_sort_option = option
        return TickerBoardState.set_sort_option(self.sort_options[option])

    @rx.event
    def set_sort_order(self, order: str):
        self.selected_sort_order = order
        return TickerBoardState.set_sort_order(order)

    def _build_filters(self) -> dict:
        """Build the filters dict from current state — used by apply/remove."""
        return {
            "industry": self.selected_industry,
            "exchange": self.selected_exchange,
            "fundamental": {
                metric: self.fundamentals_current_value[metric]
                for metric in self.selected_fundamental_metric
            },
            "technical": {
                metric: self.technicals_current_value[metric]
                for metric in self.selected_technical_metric
            },
        }

    @rx.event
    def apply_filters(self):
        return TickerBoardState.apply_filters(filters=self._build_filters())

    @rx.event
    def remove_filter_chip(self, item: str, filter_type: str):
        """Remove a filter chip and re-apply filters."""
        if filter_type == "industry":
            self.industry_filter[item] = False
            self.selected_industry = self.selected_industry - {item}
        elif filter_type == "exchange":
            self.exchange_filter[item] = False
            self.selected_exchange = self.selected_exchange - {item}
        elif filter_type == "fundamental":
            self.fundamentals_current_value[item] = [0.00, 0.00]
            self.selected_fundamental_metric = self.selected_fundamental_metric - {item}
        elif filter_type == "technical":
            self.technicals_current_value[item] = [0.00, 0.00]
            self.selected_technical_metric = self.selected_technical_metric - {item}
        return TickerBoardState.apply_filters(filters=self._build_filters())

    @rx.event
    @session_isolated
    async def get_all_industries(self) -> None:
        await self._load_industries()

    @rx.event
    @session_isolated
    async def get_all_exchanges(self) -> None:
        await self._load_exchanges()

    @rx.event
    def get_fundamentals_default_value(self) -> None:
        self._reset_fundamentals()
        self.slider_reset_key += 1

    @rx.event
    def get_technicals_default_value(self) -> None:
        self._reset_technicals()
        self.slider_reset_key += 1

    # ── Private helpers (callable from any context) ───────────────────────────
    async def _discover_metrics(self) -> None:
        """Populate all_metrics from DB — must be called inside async with self:."""
        try:
            sample_data = await get_transformed_dataframes("VNM", period="quarter")
            if sample_data and "categorized_ratios" in sample_data:
                new_metrics: dict[str, list[str]] = {}
                for category, category_data in sample_data[
                    "categorized_ratios"
                ].items():
                    if not category_data:
                        continue
                    df = pd.DataFrame(category_data)
                    new_metrics[category] = [
                        c
                        for c in df.columns
                        if c not in {"Year", "Quarter", "period"}
                    ]
                self.all_metrics = new_metrics
        except Exception:
            pass

    async def _load_industries(self) -> None:
        try:
            async with get_company_session() as session:
                stmt = select(distinct(OverviewORM.industry))
                result = await session.execute(stmt)
                industries = [row[0] for row in result.all() if row[0] is not None]
                self.industry_filter = {item: False for item in industries}
        except Exception as e:
            print(f"TICKERS PAGE ERROR: Failed to load industries: {e}")
            self.industry_filter = {}

    async def _load_exchanges(self) -> None:
        try:
            async with get_company_session() as session:
                stmt = select(distinct(OverviewORM.exchange))
                result = await session.execute(stmt)
                exchanges = [row[0] for row in result.all() if row[0] is not None]
                self.exchange_filter = {item: False for item in exchanges}
        except Exception as e:
            print(f"TICKERS PAGE ERROR: Failed to load exchanges: {e}")
            self.exchange_filter = {}

    def _reset_fundamentals(self) -> None:
        self.fundamentals_current_value = {
            key: [0.00, 0.00] for key in self.fundamentals_default_value
        }

    def _reset_technicals(self) -> None:
        self.technicals_current_value = {
            key: [0.00, 0.00] for key in self.technicals_default_value
        }

    @rx.event
    def set_exchange(self, exchange: str, value: bool) -> None:
        self.exchange_filter[exchange] = value
        if value:
            self.selected_exchange = self.selected_exchange | {exchange}
        else:
            self.selected_exchange = self.selected_exchange - {exchange}

    @rx.event
    def set_industry(self, industry: str, value: bool) -> None:
        self.industry_filter[industry] = value
        if value:
            self.selected_industry = self.selected_industry | {industry}
        else:
            self.selected_industry = self.selected_industry - {industry}

    @rx.event
    def update_fundamental_value(self, metric: str, value: list[float]) -> None:
        """Lightweight: only update the display value (called on every drag)."""
        self.fundamentals_current_value[metric] = value

    @rx.event
    def update_technical_value(self, metric: str, value: list[float]) -> None:
        """Lightweight: only update the display value (called on every drag)."""
        self.technicals_current_value[metric] = value

    @rx.event
    def set_fundamental_metric(self, metric: str, value: list[float]) -> None:
        """Full handler: update value + active-metric set (called on release)."""
        self.fundamentals_current_value[metric] = value
        default_max = self.fundamentals_default_value[metric][1]
        if value[0] > 0.0 or (value[1] > 0.0 and value[1] < default_max):
            self.selected_fundamental_metric = self.selected_fundamental_metric | {metric}
        else:
            self.selected_fundamental_metric = self.selected_fundamental_metric - {metric}

    @rx.event
    def set_technical_metric(self, metric: str, value: list[float]) -> None:
        """Full handler: update value + active-metric set (called on release)."""
        self.technicals_current_value[metric] = value
        default_max = self.technicals_default_value[metric][1]
        if value[0] > 0.0 or (value[1] > 0.0 and value[1] < default_max):
            self.selected_technical_metric = self.selected_technical_metric | {metric}
        else:
            self.selected_technical_metric = self.selected_technical_metric - {metric}

    @rx.event
    def clear_all_filters(self):
        self.selected_technical_metric = set()
        self.selected_fundamental_metric = set()
        self.selected_industry = set()
        self.selected_exchange = set()
        self._reset_technicals()
        self._reset_fundamentals()
        self.industry_filter = {k: False for k in self.industry_filter}
        self.exchange_filter = {k: False for k in self.exchange_filter}
        self.slider_reset_key += 1
        return TickerBoardState.clear_all_filters()

    # ── Compare events ────────────────────────────────────────────────────────
    @rx.event
    def remove_stock_from_compare(self, ticker: str) -> None:
        self.compare_list = [t for t in self.compare_list if t != ticker]
        self.stocks = [s for s in self.stocks if s.get("symbol") != ticker]

    @rx.event
    def add_to_compare_from_board(self, ticker: str) -> None:
        """Add a ticker from the board view and jump to the compare view."""
        self.view_mode = "compare"
        return TickersPageState.add_ticker_to_compare(ticker)  # type: ignore[return-value]

    # ── Metrics-dialog lifecycle ──────────────────────────────────────────────

    @rx.event
    def handle_metrics_dialog_change(self, open: bool) -> None:
        if open:
            self.pending_metrics = list(self.selected_metrics)
            self.metrics_dialog_open = True
        else:
            self.selected_metrics = list(self.pending_metrics)
            self.metrics_dialog_open = False

    @rx.event
    def toggle_metric(self, metric: str) -> None:
        if metric in self.pending_metrics:
            self.pending_metrics = [m for m in self.pending_metrics if m != metric]
        else:
            self.pending_metrics = self.pending_metrics + [metric]

    @rx.event
    def toggle_category(self, category: str) -> None:
        category_metrics = self.all_metrics.get(category, [])
        all_selected = all(m in self.pending_metrics for m in category_metrics)
        if all_selected:
            self.pending_metrics = [
                m for m in self.pending_metrics if m not in category_metrics
            ]
        else:
            new_metrics = [
                m for m in category_metrics if m not in self.pending_metrics
            ]
            self.pending_metrics = self.pending_metrics + new_metrics

    @rx.event
    def select_all_metrics(self) -> None:
        self.pending_metrics = list(set(self.all_available_metrics))

    @rx.event
    def clear_all_metrics(self) -> None:
        self.pending_metrics = []

    @rx.event
    def toggle_graphs(self) -> None:
        self.show_graphs = not self.show_graphs

    @rx.event
    @session_isolated
    async def toggle_time_period(self, checked: bool) -> None:
        async with self:
            self.time_period = "year" if checked else "quarter"
        await self.fetch_historical_data()

    @rx.event
    @session_isolated
    async def add_ticker_to_compare(self, ticker: str):
        async with self:
            if ticker in self.compare_list:
                yield rx.toast.error(f"{ticker} is already in the comparison!")
                return
            self.is_loading_data = True
            time_period_copy = self.time_period
        try:
            async with self:
                self.compare_list = self.compare_list + [ticker]
            async with get_company_session() as session:
                stmt = select(
                    OverviewORM.symbol, OverviewORM.industry, OverviewORM.market_cap
                ).where(OverviewORM.symbol == ticker)
                result = await session.execute(stmt)
                row = result.mappings().first()
                if row is not None:
                    # Fetch only the new ticker's data and merge incrementally
                    data = await get_transformed_dataframes(ticker, period=time_period_copy)
                    async with self:
                        self.stocks = self.stocks + [dict(row)]
                        cache_key = f"{ticker}_{time_period_copy}"
                        self._data_cache[cache_key] = data
                        self.historical_data = self._merge_one_ticker_into_historical_data(
                            ticker, data, self.historical_data, time_period_copy
                        )
                    yield rx.toast.success(f"{ticker} added!")
                else:
                    async with self:
                        self.compare_list = [
                            t for t in self.compare_list if t != ticker
                        ]
                    yield rx.toast.error(f"No data found for {ticker}")
        except Exception:
            async with self:
                self.compare_list = [t for t in self.compare_list if t != ticker]
            yield rx.toast.error(f"Error loading {ticker}")
        finally:
            async with self:
                self.is_loading_data = False

    @rx.event
    @session_isolated
    async def import_from_cart(self) -> None:
        async with self:
            cart_state = await self.get_state(CartState)
            self.compare_list = [item["name"] for item in cart_state.cart_items]
        await self.fetch_stocks_from_compare()
        await self.fetch_historical_data()

    @rx.event
    @session_isolated
    async def fetch_stocks_from_compare(self) -> None:
        async with self:
            if not self.compare_list:
                self.stocks = []
                return
            compare_list_copy = list(self.compare_list)
        stocks: list[dict[str, Any]] = []
        try:
            async with get_company_session() as session:
                stmt = select(
                    OverviewORM.symbol,
                    OverviewORM.industry,
                    OverviewORM.market_cap,
                ).where(OverviewORM.symbol.in_(compare_list_copy))
                result = await session.execute(stmt)
                stocks = [dict(row) for row in result.mappings().all()]
        except Exception:
            pass
        async with self:
            self.stocks = stocks

    @rx.event
    @session_isolated
    async def discover_all_metrics_from_db(self) -> None:
        async with self:
            await self._discover_metrics()

    @rx.event
    @session_isolated
    async def fetch_historical_data(self) -> None:
        async with self:
            if not self.compare_list:
                return
            self.is_loading_historical = True
            compare_list_copy = list(self.compare_list)
            time_period_copy = self.time_period
            data_cache_copy = dict(self._data_cache)
        try:
            ticker_data: dict[str, Any] = {}
            tickers_to_fetch: list[str] = []
            for ticker in compare_list_copy:
                cache_key = f"{ticker}_{time_period_copy}"
                if cache_key in data_cache_copy:
                    ticker_data[ticker] = data_cache_copy[cache_key]
                else:
                    tickers_to_fetch.append(ticker)
            if tickers_to_fetch:
                tasks = [
                    get_transformed_dataframes(t, period=time_period_copy)
                    for t in tickers_to_fetch
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for ticker, result in zip(tickers_to_fetch, results):
                    if isinstance(result, Exception):
                        ticker_data[ticker] = None
                        continue
                    data_cache_copy[f"{ticker}_{time_period_copy}"] = result
                    ticker_data[ticker] = result
            historical_data_temp = self._extract_historical_data_static(
                ticker_data, time_period_copy
            )
            async with self:
                self._data_cache.update(data_cache_copy)
                self.historical_data = dict(historical_data_temp)
        except Exception:
            async with self:
                self.historical_data = {}
        finally:
            async with self:
                self.is_loading_historical = False

    @staticmethod
    def _merge_one_ticker_into_historical_data(
        ticker: str,
        ticker_data: Any,
        existing: dict[str, list[dict[str, Any]]],
        time_period: str,
    ) -> dict[str, list[dict[str, Any]]]:
        """Merge a single ticker's data into an already-built historical_data dict."""
        if not ticker_data or "categorized_ratios" not in ticker_data:
            return existing
        max_periods = 8 if time_period == "quarter" else 4
        ticker_metric_periods: defaultdict[str, dict[str, Any]] = defaultdict(dict)
        new_periods_ordered: list[str] = []
        for _category, category_data in ticker_data["categorized_ratios"].items():
            if not category_data:
                continue
            df = pd.DataFrame(category_data)
            if df.empty:
                continue
            if time_period == "quarter":
                if "Quarter" not in df.columns:
                    continue
                df["period"] = (
                    "Q" + df["Quarter"].astype(str) + " " + df["Year"].astype(str)
                )
                df = df.sort_values(by=["Year", "Quarter"], ascending=False)
            else:
                if "Quarter" in df.columns:
                    continue
                df["period"] = df["Year"].astype(str)
                df = df.sort_values(by="Year", ascending=False)
            df = df.head(max_periods)
            available_columns = [
                c for c in df.columns if c not in {"Year", "Quarter", "period"}
            ]
            for _, row in df.iterrows():
                period = str(row["period"])
                if period not in new_periods_ordered:
                    new_periods_ordered.append(period)
                for metric in available_columns:
                    val = row[metric]
                    if pd.notna(val):
                        ticker_metric_periods[metric][period] = val
        result: dict[str, list[dict[str, Any]]] = dict(existing)
        for metric, period_values in ticker_metric_periods.items():
            if metric not in result:
                result[metric] = [
                    {"period": p, ticker: v}
                    for p, v in period_values.items()
                ]
            else:
                period_index = {e["period"]: i for i, e in enumerate(result[metric])}
                new_list = [dict(e) for e in result[metric]]
                for period, val in period_values.items():
                    if period in period_index:
                        new_list[period_index[period]][ticker] = val
                    else:
                        new_list.append({"period": period, ticker: val})
                result[metric] = new_list
        return result

    @staticmethod
    def _extract_historical_data_static(
        ticker_data: dict[str, Any],
        time_period: str,
    ) -> dict[str, list[dict[str, Any]]]:
        max_periods = 8 if time_period == "quarter" else 4
        metrics_by_ticker_period: defaultdict[str, defaultdict[str, dict[str, Any]]] = (
            defaultdict(lambda: defaultdict(dict))
        )
        all_periods: list[str] = []
        for ticker, data in ticker_data.items():
            if not data or "categorized_ratios" not in data:
                continue
            for _category, category_data in data["categorized_ratios"].items():
                if not category_data:
                    continue
                df = pd.DataFrame(category_data)
                if df.empty:
                    continue
                if time_period == "quarter":
                    if "Quarter" not in df.columns:
                        continue
                    df["period"] = (
                        "Q" + df["Quarter"].astype(str) + " " + df["Year"].astype(str)
                    )
                    df = df.sort_values(by=["Year", "Quarter"], ascending=False)
                else:
                    if "Quarter" in df.columns:
                        continue
                    df["period"] = df["Year"].astype(str)
                    df = df.sort_values(by="Year", ascending=False)
                df = df.head(max_periods)
                available_columns = [
                    c for c in df.columns if c not in {"Year", "Quarter", "period"}
                ]
                for _, row in df.iterrows():
                    period: str = str(row["period"])
                    if period not in all_periods:
                        all_periods.append(period)
                    for metric in available_columns:
                        val = row[metric]
                        if pd.notna(val):
                            metrics_by_ticker_period[metric][ticker][period] = val
        result: dict[str, list[dict[str, Any]]] = {}
        for metric, tickers in metrics_by_ticker_period.items():
            metric_data: list[dict[str, Any]] = []
            for period in all_periods:
                period_entry: dict[str, Any] = {"period": period}
                for ticker, periods in tickers.items():
                    period_entry[ticker] = periods.get(period)
                metric_data.append(period_entry)
            result[metric] = metric_data
        return result

    def _get_latest_values_by_ticker(self) -> dict[str, dict[str, Any]]:
        latest_values: defaultdict[str, dict[str, Any]] = defaultdict(dict)
        for metric_key, metric_data in self.historical_data.items():
            if metric_data:
                latest_period = metric_data[-1]
                for ticker in self.compare_list:
                    if ticker in latest_period:
                        latest_values[ticker][metric_key] = latest_period[ticker]
        return dict(latest_values)

    def _format_value(self, metric_name: str, value: Any) -> str:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return "N/A"
        if "(%)" in metric_name or "Margin" in metric_name or "YoY" in metric_name:
            return format_percentage(value, decimals=2)
        elif (
            "(VND)" in metric_name
            or "(Bn. VND)" in metric_name
            or "Sales" in metric_name
        ):
            return format_currency_vnd(value, use_suffix=True)
        elif "Days" in metric_name:
            return format_integer(value)
        elif "P/" in metric_name or "Ratio" in metric_name or "/" in metric_name:
            return format_ratio(value, decimals=2)
        else:
            return format_ratio(value, decimals=2)
