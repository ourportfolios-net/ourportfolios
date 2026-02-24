"""Page modules for the application."""

# Import all page modules to register them with Reflex
from . import landing
from . import analyze
from . import ticker_analysis
from . import tickers
from . import framework
from . import industry_analysis

__all__ = [
    "landing",
    "analyze",
    "ticker_analysis",
    "tickers",
    "framework",
    "industry_analysis",
]
