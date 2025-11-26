"""State for stock comparison functionality."""

import reflex as rx
import pandas as pd
from sqlalchemy import text
from typing import List, Dict, Any
from collections import defaultdict
from ..utils.scheduler import db_settings
from ..utils.preprocessing.financial_statements import get_transformed_dataframes
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

    @rx.var
    def available_metrics(self) -> List[str]:
        """All available metrics that can be selected."""
        return [
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
    def metric_labels(self) -> Dict[str, str]:
        """Get human-readable labels for metrics."""
        return {
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

    @rx.var
    def get_metric_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get historical data for all metrics."""
        return self.historical_data

    @rx.var
    def has_historical_data(self) -> bool:
        """Check if any historical data is available."""
        return any(len(data) > 0 for data in self.historical_data.values())

    @rx.var
    def compare_list_length(self) -> int:
        """Get the length of compare_list."""
        return len(self.compare_list)

    @rx.var
    def selected_metrics_length(self) -> int:
        """Get the length of selected_metrics."""
        return len(self.selected_metrics)

    @rx.var
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
        """Pre-format all stock values for display."""
        formatted = []
        for stock in self.stocks:
            formatted_stock = {}
            for key, value in stock.items():
                if key in self.selected_metrics:
                    formatted_stock[key] = self._format_value(key, value)
                else:
                    formatted_stock[key] = value
            formatted.append(formatted_stock)
        return formatted

    @rx.var
    def industry_best_performers(self) -> Dict[str, Dict[str, str]]:
        """Calculate best performer for each metric within each industry."""
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

        for industry, stocks in self.grouped_stocks.items():
            industry_best[industry] = {}

            for metric in self.selected_metrics:
                values = []
                for stock in stocks:
                    original_stock = next(
                        (
                            s
                            for s in self.stocks
                            if s.get("symbol") == stock.get("symbol")
                        ),
                        None,
                    )
                    if original_stock:
                        val = original_stock.get(metric)
                        if val is not None and isinstance(val, (int, float)):
                            values.append((val, stock.get("symbol")))

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
        if value is None:
            return "N/A"

        if key == "market_cap":
            return f"{value}B VND"
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
        if not tickers or not db_settings.conn:
            self.stocks = []
            return

        for ticker in tickers:
            try:
                overview_query = text(
                    "SELECT symbol, industry, market_cap "
                    "FROM tickers.overview_df WHERE symbol = :symbol"
                )
                overview_df = pd.read_sql(
                    overview_query, db_settings.conn, params={"symbol": ticker}
                )

                stats_query = text(
                    "SELECT symbol, roe, roa, ev_ebitda, dividend_yield, "
                    "gross_margin, net_margin, doe, alpha, beta, pe, pb, eps, ps, rsi14 "
                    "FROM tickers.stats_df WHERE symbol = :symbol"
                )
                stats_df = pd.read_sql(
                    stats_query, db_settings.conn, params={"symbol": ticker}
                )

                if not overview_df.empty and not stats_df.empty:
                    stock_data = {
                        "symbol": ticker,
                        "industry": overview_df.iloc[0]["industry"],
                        "market_cap": overview_df.iloc[0]["market_cap"],
                        "roe": stats_df.iloc[0]["roe"],
                        "roa": stats_df.iloc[0]["roa"],
                        "ev_ebitda": stats_df.iloc[0]["ev_ebitda"],
                        "dividend_yield": stats_df.iloc[0]["dividend_yield"],
                        "gross_margin": stats_df.iloc[0]["gross_margin"],
                        "net_margin": stats_df.iloc[0]["net_margin"],
                        "doe": stats_df.iloc[0]["doe"],
                        "alpha": stats_df.iloc[0]["alpha"],
                        "beta": stats_df.iloc[0]["beta"],
                        "pe": stats_df.iloc[0]["pe"],
                        "pb": stats_df.iloc[0]["pb"],
                        "eps": stats_df.iloc[0]["eps"],
                        "ps": stats_df.iloc[0]["ps"],
                        "rsi14": stats_df.iloc[0]["rsi14"],
                    }
                    stocks.append(stock_data)
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                continue

        self.stocks = stocks

    @rx.event
    async def import_and_fetch_compare(self):
        """Import tickers from cart and fetch their stock data."""
        await self.import_cart_to_compare()
        await self.fetch_stocks_from_compare()
        # Auto-fetch historical data for graphs
        await self.fetch_historical_data()

    @rx.event
    def toggle_view_mode(self):
        """Toggle between table and graph view."""
        if self.view_mode == "table":
            self.view_mode = "graph"
        else:
            self.view_mode = "table"

    @rx.event
    def set_time_period(self, period: str):
        """Set the time period for historical data (quarter or year)."""
        self.time_period = period

    @rx.event
    async def fetch_historical_data(self):
        """Fetch historical financial data for all stocks in compare list."""
        if not self.compare_list:
            return
        
        self.is_loading_historical = True
        
        # Initialize historical_data dictionary for each metric
        historical_data_temp = {metric: [] for metric in self.selected_metrics}
        
        try:
            # Fetch financial data for all tickers concurrently
            tasks = [
                get_transformed_dataframes(ticker, period=self.time_period)
                for ticker in self.compare_list
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results for each ticker
            ticker_data = {}
            for ticker, result in zip(self.compare_list, results):
                if isinstance(result, Exception):
                    print(f"Error fetching historical data for {ticker}: {result}")
                    ticker_data[ticker] = None
                    continue
                    
                if "error" in result:
                    print(f"API error for {ticker}: {result['error']}")
                    ticker_data[ticker] = None
                    continue
                
                ticker_data[ticker] = result
            
            # Extract metric values for each period
            # Limit to last 8 quarters or 4 years
            max_periods = 8 if self.time_period == "quarter" else 4
            
            # We'll use the categorized_ratios for most metrics
            all_periods = set()
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
                    
                    # Create period identifier
                    if "Quarter" in df.columns:
                        df["period"] = "Q" + df["Quarter"].astype(str) + " " + df["Year"].astype(str)
                    else:
                        df["period"] = df["Year"].astype(str)
                    
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
                    
                    for period in df["period"]:
                        all_periods.add(period)
                        period_row = df[df["period"] == period].iloc[0]
                        
                        # Extract metrics for this period
                        for api_name, metric_key in metric_mapping.items():
                            if api_name in df.columns and metric_key in self.selected_metrics:
                                value = period_row[api_name]
                                if pd.notna(value):
                                    metrics_by_ticker_period[ticker][period][metric_key] = float(value)
            
            # Now format the data for recharts
            # Each metric gets an array of {period, ticker1, ticker2, ...}
            sorted_periods = sorted(list(all_periods))
            
            # Take only the last N periods
            limited_periods = sorted_periods[-max_periods:] if len(sorted_periods) > max_periods else sorted_periods
            
            for metric in self.selected_metrics:
                metric_data = []
                for period in limited_periods:
                    period_obj = {"period": period}
                    has_data = False
                    for ticker in self.compare_list:
                        if ticker in metrics_by_ticker_period and period in metrics_by_ticker_period[ticker]:
                            if metric in metrics_by_ticker_period[ticker][period]:
                                period_obj[ticker] = metrics_by_ticker_period[ticker][period][metric]
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
            if not self.historical_data or len(self.historical_data.get(self.selected_metrics[0] if self.selected_metrics else "roe", [])) == 0:
                await self.fetch_historical_data()
        else:
            self.view_mode = "table"
