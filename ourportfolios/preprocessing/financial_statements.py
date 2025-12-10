"""Financial statements transformation and ratio computation."""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import text
from ..utils.database.database import price_engine

_cache = {}
_cache_duration = timedelta(minutes=30)


async def fetch_income_statement(
    ticker_symbol: str, period: str = "year"
) -> pd.DataFrame:
    """Fetch income statement data from database."""
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
        print(f"Error fetching income statement for {ticker_symbol}: {e}")
        return pd.DataFrame()


async def fetch_balance_sheet(ticker_symbol: str, period: str = "year") -> pd.DataFrame:
    """Fetch balance sheet data from database."""
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
        print(f"Error fetching balance sheet for {ticker_symbol}: {e}")
        return pd.DataFrame()


async def fetch_cash_flow(ticker_symbol: str, period: str = "year") -> pd.DataFrame:
    """Fetch cash flow data from database."""
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
        print(f"Error fetching cash flow for {ticker_symbol}: {e}")
        return pd.DataFrame()


def calculate_yoy_growth(series):
    """Calculate year-over-year growth percentage."""
    if len(series) < 2:
        return pd.Series(dtype=float, index=series.index)
    series_sorted = series.sort_index()
    return series_sorted.pct_change(fill_method=None) * 100


async def get_transformed_dataframes(
    ticker_symbol: str, period: str = "year"
) -> Dict[str, Any]:
    cache_key = f"{ticker_symbol}_{period}"
    if cache_key in _cache:
        cached_data, cached_time = _cache[cache_key]
        if datetime.now() - cached_time < _cache_duration:
            return cached_data

    print(f"Fetching data from database for {ticker_symbol} ({period})")

    try:
        income_df = await fetch_income_statement(ticker_symbol, period)
        balance_df = await fetch_balance_sheet(ticker_symbol, period)
        cash_flow_df = await fetch_cash_flow(ticker_symbol, period)

        if income_df.empty and balance_df.empty and cash_flow_df.empty:
            print(f"No financial data found in database for {ticker_symbol}")
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
                "error": "No data found in database. Data may need to be loaded via our_scheduler.",
            }

        # Compute ratios from the financial statements
        categorized_ratios = _compute_ratios_from_statements(
            income_df, balance_df, cash_flow_df, period
        )

        result = {
            "transformed_income_statement": income_df.to_dict(orient="records")
            if not income_df.empty
            else [],
            "transformed_balance_sheet": balance_df.to_dict(orient="records")
            if not balance_df.empty
            else [],
            "transformed_cash_flow": cash_flow_df.to_dict(orient="records")
            if not cash_flow_df.empty
            else [],
            "categorized_ratios": categorized_ratios,
        }

        _cache[cache_key] = (result, datetime.now())

        return result

    except Exception as e:
        print(f"Error fetching financial data from database for {ticker_symbol}: {e}")
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
            "error": str(e),
        }


def _compute_ratios_from_statements(
    income_df: pd.DataFrame,
    balance_df: pd.DataFrame,
    cash_flow_df: pd.DataFrame,
    period: str,
) -> Dict[str, list]:
    """Compute comprehensive financial ratios from raw statement data."""
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

    except Exception as e:
        print(f"Error computing ratios: {e}")
        import traceback

        traceback.print_exc()

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
