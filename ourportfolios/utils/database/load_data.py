"""Data retrieval functions for company data.

DEPRECATED: Use queries.py instead.
"""

from datetime import date, timedelta
import pandas as pd
from vnstock import Vnstock

from .queries import fetch_company_data  # noqa: F401


def load_historical_data(
    symbol: str,
    start: str = date.today().strftime("%Y-%m-%d"),
    end: str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
    interval: str = "15m",
) -> pd.DataFrame:
    stock = Vnstock().stock(symbol=symbol, source="TCBS")
    df = stock.quote.history(start=start, end=end, interval=interval)
    return df.drop_duplicates(keep="last")
