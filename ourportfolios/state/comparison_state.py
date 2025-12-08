"""State for stock comparison functionality."""

import reflex as rx
import pandas as pd
from sqlalchemy import text
from typing import List, Dict, Any
from collections import defaultdict
from ..utils.preprocessing.financial_statements import get_transformed_dataframes
from ..utils.database.database import get_company_session
import asyncio


class StockComparisonState(rx.State):
    """State for comparing multiple stocks side by side."""

    stocks: List[Dict[str, Any]] = []
    compare_list: List[str] = []
    selected_metrics: List[str] = [
        "roe",
        "pe",
        "pb",
        "dividend_yield",
        "gross_margin",
        "net_margin",
        "rsi14",
    ]

    # View mode and time period
    view_mode: str = "table"  # "table" or "graph"
    time_period: str = "quarter"  # "quarter" or "year"

    # Historical financial data for graphs
    historical_data: Dict[str, List[Dict[str, Any]]] = {}
    is_loading_historical: bool = False

    # Loading states for auto-load functionality
    is_loading_data: bool = False
    has_initialized: bool = False

    # Cache for API data - stores raw transformed dataframes by ticker and period
    _data_cache: Dict[str, Dict[str, Any]] = {}

    @rx.var
    def all_available_metrics(self) -> List[str]:
        """All available metrics that can be selected."""
        return [
            "market_cap",
            "roe",
            "roa",
            "pe",
            "pb",
            "ps",
            "ev_ebitda",
            "dividend_yield",
            "gross_margin",
            "net_margin",
            "doe",
            "alpha",
            "beta",
            "eps",
            "rsi14",
        ]

    @rx.var
    def metric_to_category_map(self) -> Dict[str, str]:
        """Map metrics to their categories."""
        return {
            "market_cap": "Valuation",
            "earnings": "Per Share Value",
            "book_value": "Per Share Value",
            "free_cash_flow": "Per Share Value",
            "dividend": "Per Share Value",
            "revenues": "Per Share Value",
            "eps": "Per Share Value",
            "roe": "Profitability",
            "roa": "Efficiency",
            "gross_margin": "Profitability",
            "net_margin": "Profitability",
            "pe": "Valuation",
            "pb": "Valuation",
            "ps": "Valuation",
            "ev_ebitda": "Valuation",
            "dividend_yield": "Profitability",
            "doe": "Leverage & Liquidity",
            "alpha": "Profitability",
            "beta": "Valuation",
            "rsi14": "Valuation",
        }

    @rx.var
    def all_metrics_by_category(self) -> Dict[str, List[str]]:
        """All metrics organized by category."""
        return {
            "Per Share Value": ["eps"],
            "Profitability": [
                "roe",
                "gross_margin",
                "net_margin",
                "dividend_yield",
                "alpha",
            ],
            "Valuation": ["market_cap", "pe", "pb", "ps", "ev_ebitda", "beta", "rsi14"],
            "Leverage & Liquidity": ["doe"],
            "Efficiency": ["roa"],
        }

    @rx.var(cache=True)
    def available_metrics_by_category(self) -> Dict[str, List[str]]:
        """Get available metrics organized by category based on selected framework."""
        # Note: We need to access GlobalFrameworkState synchronously
        # The framework filtering will be handled in the UI layer
        return self.all_metrics_by_category

    @rx.var
    def available_metrics(self) -> List[str]:
        """Flat list of all available metrics (for backwards compatibility)."""
        return self.all_available_metrics

    @rx.var
    def metric_labels(self) -> Dict[str, str]:
        """Get human-readable labels for metrics."""
        return {
            "market_cap": "Market Cap",
            "roe": "ROE",
            "roa": "ROA",
            "pe": "P/E Ratio",
            "pb": "P/B Ratio",
            "ps": "P/S Ratio",
            "ev_ebitda": "EV/EBITDA",
            "dividend_yield": "Dividend Yield",
            "gross_margin": "Gross Margin",
            "net_margin": "Net Margin",
            "doe": "DOE",
            "alpha": "Alpha",
            "beta": "Beta",
            "eps": "EPS",
            "rsi14": "RSI (14)",
        }

    @rx.var(cache=True)
    def get_metric_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get historical data for all metrics."""
        return self.historical_data

    @rx.var(cache=True)
    def has_historical_data(self) -> bool:
        """Check if any historical data is available."""
        return any(len(data) > 0 for data in self.historical_data.values())

    @rx.var(cache=True)
    def compare_list_length(self) -> int:
        """Get the length of compare_list."""
        return len(self.compare_list)

    @rx.var(cache=True)
    def selected_metrics_length(self) -> int:
        """Get the length of selected_metrics."""
        return len(self.selected_metrics)

    @rx.var(cache=True)
    def industry_stock_lists(self) -> Dict[str, List[str]]:
        """Get dictionary mapping industry to list of stock symbols."""
        result = {}
        for industry, stocks in self.grouped_stocks.items():
            result[industry] = [stock.get("symbol", "") for stock in stocks]
        return result

    @rx.var
    def industry_metric_data_map(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Get nested dictionary: industry -> metric -> data for inline graphs."""
        result = {}

        for industry, stocks in self.grouped_stocks.items():
            industry_tickers = [stock.get("symbol", "") for stock in stocks]
            result[industry] = {}

            for metric_key in self.selected_metrics:
                if metric_key not in self.historical_data:
                    result[industry][metric_key] = []
                    continue

                # Filter the metric data to only include this industry's stocks
                metric_data = self.historical_data.get(metric_key, [])
                filtered_data = []

                for period_data in metric_data:
                    # Only include if at least one ticker from this industry has data
                    has_data = any(ticker in period_data for ticker in industry_tickers)
                    if has_data:
                        filtered_data.append(period_data)

                result[industry][metric_key] = filtered_data

        return result

    @rx.var
    def grouped_stocks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group formatted stocks by industry."""
        groups = defaultdict(list)
        for stock in self.formatted_stocks:
            industry = stock.get("industry", "Unknown")
            groups[industry].append(stock)
        return dict(groups)

    @rx.var
    def formatted_stocks(self) -> List[Dict[str, Any]]:
        """Pre-format all stock values for display using latest period data."""
        formatted = []

        # Get the latest period data for each metric
        latest_values_by_ticker = defaultdict(dict)
        for metric_key, metric_data in self.historical_data.items():
            if metric_data and len(metric_data) > 0:
                # Get the most recent period (last item in the list)
                latest_period = metric_data[-1]
                for ticker in self.compare_list:
                    if ticker in latest_period:
                        latest_values_by_ticker[ticker][metric_key] = latest_period[
                            ticker
                        ]

        for stock in self.stocks:
            formatted_stock = {}
            ticker = stock.get("symbol", "")

            for key, value in stock.items():
                if key in self.selected_metrics or key == "market_cap":
                    # Use latest historical data if available, otherwise fall back to static data
                    if (
                        ticker in latest_values_by_ticker
                        and key in latest_values_by_ticker[ticker]
                    ):
                        formatted_value = latest_values_by_ticker[ticker][key]
                        formatted_stock[key] = self._format_value(key, formatted_value)
                    else:
                        formatted_stock[key] = self._format_value(key, value)
                else:
                    formatted_stock[key] = value
            formatted.append(formatted_stock)
        return formatted

    @rx.var
    def industry_best_performers(self) -> Dict[str, Dict[str, str]]:
        """Calculate best performer for each metric within each industry using latest period data."""
        industry_best = {}
        higher_better = [
            "roe",
            "roa",
            "dividend_yield",
            "gross_margin",
            "net_margin",
            "alpha",
            "eps",
        ]
        lower_better = ["pe", "pb", "ps", "ev_ebitda", "beta", "doe"]

        # Get the latest period data for each metric
        latest_values_by_ticker = defaultdict(dict)
        for metric_key, metric_data in self.historical_data.items():
            if metric_data and len(metric_data) > 0:
                # Get the most recent period (last item in the list)
                latest_period = metric_data[-1]
                for ticker in self.compare_list:
                    if ticker in latest_period:
                        latest_values_by_ticker[ticker][metric_key] = latest_period[
                            ticker
                        ]

        for industry, stocks in self.grouped_stocks.items():
            industry_best[industry] = {}

            for metric in self.selected_metrics:
                values = []
                for stock in stocks:
                    ticker = stock.get("symbol")
                    # Try to get value from latest historical data first
                    if (
                        ticker in latest_values_by_ticker
                        and metric in latest_values_by_ticker[ticker]
                    ):
                        val = latest_values_by_ticker[ticker][metric]
                        if val is not None and isinstance(val, (int, float)):
                            values.append((val, ticker))
                    else:
                        # Fall back to static data
                        original_stock = next(
                            (s for s in self.stocks if s.get("symbol") == ticker),
                            None,
                        )
                        if original_stock:
                            val = original_stock.get(metric)
                            if val is not None and isinstance(val, (int, float)):
                                values.append((val, ticker))

                if values:
                    if metric in higher_better:
                        best_ticker = max(values, key=lambda x: x[0])[1]
                    elif metric in lower_better:
                        best_ticker = min(values, key=lambda x: x[0])[1]
                    else:
                        best_ticker = None

                    industry_best[industry][metric] = best_ticker
                else:
                    industry_best[industry][metric] = None

        return industry_best

    def _format_value(self, key: str, value: Any) -> str:
        """Format values for display."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return "N/A"

        if key == "market_cap":
            # Format market cap with B VND suffix for table display
            try:
                return f"{float(value):.2f}B VND"
            except (ValueError, TypeError):
                return "N/A"
        elif key in [
            "roe",
            "roa",
            "dividend_yield",
            "gross_margin",
            "net_margin",
            "doe",
        ]:
            return f"{value:.1f}%"
        elif key in ["pe", "pb", "ps", "ev_ebitda", "alpha", "beta", "eps"]:
            return f"{value:.2f}"
        elif key == "rsi14":
            return f"{value:.0f}"
        else:
            return str(value)

    @rx.event
    def toggle_metric(self, metric: str):
        """Toggle a metric in the selected_metrics list."""
        if metric in self.selected_metrics:
            self.selected_metrics = [m for m in self.selected_metrics if m != metric]
        else:
            self.selected_metrics = self.selected_metrics + [metric]

    @rx.event
    def select_all_metrics(self):
        """Select all available metrics."""
        self.selected_metrics = self.available_metrics.copy()

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
        # Import here to avoid circular dependency
        from ..state import CartState

        cart_state = await self.get_state(CartState)
        tickers = [item["name"] for item in cart_state.cart_items]
        self.compare_list = tickers

    @rx.event
    async def fetch_stocks_from_compare(self):
        """Fetch stock data for tickers in compare_list from database."""
        tickers = self.compare_list
        stocks = []
        if not tickers:
            self.stocks = []
            return

        try:
            async with get_company_session() as session:
                for ticker in tickers:
                    try:
                        overview_query = text(
                            "SELECT symbol, industry, market_cap "
                            "FROM tickers.overview_df WHERE symbol = :symbol"
                        )
                        overview_result = await session.execute(
                            overview_query, {"symbol": ticker}
                        )
                        overview_row = overview_result.mappings().first()

                        stats_query = text(
                            "SELECT symbol, roe, roa, ev_ebitda, dividend_yield, "
                            "gross_margin, net_margin, doe, alpha, beta, pe, pb, eps, ps, rsi14 "
                            "FROM tickers.stats_df WHERE symbol = :symbol"
                        )
                        stats_result = await session.execute(
                            stats_query, {"symbol": ticker}
                        )
                        stats_row = stats_result.mappings().first()

                        if overview_row and stats_row:
                            stock_data = {
                                "symbol": ticker,
                                "industry": overview_row["industry"],
                                "market_cap": overview_row["market_cap"],
                                "roe": stats_row["roe"],
                                "roa": stats_row["roa"],
                                "ev_ebitda": stats_row["ev_ebitda"],
                                "dividend_yield": stats_row["dividend_yield"],
                                "gross_margin": stats_row["gross_margin"],
                                "net_margin": stats_row["net_margin"],
                                "doe": stats_row["doe"],
                                "alpha": stats_row["alpha"],
                                "beta": stats_row["beta"],
                                "pe": stats_row["pe"],
                                "pb": stats_row["pb"],
                                "eps": stats_row["eps"],
                                "ps": stats_row["ps"],
                                "rsi14": stats_row["rsi14"],
                            }
                            stocks.append(stock_data)
                    except Exception as e:
                        print(f"Error fetching data for {ticker}: {e}")
                        continue
        except Exception as e:
            print(f"Database session error: {e}")

        self.stocks = stocks

    @rx.event
    async def import_and_fetch_compare(self):
        """Import tickers from cart and fetch their stock data."""
        prev_compare_list = set(self.compare_list)
        await self.import_cart_to_compare()
        await self.fetch_stocks_from_compare()
        # Only fetch historical data if new tickers were added
        if set(self.compare_list) != prev_compare_list:
            await self.fetch_historical_data()

    @rx.event
    async def auto_load_from_cart(self):
        """Automatically load compare data from cart on page mount."""
        if self.has_initialized:
            return

        self.is_loading_data = True
        self.has_initialized = True

        try:
            await self.import_cart_to_compare()

            # Only fetch data if cart had items
            if self.compare_list:
                await self.fetch_stocks_from_compare()
                await self.fetch_historical_data()
        finally:
            self.is_loading_data = False

    @rx.event
    async def add_ticker_to_compare(self, ticker: str):
        """Add a single ticker directly to the compare list and fetch its data."""
        # Check if already in compare list
        if ticker in self.compare_list:
            yield rx.toast.error(f"{ticker} is already in the comparison!")
            return

        self.is_loading_data = True

        try:
            # Add to compare list
            self.compare_list = self.compare_list + [ticker]

            # Fetch data for the new ticker
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

                    stats_query = text(
                        "SELECT symbol, roe, roa, ev_ebitda, dividend_yield, "
                        "gross_margin, net_margin, doe, alpha, beta, pe, pb, eps, ps, rsi14 "
                        "FROM tickers.stats_df WHERE symbol = :symbol"
                    )
                    stats_result = await session.execute(
                        stats_query, {"symbol": ticker}
                    )
                    stats_row = stats_result.mappings().first()

                    if overview_row and stats_row:
                        stock_data = {
                            "symbol": ticker,
                            "industry": overview_row["industry"],
                            "market_cap": overview_row["market_cap"],
                            "roe": stats_row["roe"],
                            "roa": stats_row["roa"],
                            "ev_ebitda": stats_row["ev_ebitda"],
                            "dividend_yield": stats_row["dividend_yield"],
                            "gross_margin": stats_row["gross_margin"],
                            "net_margin": stats_row["net_margin"],
                            "doe": stats_row["doe"],
                            "alpha": stats_row["alpha"],
                            "beta": stats_row["beta"],
                            "pe": stats_row["pe"],
                            "pb": stats_row["pb"],
                            "eps": stats_row["eps"],
                            "ps": stats_row["ps"],
                            "rsi14": stats_row["rsi14"],
                        }
                        self.stocks = self.stocks + [stock_data]

                        # Fetch historical data only for the new ticker using cache-aware method
                        await self.fetch_historical_data()

                        yield rx.toast.success(f"{ticker} added to comparison!")
                    else:
                        # Remove from compare list if data not found
                        self.compare_list = [
                            t for t in self.compare_list if t != ticker
                        ]
                        yield rx.toast.error(f"No data found for {ticker}")
            except Exception as e:
                # Remove from compare list on error
                self.compare_list = [t for t in self.compare_list if t != ticker]
                print(f"Error fetching data for {ticker}: {e}")
                yield rx.toast.error(f"Error loading {ticker}")
        finally:
            self.is_loading_data = False

    @rx.event
    def toggle_view_mode(self):
        """Toggle between table and graph view."""
        if self.view_mode == "table":
            self.view_mode = "graph"
        else:
            self.view_mode = "table"

    @rx.event
    async def set_time_period(self, period: str):
        """Set the time period for historical data (quarter or year)."""
        self.time_period = period
        # Re-fetch historical data with new period
        await self.fetch_historical_data()

    @rx.event
    async def toggle_time_period(self, checked: bool):
        """Toggle between quarterly and yearly time periods."""
        period = "year" if checked else "quarter"
        self.time_period = period
        # Re-fetch historical data with new period
        await self.fetch_historical_data()

    @rx.event
    async def fetch_historical_data(self):
        """Fetch historical financial data for all stocks in compare list."""
        if not self.compare_list:
            return

        self.is_loading_historical = True

        # Initialize historical_data dictionary for each metric
        historical_data_temp = {metric: [] for metric in self.selected_metrics}

        try:
            # Determine which tickers need to be fetched
            tickers_to_fetch = []
            ticker_data = {}

            for ticker in self.compare_list:
                cache_key = f"{ticker}_{self.time_period}"

                # Check if data is cached
                if cache_key in self._data_cache:
                    print(f"Using cached data for {ticker} ({self.time_period})")
                    ticker_data[ticker] = self._data_cache[cache_key]
                else:
                    tickers_to_fetch.append(ticker)

            # Fetch only non-cached tickers
            if tickers_to_fetch:
                tasks = [
                    get_transformed_dataframes(ticker, period=self.time_period)
                    for ticker in tickers_to_fetch
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results and cache them
                for ticker, result in zip(tickers_to_fetch, results):
                    if isinstance(result, Exception):
                        print(f"Error fetching historical data for {ticker}: {result}")
                        ticker_data[ticker] = None
                        continue

                    if isinstance(result, dict) and "error" in result:
                        print(f"API error for {ticker}: {result['error']}")
                        ticker_data[ticker] = None
                        continue

                    # Cache the result
                    cache_key = f"{ticker}_{self.time_period}"
                    self._data_cache[cache_key] = result
                    ticker_data[ticker] = result

            # Extract metric values for each period
            # Limit to last 8 quarters or 4 years
            max_periods = 8 if self.time_period == "quarter" else 4

            # We'll use the categorized_ratios for most metrics
            all_periods = []  # Use list to maintain order
            metrics_by_ticker_period = defaultdict(lambda: defaultdict(dict))

            for ticker, data in ticker_data.items():
                if not data or "categorized_ratios" not in data:
                    continue

                ratios = data["categorized_ratios"]

                # Process each category
                for category, category_data in ratios.items():
                    if not category_data:
                        continue

                    # Convert to DataFrame for easier processing
                    df = pd.DataFrame(category_data)
                    if df.empty:
                        continue

                    # Filter by period type FIRST
                    if self.time_period == "quarter":
                        # Only include rows that have Quarter column (quarterly data)
                        if "Quarter" not in df.columns:
                            continue
                        df["period"] = (
                            "Q"
                            + df["Quarter"].astype(str)
                            + " "
                            + df["Year"].astype(str)
                        )
                        # Sort by Year and Quarter descending
                        df = df.sort_values(by=["Year", "Quarter"], ascending=False)
                    else:  # yearly
                        # Only include rows without Quarter column OR aggregate by year
                        if "Quarter" in df.columns:
                            # Skip quarterly data when year is selected
                            continue
                        df["period"] = df["Year"].astype(str)
                        # Sort by Year descending
                        df = df.sort_values(by="Year", ascending=False)

                    # Limit to last N periods for this ticker
                    df = df.head(max_periods)

                    # Map API metric names to our metric keys
                    metric_mapping = {
                        "ROE": "roe",
                        "ROA": "roa",
                        "P/E": "pe",
                        "P/B": "pb",
                        "P/S": "ps",
                        "EV/EBITDA": "ev_ebitda",
                        "Gross Margin": "gross_margin",
                        "Net Margin": "net_margin",
                    }

                    for _, period_row in df.iterrows():
                        period = period_row["period"]
                        if period not in all_periods:
                            all_periods.append(period)

                        # Extract metrics for this period
                        for api_name, metric_key in metric_mapping.items():
                            if (
                                api_name in df.columns
                                and metric_key in self.selected_metrics
                            ):
                                value = period_row[api_name]
                                if pd.notna(value):
                                    metrics_by_ticker_period[ticker][period][
                                        metric_key
                                    ] = float(value)

            # Now format the data for recharts
            # Each metric gets an array of {period, ticker1, ticker2, ...}
            # Remove duplicates while preserving order
            seen = set()
            unique_periods = []
            for period in all_periods:
                if period not in seen:
                    seen.add(period)
                    unique_periods.append(period)

            # Sort periods properly
            if self.time_period == "quarter":
                # Sort quarterly periods (Q1 2023, Q2 2023, etc.)
                def quarter_sort_key(p):
                    parts = p.split()
                    if len(parts) == 2:
                        quarter = int(parts[0][1:])  # Remove 'Q' and convert to int
                        year = int(parts[1])
                        return (year, quarter)
                    return (0, 0)

                sorted_periods = sorted(unique_periods, key=quarter_sort_key)
            else:
                # Sort yearly periods
                sorted_periods = sorted(
                    unique_periods, key=lambda p: int(p) if p.isdigit() else 0
                )

            # Already limited per-ticker above, so use all collected periods
            limited_periods = sorted_periods

            for metric in self.selected_metrics:
                metric_data = []
                for period in limited_periods:
                    period_obj = {"period": period}
                    has_data = False
                    for ticker in self.compare_list:
                        if (
                            ticker in metrics_by_ticker_period
                            and period in metrics_by_ticker_period[ticker]
                        ):
                            if metric in metrics_by_ticker_period[ticker][period]:
                                period_obj[ticker] = metrics_by_ticker_period[ticker][
                                    period
                                ][metric]
                                has_data = True

                    if has_data:
                        metric_data.append(period_obj)

                historical_data_temp[metric] = metric_data

            self.historical_data = historical_data_temp

        except Exception as e:
            print(f"Error fetching historical data: {e}")
            self.historical_data = {metric: [] for metric in self.selected_metrics}

        finally:
            self.is_loading_historical = False

    @rx.event
    async def toggle_and_load_graphs(self):
        """Toggle to graph view and load historical data if needed."""
        if self.view_mode == "table":
            self.view_mode = "graph"
            # Fetch historical data if not already loaded or if period changed
            if (
                not self.historical_data
                or len(
                    self.historical_data.get(
                        self.selected_metrics[0] if self.selected_metrics else "roe", []
                    )
                )
                == 0
            ):
                await self.fetch_historical_data()
        else:
            self.view_mode = "table"
