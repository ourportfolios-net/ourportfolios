"""Schema definition and single-ticker population for the tickers schema."""

import time
from datetime import UTC, datetime

import numpy as np
import pandas as pd
from database import company_sync_engine
from dateutil.relativedelta import relativedelta
from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    Double,
    Engine,
    ForeignKey,
    Identity,
    Index,
    MetaData,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy import (
    text as sa_text,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from vnstock import Trading, Vnstock

from ourportfolios.utils.preprocessing.event_texts import process_events_for_display


def _build_metadata(schema_name: str) -> tuple[MetaData, dict]:
    """Build metadata and all table objects for a given schema name."""
    metadata = MetaData(schema=schema_name)

    overview_df = Table(
        "overview_df",
        metadata,
        Column("symbol", Text, primary_key=True),
        Column("exchange", Text),
        Column("industry", Text),
        Column("no_shareholders", BigInteger),
        Column("foreign_percent", Double),
        Column("outstanding_share", Double),
        Column("issue_share", Double),
        Column("established_year", Text),
        Column("no_employees", BigInteger),
        Column("short_name", Text),
        Column("website", Text),
        Column("market_cap", BigInteger),
    )

    price_df = Table(
        "price_df",
        metadata,
        Column("symbol", Text, primary_key=True),
        Column("current_price", Double),
        Column("price_change", Double),
        Column("pct_price_change", Double),
        Column("accumulated_volume", BigInteger),
    )

    price_history = Table(
        "price_history",
        metadata,
        Column(
            "symbol",
            Text,
            ForeignKey(f"{schema_name}.overview_df.symbol"),
            nullable=False,
        ),
        Column("date", Date, nullable=False),
        Column("open", Double),
        Column("high", Double),
        Column("low", Double),
        Column("close", Double, nullable=False),
        Column("volume", BigInteger),
        UniqueConstraint("symbol", "date", name="price_history_pkey"),
        Index("idx_price_history_symbol", "symbol"),
        Index("idx_price_history_date_brin", "date", postgresql_using="brin"),
    )

    stats_df = Table(
        "stats_df",
        metadata,
        Column("id", BigInteger, Identity(), primary_key=True),
        Column("symbol", Text, ForeignKey(f"{schema_name}.overview_df.symbol")),
        Column("roe", Double),
        Column("roa", Double),
        Column("ev_ebitda", Double),
        Column("dividend_yield", Double),
        Column("gross_margin", Double),
        Column("net_margin", Double),
        Column("doe", Double),
        Column("alpha", Double),
        Column("beta", Double),
        Column("pe", Double),
        Column("pb", Double),
        Column("eps", BigInteger),
        Column("ps", Double),
        Column("ev", Double),
        Column("rsi14", Double),
    )

    shareholders_df = Table(
        "shareholders_df",
        metadata,
        Column("symbol", Text, ForeignKey(f"{schema_name}.overview_df.symbol")),
        Column("share_holder", Text),
        Column("share_own_percent", Double),
    )

    events_df = Table(
        "events_df",
        metadata,
        Column("symbol", Text, ForeignKey(f"{schema_name}.overview_df.symbol")),
        Column("event_name", Text),
        Column("price_change_ratio", Double),
        Column("event_desc", Text),
    )

    news_df = Table(
        "news_df",
        metadata,
        Column("symbol", Text, ForeignKey(f"{schema_name}.overview_df.symbol")),
        Column("title", Text),
        Column("publish_date", Text),
        Column("price_change_ratio", Double),
    )

    profile_df = Table(
        "profile_df",
        metadata,
        Column("symbol", Text, ForeignKey(f"{schema_name}.overview_df.symbol")),
        Column("company_name", Text),
        Column("company_profile", Text),
        Column("history_dev", Text),
        Column("company_promise", Text),
        Column("business_risk", Text),
        Column("key_developments", Text),
        Column("business_strategies", Text),
    )

    officers_df = Table(
        "officers_df",
        metadata,
        Column("symbol", Text, ForeignKey(f"{schema_name}.overview_df.symbol")),
        Column("officer_name", Text),
        Column("officer_position", Text),
        Column("officer_own_percent", Double),
    )

    tables = {
        "overview_df": overview_df,
        "price_df": price_df,
        "price_history": price_history,
        "stats_df": stats_df,
        "shareholders_df": shareholders_df,
        "events_df": events_df,
        "news_df": news_df,
        "profile_df": profile_df,
        "officers_df": officers_df,
    }

    return metadata, tables


def create_tickers_schema(schema_name: str, engine: Engine) -> tuple[MetaData, dict]:
    """Create tickers schema and all tables idempotently. Returns (metadata, tables)."""
    # print(f"[schema] Initializing '{schema_name}'...")

    metadata, tables = _build_metadata(schema_name)

    with engine.connect() as conn:
        conn.execute(sa_text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        conn.commit()
    # print("[schema] Schema created")

    metadata.create_all(engine, checkfirst=True)
    # print(f"[schema] Tables: {table_names}")
    # print("[schema] Indexes: idx_price_history_symbol, idx_price_history_date_brin")
    # print("[schema] Done")

    return metadata, tables


# Adjust to new vnstock version.
def add_ticker(  # noqa: C901,PLR0912,PLR0915
    symbol: str,
    engine: Engine,
    schema_name: str,
    years_history: int = 3,
) -> None:
    """Fetch all data for one ticker from vnstock and insert into every table."""
    _, tables = _build_metadata(schema_name)
    overview_df = tables["overview_df"]
    price_df = tables["price_df"]
    price_history = tables["price_history"]
    shareholders_df = tables["shareholders_df"]
    events_df = tables["events_df"]
    news_df = tables["news_df"]
    profile_df = tables["profile_df"]
    officers_df = tables["officers_df"]

    # print(f"[{symbol}] Starting population...")
    stock = Vnstock().stock(symbol=symbol, source="VCI")
    company = stock.company

    # print(f"[{symbol}] Fetching overview...")
    raw = company.overview()
    if raw is None or raw.empty:
        msg = f"[{symbol}] No overview data returned — aborting"
        raise ValueError(msg)

    if "website" in raw.columns:
        raw["website"] = (
            raw["website"].str.removeprefix("https://").str.removeprefix("http://")
        )
    if "foreign_percent" in raw.columns:
        raw["foreign_percent"] = round(raw["foreign_percent"] * 100, 2)
    valid_cols = {c.name for c in overview_df.c}
    raw = raw.loc[:, raw.columns.isin(valid_cols)]

    stmt = (
        pg_insert(overview_df)
        .values(raw.to_dict("records"))
        .on_conflict_do_update(
            index_elements=["symbol"],
            set_={
                c.name: pg_insert(overview_df).excluded[c.name]
                for c in overview_df.c
                if c.name not in ("symbol", "market_cap")
            },
        )
    )
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()
    # print(f"[{symbol}] ✓ overview_df")
    time.sleep(1)

    try:
        # print(f"[{symbol}] Fetching shareholders...")
        df = company.shareholders()
        if df is not None and not df.empty:
            df["symbol"] = symbol
            df["share_own_percent"] = (df["share_own_percent"] * 100).round(2)
            with engine.connect() as conn:
                conn.execute(
                    shareholders_df.delete().where(shareholders_df.c.symbol == symbol),
                )
                conn.execute(
                    shareholders_df.insert(),
                    df[["symbol", "share_holder", "share_own_percent"]].to_dict(
                        "records",
                    ),
                )
                conn.commit()
        # print(f"[{symbol}] ✓ shareholders_df")
    except (ValueError, RuntimeError, KeyError, TypeError):
        # print(f"[{symbol}] ✗ shareholders_df: {e}")
        time.sleep(1)

    try:
        # print(f"[{symbol}] Fetching events...")
        df = company.events()
        if df is not None and not df.empty:
            df["symbol"] = symbol
            df["price_change_ratio"] = (
                df["price_change_ratio"].fillna(np.nan) * 100
            ).round(2)
            df = pd.DataFrame(process_events_for_display(df.to_dict("records")))
            df = df[["symbol", "event_name", "price_change_ratio", "event_desc"]]
            with engine.connect() as conn:
                conn.execute(events_df.delete().where(events_df.c.symbol == symbol))
                conn.execute(events_df.insert(), df.to_dict("records"))
                conn.commit()
        # print(f"[{symbol}] ✓ events_df")
    except (ValueError, RuntimeError, KeyError, TypeError):
        # print(f"[{symbol}] ✗ events_df: {e}")
        time.sleep(1)

    try:
        # print(f"[{symbol}] Fetching news...")
        df = company.news()
        if df is not None and not df.empty:
            df["symbol"] = symbol
            df["price_change_ratio"] = pd.to_numeric(
                df["price_change_ratio"],
                errors="coerce",
            )
            df = df[~df["title"].str.contains("insider", case=False, na=False)]
            df["price_change_ratio"] = (df["price_change_ratio"] * 100).round(2)
            df = df[["symbol", "title", "publish_date", "price_change_ratio"]]
            with engine.connect() as conn:
                conn.execute(news_df.delete().where(news_df.c.symbol == symbol))
                conn.execute(news_df.insert(), df.to_dict("records"))
                conn.commit()
        # print(f"[{symbol}] ✓ news_df")
    except (ValueError, RuntimeError, KeyError, TypeError):
        # print(f"[{symbol}] ✗ news_df: {e}")
        time.sleep(1)

    try:
        # print(f"[{symbol}] Fetching officers...")
        df = company.officers()
        if df is not None and not df.empty:
            df["symbol"] = symbol
            df = df.dropna(subset=["officer_name"]).fillna("")
            df = (
                df.groupby(["symbol", "officer_name"])
                .agg(
                    {
                        "officer_position": lambda x: ", ".join(
                            sorted(
                                {
                                    p.strip()
                                    for p in x
                                    if isinstance(p, str) and p.strip()
                                },
                            ),
                        ),
                        "officer_own_percent": "first",
                    },
                )
                .reset_index()
            )
            df["officer_own_percent"] = (
                pd.to_numeric(df["officer_own_percent"], errors="coerce") * 100
            ).round(2)
            with engine.connect() as conn:
                conn.execute(officers_df.delete().where(officers_df.c.symbol == symbol))
                conn.execute(
                    officers_df.insert(),
                    df[
                        [
                            "symbol",
                            "officer_name",
                            "officer_position",
                            "officer_own_percent",
                        ]
                    ].to_dict("records"),
                )
                conn.commit()
        # print(f"[{symbol}] ✓ officers_df")
    except (ValueError, RuntimeError, KeyError, TypeError):
        # print(f"[{symbol}] ✗ officers_df: {e}")
        pass
    time.sleep(1)

    try:
        # print(f"[{symbol}] Fetching profile...")
        df = company.profile()
        if df is not None and not df.empty:
            df["symbol"] = symbol
            keep = [
                "symbol",
                "company_name",
                "company_profile",
                "history_dev",
                "company_promise",
                "business_risk",
                "key_developments",
                "business_strategies",
            ]
            df = df[[c for c in keep if c in df.columns]]
            with engine.connect() as conn:
                conn.execute(profile_df.delete().where(profile_df.c.symbol == symbol))
                conn.execute(profile_df.insert(), df.to_dict("records"))
                conn.commit()
        # print(f"[{symbol}] ✓ profile_df")
    except (ValueError, RuntimeError, KeyError, TypeError):
        # print(f"[{symbol}] ✗ profile_df: {e}")
        pass
    time.sleep(1)

    try:
        # print(f"[{symbol}] Fetching price snapshot...")
        snap = load_price_df([symbol])
        if not snap.empty:
            stmt = (
                pg_insert(price_df)
                .values(snap.to_dict("records"))
                .on_conflict_do_update(
                    index_elements=["symbol"],
                    set_={
                        c.name: pg_insert(price_df).excluded[c.name]
                        for c in price_df.c
                        if c.name != "symbol"
                    },
                )
            )
            with engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()
        # print(f"[{symbol}] ✓ price_df")
    except (ValueError, RuntimeError, KeyError, TypeError):
        # print(f"[{symbol}] ✗ price_df: {e}")
        pass

    try:
        # print(f"[{symbol}] Fetching price history ({years_history}y)...")
        start = (
            datetime.now(UTC).date() - relativedelta(years=years_history)
        ).strftime(
            "%Y-%m-%d",
        )
        end = (datetime.now(UTC).date() + relativedelta(days=1)).strftime("%Y-%m-%d")

        hist = stock.quote.history(start=start, end=end, interval="1D")
        if hist is not None and not hist.empty:
            hist = hist.reset_index() if "time" not in hist.columns else hist.copy()
            hist["time"] = pd.to_datetime(hist["time"]).dt.date
            hist = hist.rename(columns={"time": "date"})
            hist.insert(0, "symbol", symbol)
            keep = ["symbol", "date", "open", "high", "low", "close", "volume"]
            hist = hist[[c for c in keep if c in hist.columns]].dropna(subset=["close"])

            exc = pg_insert(price_history).excluded
            stmt = (
                pg_insert(price_history)
                .values(hist.to_dict("records"))
                .on_conflict_do_update(
                    index_elements=["symbol", "date"],
                    set_={
                        "open": exc.open,
                        "high": exc.high,
                        "low": exc.low,
                        "close": exc.close,
                        "volume": exc.volume,
                    },
                    where=(
                        (price_history.c.close != exc.close)
                        | (price_history.c.open != exc.open)
                    ),
                )
            )
            with engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()
            # print(f"[{symbol}] ✓ price_history ({len(hist)} rows)")
    except (ValueError, RuntimeError, KeyError, TypeError):
        # print(f"[{symbol}] ✗ price_history: {e}")
        pass

    # print(f"[{symbol}] Done")


def load_price_df(tickers: list[str], *, verbose: bool = False) -> pd.DataFrame:
    """Load price board for given tickers and return a cleaned DataFrame."""
    if verbose:
        pass

    _empty = pd.DataFrame(
        columns=[
            "symbol",
            "current_price",
            "price_change",
            "pct_price_change",
            "accumulated_volume",
        ],
    )

    try:
        df = Trading(source="vci", symbol="ACB").price_board(symbols_list=tickers)
    except (ValueError, RuntimeError, KeyError, TypeError):
        if verbose:
            pass
        return _empty

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(0)
    if "exchange" in df.columns:
        df = df.drop("exchange", axis=1)
    df = df.loc[:, ~df.columns.duplicated()]

    if "match_price" in df.columns:
        df = df.rename(columns={"match_price": "current_price"})
        df["price_change"] = df["current_price"] - df["ref_price"]
        df["pct_price_change"] = (
            df["price_change"] / df["ref_price"].replace({0: pd.NA})
        ) * 100
    elif "ref_price" in df.columns:
        df = df.rename(columns={"ref_price": "current_price"})
        df["price_change"] = 0
        df["pct_price_change"] = 0
    else:
        return _empty

    df["current_price"] = round(df["current_price"] * 1e-3, 2)
    df["price_change"] = round(df["price_change"] * 1e-3, 2)
    df["pct_price_change"] = round(df["pct_price_change"], 2)

    if verbose:
        pass

    return df[
        [
            "symbol",
            "current_price",
            "price_change",
            "pct_price_change",
            "accumulated_volume",
        ]
    ]


if __name__ == "__main__":
    create_tickers_schema("tickers2", company_sync_engine)
    # add_ticker("FPT", company_sync_engine, schema_name="tickers2")
