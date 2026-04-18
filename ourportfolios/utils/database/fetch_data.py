"""Database query functions for data retrieval only."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ourportfolios.utils.database.database import (
    company_engine,
    company_sync_engine,
    price_engine,
    price_sync_engine,
)

_RESAMPLE_MAP = {
    "1D": None,
    "1W": "W",
    "1M": "ME",
}

_OHLCV_AGG = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
}

_STATEMENT_QUERIES = {
    "income_statement": {
        "year": text("""
            SELECT year, metric, value
            FROM financial_statements.income_statement_yearly
            WHERE symbol = :symbol
            ORDER BY year DESC
        """),
        "quarter": text("""
            SELECT year, quarter, metric, value
            FROM financial_statements.income_statement_quarterly
            WHERE symbol = :symbol
            ORDER BY year DESC, quarter DESC
        """),
    },
    "balance_sheet": {
        "year": text("""
            SELECT year, metric, value
            FROM financial_statements.balance_sheet_yearly
            WHERE symbol = :symbol
            ORDER BY year DESC
        """),
        "quarter": text("""
            SELECT year, quarter, metric, value
            FROM financial_statements.balance_sheet_quarterly
            WHERE symbol = :symbol
            ORDER BY year DESC, quarter DESC
        """),
    },
    "cash_flow": {
        "year": text("""
            SELECT year, metric, value
            FROM financial_statements.cash_flow_yearly
            WHERE symbol = :symbol
            ORDER BY year DESC
        """),
        "quarter": text("""
            SELECT year, quarter, metric, value
            FROM financial_statements.cash_flow_quarterly
            WHERE symbol = :symbol
            ORDER BY year DESC, quarter DESC
        """),
    },
}

_COMPANY_TABLE_QUERIES = {
    "overview": text("SELECT * FROM tickers.overview_df WHERE symbol = :symbol"),
    "shareholders": text(
        "SELECT * FROM tickers.shareholders_df WHERE symbol = :symbol",
    ),
    "events": text("SELECT * FROM tickers.events_df WHERE symbol = :symbol"),
    "news": text("SELECT * FROM tickers.news_df WHERE symbol = :symbol"),
    "profile": text("SELECT * FROM tickers.profile_df WHERE symbol = :symbol"),
    "officers": text("SELECT * FROM tickers.officers_df WHERE symbol = :symbol"),
}


def _empty_price_history_df() -> pd.DataFrame:
    return pd.DataFrame(columns=["time", "open", "high", "low", "close", "volume"])


def _statement_query(statement_name: str, period: str) -> object:
    statement_map = _STATEMENT_QUERIES.get(statement_name)
    if statement_map is None:
        message = "Unsupported statement"
        raise ValueError(message)
    return statement_map["quarter" if period == "quarter" else "year"]


def _ratios_query(period: str) -> object:
    if period == "quarter":
        return text("""
            SELECT year, quarter, metric, value
            FROM tickers.ratio_quarterly
            WHERE symbol = :symbol
            ORDER BY year DESC, quarter DESC
        """)

    return text("""
        SELECT year, metric, value
        FROM tickers.ratio_yearly
        WHERE symbol = :symbol
        ORDER BY year DESC
    """)


def _pivot_financials(df: pd.DataFrame, period: str) -> pd.DataFrame:
    if period == "quarter":
        quarter_df = df.copy()
        quarter_df["period"] = (
            "Q"
            + quarter_df["quarter"].astype(str)
            + " "
            + quarter_df["year"].astype(str)
        )
        pivot_df = quarter_df.pivot_table(
            index="period",
            columns="metric",
            values="value",
            aggfunc="first",
        ).reset_index()
        period_map = quarter_df.set_index("period")[
            ["year", "quarter"]
        ].drop_duplicates()
        return (
            pivot_df.merge(period_map, on="period", how="left")
            .drop(columns=["period"])
            .sort_values(["year", "quarter"], ascending=[False, False])
            .reset_index(drop=True)
        )

    return (
        df.pivot_table(index="year", columns="metric", values="value", aggfunc="first")
        .reset_index()
        .sort_values("year", ascending=False)
        .reset_index(drop=True)
    )


def _safe_read_sql(query: object, params: dict[str, str] | None = None) -> pd.DataFrame:
    with price_sync_engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)


def _fetch_statement_sync(
    statement_name: str, ticker_symbol: str, period: str,
) -> pd.DataFrame:
    query = _statement_query(statement_name, period)
    try:
        df = _safe_read_sql(query, params={"symbol": ticker_symbol})
    except (SQLAlchemyError, ValueError, TypeError):
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()
    return _pivot_financials(df, period)


async def _fetch_statement_async(
    statement_name: str,
    ticker_symbol: str,
    period: str,
) -> pd.DataFrame:
    query = _statement_query(statement_name, period)
    try:
        async with price_engine.connect() as conn:
            result = await conn.execute(query, {"symbol": ticker_symbol})
            rows = result.fetchall()
            df = pd.DataFrame(rows, columns=result.keys())
    except (SQLAlchemyError, ValueError, TypeError):
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()
    return _pivot_financials(df, period)


def fetch_income_statement(ticker_symbol: str, period: str = "year") -> pd.DataFrame:
    return _fetch_statement_sync("income_statement", ticker_symbol, period)


def fetch_balance_sheet(ticker_symbol: str, period: str = "year") -> pd.DataFrame:
    return _fetch_statement_sync("balance_sheet", ticker_symbol, period)


def fetch_cash_flow(ticker_symbol: str, period: str = "year") -> pd.DataFrame:
    return _fetch_statement_sync("cash_flow", ticker_symbol, period)


def fetch_company_data(symbol: str) -> dict[str, pd.DataFrame]:
    result: dict[str, pd.DataFrame] = {}
    try:
        with company_sync_engine.connect() as conn:
            for table_name, query in _COMPANY_TABLE_QUERIES.items():
                try:
                    df = pd.read_sql(query, conn, params={"symbol": symbol})
                    result[table_name] = df if not df.empty else pd.DataFrame()
                except (SQLAlchemyError, ValueError, TypeError):
                    result[table_name] = pd.DataFrame()
    except (SQLAlchemyError, ValueError, TypeError):
        for table_name in _COMPANY_TABLE_QUERIES:
            result[table_name] = pd.DataFrame()

    return result


async def fetch_price_data_async(symbol: str) -> pd.DataFrame:
    query = text("""
        SELECT symbol, current_price, price_change, pct_price_change, accumulated_volume
        FROM tickers.price_df
        WHERE symbol = :symbol
    """)
    try:
        async with company_engine.connect() as conn:
            result = await conn.execute(query, {"symbol": symbol})
            rows = result.fetchall()
            df = pd.DataFrame(rows, columns=result.keys())
    except (SQLAlchemyError, ValueError, TypeError):
        return pd.DataFrame()

    return df if not df.empty else pd.DataFrame()


def fetch_stats_for_ticker(symbol: str) -> pd.DataFrame:
    query = text("""
        SELECT * FROM tickers.stats_df WHERE ticker = :symbol
    """)
    try:
        with company_sync_engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"symbol": symbol})
    except (SQLAlchemyError, ValueError, TypeError):
        return pd.DataFrame()

    return df if not df.empty else pd.DataFrame()


def fetch_all_tickers() -> pd.DataFrame:
    query = text("""
        SELECT ticker, market_cap, roe, roa, pe, pb
        FROM tickers.stats_df
        ORDER BY market_cap DESC
    """)
    try:
        with company_sync_engine.connect() as conn:
            df = pd.read_sql(query, conn)
    except (SQLAlchemyError, ValueError, TypeError):
        return pd.DataFrame()

    return df if not df.empty else pd.DataFrame()


def _default_date_range() -> tuple[str, str]:
    today = datetime.now(tz=UTC).date()
    start = today.strftime("%Y-%m-%d")
    end = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    return start, end


def load_historical_data(
    symbol: str,
    start: str | None = None,
    end: str | None = None,
    interval: str = "1D",
) -> pd.DataFrame:
    if start is None or end is None:
        default_start, default_end = _default_date_range()
        start = start or default_start
        end = end or default_end

    query = text("""
        SELECT date AS time, open, high, low, close, volume
        FROM tickers.price_history
        WHERE symbol = :symbol
          AND date >= :start
          AND date <  :end
        ORDER BY date ASC
    """)

    try:
        with company_sync_engine.connect() as conn:
            df = pd.read_sql(
                query,
                conn,
                params={"symbol": symbol, "start": start, "end": end},
            )
    except (SQLAlchemyError, ValueError, TypeError):
        return _empty_price_history_df()

    if df.empty:
        return df

    df["time"] = pd.to_datetime(df["time"])
    df = df.set_index("time")

    rule = _RESAMPLE_MAP.get(interval)
    if rule:
        df = df.resample(rule).agg(_OHLCV_AGG).dropna(subset=["close"])

    return df.reset_index()


async def fetch_income_statement_async(
    ticker_symbol: str,
    period: str = "year",
) -> pd.DataFrame:
    return await _fetch_statement_async("income_statement", ticker_symbol, period)


async def fetch_balance_sheet_async(
    ticker_symbol: str,
    period: str = "year",
) -> pd.DataFrame:
    return await _fetch_statement_async("balance_sheet", ticker_symbol, period)


async def fetch_cash_flow_async(
    ticker_symbol: str,
    period: str = "year",
) -> pd.DataFrame:
    return await _fetch_statement_async("cash_flow", ticker_symbol, period)


async def fetch_ratios_async(ticker_symbol: str, period: str = "year") -> pd.DataFrame:
    query = _ratios_query(period)
    try:
        async with company_engine.connect() as conn:
            result = await conn.execute(query, {"symbol": ticker_symbol})
            rows = result.fetchall()
            df = pd.DataFrame(rows, columns=result.keys())
    except (SQLAlchemyError, ValueError, TypeError):
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()
    return _pivot_financials(df, period)
