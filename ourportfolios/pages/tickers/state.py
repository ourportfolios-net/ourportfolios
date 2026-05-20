"""State for the combined tickers allrounder page."""

import asyncio
from collections import defaultdict
from typing import cast

import pandas as pd
import reflex as rx
from sqlalchemy import distinct, select
from sqlalchemy.exc import SQLAlchemyError

from ourportfolios.state import TickerBoardState
from ourportfolios.state.cart_state import CartState
from ourportfolios.utils.database.database import get_company_session
from ourportfolios.utils.database.models import OverviewORM, ProfileORM
from ourportfolios.utils.preprocessing.financial_statements import (
    get_transformed_dataframes,
)
from ourportfolios.utils.preprocessing.formatters import (
    format_currency_vnd,
    format_integer,
    format_large_number,
    format_percentage,
    format_ratio,
)
from ourportfolios.utils.session_manager import (
    SessionIsolatedStateMixin,
)


class TickersPageState(SessionIsolatedStateMixin, rx.State):
    # ── View mode ─────────────────────────────────────────────────────────────
    view_mode: str = "board"  # "board" | "compare"

    # ── Board / filter state ──────────────────────────────────────────────────
    search_query: str = ""
    _data_loaded: bool = False
    _data_loading: bool = False
    _data_load_error: str = ""
    show_arrow: bool = True

    fundamentals_default_value: rx.Field[dict[str, list[float]]] = rx.Field(
        default_factory=lambda: {
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
        },
    )
    technicals_default_value: rx.Field[dict[str, list[float]]] = rx.Field(
        default_factory=lambda: {
            "rsi14": [0.00, 100.00],
            "alpha": [0.00, 5.00],
            "beta": [0.00, 5.00],
        },
    )

    selected_sort_order: str = "ASC"
    selected_sort_option: str = "A-Z"
    sort_orders: rx.Field[list[str]] = rx.Field(
        default_factory=lambda: ["ASC", "DESC"],
    )
    sort_options: rx.Field[dict[str, str]] = rx.Field(
        default_factory=lambda: {
            "A-Z": "symbol",
            "Market Cap": "market_cap",
            "% Change": "pct_price_change",
            "Volume": "accumulated_volume",
        },
    )

    selected_exchange: rx.Field[set[str]] = rx.Field(default_factory=set)
    selected_industry: rx.Field[set[str]] = rx.Field(default_factory=set)
    selected_technical_metric: rx.Field[set[str]] = rx.Field(default_factory=set)
    selected_fundamental_metric: rx.Field[set[str]] = rx.Field(default_factory=set)

    exchange_filter: rx.Field[dict[str, bool]] = rx.Field(default_factory=dict)
    industry_filter: rx.Field[dict[str, bool]] = rx.Field(default_factory=dict)
    technicals_current_value: rx.Field[dict[str, list[float]]] = rx.Field(
        default_factory=dict,
    )
    fundamentals_current_value: rx.Field[dict[str, list[float]]] = rx.Field(
        default_factory=dict,
    )
    slider_reset_key: int = 0

    # Applied (committed) filter state — only updated when Apply is clicked
    applied_fundamental_filters: rx.Field[dict[str, list[float]]] = rx.Field(
        default_factory=dict,
    )
    applied_technical_filters: rx.Field[dict[str, list[float]]] = rx.Field(
        default_factory=dict,
    )
    applied_industry: rx.Field[set[str]] = rx.Field(default_factory=set)
    applied_exchange: rx.Field[set[str]] = rx.Field(default_factory=set)

    # ── Compare state ─────────────────────────────────────────────────────────
    stocks: rx.Field[list[dict[str, object]]] = rx.Field(default_factory=list)
    compare_list: rx.Field[list[str]] = rx.Field(default_factory=list)
    selected_metrics: rx.Field[list[str]] = rx.Field(default_factory=list)
    all_metrics: rx.Field[dict[str, list[str]]] = rx.Field(default_factory=dict)
    historical_data: rx.Field[dict[str, list[dict[str, object]]]] = rx.Field(
        default_factory=dict,
    )
    time_period: str = "quarter"
    show_graphs: bool = True
    is_loading_data: bool = False
    is_loading_historical: bool = False
    _data_cache: rx.Field[dict[str, dict[str, object]]] = rx.Field(
        default_factory=dict,
    )

    pending_metrics: rx.Field[list[str]] = rx.Field(default_factory=list)
    metrics_dialog_open: bool = False

    # ── Computed vars ─────────────────────────────────────────────────────────
    @rx.var
    def has_filter(self) -> bool:
        return bool(
            self.applied_industry
            or self.applied_exchange
            or self.applied_fundamental_filters
            or self.applied_technical_filters,
        )

    @rx.var
    def fundamental_chip_items(self) -> list[list[str]]:
        """[[metric, 'lo-hi'], ...] for applied fundamental filter chips."""

        def fmt(n: float) -> str:
            return str(int(n)) if n == int(n) else f"{n:.1f}"

        return [
            [metric, f"{fmt(bounds[0])}-{fmt(bounds[1])}"]
            for metric, bounds in self.applied_fundamental_filters.items()
        ]

    @rx.var
    def technical_chip_items(self) -> list[list[str]]:
        """[[metric, 'lo-hi'], ...] for applied technical filter chips."""

        def fmt(n: float) -> str:
            return str(int(n)) if n == int(n) else f"{n:.1f}"

        return [
            [metric, f"{fmt(bounds[0])}-{fmt(bounds[1])}"]
            for metric, bounds in self.applied_technical_filters.items()
        ]

    @rx.var
    def is_board_loading(self) -> bool:
        return self._data_loading or not self._data_loaded

    @rx.var
    def max_ticker_volume(self) -> float:
        return 0.0

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
    def latest_values_by_ticker(self) -> dict[str, dict[str, object]]:
        latest: defaultdict[str, dict[str, object]] = defaultdict(dict)
        for metric_key, metric_data in self.historical_data.items():
            if metric_data:
                latest_period = metric_data[-1]
                for ticker in self.compare_list:
                    try:
                        if ticker in latest_period:
                            latest[ticker][metric_key] = latest_period[ticker]
                    except (TypeError, KeyError):
                        pass
        return dict(latest)

    @rx.var
    def formatted_stocks(self) -> list[dict[str, object]]:
        formatted: list[dict[str, object]] = []
        latest_values_by_ticker = self.latest_values_by_ticker
        for stock in self.stocks:
            formatted_stock: dict[str, object] = {}
            ticker_value = stock.get("symbol", "")
            ticker = ticker_value if isinstance(ticker_value, str) else ""
            formatted_stock["symbol"] = ticker
            formatted_stock["industry"] = stock.get("industry", "Unknown")
            formatted_stock["company_name"] = stock.get("company_name", "")
            try:
                if stock.get("market_cap") is not None:
                    formatted_stock["market_cap"] = format_large_number(
                        stock["market_cap"],
                        decimals=2,
                    )
            except (TypeError, KeyError):
                pass
            for metric_name in self.selected_metrics:
                try:
                    if (
                        ticker in latest_values_by_ticker
                        and metric_name in latest_values_by_ticker[ticker]
                    ):
                        value = latest_values_by_ticker[ticker][metric_name]
                        formatted_stock[metric_name] = self._format_value(
                            metric_name,
                            value,
                        )
                        continue
                except (TypeError, KeyError):
                    pass
                if metric_name in stock:
                    formatted_stock[metric_name] = self._format_value(
                        metric_name,
                        stock[metric_name],
                    )
                else:
                    formatted_stock[metric_name] = "N/A"
            formatted.append(formatted_stock)
        return formatted

    @rx.var
    def grouped_stocks(self) -> dict[str, list[dict[str, object]]]:
        groups: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
        for stock in self.formatted_stocks:
            industry_value = stock.get("industry", "Unknown")
            industry = industry_value if isinstance(industry_value, str) else "Unknown"
            groups[industry].append(stock)
        return dict(groups)

    @rx.var
    def pending_tickers(self) -> list[str]:
        """Tickers in compare_list that don't yet have loaded stock data."""
        loaded = {
            symbol
            for s in self.stocks
            for symbol in [s.get("symbol", "")]
            if isinstance(symbol, str)
        }
        return [t for t in self.compare_list if t not in loaded]

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
                    ticker_value = stock.get("symbol", "")
                    ticker = ticker_value if isinstance(ticker_value, str) else ""
                    try:
                        if ticker in latest_values and metric in latest_values[ticker]:
                            val = latest_values[ticker][metric]
                            if val is not None and isinstance(val, (int, float)):
                                values.append((float(val), ticker))
                    except (TypeError, KeyError):
                        pass
                if values:
                    best_ticker = (min if metric in lower_is_better else max)(
                        values,
                        key=lambda x: x[0],
                    )[1]
                    industry_best[industry][metric] = best_ticker
        return industry_best

    @rx.var
    def industry_metric_data_map(self) -> dict[str, dict[str, list[dict[str, object]]]]:
        result: dict[str, dict[str, list[dict[str, object]]]] = {}
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
    def on_mount(self) -> object:
        super().on_mount()
        # Always reset page-load flags on mount so each mount has a predictable
        # load cycle, regardless of how session ids were recycled.
        self._data_loaded = False
        self._data_loading = False
        self._data_load_error = ""
        return TickersPageState.auto_load_data

    def on_unmount(self) -> None:
        super().on_unmount()

    def _apply_board_load_result(
        self,
        tbs: TickerBoardState,
        industry_filter: dict[str, bool],
        exchange_filter: dict[str, bool],
        board_rows: list,
    ) -> str:
        """Apply fetched board data to self and tbs; return a non-empty error string on failure."""
        tbs.search_query = ""
        tbs.selected_exchange = set()
        tbs.selected_industry = set()
        tbs.selected_fundamental_metric = {}
        tbs.selected_technical_metric = {}
        tbs.tickers_data = board_rows
        tbs.load_error = ""
        self.industry_filter = industry_filter
        self.exchange_filter = exchange_filter
        self._reset_fundamentals()
        self._reset_technicals()
        self.selected_fundamental_metric = set()
        self.selected_technical_metric = set()
        self.selected_industry = set()
        self.selected_exchange = set()
        self.applied_fundamental_filters = {}
        self.applied_technical_filters = {}
        self.applied_industry = set()
        self.applied_exchange = set()
        self.slider_reset_key += 1
        self.search_query = ""
        self._data_loaded = True
        if not board_rows:
            tbs.load_error = "Failed to load ticker data."
            return "Unable to load ticker data. Please retry in a few seconds."
        return ""

    @rx.event(background=True)
    async def auto_load_data(self) -> None:
        load_error = ""
        try:
            async with self:
                if self._data_loaded or self._data_loading or not self.is_mounted():
                    return
                self._data_loading = True
                self._data_load_error = ""
        except asyncio.CancelledError:
            return

        try:
            industry_filter, exchange_filter = await asyncio.gather(
                self._load_industries(),
                self._load_exchanges(),
            )
            try:
                board_rows = await TickerBoardState._fetch_tickers_data()  # noqa: SLF001
            except Exception:  # noqa: BLE001
                board_rows = await TickerBoardState._fetch_tickers_data_fallback()  # noqa: SLF001
            async with self:
                tbs = await self.get_state(TickerBoardState)
                load_error = self._apply_board_load_result(
                    tbs,
                    industry_filter,
                    exchange_filter,
                    board_rows,
                )
        except asyncio.CancelledError:
            load_error = "Loading interrupted. Retrying may help."
        except Exception:  # noqa: BLE001
            load_error = "Unable to load ticker data."
        finally:
            try:
                async with self:
                    self._data_loading = False
                    if load_error and not self._data_load_error:
                        self._data_load_error = load_error
            except asyncio.CancelledError:
                pass

    # ── View mode ─────────────────────────────────────────────────────────────
    @rx.event
    def set_view_mode(self, mode: str | list[str]) -> object:
        if isinstance(mode, list):
            self.view_mode = mode[0] if mode else "board"
        else:
            self.view_mode = mode
        # Lazily load compare metrics the first time the user opens compare.
        if self.view_mode == "compare" and not self.all_metrics:
            return TickersPageState.load_compare_metrics
        return None

    @rx.event(background=True)
    async def load_compare_metrics(self) -> None:
        try:
            async with self:
                if self.all_metrics or not self.is_mounted():
                    return
        except asyncio.CancelledError:
            return
        all_metrics = await TickersPageState._discover_metrics()
        try:
            async with self:
                if not self.is_mounted():
                    return
                self.all_metrics = all_metrics
        except asyncio.CancelledError:
            return

    # ── Board / filter events ─────────────────────────────────────────────────
    @rx.event
    def set_search_query(self, value: str) -> object:
        self.search_query = value
        return TickerBoardState.set_search_query(value)

    @rx.event
    def set_sort_option(self, option: str) -> object:
        self.selected_sort_option = option
        return TickerBoardState.set_sort_option(self.sort_options[option])

    @rx.event
    def set_sort_order(self, order: str) -> object:
        self.selected_sort_order = order
        return TickerBoardState.set_sort_order(order)

    @rx.event
    def toggle_sort(self, field: str) -> object:
        """Toggle sort on a column.

        DESC first for numeric fields, ASC first for symbol.
        """
        current_field = self.sort_options.get(self.selected_sort_option, "")
        if current_field == field:
            new_order = "DESC" if self.selected_sort_order == "ASC" else "ASC"
            self.selected_sort_order = new_order
            return TickerBoardState.set_sort_order(new_order)
        for key, val in self.sort_options.items():
            if val == field:
                self.selected_sort_option = key
                break
        default_order = "ASC" if field == "symbol" else "DESC"
        self.selected_sort_order = default_order
        return [
            TickerBoardState.set_sort_option(field),
            TickerBoardState.set_sort_order(default_order),
        ]

    @rx.event(background=True)
    async def apply_filters(self) -> None:
        """Commit pending dialog state to applied state and push to TickerBoardState."""
        async with self:
            self.applied_fundamental_filters = {
                metric: list(self.fundamentals_current_value.get(metric, [0.0, 0.0]))
                for metric in self.selected_fundamental_metric
            }
            self.applied_technical_filters = {
                metric: list(self.technicals_current_value.get(metric, [0.0, 0.0]))
                for metric in self.selected_technical_metric
            }
            self.applied_industry = set(self.selected_industry)
            self.applied_exchange = set(self.selected_exchange)
            tbs = await self.get_state(TickerBoardState)
            tbs.selected_fundamental_metric = dict(self.applied_fundamental_filters)
            tbs.selected_technical_metric = dict(self.applied_technical_filters)
            tbs.selected_industry = set(self.applied_industry)
            tbs.selected_exchange = set(self.applied_exchange)

    @rx.event(background=True)
    async def remove_filter_chip(self, item: str, filter_type: str) -> None:
        """Remove a single applied filter chip and re-apply remaining filters."""
        async with self:
            if filter_type == "industry":
                self.industry_filter[item] = False
                self.selected_industry = self.selected_industry - {item}
                self.applied_industry = self.applied_industry - {item}
            elif filter_type == "exchange":
                self.exchange_filter[item] = False
                self.selected_exchange = self.selected_exchange - {item}
                self.applied_exchange = self.applied_exchange - {item}
            elif filter_type == "fundamental":
                self.fundamentals_current_value[item] = [0.00, 0.00]
                self.selected_fundamental_metric = self.selected_fundamental_metric - {
                    item,
                }
                self.applied_fundamental_filters = {
                    k: v
                    for k, v in self.applied_fundamental_filters.items()
                    if k != item
                }
                self.slider_reset_key += 1
            elif filter_type == "technical":
                self.technicals_current_value[item] = [0.00, 0.00]
                self.selected_technical_metric = self.selected_technical_metric - {item}
                self.applied_technical_filters = {
                    k: v for k, v in self.applied_technical_filters.items() if k != item
                }
                self.slider_reset_key += 1
            tbs = await self.get_state(TickerBoardState)
            tbs.selected_fundamental_metric = dict(self.applied_fundamental_filters)
            tbs.selected_technical_metric = dict(self.applied_technical_filters)
            tbs.selected_industry = set(self.applied_industry)
            tbs.selected_exchange = set(self.applied_exchange)

    @rx.event
    async def get_all_industries(self) -> None:
        self.industry_filter = await self._load_industries()

    @rx.event
    async def get_all_exchanges(self) -> None:
        self.exchange_filter = await self._load_exchanges()

    @rx.event
    def get_fundamentals_default_value(self) -> None:
        self._reset_fundamentals()
        self.slider_reset_key += 1

    @rx.event
    def get_technicals_default_value(self) -> None:
        self._reset_technicals()
        self.slider_reset_key += 1

    @staticmethod
    async def _discover_metrics() -> dict[str, list[str]]:
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
                        c for c in df.columns if c not in {"Year", "Quarter", "period"}
                    ]
                return new_metrics
        except (KeyError, ValueError, TypeError):
            pass
        return {}

    async def _load_industries(self) -> dict[str, bool]:
        try:
            async with get_company_session() as session:
                stmt = select(distinct(OverviewORM.industry))
                result = await session.execute(stmt)
                industries = [row[0] for row in result.all() if row[0] is not None]
            return dict.fromkeys(industries, False)
        except (SQLAlchemyError, asyncio.CancelledError):
            return {}

    async def _load_exchanges(self) -> dict[str, bool]:
        try:
            async with get_company_session() as session:
                stmt = select(distinct(OverviewORM.exchange))
                result = await session.execute(stmt)
                exchanges = [row[0] for row in result.all() if row[0] is not None]
            return dict.fromkeys(exchanges, False)
        except (SQLAlchemyError, asyncio.CancelledError):
            return {}

    def _reset_fundamentals(self) -> None:
        """Reset slider positions to [0, 0] — unselected/no-filter state."""
        self.fundamentals_current_value = {
            key: [0.00, 0.00] for key in self.fundamentals_default_value
        }

    def _reset_technicals(self) -> None:
        """Reset slider positions to [0, 0] — unselected/no-filter state."""
        self.technicals_current_value = {
            key: [0.00, 0.00] for key in self.technicals_default_value
        }

    @rx.event
    def set_exchange(self, exchange: str, *, value: bool) -> None:
        self.exchange_filter[exchange] = value
        if value:
            self.selected_exchange = self.selected_exchange | {exchange}
        else:
            self.selected_exchange = self.selected_exchange - {exchange}

    @rx.event
    def set_industry(self, industry: str, *, value: bool) -> None:
        self.industry_filter[industry] = value
        if value:
            self.selected_industry = self.selected_industry | {industry}
        else:
            self.selected_industry = self.selected_industry - {industry}

    @rx.event
    def update_fundamental_value(self, metric: str, value: list[float]) -> None:
        self.fundamentals_current_value[metric] = value

    @rx.event
    def update_technical_value(self, metric: str, value: list[float]) -> None:
        self.technicals_current_value[metric] = value

    @rx.event
    def set_fundamental_metric(self, metric: str, value: list[float]) -> None:
        self.fundamentals_current_value[metric] = value
        default_max = self.fundamentals_default_value[metric][1]
        if value[0] > 0.0 or (value[1] > 0.0 and value[1] < default_max):
            self.selected_fundamental_metric = self.selected_fundamental_metric | {
                metric,
            }
        else:
            self.selected_fundamental_metric = self.selected_fundamental_metric - {
                metric,
            }

    @rx.event
    def set_technical_metric(self, metric: str, value: list[float]) -> None:
        self.technicals_current_value[metric] = value
        default_max = self.technicals_default_value[metric][1]
        if value[0] > 0.0 or (value[1] > 0.0 and value[1] < default_max):
            self.selected_technical_metric = self.selected_technical_metric | {metric}
        else:
            self.selected_technical_metric = self.selected_technical_metric - {metric}

    @rx.event(background=True)
    async def clear_all_filters(self) -> None:
        """Clear all pending and applied filters and reset TickerBoardState."""
        async with self:
            self.selected_technical_metric = set()
            self.selected_fundamental_metric = set()
            self.selected_industry = set()
            self.selected_exchange = set()
            self.applied_fundamental_filters = {}
            self.applied_technical_filters = {}
            self.applied_industry = set()
            self.applied_exchange = set()
            self._reset_technicals()
            self._reset_fundamentals()
            self.industry_filter = dict.fromkeys(self.industry_filter, False)
            self.exchange_filter = dict.fromkeys(self.exchange_filter, False)
            self.slider_reset_key += 1
            tbs = await self.get_state(TickerBoardState)
            tbs.selected_fundamental_metric = {}
            tbs.selected_technical_metric = {}
            tbs.selected_industry = set()
            tbs.selected_exchange = set()

    # ── Compare events ────────────────────────────────────────────────────────
    @rx.event
    def remove_stock_from_compare(self, ticker: str) -> None:
        self.compare_list = [t for t in self.compare_list if t != ticker]
        self.stocks = [s for s in self.stocks if s.get("symbol") != ticker]

    @rx.event
    def add_to_compare_from_board(self, ticker: str) -> object:
        return TickersPageState.add_ticker_to_compare(ticker)  # type: ignore[return-value]

    # ── Metrics-dialog lifecycle ──────────────────────────────────────────────
    @rx.event
    def handle_metrics_dialog_change(self, *, is_open: bool) -> None:
        if is_open:
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
            self.pending_metrics = [*self.pending_metrics, metric]

    @rx.event
    def toggle_category(self, category: str) -> None:
        category_metrics = self.all_metrics.get(category, [])
        all_selected = all(m in self.pending_metrics for m in category_metrics)
        if all_selected:
            self.pending_metrics = [
                m for m in self.pending_metrics if m not in category_metrics
            ]
        else:
            new_metrics = [m for m in category_metrics if m not in self.pending_metrics]
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
    async def toggle_time_period(self, *, checked: bool) -> None:
        async with self:
            self.time_period = "year" if checked else "quarter"
        await self.fetch_historical_data()

    @rx.event(background=True)
    async def add_ticker_to_compare(self, ticker: str):
        # ── Phase 1: guard + optimistic update
        duplicate = False
        time_period_copy = "quarter"
        needs_metrics = False
        async with self:
            if ticker in self.compare_list:
                duplicate = True
            else:
                self.is_loading_data = True
                time_period_copy = self.time_period
                self.compare_list = [*self.compare_list, ticker]
                needs_metrics = not self.all_metrics

        if duplicate:
            yield rx.toast.error(f"{ticker} is already in the comparison!")
            return

        # ── Phase 2: fetch data
        try:
            row = None
            async with get_company_session() as session:
                stmt = (
                    select(
                        OverviewORM.symbol,
                        OverviewORM.industry,
                        OverviewORM.market_cap,
                        ProfileORM.company_name,
                    )
                    .outerjoin(ProfileORM, OverviewORM.symbol == ProfileORM.symbol)
                    .where(OverviewORM.symbol == ticker)
                )
                result = await session.execute(stmt)
                row = result.mappings().first()

            if row is not None:
                if needs_metrics:
                    data, all_metrics = await asyncio.gather(
                        get_transformed_dataframes(ticker, period=time_period_copy),
                        TickersPageState._discover_metrics(),
                    )
                else:
                    data = await get_transformed_dataframes(
                        ticker,
                        period=time_period_copy,
                    )
                    all_metrics = {}
                async with self:
                    self.stocks = [*self.stocks, dict(row)]
                    cache_key = f"{ticker}_{time_period_copy}"
                    self._data_cache[cache_key] = data
                    self.historical_data = (
                        self._merge_one_ticker_into_historical_data(
                            ticker,
                            data,
                            self.historical_data,
                            time_period_copy,
                        )
                    )
                    if all_metrics and not self.all_metrics:
                        self.all_metrics = all_metrics
                    if not self.selected_metrics and self.all_metrics:
                        all_m: list[str] = []
                        for ms in self.all_metrics.values():
                            all_m.extend(ms)
                        self.selected_metrics = all_m
                        self.pending_metrics = list(all_m)
                yield rx.toast.success(
                    f"{ticker} added to Compare",
                    action={
                        "label": "View",
                        "on_click": TickersPageState.set_view_mode("compare"),
                    },
                    position="bottom-right",
                    duration=5000,
                )
            else:
                async with self:
                    self.compare_list = [t for t in self.compare_list if t != ticker]
                yield rx.toast.error(f"No data found for {ticker}")
        except Exception:  # noqa: BLE001
            async with self:
                self.compare_list = [t for t in self.compare_list if t != ticker]
            yield rx.toast.error(f"Error loading {ticker}")
        finally:
            async with self:
                self.is_loading_data = False

    @rx.event
    async def import_from_cart(self) -> None:
        async with self:
            cart_state = await self.get_state(CartState)
            self.compare_list = [item["name"] for item in cart_state.cart_items]
        await self.fetch_stocks_from_compare()
        await self.fetch_historical_data()

    @rx.event
    async def fetch_stocks_from_compare(self) -> None:
        async with self:
            if not self.compare_list:
                self.stocks = []
                return
            compare_list_copy = list(self.compare_list)
        stocks: list[dict[str, object]] = []
        try:
            async with get_company_session() as session:
                stmt = (
                    select(
                        OverviewORM.symbol,
                        OverviewORM.industry,
                        OverviewORM.market_cap,
                        ProfileORM.company_name,
                    )
                    .outerjoin(ProfileORM, OverviewORM.symbol == ProfileORM.symbol)
                    .where(OverviewORM.symbol.in_(compare_list_copy))
                )
                result = await session.execute(stmt)
                stocks = [dict(row) for row in result.mappings().all()]
        except (SQLAlchemyError, asyncio.CancelledError):
            pass
        async with self:
            self.stocks = stocks

    @rx.event
    async def discover_all_metrics_from_db(self) -> None:
        self.all_metrics = await self._discover_metrics()

    @rx.event
    async def fetch_historical_data(self) -> None:
        async with self:
            if not self.compare_list:
                return
            self.is_loading_historical = True
            compare_list_copy = list(self.compare_list)
            time_period_copy = self.time_period
            data_cache_copy = dict(self._data_cache)
        try:
            ticker_data: dict[str, object] = {}
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
                for ticker, result in zip(tickers_to_fetch, results, strict=True):
                    if isinstance(result, BaseException):
                        ticker_data[ticker] = None
                        continue
                    data_cache_copy[f"{ticker}_{time_period_copy}"] = result
                    ticker_data[ticker] = result
            historical_data_temp = self._extract_historical_data_static(
                ticker_data,
                time_period_copy,
            )
            async with self:
                self._data_cache.update(data_cache_copy)
                self.historical_data = dict(historical_data_temp)
        except (ValueError, KeyError, RuntimeError):
            async with self:
                self.historical_data = {}
        finally:
            async with self:
                self.is_loading_historical = False

    @staticmethod
    def _merge_one_ticker_into_historical_data(  # noqa: C901, PLR0912
        ticker: str,
        ticker_data: object,
        existing: dict[str, list[dict[str, object]]],
        time_period: str,
    ) -> dict[str, list[dict[str, object]]]:
        if not isinstance(ticker_data, dict):
            return existing
        ticker_data_dict = cast("dict[str, object]", ticker_data)
        categorized_ratios = ticker_data_dict.get("categorized_ratios")
        if not isinstance(categorized_ratios, dict):
            return existing
        max_periods = 8 if time_period == "quarter" else 4
        ticker_metric_periods: defaultdict[str, dict[str, object]] = defaultdict(dict)
        new_periods_ordered: list[str] = []
        for raw_category_data in categorized_ratios.values():
            if not isinstance(raw_category_data, list) or not raw_category_data:
                continue
            category_data = raw_category_data
            df = pd.DataFrame(category_data)
            if df.empty:
                continue
            if time_period == "quarter":
                if "Quarter" not in df.columns:
                    continue
                df["period"] = (
                    "Q" + df["Quarter"].astype(str) + " " + df["Year"].astype(str)
                )
                df = df.sort_values(by=["Year", "Quarter"], ascending=True)
            else:
                if "Quarter" in df.columns:
                    continue
                df["period"] = df["Year"].astype(str)
                df = df.sort_values(by="Year", ascending=True)
            df = df.tail(max_periods)
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
        result: dict[str, list[dict[str, object]]] = dict(existing)
        for metric, period_values in ticker_metric_periods.items():
            if metric not in result:
                result[metric] = [
                    {"period": p, ticker: v} for p, v in period_values.items()
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
    def _extract_historical_data_static(  # noqa: C901, PLR0912
        ticker_data: dict[str, object],
        time_period: str,
    ) -> dict[str, list[dict[str, object]]]:
        max_periods = 8 if time_period == "quarter" else 4
        metrics_by_ticker_period: defaultdict[
            str,
            defaultdict[str, dict[str, object]],
        ] = defaultdict(lambda: defaultdict(dict))
        all_periods: list[str] = []
        for ticker, data in ticker_data.items():
            if not isinstance(data, dict):
                continue
            data_dict = cast("dict[str, object]", data)
            categorized_ratios = data_dict.get("categorized_ratios")
            if not isinstance(categorized_ratios, dict):
                continue
            for raw_category_data in categorized_ratios.values():
                if not isinstance(raw_category_data, list) or not raw_category_data:
                    continue
                category_data = raw_category_data
                df = pd.DataFrame(category_data)
                if df.empty:
                    continue
                if time_period == "quarter":
                    if "Quarter" not in df.columns:
                        continue
                    df["period"] = (
                        "Q" + df["Quarter"].astype(str) + " " + df["Year"].astype(str)
                    )
                    df = df.sort_values(by=["Year", "Quarter"], ascending=True)
                else:
                    if "Quarter" in df.columns:
                        continue
                    df["period"] = df["Year"].astype(str)
                    df = df.sort_values(by="Year", ascending=True)
                df = df.tail(max_periods)
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
        result: dict[str, list[dict[str, object]]] = {}
        for metric, tickers_data in metrics_by_ticker_period.items():
            period_dicts: dict[str, dict[str, object]] = {}
            for tkr, period_vals in tickers_data.items():
                for period, val in period_vals.items():
                    if period not in period_dicts:
                        period_dicts[period] = {"period": period}
                    period_dicts[period][tkr] = val
            result[metric] = [period_dicts[p] for p in all_periods if p in period_dicts]
        return result

    @staticmethod
    def _get_latest_values_by_ticker(
        historical_data: dict[str, list[dict[str, object]]],
        compare_list: list[str],
    ) -> dict[str, dict[str, object]]:
        latest: defaultdict[str, dict[str, object]] = defaultdict(dict)
        for metric_key, metric_data in historical_data.items():
            if metric_data:
                latest_period = metric_data[-1]
                for ticker in compare_list:
                    try:
                        if ticker in latest_period:
                            latest[ticker][metric_key] = latest_period[ticker]
                    except (TypeError, KeyError):
                        pass
        return dict(latest)

    @staticmethod
    def _format_value(metric_name: str, value: object) -> str:
        if value is None:
            return "N/A"
        metric_lower = metric_name.lower()
        if (
            "vnd" in metric_lower
            or "revenue" in metric_lower
            or "asset" in metric_lower
        ) and isinstance(value, (int, float)):
            return format_currency_vnd(float(value))
        if (
            "%" in metric_name
            or any(
                k in metric_lower
                for k in ("margin", "yield", "return", "growth", "rate", "ratio")
            )
        ) and isinstance(value, (int, float)):
            return format_percentage(float(value))
        if ("share" in metric_lower or "mil" in metric_lower) and isinstance(
            value,
            (int, float),
        ):
            return format_integer(int(value))
        if isinstance(value, float):
            return format_ratio(value)
        return (
            format_large_number(float(value), decimals=2)
            if isinstance(value, int)
            else str(value)
        )
