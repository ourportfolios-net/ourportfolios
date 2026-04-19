import itertools
from typing import Any

import pandas as pd
from sqlalchemy import text

from ourportfolios.utils.database.database import get_company_session


async def get_suggest_ticker(
    search_query: str,
    return_type: str,
) -> tuple[str, Any] | pd.DataFrame:
    """Attempt to retrieve data with strategy.

    1. Fetch ticker with full query at first
    2. Fetch with all permutation of the search query if (1) failed to returns any data
    3. Fetch with first letter as the final result if still no data retrieved

    Args:
        search_query (str): search query
        return_type (str): which data-type to returns. Available options are ["query", "df"]

    Returns:
        Tuple[str, Any] | pd.DataFrame: Can either returns search params or a full dataframe

    """
    # Fetch exact ticker
    match_query = "pb.symbol LIKE :pattern"
    match_params = {"pattern": f"{search_query}%"}
    result: pd.DataFrame = await fetch_ticker(
        match_query=match_query,
        params=match_params,
        return_type=return_type,
    )

    # In-case of mistype or no ticker returned, calculate all possible combination of provided search_query with fixed length
    if result.empty:
        combos: list[tuple] = list(
            itertools.permutations(list(search_query), len(search_query)),
        )
        match_params = {
            f"pattern_{idx}": f"{''.join(combo)}%" for idx, combo in enumerate(combos)
        }
        match_query = " OR ".join(
            [f"pb.symbol LIKE :pattern_{i}" for i in range(len(match_params))],
        )

        result: pd.DataFrame = await fetch_ticker(
            match_query=match_query,
            params=match_params,
            return_type=return_type,
        )

    # Matches first letter if still no ticker retrieved
    if result.empty:
        match_query = "pb.symbol LIKE :pattern"
        match_params = {"pattern": f"{search_query[0]}%"}  # First letter
        result: bool = await fetch_ticker(
            match_query=match_query,
            params=match_params,
            return_type=return_type,
        )

    return (
        (match_query, match_params)
        if return_type == "query"
        else result.to_dict("records")
    )


async def fetch_ticker(
    match_query: str = "all",
    params: dict[str, object] | None = None,
    return_type: str = "df",
) -> pd.DataFrame:
    """Fetch data from NeonDB.

    Designed to be used in conjunction with get_suggest_ticker but can also be used independently.

    Args:
        match_query (str, optional): match query in SQLAlchemy syntax. "all" flag is uses to fetch all data. Defaults to "all".
        params (Any, optional): passed in parameters to combine with match query. Defaults to None.
        return_type (str, optional): which data-type to returns. Available options are ["query", "df"]. Defaults to "df".

    Returns:
        pd.DataFrame: _description_

    """
    if return_type == "df":
        completed_query = """
            SELECT pb.symbol, pb.pct_price_change, od.industry
            FROM tickers.price_df AS pb
            JOIN tickers.overview_df AS od
            ON pb.symbol = od.symbol
        """
    else:
        completed_query = """
            SELECT pb.symbol
            FROM tickers.price_df AS pb
            JOIN tickers.overview_df AS od
            ON pb.symbol = od.symbol
        """

    if match_query != "all":
        completed_query += f"WHERE {match_query}\n"

    if return_type == "df":
        completed_query += "ORDER BY accumulated_volume DESC"

    try:
        async with get_company_session() as session:
            result = await session.execute(text(completed_query), params or {})
            rows = result.mappings().all()
            return pd.DataFrame([dict(row) for row in rows])
    except (ValueError, RuntimeError, KeyError):
        return pd.DataFrame()
