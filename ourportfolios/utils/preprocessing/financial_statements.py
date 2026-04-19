"""Financial statements transformation and ratio computation."""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

import pandas as pd

from ourportfolios.utils.database.fetch_data import (
    fetch_balance_sheet_async,
    fetch_cash_flow_async,
    fetch_income_statement_async,
    fetch_ratios_async,
)

_cache = {}
_cache_duration = timedelta(minutes=30)
_MIN_POINTS_FOR_GROWTH = 2

# ---------------------------------------------------------------------------
# Column ordering: (display_name, db_column_name)
# If display_name != db_column_name the column is renamed for the UI.
# Columns not in the DB are silently skipped.
# ---------------------------------------------------------------------------

_INCOME_COLS: list[tuple[str, str]] = [
    ("Sales", "Sales"),
    ("Sales deductions", "Sales deductions"),
    ("Net Sales", "Net Sales"),
    ("Cost of Sales", "Cost of Sales"),
    ("Gross Profit", "Gross Profit"),
    ("Financial Income", "Financial Income"),
    ("Financial Expenses", "Financial Expenses"),
    ("Interest Expenses", "Interest Expenses"),
    ("Share of profit (loss) of associates", "Gain/(loss) from joint ventures"),
    ("Net income from associated companies", "Net income from associated companies"),
    ("Selling Expenses", "Selling Expenses"),
    ("General & Admin Expenses", "General & Admin Expenses"),
    ("Operating Profit/Loss", "Operating Profit/Loss"),
    ("Net other income/expenses", "Net other income/expenses"),
    ("Other Income", "Other Income"),
    ("Other Income/Expenses", "Other Income/Expenses"),
    ("Profit before tax", "Profit before tax"),
    ("Business income tax - current", "Business income tax - current"),
    ("Business income tax - deferred", "Business income tax - deferred"),
    ("Net Profit For the Year", "Net Profit For the Year"),
    ("Attributable to parent company", "Attributable to parent company"),
    ("Minority Interest", "Minority Interest"),
    ("EPS (VND)", "EPS (VND)"),
    ("Outstanding Share (Mil. Shares)", "Outstanding Share (Mil. Shares)"),
    ("EBITDA (Bn. VND)", "EBITDA (Bn. VND)"),
]

_BALANCE_COLS: list[tuple[str, str]] = [
    ("TOTAL ASSETS (Bn. VND)", "TOTAL ASSETS (Bn. VND)"),
    ("CURRENT ASSETS (Bn. VND)", "CURRENT ASSETS (Bn. VND)"),
    ("Cash and cash equivalents (Bn. VND)", "Cash and cash equivalents (Bn. VND)"),
    ("Short-term investments (Bn. VND)", "Short-term investments (Bn. VND)"),
    ("Accounts receivable (Bn. VND)", "Accounts receivable (Bn. VND)"),
    ("Net Inventories", "Net Inventories"),
    ("Other current assets", "Other current assets"),
    ("LONG-TERM ASSETS (Bn. VND)", "LONG-TERM ASSETS (Bn. VND)"),
    ("Long-term trade receivables (Bn. VND)", "Long-term trade receivables (Bn. VND)"),
    ("Fixed assets (Bn. VND)", "Fixed assets (Bn. VND)"),
    ("Investment in properties", "Investment in properties"),
    ("Long-term assets in progress", "Long-term assets in progress"),
    ("Long-term investments (Bn. VND)", "Long-term investments (Bn. VND)"),
    ("Other non-current assets", "Other non-current assets"),
    ("TOTAL RESOURCES (Bn. VND)", "TOTAL RESOURCES (Bn. VND)"),
    ("LIABILITIES (Bn. VND)", "LIABILITIES (Bn. VND)"),
    ("Current liabilities (Bn. VND)", "Current liabilities (Bn. VND)"),
    ("Short-term borrowings (Bn. VND)", "Short-term borrowings (Bn. VND)"),
    ("Long-term liabilities (Bn. VND)", "Long-term liabilities (Bn. VND)"),
    ("Long-term borrowings (Bn. VND)", "Long-term borrowings (Bn. VND)"),
    ("OWNER'S EQUITY(Bn.VND)", "OWNER'S EQUITY(Bn.VND)"),
    ("Capital and reserves (Bn. VND)", "Capital and reserves (Bn. VND)"),
    ("Paid-in capital (Bn. VND)", "Paid-in capital (Bn. VND)"),
    ("Other Reserves", "Other Reserves"),
    ("Undistributed earnings (Bn. VND)", "Undistributed earnings (Bn. VND)"),
    ("MINORITY INTERESTS", "MINORITY INTERESTS"),
    ("Budget sources and other funds", "Budget sources and other funds"),
    ("BVPS (VND)", "BVPS (VND)"),
]

_CASHFLOW_COLS: list[tuple[str, str]] = [
    (
        "Net cash inflows/outflows from operating activities",
        "Net cash inflows/outflows from operating activities",
    ),
    (
        "Net Cash Flows from Investing Activities",
        "Net Cash Flows from Investing Activities",
    ),
    ("Cash flows from financial activities", "Cash flows from financial activities"),
    (
        "Cash and Cash Equivalents at the end of period",
        "Cash and Cash Equivalents at the end of period",
    ),
    ("Dividends paid", "Dividends paid"),
    ("Payments for share repurchases", "Payments for share repurchases"),
    ("Purchase of fixed assets", "Purchase of fixed assets"),
    ("Free cash flow", "Free cash flow"),
]

# Period columns always go first
_YEAR_COLS = ["year"]
_QUARTER_COLS = ["year", "quarter"]


def _reorder(
    df: pd.DataFrame,
    spec: list[tuple[str, str]],
    period: str,
) -> pd.DataFrame:
    """Reorder + rename columns per spec in O(n) time.

    Steps:
    1. Build rename map for db_col -> display_name (only differing names).
    2. Build ordered column list: period cols first, then spec cols that exist.
    3. Reindex + rename in two vectorised operations.
    """
    if df.empty:
        return df

    period_cols = _QUARTER_COLS if period == "quarter" else _YEAR_COLS
    existing = set(df.columns)

    # Step 1: rename map (only where names differ)
    rename_map = {
        db: display for display, db in spec if db != display and db in existing
    }
    if rename_map:
        df = df.rename(columns=rename_map)
    existing_after_rename = set(df.columns)

    # Step 2: ordered column list
    ordered = [c for c in period_cols if c in existing_after_rename]
    seen = set(ordered)
    for display, _db in spec:
        col = display  # after rename, column is now display name
        if col in existing_after_rename and col not in seen:
            ordered.append(col)
            seen.add(col)

    # Step 3: reindex (drops unlisted cols, keeps order)
    return df[ordered]


def _compute_free_cash_flow(df: pd.DataFrame) -> pd.DataFrame:
    """Add Free cash flow = operating CF + capex (capex is usually negative)."""
    op = "Net cash inflows/outflows from operating activities"
    capex = "Purchase of fixed assets"
    if op in df.columns and capex in df.columns:
        df["Free cash flow"] = df[op].fillna(0) + df[capex].fillna(0)
    return df


def calculate_yoy_growth(series: pd.Series) -> pd.Series:
    if len(series) < _MIN_POINTS_FOR_GROWTH:
        return pd.Series(dtype=float, index=series.index)
    return series.sort_index().pct_change(fill_method=None) * 100


async def get_transformed_dataframes(
    ticker_symbol: str,
    period: str = "year",
) -> dict[str, Any]:
    cache_key = f"{ticker_symbol}_{period}"
    if cache_key in _cache:
        cached_data, cached_time = _cache[cache_key]
        if datetime.now(UTC) - cached_time < _cache_duration:
            return cached_data

    try:
        ratios_df, income_df, balance_df, cashflow_df = await asyncio.gather(
            fetch_ratios_async(ticker_symbol, period),
            fetch_income_statement_async(ticker_symbol, period),
            fetch_balance_sheet_async(ticker_symbol, period),
            fetch_cash_flow_async(ticker_symbol, period),
        )

        # Add computed free cash flow before reordering
        if not cashflow_df.empty:
            cashflow_df = _compute_free_cash_flow(cashflow_df)

        # Reorder columns per display spec
        income_ordered = _reorder(income_df, _INCOME_COLS, period)
        balance_ordered = _reorder(balance_df, _BALANCE_COLS, period)
        cashflow_ordered = _reorder(cashflow_df, _CASHFLOW_COLS, period)

        if ratios_df.empty:
            categorized_ratios = {
                "Per Share Value": [],
                "Growth Rate": [],
                "Profitability": [],
                "Valuation": [],
                "Leverage & Liquidity": [],
                "Efficiency": [],
            }
        else:
            categorized_ratios = _categorize_ratios(
                ratios_df,
                period,
                income_df,
                balance_df,
                cashflow_df,
            )

        result = {
            "transformed_income_statement": income_ordered.to_dict("records")
            if not income_ordered.empty
            else [],
            "transformed_balance_sheet": balance_ordered.to_dict("records")
            if not balance_ordered.empty
            else [],
            "transformed_cash_flow": cashflow_ordered.to_dict("records")
            if not cashflow_ordered.empty
            else [],
            "categorized_ratios": categorized_ratios,
        }

        _cache[cache_key] = (result, datetime.now(UTC))

    except (ValueError, TypeError, KeyError, RuntimeError) as e:
        error_msg = f"{type(e).__name__}: {e!s}"
        return {
            "transformed_income_statement": [],
            "transformed_balance_sheet": [],
            "transformed_cash_flow": [],
            "categorized_ratios": {
                "Per Share Value": [],
                "Growth Rate": [],
                "Profitability": [],
                "Valuation": [],
                "Leverage & Liquidity": [],
                "Efficiency": [],
            },
            "error": error_msg,
        }
    else:
        return result


def _categorize_ratios(  # noqa: C901
    ratios_df: pd.DataFrame,
    period: str,
    income_df: pd.DataFrame | None = None,
    balance_df: pd.DataFrame | None = None,
    cashflow_df: pd.DataFrame | None = None,
) -> dict[str, list]:
    categorized_ratios = {
        "Per Share Value": [],
        "Growth Rate": [],
        "Profitability": [],
        "Valuation": [],
        "Leverage & Liquidity": [],
        "Efficiency": [],
    }

    combined_df = ratios_df.copy() if not ratios_df.empty else pd.DataFrame()

    merge_on = ["year"] if period == "year" else ["year", "quarter"]

    for df in [income_df, balance_df, cashflow_df]:
        if df is not None and not df.empty:
            if not combined_df.empty:
                combined_df = combined_df.merge(df, on=merge_on, how="outer")
            else:
                combined_df = df.copy()

    if combined_df.empty:
        return categorized_ratios

    per_share_metrics = [
        "EPS (VND)",
        "BVPS (VND)",
        "Net Sales",
        "Free Cash Flow",
        "Dividends paid",
        "OWNER'S EQUITY(Bn.VND)",
    ]
    profitability_metrics = [
        "Gross Profit Margin (%)",
        "Net Profit Margin (%)",
        "EBIT Margin (%)",
        "Operating Profit/Loss",
        "ROE (%)",
        "ROA (%)",
        "ROIC (%)",
        "EBITDA (Bn. VND)",
    ]
    valuation_metrics = [
        "P/E",
        "P/B",
        "P/S",
        "P/Cash Flow",
        "EV/EBITDA",
        "Market Capital (Bn. VND)",
        "Outstanding Share (Mil. Shares)",
    ]
    leverage_liquidity_metrics = [
        "Debt/Equity",
        "(ST+LT borrowings)/Equity",
        "EBITDA (Bn. VND)",
        "Short-term borrowings (Bn. VND)",
        "Long-term borrowings (Bn. VND)",
        "Financial Leverage",
        "Current Ratio",
        "Quick Ratio",
        "Cash Ratio",
        "Interest Coverage",
    ]
    efficiency_metrics = [
        "Asset Turnover",
        "Fixed Asset Turnover",
        "Inventory Turnover",
        "Days Sales Outstanding",
        "Days Inventory Outstanding",
        "Days Payable Outstanding",
        "Cash Cycle",
        "Fixed Asset-To-Equity",
        "Owners' Equity/Charter Capital",
        "Accounts receivable (Bn. VND)",
        "Dividends paid",
    ]

    time_cols = {"year", "Year", "quarter", "Quarter", "period"}
    available_cols = set(combined_df.columns) - time_cols

    def extract_category(metrics_list: list[str]) -> list[dict[str, Any]]:
        found = [m for m in metrics_list if m in available_cols]
        if not found:
            return []
        cols = []
        if "year" in combined_df.columns:
            cols.append("year")
        elif "Year" in combined_df.columns:
            cols.append("Year")
        if period == "quarter":
            if "quarter" in combined_df.columns:
                cols.append("quarter")
            elif "Quarter" in combined_df.columns:
                cols.append("Quarter")
        cols.extend(found)
        cols = [c for c in cols if c in combined_df.columns]
        subset = combined_df[cols].copy()
        rename = {}
        if "year" in subset.columns:
            rename["year"] = "Year"
        if "quarter" in subset.columns:
            rename["quarter"] = "Quarter"
        if rename:
            subset = subset.rename(columns=rename)
        return subset.to_dict(orient="records")

    categorized_ratios["Per Share Value"] = extract_category(per_share_metrics)
    categorized_ratios["Profitability"] = extract_category(profitability_metrics)
    categorized_ratios["Valuation"] = extract_category(valuation_metrics)
    categorized_ratios["Leverage & Liquidity"] = extract_category(
        leverage_liquidity_metrics,
    )
    categorized_ratios["Efficiency"] = extract_category(efficiency_metrics)
    categorized_ratios["Growth Rate"] = _compute_growth_rates(combined_df, period)

    return categorized_ratios


def _compute_growth_rates(ratios_df: pd.DataFrame, period: str) -> list:
    if ratios_df.empty:
        return []

    growth_mappings = {
        "Revenue YoY": "Net Sales",
        "Earnings YoY": "EPS (VND)",
        "Free Cash Flow YoY": "Free Cash Flow",
        "Dividends YoY": "Dividends paid",
        "Book Value YoY": "BVPS (VND)",
    }

    df = ratios_df.copy()
    year_col = "year" if "year" in df.columns else "Year"
    if year_col not in df.columns:
        return []

    sort_cols = [year_col]
    quarter_col = None
    if period == "quarter":
        quarter_col = "quarter" if "quarter" in df.columns else "Quarter"
        if quarter_col in df.columns:
            sort_cols.append(quarter_col)

    df = df.sort_values(sort_cols)
    growth_df = pd.DataFrame()
    growth_df["Year"] = df[year_col].to_numpy()
    if quarter_col and quarter_col in df.columns:
        growth_df["Quarter"] = df[quarter_col].to_numpy()

    for growth_name, source_metric in growth_mappings.items():
        if source_metric in df.columns:
            series = df[source_metric].apply(
                lambda x: float(x) if x is not None else None,
            )
            growth_df[growth_name] = series.pct_change() * 100

    growth_cols = [c for c in growth_df.columns if c not in ["Year", "Quarter"]]
    if growth_cols:
        growth_df = growth_df[growth_df[growth_cols].notna().any(axis=1)]

    return growth_df.to_dict(orient="records")


def format_quarter_data(data_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    processed_data = []
    for item in data_list:
        processed_item = item.copy()
        year = item.get("Year", "") or item.get("year", "")
        quarter = item.get("Quarter", "") or item.get("quarter", "")
        processed_item["formatted_quarter"] = (
            f"Q{quarter} {year}" if year and quarter else str(year)
        )
        processed_item.pop("Quarter", None)
        processed_item.pop("quarter", None)
        processed_data.append(processed_item)
    return processed_data
