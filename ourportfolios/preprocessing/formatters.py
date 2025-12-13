"""Utility functions for formatting numbers and values for display."""

from typing import Any, Union
import pandas as pd


def format_large_number(value: Union[int, float], decimals: int = 2) -> str:
    """
    Format large numbers with K, M, B, T suffixes.

    Args:
        value: The number to format
        decimals: Number of decimal places to show (default 2)

    Returns:
        Formatted string with appropriate suffix

    Examples:
        1500 -> "1.50 K"
        1500000 -> "1.50 M"
        1500000000 -> "1.50 B"
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"

    try:
        num = float(value)

        # Handle negative numbers
        is_negative = num < 0
        num = abs(num)

        if num >= 1_000_000_000_000:  # Trillion
            formatted = f"{num / 1_000_000_000_000:.{decimals}f} T"
        elif num >= 1_000_000_000:  # Billion
            formatted = f"{num / 1_000_000_000:.{decimals}f} B"
        elif num >= 1_000_000:  # Million
            formatted = f"{num / 1_000_000:.{decimals}f} M"
        else:
            # Don't format thousands, keep as-is with decimals
            formatted = f"{num:.{decimals}f}"

        return f"-{formatted}" if is_negative else formatted

    except (ValueError, TypeError):
        return "N/A"


def format_percentage(value: Union[int, float], decimals: int = 2) -> str:
    """
    Format a number as a percentage.

    Args:
        value: The number to format
        decimals: Number of decimal places to show (default 2)

    Returns:
        Formatted percentage string
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"

    try:
        return f"{float(value):.{decimals}f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_ratio(value: Union[int, float], decimals: int = 2) -> str:
    """
    Format a ratio or decimal number.

    Args:
        value: The number to format
        decimals: Number of decimal places to show (default 2)

    Returns:
        Formatted ratio string
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"

    try:
        return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_integer(value: Union[int, float]) -> str:
    """
    Format a number as an integer.

    Args:
        value: The number to format

    Returns:
        Formatted integer string
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"

    try:
        return f"{int(float(value))}"
    except (ValueError, TypeError):
        return "N/A"


def format_currency_vnd(value: Union[int, float], use_suffix: bool = True) -> str:
    """
    Format VND currency values.

    Args:
        value: The number to format
        use_suffix: If True, use K/M/B suffixes for large numbers

    Returns:
        Formatted currency string
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"

    if use_suffix:
        return format_large_number(value, decimals=2)

    try:
        return f"{float(value):,.0f}"
    except (ValueError, TypeError):
        return "N/A"
