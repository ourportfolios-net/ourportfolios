"""Database query functions for data retrieval ONLY."""

from datetime import date, timedelta
import pandas as pd
from sqlalchemy import text
from vnstock import Vnstock

from .database import (
    company_sync_engine,
    company_engine,
    price_sync_engine,
    price_engine,
)


def fetch_income_statement(ticker_symbol: str, period: str = "year") -> pd.DataFrame:
    """Fetch income statement data from dedicated tables.

    Args:
        ticker_symbol: Stock ticker symbol
        period: 'year' or 'quarter'

    Returns:
        DataFrame with income statement data in wide format (columns = metrics, rows = periods)
    """
    try:
        if period == "quarter":
            query = text("""
                SELECT year, quarter, metric, value
                FROM financial_statements.income_statement_quarterly
                WHERE symbol = :symbol
                ORDER BY year DESC, quarter DESC
            """)
        else:
            query = text("""
                SELECT year, metric, value
                FROM financial_statements.income_statement_yearly
                WHERE symbol = :symbol
                ORDER BY year DESC
            """)

        with price_sync_engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"symbol": ticker_symbol})

        if df.empty:
            return pd.DataFrame()

        # Pivot from normalized format to wide format
        if period == "quarter":
            df["period"] = (
                "Q" + df["quarter"].astype(str) + " " + df["year"].astype(str)
            )
            pivot_df = df.pivot(
                index="period", columns="metric", values="value"
            ).reset_index()
            # Add year and quarter columns back
            period_map = df.set_index("period")[["year", "quarter"]].drop_duplicates()
            pivot_df = pivot_df.merge(period_map, on="period")
            # Sort by year and quarter descending to show newest first
            pivot_df = pivot_df.sort_values(
                ["year", "quarter"], ascending=False
            ).reset_index(drop=True)
        else:
            pivot_df = df.pivot(
                index="year", columns="metric", values="value"
            ).reset_index()
            # Sort by year descending to show newest first
            pivot_df = pivot_df.sort_values("year", ascending=False).reset_index(
                drop=True
            )

        return pivot_df

    except Exception:
        return pd.DataFrame()


def fetch_balance_sheet(ticker_symbol: str, period: str = "year") -> pd.DataFrame:
    """Fetch balance sheet data from dedicated tables.

    Args:
        ticker_symbol: Stock ticker symbol
        period: 'year' or 'quarter'

    Returns:
        DataFrame with balance sheet data in wide format (columns = metrics, rows = periods)
    """
    try:
        if period == "quarter":
            query = text("""
                SELECT year, quarter, metric, value
                FROM financial_statements.balance_sheet_quarterly
                WHERE symbol = :symbol
                ORDER BY year DESC, quarter DESC
            """)
        else:
            query = text("""
                SELECT year, metric, value
                FROM financial_statements.balance_sheet_yearly
                WHERE symbol = :symbol
                ORDER BY year DESC
            """)

        with price_sync_engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"symbol": ticker_symbol})

        if df.empty:
            return pd.DataFrame()

        # Pivot from normalized format to wide format
        if period == "quarter":
            df["period"] = (
                "Q" + df["quarter"].astype(str) + " " + df["year"].astype(str)
            )
            pivot_df = df.pivot(
                index="period", columns="metric", values="value"
            ).reset_index()
            # Add year and quarter columns back
            period_map = df.set_index("period")[["year", "quarter"]].drop_duplicates()
            pivot_df = pivot_df.merge(period_map, on="period")
            # Sort by year and quarter descending to show newest first
            pivot_df = pivot_df.sort_values(
                ["year", "quarter"], ascending=False
            ).reset_index(drop=True)
        else:
            pivot_df = df.pivot(
                index="year", columns="metric", values="value"
            ).reset_index()
            # Sort by year descending to show newest first
            pivot_df = pivot_df.sort_values("year", ascending=False).reset_index(
                drop=True
            )

        return pivot_df

    except Exception:
        return pd.DataFrame()


def fetch_cash_flow(ticker_symbol: str, period: str = "year") -> pd.DataFrame:
    """Fetch cash flow data from dedicated tables.

    Args:
        ticker_symbol: Stock ticker symbol
        period: 'year' or 'quarter'

    Returns:
        DataFrame with cash flow data in wide format (columns = metrics, rows = periods)
    """
    try:
        if period == "quarter":
            query = text("""
                SELECT year, quarter, metric, value
                FROM financial_statements.cash_flow_quarterly
                WHERE symbol = :symbol
                ORDER BY year DESC, quarter DESC
            """)
        else:
            query = text("""
                SELECT year, metric, value
                FROM financial_statements.cash_flow_yearly
                WHERE symbol = :symbol
                ORDER BY year DESC
            """)

        with price_sync_engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"symbol": ticker_symbol})

        if df.empty:
            return pd.DataFrame()

        # Pivot from normalized format to wide format
        if period == "quarter":
            df["period"] = (
                "Q" + df["quarter"].astype(str) + " " + df["year"].astype(str)
            )
            pivot_df = df.pivot(
                index="period", columns="metric", values="value"
            ).reset_index()
            # Add year and quarter columns back
            period_map = df.set_index("period")[["year", "quarter"]].drop_duplicates()
            pivot_df = pivot_df.merge(period_map, on="period")
            # Sort by year and quarter descending to show newest first
            pivot_df = pivot_df.sort_values(
                ["year", "quarter"], ascending=False
            ).reset_index(drop=True)
        else:
            pivot_df = df.pivot(
                index="year", columns="metric", values="value"
            ).reset_index()
            # Sort by year descending to show newest first
            pivot_df = pivot_df.sort_values("year", ascending=False).reset_index(
                drop=True
            )

        return pivot_df

    except Exception:
        return pd.DataFrame()


def fetch_company_data(symbol: str) -> dict[str, pd.DataFrame]:
    """Fetch all company data tables for a given ticker from the tickers schema.

    Args:
        symbol: Ticker symbol to fetch data for

    Returns:
        Dictionary with dataframes for each data type
    """
    tables = [
        "overview",
        "shareholders",
        "events",
        "news",
        "profile",
        "officers",
    ]

    result: dict[str, pd.DataFrame] = {}

    try:
        with company_sync_engine.connect() as conn:
            for table in tables:
                try:
                    query = text(
                        f"SELECT * FROM tickers.{table}_df WHERE symbol = :symbol"
                    )
                    df = pd.read_sql(query, conn, params={"symbol": symbol})
                    result[table] = df if not df.empty else pd.DataFrame()
                except Exception:
                    result[table] = pd.DataFrame()
    except Exception:
        for table in tables:
            result[table] = pd.DataFrame()

    return result


async def fetch_price_data_async(symbol: str) -> pd.DataFrame:
    """Fetch current price board data for a given ticker from database.

    Note: This fetches the current price board (latest prices), NOT historical OHLC data.
    Historical candlestick data is fetched from vnstock API via load_historical_data().

    Args:
        symbol: Ticker symbol

    Returns:
        DataFrame with current price board data (current_price, price_change, etc.)
    """
    try:
        query = text("""
            SELECT symbol, current_price, price_change, pct_price_change, accumulated_volume
            FROM tickers.price_df 
            WHERE symbol = :symbol
        """)
        async with price_engine.connect() as conn:
            result = await conn.execute(query, {"symbol": symbol})
            rows = result.fetchall()
            df = pd.DataFrame(rows, columns=result.keys())

        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def fetch_stats_for_ticker(symbol: str) -> pd.DataFrame:
    """Fetch statistics for a specific ticker.

    Args:
        symbol: Ticker symbol

    Returns:
        DataFrame with ticker statistics
    """
    try:
        query = text("""
            SELECT * FROM tickers.stats_df WHERE ticker = :symbol
        """)
        with company_sync_engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"symbol": symbol})
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def fetch_all_tickers() -> pd.DataFrame:
    """Fetch list of all available tickers.

    Returns:
        DataFrame with ticker information
    """
    try:
        query = text("""
            SELECT ticker, market_cap, roe, roa, pe, pb 
            FROM tickers.stats_df 
            ORDER BY market_cap DESC
        """)
        with company_sync_engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def load_historical_data(
    symbol: str,
    start: str = date.today().strftime("%Y-%m-%d"),
    end: str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
    interval: str = "15m",
) -> pd.DataFrame:
    """Load historical OHLC candlestick data from vnstock API.

    Note: This fetches time-series OHLC data from the external vnstock API for charting.
    For current price snapshot from database, use fetch_price_data_async() instead.

    Args:
        symbol: Stock ticker symbol
        start: Start date (YYYY-MM-DD format)
        end: End date (YYYY-MM-DD format)
        interval: Data interval ('1m', '15m', '1h', '1d', etc.)

    Returns:
        DataFrame with columns: time, open, high, low, close, volume
        Returns empty DataFrame if API is unavailable
    """
    try:
        stock = Vnstock().stock(symbol=symbol, source="VCI")
        df = stock.quote.history(start=start, end=end, interval=interval)
        return df.drop_duplicates(keep="last")
    except Exception:
        return pd.DataFrame(columns=["time", "open", "high", "low", "close", "volume"])


async def fetch_income_statement_async(
    ticker_symbol: str, period: str = "year"
) -> pd.DataFrame:
    """Fetch income statement data from database (async version).

    Args:
        ticker_symbol: Stock ticker symbol
        period: 'year' or 'quarter'

    Returns:
        DataFrame with income statement data in wide format
    """
    try:
        if period == "quarter":
            query = text("""
                SELECT year, quarter, metric, value
                FROM financial_statements.income_statement_quarterly
                WHERE symbol = :symbol
                ORDER BY year DESC, quarter DESC
            """)
        else:
            query = text("""
                SELECT year, metric, value
                FROM financial_statements.income_statement_yearly
                WHERE symbol = :symbol
                ORDER BY year DESC
            """)

        async with price_engine.connect() as conn:
            result = await conn.execute(query, {"symbol": ticker_symbol})
            rows = result.fetchall()
            df = pd.DataFrame(rows, columns=result.keys())

        if df.empty:
            return pd.DataFrame()

        if period == "quarter":
            df["period"] = (
                "Q" + df["quarter"].astype(str) + " " + df["year"].astype(str)
            )
            pivot_df = df.pivot(
                index="period", columns="metric", values="value"
            ).reset_index()
            period_map = df.set_index("period")[["year", "quarter"]].drop_duplicates()
            pivot_df = pivot_df.merge(period_map, on="period", how="left")
            pivot_df = pivot_df.sort_values(
                ["year", "quarter"], ascending=[False, False]
            )
            return pivot_df
        else:
            pivot_df = df.pivot(
                index="year", columns="metric", values="value"
            ).reset_index()
            pivot_df = pivot_df.sort_values("year", ascending=False)
            return pivot_df

    except Exception as e:
        return pd.DataFrame()


async def fetch_balance_sheet_async(
    ticker_symbol: str, period: str = "year"
) -> pd.DataFrame:
    """Fetch balance sheet data from database (async version).

    Args:
        ticker_symbol: Stock ticker symbol
        period: 'year' or 'quarter'

    Returns:
        DataFrame with balance sheet data in wide format
    """
    try:
        if period == "quarter":
            query = text("""
                SELECT year, quarter, metric, value
                FROM financial_statements.balance_sheet_quarterly
                WHERE symbol = :symbol
                ORDER BY year DESC, quarter DESC
            """)
        else:
            query = text("""
                SELECT year, metric, value
                FROM financial_statements.balance_sheet_yearly
                WHERE symbol = :symbol
                ORDER BY year DESC
            """)

        async with price_engine.connect() as conn:
            result = await conn.execute(query, {"symbol": ticker_symbol})
            rows = result.fetchall()
            df = pd.DataFrame(rows, columns=result.keys())

        if df.empty:
            return pd.DataFrame()

        if period == "quarter":
            df["period"] = (
                "Q" + df["quarter"].astype(str) + " " + df["year"].astype(str)
            )
            pivot_df = df.pivot(
                index="period", columns="metric", values="value"
            ).reset_index()
            period_map = df.set_index("period")[["year", "quarter"]].drop_duplicates()
            pivot_df = pivot_df.merge(period_map, on="period", how="left")
            pivot_df = pivot_df.sort_values(
                ["year", "quarter"], ascending=[False, False]
            )
            return pivot_df
        else:
            pivot_df = df.pivot(
                index="year", columns="metric", values="value"
            ).reset_index()
            pivot_df = pivot_df.sort_values("year", ascending=False)
            return pivot_df

    except Exception as e:
        return pd.DataFrame()


async def fetch_cash_flow_async(
    ticker_symbol: str, period: str = "year"
) -> pd.DataFrame:
    """Fetch cash flow data from database (async version).

    Args:
        ticker_symbol: Stock ticker symbol
        period: 'year' or 'quarter'

    Returns:
        DataFrame with cash flow data in wide format
    """
    try:
        if period == "quarter":
            query = text("""
                SELECT year, quarter, metric, value
                FROM financial_statements.cash_flow_quarterly
                WHERE symbol = :symbol
                ORDER BY year DESC, quarter DESC
            """)
        else:
            query = text("""
                SELECT year, metric, value
                FROM financial_statements.cash_flow_yearly
                WHERE symbol = :symbol
                ORDER BY year DESC
            """)

        async with price_engine.connect() as conn:
            result = await conn.execute(query, {"symbol": ticker_symbol})
            rows = result.fetchall()
            df = pd.DataFrame(rows, columns=result.keys())

        if df.empty:
            return pd.DataFrame()

        if period == "quarter":
            df["period"] = (
                "Q" + df["quarter"].astype(str) + " " + df["year"].astype(str)
            )
            pivot_df = df.pivot(
                index="period", columns="metric", values="value"
            ).reset_index()
            period_map = df.set_index("period")[["year", "quarter"]].drop_duplicates()
            pivot_df = pivot_df.merge(period_map, on="period", how="left")
            pivot_df = pivot_df.sort_values(
                ["year", "quarter"], ascending=[False, False]
            )
            return pivot_df
        else:
            pivot_df = df.pivot(
                index="year", columns="metric", values="value"
            ).reset_index()
            pivot_df = pivot_df.sort_values("year", ascending=False)
            return pivot_df

    except Exception as e:
        return pd.DataFrame()


async def fetch_ratios_async(ticker_symbol: str, period: str = "year") -> pd.DataFrame:
    """Fetch pre-computed ratios from database (async version).

    Args:
        ticker_symbol: Stock ticker symbol
        period: 'year' or 'quarter'

    Returns:
        DataFrame with ratios in wide format (columns = metrics, rows = periods)
    """
    try:
        if period == "quarter":
            query = text("""
                SELECT year, quarter, metric, value
                FROM tickers.ratio_quarterly
                WHERE symbol = :symbol
                ORDER BY year DESC, quarter DESC
            """)
        else:
            query = text("""
                SELECT year, metric, value
                FROM tickers.ratio_yearly
                WHERE symbol = :symbol
                ORDER BY year DESC
            """)

        async with company_engine.connect() as conn:
            result = await conn.execute(query, {"symbol": ticker_symbol})
            rows = result.fetchall()
            df = pd.DataFrame(rows, columns=result.keys())

        if df.empty:
            return pd.DataFrame()

        if period == "quarter":
            df["period"] = (
                "Q" + df["quarter"].astype(str) + " " + df["year"].astype(str)
            )
            pivot_df = df.pivot(
                index="period", columns="metric", values="value"
            ).reset_index()
            period_map = df.set_index("period")[["year", "quarter"]].drop_duplicates()
            pivot_df = pivot_df.merge(period_map, on="period", how="left")
            pivot_df = pivot_df.sort_values(
                ["year", "quarter"], ascending=[False, False]
            )
            return pivot_df
        else:
            pivot_df = df.pivot(
                index="year", columns="metric", values="value"
            ).reset_index()
            pivot_df = pivot_df.sort_values("year", ascending=False)
            return pivot_df

    except Exception as e:
        return pd.DataFrame()
