"""Financial statements transformation and ratio computation."""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

from ..utils.database.fetch_data import (
    fetch_income_statement_async,
    fetch_balance_sheet_async,
    fetch_cash_flow_async,
    fetch_ratios_async,
)

_cache = {}
_cache_duration = timedelta(minutes=30)


def calculate_yoy_growth(series):
    """Calculate year-over-year growth percentage."""
    if len(series) < 2:
        return pd.Series(dtype=float, index=series.index)
    series_sorted = series.sort_index()
    return series_sorted.pct_change(fill_method=None) * 100


async def get_transformed_dataframes(
    ticker_symbol: str, period: str = "year"
) -> Dict[str, Any]:
    """Fetch pre-computed financial ratios from database.

    This function fetches ratios that have already been computed and stored
    in the database by ourscheduler. It does NOT compute ratios on the fly.

    Args:
        ticker_symbol: Stock ticker symbol
        period: 'year' or 'quarter'

    Returns:
        Dictionary containing categorized ratios ready for display
    """
    cache_key = f"{ticker_symbol}_{period}"
    if cache_key in _cache:
        cached_data, cached_time = _cache[cache_key]
        if datetime.now() - cached_time < _cache_duration:
            return cached_data

    try:
        # Fetch all financial data in parallel
        ratios_df, income_df, balance_df, cashflow_df = await asyncio.gather(
            fetch_ratios_async(ticker_symbol, period),
            fetch_income_statement_async(ticker_symbol, period),
            fetch_balance_sheet_async(ticker_symbol, period),
            fetch_cash_flow_async(ticker_symbol, period),
        )

        if ratios_df.empty:
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
                "error": "No ratio data found in database. Data may need to be loaded via ourscheduler.",
            }

        # Categorize the ratios based on metric names, including financial statement metrics
        categorized_ratios = _categorize_ratios(
            ratios_df, period, income_df, balance_df, cashflow_df
        )

        # Convert DataFrames to list of dicts for UI
        result = {
            "transformed_income_statement": income_df.to_dict("records")
            if not income_df.empty
            else [],
            "transformed_balance_sheet": balance_df.to_dict("records")
            if not balance_df.empty
            else [],
            "transformed_cash_flow": cashflow_df.to_dict("records")
            if not cashflow_df.empty
            else [],
            "categorized_ratios": categorized_ratios,
        }

        _cache[cache_key] = (result, datetime.now())

        return result

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
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


def _categorize_ratios(
    ratios_df: pd.DataFrame,
    period: str,
    income_df: pd.DataFrame = None,
    balance_df: pd.DataFrame = None,
    cashflow_df: pd.DataFrame = None,
) -> Dict[str, list]:
    """Categorize ratios from database into display categories.

    Args:
        ratios_df: DataFrame with all ratios in wide format
        period: 'year' or 'quarter'
        income_df: Income statement DataFrame (optional)
        balance_df: Balance sheet DataFrame (optional)
        cashflow_df: Cash flow DataFrame (optional)

    Returns:
        Dictionary of categorized ratios ready for display
    """
    categorized_ratios = {
        "Per Share Value": [],
        "Growth Rate": [],
        "Profitability": [],
        "Valuation": [],
        "Leverage & Liquidity": [],
        "Efficiency": [],
    }

    # Merge all dataframes to get complete metric set
    combined_df = ratios_df.copy() if not ratios_df.empty else pd.DataFrame()

    # Merge financial statements if provided
    if income_df is not None and not income_df.empty:
        if not combined_df.empty:
            combined_df = combined_df.merge(
                income_df,
                on=["year"] if period == "year" else ["year", "quarter"],
                how="outer",
            )
        else:
            combined_df = income_df.copy()

    if balance_df is not None and not balance_df.empty:
        if not combined_df.empty:
            combined_df = combined_df.merge(
                balance_df,
                on=["year"] if period == "year" else ["year", "quarter"],
                how="outer",
            )
        else:
            combined_df = balance_df.copy()

    if cashflow_df is not None and not cashflow_df.empty:
        if not combined_df.empty:
            combined_df = combined_df.merge(
                cashflow_df,
                on=["year"] if period == "year" else ["year", "quarter"],
                how="outer",
            )
        else:
            combined_df = cashflow_df.copy()

    if combined_df.empty:
        return categorized_ratios

    # Define metric categories based on actual database metric names
    per_share_metrics = [
        "EPS (VND)",
        "BVPS (VND)",
        "Net Sales",  # Revenues
        "Free Cash Flow",  # Will be computed if not in DB
        "Dividends paid",
        "OWNER'S EQUITY(Bn.VND)",  # Book Value
    ]

    # Growth metrics - will be computed from the time-series data
    # growth_metrics = []  # Computed from YoY changes

    profitability_metrics = [
        "Gross Profit Margin (%)",
        "Net Profit Margin (%)",
        "EBIT Margin (%)",
        "Operating Profit/Loss",  # Operating Margin (will compute %)
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
        "Outstanding Share (Mil. Shares)",  # PEG Ratio component
    ]

    leverage_liquidity_metrics = [
        "Debt/Equity",
        "(ST+LT borrowings)/Equity",
        "EBITDA (Bn. VND)",  # For Debt to EBITDA
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
        "Accounts receivable (Bn. VND)",  # For Receivables Turnover
        "Dividends paid",  # For Dividend Payout %
    ]

    # Get available columns (excluding time columns)
    time_cols = ["year", "Year", "quarter", "Quarter", "period"]
    available_cols = [col for col in combined_df.columns if col not in time_cols]

    # Helper function to extract metrics for a category
    def extract_category(metrics_list):
        # Find which metrics exist in the dataframe
        found_metrics = [m for m in metrics_list if m in available_cols]
        if not found_metrics:
            return []

        # Select time columns and found metrics
        cols_to_keep = ["year" if "year" in combined_df.columns else "Year"]
        if period == "quarter":
            cols_to_keep.append(
                "quarter" if "quarter" in combined_df.columns else "Quarter"
            )
        cols_to_keep.extend(found_metrics)

        # Filter to existing columns only
        cols_to_keep = [c for c in cols_to_keep if c in combined_df.columns]

        if not cols_to_keep:
            return []

        subset_df = combined_df[cols_to_keep].copy()

        # Rename columns to consistent case
        rename_map = {}
        if "year" in subset_df.columns:
            rename_map["year"] = "Year"
        if "quarter" in subset_df.columns:
            rename_map["quarter"] = "Quarter"

        if rename_map:
            subset_df = subset_df.rename(columns=rename_map)

        return subset_df.to_dict(orient="records")

    # Populate each category
    categorized_ratios["Per Share Value"] = extract_category(per_share_metrics)
    categorized_ratios["Profitability"] = extract_category(profitability_metrics)
    categorized_ratios["Valuation"] = extract_category(valuation_metrics)
    categorized_ratios["Leverage & Liquidity"] = extract_category(
        leverage_liquidity_metrics
    )
    categorized_ratios["Efficiency"] = extract_category(efficiency_metrics)

    # Compute Growth Rate category from YoY changes in per-share metrics
    categorized_ratios["Growth Rate"] = _compute_growth_rates(combined_df, period)

    return categorized_ratios


def _compute_growth_rates(ratios_df: pd.DataFrame, period: str) -> list:
    """Compute year-over-year growth rates from time-series ratio data.

    Args:
        ratios_df: DataFrame with ratios in wide format
        period: 'year' or 'quarter'

    Returns:
        List of dictionaries with computed growth rates
    """
    if ratios_df.empty:
        return []

    # Map of growth metric names to their source metrics
    growth_mappings = {
        "Revenue YoY": "Net Sales",
        "Earnings YoY": "EPS (VND)",
        "Free Cash Flow YoY": "Free Cash Flow",
        "Dividends YoY": "Dividends paid",
        "Book Value YoY": "BVPS (VND)",
    }

    # Prepare dataframe sorted by time
    df = ratios_df.copy()

    # Ensure we have year column
    year_col = "year" if "year" in df.columns else "Year"
    if year_col not in df.columns:
        return []

    # Sort by year (and quarter if quarterly data)
    sort_cols = [year_col]
    quarter_col = None
    if period == "quarter":
        quarter_col = "quarter" if "quarter" in df.columns else "Quarter"
        if quarter_col in df.columns:
            sort_cols.append(quarter_col)

    df = df.sort_values(sort_cols)

    # Initialize result dataframe with time columns
    growth_df = pd.DataFrame()
    growth_df["Year"] = df[year_col]
    if quarter_col and quarter_col in df.columns:
        growth_df["Quarter"] = df[quarter_col]

    # Compute YoY growth for each metric
    for growth_name, source_metric in growth_mappings.items():
        if source_metric in df.columns:
            # Calculate percentage change from previous period
            series = df[source_metric]
            # Convert Decimal to float to avoid division issues
            series = series.apply(lambda x: float(x) if x is not None else None)
            pct_change = series.pct_change() * 100
            growth_df[growth_name] = pct_change

    # Remove rows with all NaN growth values (typically the first row)
    growth_cols = [col for col in growth_df.columns if col not in ["Year", "Quarter"]]
    if growth_cols:
        # Keep row if at least one growth metric is not NaN
        mask = growth_df[growth_cols].notna().any(axis=1)
        growth_df = growth_df[mask]

    return growth_df.to_dict(orient="records")


def _compute_ratios_from_statements(
    income_df: pd.DataFrame,
    balance_df: pd.DataFrame,
    cash_flow_df: pd.DataFrame,
    period: str,
) -> Dict[str, list]:
    """DEPRECATED: Compute comprehensive financial ratios from raw statement data.

    This function is no longer used in production. Ratios are pre-computed
    and stored in the database by ourscheduler.
    """
    categorized_ratios = {
        "Per Share Value": [],
        "Growth Rate": [],
        "Profitability": [],
        "Valuation": [],
        "Leverage & Liquidity": [],
        "Efficiency": [],
    }

    if income_df.empty and balance_df.empty and cash_flow_df.empty:
        return categorized_ratios

    try:
        # Set index to year (or year+quarter for quarterly data)
        if (
            period == "quarter"
            and not income_df.empty
            and "quarter" in income_df.columns
        ):
            income_df = income_df.set_index(["year", "quarter"])
            if not balance_df.empty:
                balance_df = balance_df.set_index(["year", "quarter"])
            if not cash_flow_df.empty:
                cash_flow_df = cash_flow_df.set_index(["year", "quarter"])
        else:
            if not income_df.empty:
                income_df = income_df.set_index("year")
            if not balance_df.empty:
                balance_df = balance_df.set_index("year")
            if not cash_flow_df.empty:
                cash_flow_df = cash_flow_df.set_index("year")

        # Get the index for our ratio dataframes
        if not income_df.empty:
            ratios_index = income_df.index
        elif not balance_df.empty:
            ratios_index = balance_df.index
        else:
            ratios_index = cash_flow_df.index

        # Initialize categorized ratio DataFrames
        per_share = pd.DataFrame(index=ratios_index)
        growth_rate = pd.DataFrame(index=ratios_index)
        profitability = pd.DataFrame(index=ratios_index)
        valuation = pd.DataFrame(index=ratios_index)
        leverage_liquidity = pd.DataFrame(index=ratios_index)
        efficiency = pd.DataFrame(index=ratios_index)

        # Add time period columns
        if period == "quarter":
            per_share["Year"] = [idx[0] for idx in ratios_index]
            per_share["Quarter"] = [idx[1] for idx in ratios_index]
            growth_rate["Year"] = [idx[0] for idx in ratios_index]
            growth_rate["Quarter"] = [idx[1] for idx in ratios_index]
            profitability["Year"] = [idx[0] for idx in ratios_index]
            profitability["Quarter"] = [idx[1] for idx in ratios_index]
            valuation["Year"] = [idx[0] for idx in ratios_index]
            valuation["Quarter"] = [idx[1] for idx in ratios_index]
            leverage_liquidity["Year"] = [idx[0] for idx in ratios_index]
            leverage_liquidity["Quarter"] = [idx[1] for idx in ratios_index]
            efficiency["Year"] = [idx[0] for idx in ratios_index]
            efficiency["Quarter"] = [idx[1] for idx in ratios_index]
        else:
            per_share["Year"] = ratios_index
            growth_rate["Year"] = ratios_index
            profitability["Year"] = ratios_index
            valuation["Year"] = ratios_index
            leverage_liquidity["Year"] = ratios_index
            efficiency["Year"] = ratios_index

        # === PER SHARE VALUE ===
        # Get outstanding shares from income statement metrics
        outstanding_shares = (
            income_df["Outstanding Share (Mil. Shares)"]
            if "Outstanding Share (Mil. Shares)" in income_df.columns
            else pd.Series(dtype=float, index=ratios_index)
        )

        # Earnings per share
        per_share["Earnings"] = (
            income_df["EPS (VND)"] if "EPS (VND)" in income_df.columns else pd.NA
        )

        # Book Value per share
        per_share["Book Value"] = (
            balance_df["BVPS (VND)"]
            if not balance_df.empty and "BVPS (VND)" in balance_df.columns
            else pd.NA
        )

        # Revenue per share
        net_sales = (
            income_df["Net Sales"]
            if "Net Sales" in income_df.columns
            else pd.Series(dtype=float, index=ratios_index)
        )
        if not net_sales.isna().all() and not outstanding_shares.isna().all():
            per_share["Revenues"] = net_sales / outstanding_shares.replace(0, pd.NA)
        else:
            per_share["Revenues"] = pd.NA

        # Free Cash Flow per share
        if not cash_flow_df.empty:
            operating_cf = (
                cash_flow_df["Operating cash flow"]
                if "Operating cash flow" in cash_flow_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )
            capex = (
                cash_flow_df["Capital expenditure"]
                if "Capital expenditure" in cash_flow_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )
            dividends_paid = (
                cash_flow_df["Dividends paid"]
                if "Dividends paid" in cash_flow_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )

            if not operating_cf.isna().all() and not outstanding_shares.isna().all():
                fcf_total = operating_cf.fillna(0) + capex.fillna(0)
                per_share["Free Cash Flow"] = fcf_total / outstanding_shares.replace(
                    0, pd.NA
                )
            else:
                per_share["Free Cash Flow"] = pd.NA

            # Dividend per share
            if not dividends_paid.isna().all() and not outstanding_shares.isna().all():
                per_share["Dividend"] = (-dividends_paid) / outstanding_shares.replace(
                    0, pd.NA
                )
            else:
                per_share["Dividend"] = pd.NA
        else:
            per_share["Free Cash Flow"] = pd.NA
            per_share["Dividend"] = pd.NA

        # === GROWTH RATES ===
        growth_rate["Revenues YoY"] = calculate_yoy_growth(per_share["Revenues"])
        growth_rate["Earnings YoY"] = calculate_yoy_growth(per_share["Earnings"])
        growth_rate["Free Cash Flow YoY"] = calculate_yoy_growth(
            per_share["Free Cash Flow"]
        )
        growth_rate["Dividend YoY"] = calculate_yoy_growth(per_share["Dividend"])
        growth_rate["Book Value YoY"] = calculate_yoy_growth(per_share["Book Value"])

        # === PROFITABILITY ===
        # Margins
        profitability["Gross Margin"] = (
            (income_df["Gross Profit"] / net_sales.replace(0, pd.NA)) * 100
            if "Gross Profit" in income_df.columns and not net_sales.isna().all()
            else pd.NA
        )

        operating_profit = (
            income_df["Operating Profit/Loss"]
            if "Operating Profit/Loss" in income_df.columns
            else pd.Series(dtype=float, index=ratios_index)
        )
        profitability["Operating Margin"] = (
            (operating_profit / net_sales.replace(0, pd.NA)) * 100
            if not operating_profit.isna().all() and not net_sales.isna().all()
            else pd.NA
        )

        net_profit = (
            income_df["Net Profit For the Year"]
            if "Net Profit For the Year" in income_df.columns
            else pd.Series(dtype=float, index=ratios_index)
        )
        profitability["Net Margin"] = (
            (net_profit / net_sales.replace(0, pd.NA)) * 100
            if not net_profit.isna().all() and not net_sales.isna().all()
            else pd.NA
        )

        # EBITDA and EBIT margins
        ebitda = (
            income_df["EBITDA (Bn. VND)"]
            if "EBITDA (Bn. VND)" in income_df.columns
            else pd.Series(dtype=float, index=ratios_index)
        )
        ebit = (
            income_df["EBIT (Bn. VND)"]
            if "EBIT (Bn. VND)" in income_df.columns
            else pd.Series(dtype=float, index=ratios_index)
        )

        profitability["EBITDA Margin"] = (
            (ebitda / net_sales.replace(0, pd.NA)) * 100
            if not ebitda.isna().all() and not net_sales.isna().all()
            else pd.NA
        )
        profitability["EBIT Margin"] = (
            (ebit / net_sales.replace(0, pd.NA)) * 100
            if not ebit.isna().all() and not net_sales.isna().all()
            else pd.NA
        )

        # Return ratios
        equity = (
            balance_df["OWNER'S EQUITY(Bn.VND)"]
            if not balance_df.empty and "OWNER'S EQUITY(Bn.VND)" in balance_df.columns
            else pd.Series(dtype=float, index=ratios_index)
        )
        total_assets = (
            balance_df["TOTAL ASSETS (Bn. VND)"]
            if not balance_df.empty and "TOTAL ASSETS (Bn. VND)" in balance_df.columns
            else pd.Series(dtype=float, index=ratios_index)
        )

        profitability["ROE"] = (
            (net_profit / equity.replace(0, pd.NA)) * 100
            if not net_profit.isna().all() and not equity.isna().all()
            else pd.NA
        )
        profitability["ROA"] = (
            (net_profit / total_assets.replace(0, pd.NA)) * 100
            if not net_profit.isna().all() and not total_assets.isna().all()
            else pd.NA
        )

        # ROIC (Return on Invested Capital)
        if not balance_df.empty:
            lt_debt = (
                balance_df["Long-term borrowings (Bn. VND)"]
                if "Long-term borrowings (Bn. VND)" in balance_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )
            st_debt = (
                balance_df["Short-term borrowings (Bn. VND)"]
                if "Short-term borrowings (Bn. VND)" in balance_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )
            invested_capital = equity + lt_debt.fillna(0) + st_debt.fillna(0)
            profitability["ROIC"] = (
                (net_profit / invested_capital.replace(0, pd.NA)) * 100
                if not net_profit.isna().all()
                else pd.NA
            )
        else:
            profitability["ROIC"] = pd.NA

        # ROCE (Return on Capital Employed)
        if not balance_df.empty and not ebit.isna().all():
            current_liabilities = (
                balance_df["Current liabilities (Bn. VND)"]
                if "Current liabilities (Bn. VND)" in balance_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )
            employed_capital = total_assets - current_liabilities
            profitability["ROCE"] = (
                (ebit / employed_capital.replace(0, pd.NA)) * 100
                if not current_liabilities.isna().all()
                else pd.NA
            )
        else:
            profitability["ROCE"] = pd.NA

        # === VALUATION ===
        # P/E, P/B, P/S ratios (these would typically come from market data, set to NA for now)
        valuation["P/E"] = pd.NA
        valuation["P/B"] = pd.NA
        valuation["P/S"] = pd.NA
        valuation["P/Cash Flow"] = pd.NA
        valuation["EV/EBITDA"] = pd.NA
        valuation["EV/Revenue"] = pd.NA

        # === LEVERAGE & LIQUIDITY ===
        if not balance_df.empty:
            lt_debt = (
                balance_df["Long-term borrowings (Bn. VND)"]
                if "Long-term borrowings (Bn. VND)" in balance_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )
            st_debt = (
                balance_df["Short-term borrowings (Bn. VND)"]
                if "Short-term borrowings (Bn. VND)" in balance_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )
            total_debt = lt_debt.fillna(0) + st_debt.fillna(0)

            leverage_liquidity["Debt/Equity"] = (
                total_debt / equity.replace(0, pd.NA)
                if not equity.isna().all()
                else pd.NA
            )
            leverage_liquidity["Debt to EBITDA"] = (
                total_debt / ebitda.replace(0, pd.NA)
                if not ebitda.isna().all()
                else pd.NA
            )

            # Financial leverage
            leverage_liquidity["Financial Leverage"] = (
                total_assets / equity.replace(0, pd.NA)
                if not total_assets.isna().all() and not equity.isna().all()
                else pd.NA
            )

            # Liquidity ratios
            current_assets = (
                balance_df["CURRENT ASSETS (Bn. VND)"]
                if "CURRENT ASSETS (Bn. VND)" in balance_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )
            current_liabilities = (
                balance_df["Current liabilities (Bn. VND)"]
                if "Current liabilities (Bn. VND)" in balance_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )

            leverage_liquidity["Current Ratio"] = (
                current_assets / current_liabilities.replace(0, pd.NA)
                if not current_assets.isna().all()
                and not current_liabilities.isna().all()
                else pd.NA
            )

            # Quick ratio (current assets - inventory) / current liabilities
            inventory = (
                balance_df["Net Inventories"]
                if "Net Inventories" in balance_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )
            quick_assets = current_assets - inventory.fillna(0)
            leverage_liquidity["Quick Ratio"] = (
                quick_assets / current_liabilities.replace(0, pd.NA)
                if not current_liabilities.isna().all()
                else pd.NA
            )

            # Cash ratio
            cash = (
                balance_df["Cash and cash equivalents (Bn. VND)"]
                if "Cash and cash equivalents (Bn. VND)" in balance_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )
            leverage_liquidity["Cash Ratio"] = (
                cash / current_liabilities.replace(0, pd.NA)
                if not cash.isna().all() and not current_liabilities.isna().all()
                else pd.NA
            )

            # Interest coverage
            interest_expense = (
                income_df["Interest Expenses"]
                if "Interest Expenses" in income_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )
            leverage_liquidity["Interest Coverage"] = (
                ebit / interest_expense.replace(0, pd.NA)
                if not ebit.isna().all() and not interest_expense.isna().all()
                else pd.NA
            )
        else:
            leverage_liquidity["Debt/Equity"] = pd.NA
            leverage_liquidity["Current Ratio"] = pd.NA
            leverage_liquidity["Quick Ratio"] = pd.NA
            leverage_liquidity["Cash Ratio"] = pd.NA
            leverage_liquidity["Interest Coverage"] = pd.NA

        # === EFFICIENCY ===
        efficiency["ROA"] = profitability["ROA"]
        efficiency["Asset Turnover"] = (
            net_sales / total_assets.replace(0, pd.NA)
            if not net_sales.isna().all() and not total_assets.isna().all()
            else pd.NA
        )

        # Dividend payout ratio
        if not cash_flow_df.empty:
            dividends_paid = (
                cash_flow_df["Dividends paid"]
                if "Dividends paid" in cash_flow_df.columns
                else pd.Series(dtype=float, index=ratios_index)
            )
            attributable_profit = (
                income_df["Attributable to parent company"]
                if "Attributable to parent company" in income_df.columns
                else net_profit
            )
            efficiency["Dividend Payout %"] = (
                (-dividends_paid / attributable_profit.replace(0, pd.NA)) * 100
                if not dividends_paid.isna().all()
                and not attributable_profit.isna().all()
                else pd.NA
            )
        else:
            efficiency["Dividend Payout %"] = pd.NA

        # Convert to records format
        categorized_ratios["Per Share Value"] = per_share.to_dict(orient="records")
        categorized_ratios["Growth Rate"] = growth_rate.to_dict(orient="records")
        categorized_ratios["Profitability"] = profitability.to_dict(orient="records")
        categorized_ratios["Valuation"] = valuation.to_dict(orient="records")
        categorized_ratios["Leverage & Liquidity"] = leverage_liquidity.to_dict(
            orient="records"
        )
        categorized_ratios["Efficiency"] = efficiency.to_dict(orient="records")

    except Exception:
        pass

    return categorized_ratios


def format_quarter_data(data_list):
    processed_data = []

    for item in data_list:
        processed_item = item.copy()

        year = item.get("Year", "") or item.get("year", "")
        quarter = item.get("Quarter", "") or item.get("quarter", "")

        if year and quarter:
            quarter_str = f"Q{quarter} {year}"
        else:
            quarter_str = f"{year}" if year else ""

        processed_item["formatted_quarter"] = quarter_str
        processed_item.pop("Quarter", None)
        processed_item.pop("quarter", None)
        processed_data.append(processed_item)

    return processed_data
