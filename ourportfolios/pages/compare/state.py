"""Simplified state for stock comparison functionality."""

import reflex as rx
import pandas as pd
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from collections import defaultdict
import asyncio

from ourportfolios.state.cart_state import CartState

from ourportfolios.preprocessing.financial_statements import (
    get_transformed_dataframes,
)
from ourportfolios.preprocessing.formatters import (
    format_large_number,
    format_percentage,
    format_ratio,
    format_integer,
    format_currency_vnd,
)
from ...utils.database.database import get_company_session
from ...state.framework_state import GlobalFrameworkState


class StockComparisonState(rx.State):
    """State for comparing multiple stocks side by side."""

    # Core data
    stocks: List[Dict[str, Any]] = []
    compare_list: List[str] = []
    selected_metrics: List[str] = []

    # All available metrics from database (unfiltered)
    all_metrics: Dict[str, List[str]] = {}  # category -> [metric_names]

    # Framework-filtered metrics (if framework is active)
    framework_metrics: Dict[str, List[str]] = {}  # category -> [metric_names]

    # Historical data
    historical_data: Dict[str, List[Dict[str, Any]]] = {}

    # View configuration
    view_mode: str = "table"  # "table" or "graph"
    time_period: str = "quarter"  # "quarter" or "year"
    show_graphs: bool = True  # Toggle inline sparklines on/off

    # Loading states
    is_loading_data: bool = False
    is_loading_historical: bool = False
    has_initialized: bool = False

    # Cache for API data
    _data_cache: Dict[str, Dict[str, Any]] = {}

    @rx.var(cache=True)
    def compare_list_length(self) -> int:
        """Get the length of compare_list."""
        return len(self.compare_list)

    @rx.var(cache=True)
    def selected_metrics_length(self) -> int:
        """Get the length of selected_metrics."""
        return len(self.selected_metrics)

    @rx.var(cache=True)
    def get_metric_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get historical data for all metrics."""
        return self.historical_data

    @rx.var
    def available_metrics_by_category(self) -> Dict[str, List[str]]:
        """Get available metrics organized by category, filtered by framework if active."""
        if self.framework_metrics:
            return self.framework_metrics
        return self.all_metrics

    @rx.var
    def all_available_metrics(self) -> List[str]:
        """Flat list of all available metrics."""
        all_metrics = []
        for metrics in self.available_metrics_by_category.values():
            all_metrics.extend(metrics)
        return all_metrics

    @rx.var
    def metric_labels(self) -> Dict[str, str]:
        """Get human-readable labels for metrics (clean up display names)."""
        labels = {}
        for metric in self.all_available_metrics:
            # Remove common suffixes for display
            clean = metric.replace("(VND)", "").replace("(Bn. VND)", "")
            clean = clean.replace("(Mil. Shares)", "").replace("(%)", "")
            labels[metric] = clean.strip()
        return labels

    @rx.var
    def category_selection_state(self) -> Dict[str, bool]:
        """Get selection state for each category."""
        state = {}
        for category, metrics in self.available_metrics_by_category.items():
            if not metrics:
                state[category] = False
            else:
                state[category] = all(m in self.selected_metrics for m in metrics)
        return state

    @rx.var
    def metric_selection_state(self) -> Dict[str, bool]:
        """Get selection state for each metric."""
        return {
            metric: metric in self.selected_metrics
            for metric in self.all_available_metrics
        }

    @rx.var
    def formatted_stocks(self) -> List[Dict[str, Any]]:
        """Pre-format all stock values for display using latest period data."""
        formatted = []
        latest_values_by_ticker = self._get_latest_values_by_ticker()

        for stock in self.stocks:
            formatted_stock = {}
            ticker = stock.get("symbol", "")

            formatted_stock["symbol"] = ticker
            formatted_stock["industry"] = stock.get("industry", "Unknown")

            # Add market_cap if available
            if "market_cap" in stock:
                formatted_stock["market_cap"] = format_large_number(
                    stock["market_cap"], decimals=2
                )

            # Add all selected metrics
            for metric_name in self.selected_metrics:
                # Try latest historical data first
                if (
                    ticker in latest_values_by_ticker
                    and metric_name in latest_values_by_ticker[ticker]
                ):
                    value = latest_values_by_ticker[ticker][metric_name]
                    formatted_stock[metric_name] = self._format_value(
                        metric_name, value
                    )
                # Fall back to static data
                elif metric_name in stock:
                    formatted_stock[metric_name] = self._format_value(
                        metric_name, stock[metric_name]
                    )
                else:
                    formatted_stock[metric_name] = "N/A"

            formatted.append(formatted_stock)

        return formatted

    @rx.var
    def grouped_stocks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group formatted stocks by industry."""
        groups = defaultdict(list)
        for stock in self.formatted_stocks:
            industry = stock.get("industry", "Unknown")
            groups[industry].append(stock)
        return dict(groups)

    @rx.var
    def industry_best_performers(self) -> Dict[str, Dict[str, str]]:
        """Calculate best performer for each metric within each industry."""
        industry_best = {}
        latest_values = self._get_latest_values_by_ticker()

        # Metrics where lower is better
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
                values = []

                for stock in stocks:
                    ticker = stock.get("symbol")
                    if ticker in latest_values and metric in latest_values[ticker]:
                        val = latest_values[ticker][metric]
                        if val is not None and isinstance(val, (int, float)):
                            values.append((val, ticker))

                if values:
                    if metric in lower_is_better:
                        best_ticker = min(values, key=lambda x: x[0])[1]
                    else:
                        best_ticker = max(values, key=lambda x: x[0])[1]
                    industry_best[industry][metric] = best_ticker

        return industry_best

    @rx.var
    def industry_metric_data_map(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Get nested dictionary: industry -> metric -> data for inline graphs."""
        result = {}

        for industry, stocks in self.grouped_stocks.items():
            industry_tickers = [stock.get("symbol", "") for stock in stocks]
            result[industry] = {}

            for metric_key in self.selected_metrics:
                metric_data = self.historical_data.get(metric_key, [])
                filtered_data = []

                for period_data in metric_data:
                    has_data = any(ticker in period_data for ticker in industry_tickers)
                    if has_data:
                        filtered_data.append(period_data)

                result[industry][metric_key] = filtered_data

        return result

    def _get_latest_values_by_ticker(self) -> Dict[str, Dict[str, Any]]:
        """Get latest period values for each ticker and metric."""
        latest_values = defaultdict(dict)

        for metric_key, metric_data in self.historical_data.items():
            if metric_data and len(metric_data) > 0:
                latest_period = metric_data[-1]
                for ticker in self.compare_list:
                    if ticker in latest_period:
                        latest_values[ticker][metric_key] = latest_period[ticker]

        return latest_values

    def _format_value(self, metric_name: str, value: Any) -> str:
        """Format values for display based on metric patterns."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return "N/A"

        # Pattern-based formatting
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
    async def discover_all_metrics_from_db(self):
        """Discover ALL available metrics by fetching a sample ticker's data."""
        try:
            sample_ticker = "VNM"  # Well-known ticker with complete data

            sample_data = await get_transformed_dataframes(
                sample_ticker,
                period="quarter",
            )

            if sample_data and "categorized_ratios" in sample_data:
                self._extract_all_metrics(sample_data)
                return True
            return False

        except Exception as e:
            print(f"[ERROR] Failed to discover metrics: {e}")
            return False

    def _extract_all_metrics(self, data: Dict[str, Any]) -> None:
        """Extract all metrics from API data and store in state."""
        if "categorized_ratios" not in data:
            return

        categorized_ratios = data["categorized_ratios"]
        new_metrics = {}

        for category, category_data in categorized_ratios.items():
            if not category_data or len(category_data) == 0:
                continue

            df = pd.DataFrame(category_data)
            # Get all column names except Year, Quarter, period
            metric_columns = [
                col for col in df.columns if col not in ["Year", "Quarter", "period"]
            ]

            new_metrics[category] = metric_columns

        self.all_metrics = new_metrics

    @rx.event
    def toggle_metric(self, metric: str):
        """Toggle a metric in the selected_metrics list."""
        if metric in self.selected_metrics:
            self.selected_metrics = [m for m in self.selected_metrics if m != metric]
        else:
            self.selected_metrics = self.selected_metrics + [metric]

    @rx.event
    def toggle_category(self, category: str):
        """Toggle all metrics in a category."""
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
    def select_all_metrics(self):
        """Select all available metrics."""
        self.selected_metrics = list(set(self.all_available_metrics))

    @rx.event
    def clear_all_metrics(self):
        """Clear all selected metrics."""
        self.selected_metrics = []

    @rx.event
    def remove_stock_from_compare(self, ticker: str):
        """Remove a stock from comparison list."""
        self.compare_list = [t for t in self.compare_list if t != ticker]
        self.stocks = [s for s in self.stocks if s.get("symbol") != ticker]

    @rx.event
    async def import_cart_to_compare(self):
        """Import tickers from cart to comparison list."""
        # Import here to avoid circular dependenc

        cart_state = await self.get_state(CartState)
        tickers = [item["name"] for item in cart_state.cart_items]
        self.compare_list = tickers

    @rx.event
    async def fetch_stocks_from_compare(self):
        """Fetch stock data for tickers in compare_list from database."""
        if not self.compare_list:
            self.stocks = []
            return

        stocks = []

        try:
            async with get_company_session() as session:
                for ticker in self.compare_list:
                    try:
                        overview_query = text(
                            "SELECT symbol, industry, market_cap "
                            "FROM tickers.overview_df WHERE symbol = :symbol"
                        )
                        overview_result = await session.execute(
                            overview_query, {"symbol": ticker}
                        )
                        overview_row = overview_result.mappings().first()

                        if overview_row:
                            stock_data = {
                                "symbol": ticker,
                                "industry": overview_row["industry"],
                                "market_cap": overview_row["market_cap"],
                            }
                            stocks.append(stock_data)
                    except Exception:
                        continue
        except Exception:
            pass

        self.stocks = stocks

    @rx.event
    async def fetch_historical_data(self):
        """Fetch historical financial data for all stocks in compare list."""
        if not self.compare_list:
            return

        self.is_loading_historical = True

        try:
            ticker_data = {}
            tickers_to_fetch = []

            for ticker in self.compare_list:
                cache_key = f"{ticker}_{self.time_period}"
                if cache_key in self._data_cache:
                    ticker_data[ticker] = self._data_cache[cache_key]
                else:
                    tickers_to_fetch.append(ticker)

            # Fetch non-cached tickers
            if tickers_to_fetch:
                tasks = [
                    get_transformed_dataframes(ticker, period=self.time_period)
                    for ticker in tickers_to_fetch
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for ticker, result in zip(tickers_to_fetch, results):
                    if isinstance(result, Exception) or (
                        isinstance(result, dict) and "error" in result
                    ):
                        ticker_data[ticker] = None
                        continue

                    cache_key = f"{ticker}_{self.time_period}"
                    self._data_cache[cache_key] = result
                    ticker_data[ticker] = result

                    # Extract metrics from this data
                    self._extract_all_metrics(result)

            # Extract historical values
            historical_data_temp = self._extract_historical_data(ticker_data)
            self.historical_data = dict(historical_data_temp)

        except Exception as e:
            print(f"[ERROR] Failed to fetch historical data: {e}")
            self.historical_data = {}
        finally:
            self.is_loading_historical = False

    def _extract_historical_data(
        self, ticker_data: Dict[str, Optional[Dict[str, Any]]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Extract historical data from ticker data for all metrics."""
        max_periods = 8 if self.time_period == "quarter" else 4

        metrics_by_ticker_period = defaultdict(lambda: defaultdict(dict))
        all_periods = []

        for ticker, data in ticker_data.items():
            if not data or "categorized_ratios" not in data:
                continue

            ratios = data["categorized_ratios"]

            for category, category_data in ratios.items():
                if not category_data:
                    continue

                df = pd.DataFrame(category_data)
                if df.empty:
                    continue

                # Filter by period type
                if self.time_period == "quarter":
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
                    col
                    for col in df.columns
                    if col not in ["Year", "Quarter", "period"]
                ]

                for _, period_row in df.iterrows():
                    period = period_row["period"]
                    if period not in all_periods:
                        all_periods.append(period)

                    for column_name in available_columns:
                        value = period_row[column_name]
                        if pd.notna(value):
                            metrics_by_ticker_period[ticker][period][column_name] = (
                                float(value)
                            )

        # Sort periods
        unique_periods = list(dict.fromkeys(all_periods))

        if self.time_period == "quarter":

            def quarter_sort_key(p):
                parts = p.split()
                if len(parts) == 2:
                    quarter = int(parts[0][1:])
                    year = int(parts[1])
                    return (year, quarter)
                return (0, 0)

            sorted_periods = sorted(unique_periods, key=quarter_sort_key)
        else:
            sorted_periods = sorted(
                unique_periods, key=lambda p: int(p) if p.isdigit() else 0
            )

        # Build historical data structure
        historical_data = {}
        metrics_to_process = (
            self.selected_metrics
            if self.selected_metrics
            else self.all_available_metrics
        )

        for metric in metrics_to_process:
            metric_data = []

            for period in sorted_periods:
                period_obj = {"period": period}
                has_data = False

                for ticker in self.compare_list:
                    if (
                        ticker in metrics_by_ticker_period
                        and period in metrics_by_ticker_period[ticker]
                        and metric in metrics_by_ticker_period[ticker][period]
                    ):
                        period_obj[ticker] = metrics_by_ticker_period[ticker][period][
                            metric
                        ]
                        has_data = True

                if has_data:
                    metric_data.append(period_obj)

            historical_data[metric] = metric_data

        return historical_data

    @rx.event
    async def apply_framework_filter(self):
        """Apply framework filtering to available metrics."""
        framework_state = await self.get_state(GlobalFrameworkState)

        if not framework_state.has_selected_framework:
            # No framework - reset filtering
            self.framework_metrics = {}
            return

        # Load framework metrics if needed
        if not framework_state.framework_metrics:
            await framework_state.load_framework_metrics()

        # Match framework metrics to database metrics
        framework_categories = {}

        for (
            category,
            framework_metric_names,
        ) in framework_state.framework_metrics.items():
            matched_metrics = []

            for framework_name in framework_metric_names:
                # Normalize framework name
                fw_name = str(framework_name).strip().lower()

                # Search in all available metrics
                for db_category, db_metrics in self.all_metrics.items():
                    for db_metric in db_metrics:
                        db_name = str(db_metric).strip().lower()

                        # Simple substring matching
                        if fw_name in db_name or db_name in fw_name:
                            matched_metrics.append(db_metric)
                            break

            if matched_metrics:
                framework_categories[category] = list(set(matched_metrics))

        self.framework_metrics = framework_categories

        # Auto-select framework metrics
        if framework_categories:
            all_framework_metrics = []
            for metrics in framework_categories.values():
                all_framework_metrics.extend(metrics)
            self.selected_metrics = list(set(all_framework_metrics))

    @rx.event
    async def auto_load_from_cart(self):
        """Automatically load compare data from cart on page mount."""
        self.is_loading_data = True

        try:
            # Discover all available metrics first
            await self.discover_all_metrics_from_db()

            # Import from cart
            await self.import_cart_to_compare()

            if self.compare_list:
                # Fetch data for cart items
                await self.fetch_stocks_from_compare()
                # Always fetch historical data for inline graphs
                await self.fetch_historical_data()

            # Apply framework filtering after data is loaded
            await self.apply_framework_filter()

            self.has_initialized = True
        finally:
            self.is_loading_data = False

    @rx.event
    async def add_ticker_to_compare(self, ticker: str):
        """Add a single ticker directly to the compare list and fetch its data."""
        if ticker in self.compare_list:
            yield rx.toast.error(f"{ticker} is already in the comparison!")
            return

        self.is_loading_data = True

        try:
            self.compare_list = self.compare_list + [ticker]

            try:
                async with get_company_session() as session:
                    overview_query = text(
                        "SELECT symbol, industry, market_cap "
                        "FROM tickers.overview_df WHERE symbol = :symbol"
                    )
                    overview_result = await session.execute(
                        overview_query, {"symbol": ticker}
                    )
                    overview_row = overview_result.mappings().first()

                    if overview_row:
                        stock_data = {
                            "symbol": ticker,
                            "industry": overview_row["industry"],
                            "market_cap": overview_row["market_cap"],
                        }
                        self.stocks = self.stocks + [stock_data]

                        await self.fetch_historical_data()

                        yield rx.toast.success(f"{ticker} added to comparison!")
                    else:
                        self.compare_list = [
                            t for t in self.compare_list if t != ticker
                        ]
                        yield rx.toast.error(f"No data found for {ticker}")
            except Exception:
                self.compare_list = [t for t in self.compare_list if t != ticker]
                yield rx.toast.error(f"Error loading {ticker}")
        finally:
            self.is_loading_data = False

    @rx.event
    def toggle_view_mode(self):
        """Toggle between table and graph view."""
        self.view_mode = "graph" if self.view_mode == "table" else "table"

    @rx.event
    def toggle_graphs(self):
        """Toggle inline sparkline graphs on/off."""
        self.show_graphs = not self.show_graphs

    @rx.event
    async def toggle_time_period(self, checked: bool):
        """Toggle between quarterly and yearly time periods."""
        self.time_period = "year" if checked else "quarter"
        await self.fetch_historical_data()

    @rx.event
    async def import_and_fetch_compare(self):
        """Import tickers from cart and fetch their stock data."""
        prev_compare_list = set(self.compare_list)

        await self.import_cart_to_compare()
        await self.fetch_stocks_from_compare()

        if set(self.compare_list) != prev_compare_list:
            await self.fetch_historical_data()
            await self.apply_framework_filter()

    @rx.event
    async def toggle_and_load_graphs(self):
        """Toggle to graph view and load historical data if needed."""
        if self.view_mode == "table":
            self.view_mode = "graph"
            if not self.historical_data:
                await self.fetch_historical_data()
        else:
            self.view_mode = "table"
