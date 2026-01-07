"""Page modules for the application."""

# Import all page modules to register them with Reflex
from . import landing
from . import analyze
from . import ticker_analysis
from . import compare
from . import recommend
from . import select
from . import industry_analysis

__all__ = [
    "landing",
    "analyze",
    "ticker_analysis",
    "compare",
    "recommend",
    "select",
    "industry_analysis",
]
