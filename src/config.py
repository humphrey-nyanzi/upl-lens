"""
Configuration and constants for the UPL Event Data Analysis project.

This module centralizes file paths, constants, and configuration settings
to avoid hardcoding values in notebooks and scripts.
"""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW = DATA_DIR / "raw"
LEGACY_RAW_ARCHIVE_DIR = DATA_RAW / "Goal_scraper_V1_data"
DATA_PROCESSED = DATA_DIR / "processed"
DATA_CACHE = DATA_DIR / "cache"

# Report directories
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


# Notebooks directory
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# CSV file paths
RAW_SEASON_FILES = {
    "2019_20": DATA_RAW / "upl_goals_2019_20.csv",
    "2020_21": DATA_RAW / "upl_goals_2020_21.csv",
    "2021_22": DATA_RAW / "upl_goals_2021_22.csv",
    "2022_23": DATA_RAW / "upl_goals_2022_23.csv",
    "2023_24": DATA_RAW / "upl_goals_2023_24.csv",
    "2024_25": DATA_RAW / "upl_goals_2024_25.csv",
    "2025_26": DATA_RAW / "upl_goals_2025_26.csv",
}

CLEANED_CSV = DATA_PROCESSED / "upl_goals_2019_2025_cleaned.csv"
FINAL_CSV = DATA_PROCESSED / "upl_goals_2019_2025_final.csv"

# Web scraping
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
)

UPL_BASE_URL = "https://upl.co.ug"
UPL_CALENDAR_URL = f"{UPL_BASE_URL}/calendar/{{season}}-fixtures-results/"
UPL_EVENT_URL_PREFIX = f"{UPL_BASE_URL}/event/"

# Scraping configuration
REQUEST_TIMEOUT = 60  # seconds
SCRAPE_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 1.5
RATE_LIMIT_SECONDS = 0.75
MAX_CONCURRENT_REQUESTS = 4
CHECKPOINT_EVERY = 25
USE_HTML_CACHE = True
SCRAPER_STATUS_FORCELIST = (429, 500, 502, 503, 504)
MIN_CALENDAR_MATCH_LINKS = 1
MIN_RAW_SEASON_MATCH_ROWS = 1
MIN_RAW_SEASON_MATCH_RATIO = 0.5
UPL_MAX_SEASON_MATCH_COUNT = 240
# Trusted baselines are reviewed operational data, not values learned from the
# current HTTP response. Rotate a baseline only after validating a known-good
# official calendar snapshot and recording the evidence in the same code review.
# Uganda Premier League seasons should not exceed the 240-match league maximum.
TRUSTED_SEASON_CALENDAR_BASELINES = {
    "2025_26": {
        "expected_match_count": 240,
        "version": "2026-07-08",
        "evidence": (
            "validated official 2025-26 calendar snapshot and hosted raw match "
            "identity set from GitHub Actions run 28786442845"
        ),
    },
}

# Team name corrections mapping
CLUB_NAME_CORRECTIONS = {
    "Vipers FC": "Vipers SC",
    "Vipers": "Vipers SC",
    "Bright Stars FC": "Soltilo Bright Stars FC",
    "Soltilo Bright Stars": "Soltilo Bright Stars FC",
    "Mbarara City": "Mbarara City FC",
    "Police": "Police FC",
    "Ondupraka FC": "Onduparaka FC",
    "Odumparaka FC": "Onduparaka FC",
    "Sc Villa": "SC Villa",
    "Gaddafi FC": "Entebbe UPPC FC",
    "Tooro United": "Tooro United FC",
    "Tooro FC": "Tooro United FC",
    "Mbaara City FC": "Mbarara City FC",
    "Onduparak FC": "Onduparaka FC",
    "Ondupararka FC": "Onduparaka FC",
    "KCCA": "KCCA FC",
    "URA": "URA FC",
    "Busoga United": "Busoga United FC",
    "Wakiso Giants": "Wakiso Giants FC",
    "Wakiso Giants FSC": "Wakiso Giants FC",
    "Kyetume FC": "Kyetume",
    "Tooro Uinted FC": "Tooro United FC",
}

# Uppercase abbreviations in team names
UPPERCASE_TERMS = {"fc", "sc", "kcca", "ura", "myda", "updf", "nec", "bul", "uppc"}

# Goal type constants
GOAL_TYPE_REGULAR = "Regular"
GOAL_TYPE_PENALTY = "Penalty"
GOAL_TYPE_OWN_GOAL = "Own Goal"

# Match sides
SIDE_HOME = "home"
SIDE_AWAY = "away"

# Analysis constants
SEASONS = ["2019/20", "2020/21", "2021/22", "2022/23", "2023/24", "2024/25"]

# Phase 5 automation starts with the active season. Keep this centralized so
# local scripts and GitHub Actions use the same default season value.
CURRENT_SEASON = "2025-26"

RAW_TABLE_FILE_PREFIXES = {
    "matches": "upl_matches",
    "events": "upl_events",
    "lineups": "upl_lineups",
    "staff": "upl_staff",
    "officials": "upl_officials",
    "stats": "upl_stats",
}

FAILED_MATCHES_FILE_PREFIX = "upl_failed_matches"
SOURCE_PREFLIGHT_FILE_PREFIX = "upl_source_preflight"
RAW_LOAD_SAFETY_FILE_PREFIX = "upl_raw_load_safety"
RAW_REFRESH_PLAN_FILE_PREFIX = "upl_raw_refresh_plan"


def season_key(season: str) -> str:
    """Convert a season like '2025-26' or '2025/26' to '2025_26'."""
    return season.replace("-", "_").replace("/", "_")


def raw_season_dir(season: str) -> Path:
    """Return the raw-data directory for one season."""
    return DATA_RAW / season_key(season)


def raw_season_file(season: str, table_name: str) -> Path:
    """Return the CSV path for one scraped table in its season subfolder."""
    prefix = RAW_TABLE_FILE_PREFIXES[table_name]
    return raw_season_dir(season) / f"{prefix}_{season_key(season)}.csv"


def raw_season_failed_matches_file(season: str) -> Path:
    """Return the per-season CSV that tracks failed match URLs."""
    return (
        raw_season_dir(season)
        / f"{FAILED_MATCHES_FILE_PREFIX}_{season_key(season)}.csv"
    )


def raw_season_source_preflight_file(season: str) -> Path:
    """Return the source-calendar preflight contract for one season."""
    return (
        raw_season_dir(season)
        / f"{SOURCE_PREFLIGHT_FILE_PREFIX}_{season_key(season)}.json"
    )


def raw_season_load_safety_file(season: str) -> Path:
    """Return the raw-loader safety evidence file for one season."""
    return (
        raw_season_dir(season)
        / f"{RAW_LOAD_SAFETY_FILE_PREFIX}_{season_key(season)}.json"
    )


def raw_season_refresh_plan_file(season: str) -> Path:
    """Return the scraper-to-loader match-level refresh plan."""
    return (
        raw_season_dir(season)
        / f"{RAW_REFRESH_PLAN_FILE_PREFIX}_{season_key(season)}.json"
    )
