"""Official Uganda Premier League scraper package.

The package keeps scraping concerns separate: HTTP/cache behavior, HTML parsing,
checkpoint state, Postgres change detection, output shaping, and CLI orchestration.
The historical script path re-exports these names for compatibility.
"""

from src.scraping.upl.cli import main
from src.scraping.upl.pipeline import scrape_season

__all__ = ["main", "scrape_season"]
