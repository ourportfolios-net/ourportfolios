"""State for stock comparison functionality."""

import reflex as rx
import pandas as pd
from sqlalchemy import select
from typing import Any, Optional
from collections import defaultdict
import asyncio

from ourportfolios.state.cart_state import CartState
from ourportfolios.utils.preprocessing.financial_statements import (
    get_transformed_dataframes,
)
from ourportfolios.utils.preprocessing.formatters import (
    format_large_number,
    format_percentage,
    format_ratio,
    format_integer,
    format_currency_vnd,
)
from ...utils.database.database import get_company_session
from ...utils.database.models import OverviewORM
from ...state.framework_state import GlobalFrameworkState
from ...utils.session_manager import SessionIsolatedStateMixin, session_isolated


class StockComparisonState(SessionIsolatedStateMixin, rx.State):
    stocks: list[dict[str, Any]] = []
    compare_list: list[str] = []
    selected_metrics: list[str] = []

    all_metrics: dict[str, list[str]] = {}
    framework_metrics: dict[str, list[str]] = {}
    historical_data: dict[str, list[dict[str, Any]]] = {}

    view_mode: str = "table"
    time_period: str = "quarter"
    show_graphs: bool = True

    is_loading_data: bool = False
    is_loading_historical: bool = False
    has_initialized: bool = False

    _data_cache: dict[str, dict[str, Any]] = {}

    @rx.var(cache=True)
    def compare_list_length(self) -> int:
        return len(self.compare_list)

    @rx.var(cache=True)
    def selected_metrics_length(self) -> int:
        return len(self.selected_metrics)

    @rx.var(cache=True)
    def get_metric_data(self) -> dict[str, list[dict[str, Any]]]:
        return self.historical_data

    @rx.var
    def available_metrics_by_category(self) -> dict[str, list[str]]:
        if self.framework_metrics:
            return self.framework_metrics
        return self.all_metrics

    @rx.var
    def all_available_metrics(self) -> list[str]:
        metrics: list[str] = []
        for category_metrics in self.available_metrics_by_category.values():
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
        for category, metrics in self.available_metrics_by_category.items():
            state[category] = bool(metrics) and all(
                m in self.selected_metrics for m in metrics
            )
        return state

    @rx.var
    def metric_selection_state(self) -> dict[str, bool]:
        return {
            metric: metric in self.selected_metrics
            for metric in self.all_available_metrics
        }

    @rx.var
    def formatted_stocks(self) -> list[dict[str, Any]]:
        formatted: list[dict[str, Any]] = []
        latest_values_by_ticker = self._get_latest_values_by_ticker()

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
        latest_values = self._get_latest_values_by_ticker()
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

    @rx.event
    @session_isolated
    async def discover_all_metrics_from_db(self) -> bool:
        try:
            sample_data = await get_transformed_dataframes("VNM", period="quarter")
            if sample_data and "categorized_ratios" in sample_data:
                await self._extract_all_metrics_async(sample_data)
                return True
            return False
        except Exception:
            return False

    def _extract_all_metrics(self, data: dict[str, Any]) -> None:
        if "categorized_ratios" not in data:
            return
        new_metrics: dict[str, list[str]] = {}
        for category, category_data in data["categorized_ratios"].items():
            if not category_data:
                continue
            df = pd.DataFrame(category_data)
            new_metrics[category] = [
                c for c in df.columns if c not in {"Year", "Quarter", "period"}
            ]
        self.all_metrics = new_metrics

    async def _extract_all_metrics_async(self, data: dict[str, Any]) -> None:
        if "categorized_ratios" not in data:
            return
        new_metrics: dict[str, list[str]] = {}
        for category, category_data in data["categorized_ratios"].items():
            if not category_data:
                continue
            df = pd.DataFrame(category_data)
            new_metrics[category] = [
                c for c in df.columns if c not in {"Year", "Quarter", "period"}
            ]
        async with self:
            self.all_metrics = new_metrics

    @rx.event
    def toggle_metric(self, metric: str) -> None:
        if metric in self.selected_metrics:
            self.selected_metrics = [m for m in self.selected_metrics if m != metric]
        else:
            self.selected_metrics = self.selected_metrics + [metric]

    @rx.event
    def toggle_category(self, category: str) -> None:
        category_metrics = self.available_metrics_by_category.get(category, [])
        all_selected = all(m in self.selected_metrics for m in category_metrics)
        if all_selected:
            self.selected_metrics = [
                m for m in self.selected_metrics if m not in category_metrics
            ]
        else:
            new_metrics = [
                m for m in category_metrics if m not in self.selected_metrics
            ]
            self.selected_metrics = self.selected_metrics + new_metrics

    @rx.event
    def select_all_metrics(self) -> None:
        self.selected_metrics = list(set(self.all_available_metrics))

    @rx.event
    def clear_all_metrics(self) -> None:
        self.selected_metrics = []

    @rx.event
    def remove_stock_from_compare(self, ticker: str) -> None:
        self.compare_list = [t for t in self.compare_list if t != ticker]
        self.stocks = [s for s in self.stocks if s.get("symbol") != ticker]

    @rx.event
    async def import_cart_to_compare(self) -> None:
        async with self:
            cart_state = await self.get_state(CartState)
            self.compare_list = [item["name"] for item in cart_state.cart_items]

    @rx.event
    @session_isolated
    async def fetch_stocks_from_compare(self) -> None:
        async with self:
            if not self.compare_list:
                self.stocks = []
                return

        stocks: list[dict[str, Any]] = []
        try:
            async with get_company_session() as session:
                async with self:
                    compare_list_copy = list(self.compare_list)
                for ticker in compare_list_copy:
                    try:
                        stmt = select(
                            OverviewORM.symbol,
                            OverviewORM.industry,
                            OverviewORM.market_cap,
                        ).where(OverviewORM.symbol == ticker)
                        result = await session.execute(stmt)
                        row = result.mappings().first()
                        if row is not None:
                            stocks.append(dict(row))
                    except Exception:
                        continue
        except Exception:
            pass

        async with self:
            self.stocks = stocks

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
            ticker_data: dict[str, Optional[dict[str, Any]]] = {}
            tickers_to_fetch: list[str] = []

            for ticker in compare_list_copy:
                cache_key = f"{ticker}_{time_period_copy}"
                if cache_key in data_cache_copy:
                    ticker_data[ticker] = data_cache_copy[cache_key]
                else:
                    tickers_to_fetch.append(ticker)

            if tickers_to_fetch:
                tasks = [
                    get_transformed_dataframes(ticker, period=time_period_copy)
                    for ticker in tickers_to_fetch
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for ticker, result in zip(tickers_to_fetch, results):
                    if isinstance(result, Exception) or (
                        isinstance(result, dict) and "error" in result
                    ):
                        ticker_data[ticker] = None
                        continue
                    fetched: dict[str, Any] = result  # type: ignore[assignment]
                    data_cache_copy[f"{ticker}_{time_period_copy}"] = fetched
                    ticker_data[ticker] = fetched
                    await self._extract_all_metrics_async(fetched)

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
    def _extract_historical_data_static(
        ticker_data: dict[str, Optional[dict[str, Any]]],
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

    def _extract_historical_data(
        self, ticker_data: dict[str, Optional[dict[str, Any]]]
    ) -> dict[str, list[dict[str, Any]]]:
        return self._extract_historical_data_static(ticker_data, self.time_period)

    @rx.event
    @session_isolated
    async def apply_framework_filter(self) -> None:
        async with self:
            framework_state = await self.get_state(GlobalFrameworkState)
            if not framework_state.has_selected_framework:
                self.framework_metrics = {}
                return
            if not framework_state.framework_metrics:
                await framework_state.load_framework_metrics()
            framework_categories = {
                cat: self.all_metrics[cat]
                for cat in framework_state.framework_metrics
                if cat in self.all_metrics
            }
            self.framework_metrics = framework_categories
            if framework_categories:
                all_fw_metrics = [
                    m for metrics in framework_categories.values() for m in metrics
                ]
                self.selected_metrics = list(set(all_fw_metrics))

    def on_mount(self):
        super().on_mount()
        return StockComparisonState.auto_load_from_cart

    def on_unmount(self):
        super().on_unmount()

    @rx.event(background=True)
    @session_isolated
    async def auto_load_from_cart(self) -> None:
        async with self:
            if not self.is_mounted():
                return
            self.is_loading_data = True

        try:
            if not self.is_mounted():
                return
            await self.discover_all_metrics_from_db()
            if not self.is_mounted():
                return
            await self.import_cart_to_compare()
            if not self.is_mounted():
                return
            if self.compare_list:
                await self.fetch_stocks_from_compare()
                if not self.is_mounted():
                    return
                await self.fetch_historical_data()
            if not self.is_mounted():
                return
            await self.apply_framework_filter()
            async with self:
                self.has_initialized = True
        except Exception:
            pass
        finally:
            async with self:
                self.is_loading_data = False

    @rx.event
    @session_isolated
    async def add_ticker_to_compare(self, ticker: str):
        async with self:
            if ticker in self.compare_list:
                yield rx.toast.error(f"{ticker} is already in the comparison!")
                return
            self.is_loading_data = True

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
                    async with self:
                        self.stocks = self.stocks + [dict(row)]
                    await self.fetch_historical_data()
                    yield rx.toast.success(f"{ticker} added to comparison!")
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
    def toggle_view_mode(self) -> None:
        self.view_mode = "graph" if self.view_mode == "table" else "table"

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
    async def import_and_fetch_compare(self) -> None:
        async with self:
            prev_compare_list = set(self.compare_list)

        await self.import_cart_to_compare()
        await self.fetch_stocks_from_compare()

        changed: bool = False
        async with self:
            changed = set(self.compare_list) != prev_compare_list

        if changed:
            await self.fetch_historical_data()
            await self.apply_framework_filter()

    @rx.event
    @session_isolated
    async def toggle_and_load_graphs(self) -> None:
        should_load = False
        async with self:
            if self.view_mode == "table":
                self.view_mode = "graph"
                if not self.historical_data:
                    should_load = True
            else:
                self.view_mode = "table"

        if should_load:
            await self.fetch_historical_data()
