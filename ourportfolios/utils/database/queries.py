"""Database query functions for data retrieval ONLY."""

import pandas as pd
from sqlalchemy import text

from .database import company_sync_engine, price_sync_engine


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

    except Exception as e:
        print(f"Error fetching income statement for {ticker_symbol}: {e}")
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

    except Exception as e:
        print(f"Error fetching balance sheet for {ticker_symbol}: {e}")
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

    except Exception as e:
        print(f"Error fetching cash flow for {ticker_symbol}: {e}")
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


def fetch_price_data(symbol: str) -> pd.DataFrame:
    """Fetch price data for a given ticker.

    Args:
        symbol: Ticker symbol

    Returns:
        DataFrame with price data
    """
    try:
        query = text("""
            SELECT * FROM tickers.price_df WHERE symbol = :symbol
        """)
        with price_sync_engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"symbol": symbol})
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
