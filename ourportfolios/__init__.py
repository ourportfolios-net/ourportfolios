"""OurPortfolios application."""

import warnings

# Suppress pandas FutureWarning about 'M' frequency alias deprecation globally
warnings.filterwarnings('ignore', category=FutureWarning, message=".*'M' is deprecated.*")
