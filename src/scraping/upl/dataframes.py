"""DataFrame shaping and CSV-output helpers for scraped tables."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.config import DATA_RAW, raw_season_dir, raw_season_file, season_key
from src.dataset import save_dataframe
from src.scraping.upl.constants import LEGACY_GOAL_COLUMNS, TABLE_NAMES


def _build_output_dataframe(rows: list[dict[str, Any]], columns: list[str]) -> pd.DataFrame:
    """Create a dataframe with a stable column order for one output table."""
    if not rows:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(rows)
    for column in columns:
        if column not in df.columns:
            df[column] = None

    return df[columns]


def _build_legacy_goal_dataframe(events_df: pd.DataFrame) -> pd.DataFrame:
    """Create the legacy goal-only export used by the existing cleaning step."""
    if events_df.empty:
        return pd.DataFrame(columns=LEGACY_GOAL_COLUMNS)

    goal_events = events_df.loc[events_df["event_type"] == "goal"].copy()
    if goal_events.empty:
        return pd.DataFrame(columns=LEGACY_GOAL_COLUMNS)

    goal_events = goal_events.rename(
        columns={
            "date": "Date",
            "time": "Time",
            "league": "League",
            "season": "Season",
            "match_day": "Match Day",
            "event_minute": "goal_minute",
        }
    )

    for column in LEGACY_GOAL_COLUMNS:
        if column not in goal_events.columns:
            goal_events[column] = None

    return goal_events[LEGACY_GOAL_COLUMNS]


def _filter_tables_to_requested_season(
    season: str,
    season_tables: dict[str, pd.DataFrame],
) -> tuple[dict[str, pd.DataFrame], dict[str, int]]:
    """Keep raw season outputs scoped to the requested season folder.

    The official calendar can occasionally expose match URLs whose match page
    belongs to a different season. We filter those rows before writing CSVs so
    `data/raw/<season>/` remains a true season slice. The raw Postgres loader
    has the same guard, but catching it here keeps artifacts cleaner too.
    """

    expected_season = season_key(season)
    filtered_tables: dict[str, pd.DataFrame] = {}
    spill_counts: dict[str, int] = {}

    for table_name, df in season_tables.items():
        if df.empty or "season" not in df.columns:
            filtered_tables[table_name] = df.copy()
            spill_counts[table_name] = 0
            continue

        normalized_seasons = df["season"].fillna("").astype(str).str.strip().map(season_key)
        in_season_mask = normalized_seasons == expected_season
        spill_counts[table_name] = int((~in_season_mask).sum())
        filtered_tables[table_name] = df.loc[in_season_mask].copy()

    return filtered_tables, spill_counts


def _save_structured_outputs(season: str, season_tables: dict[str, pd.DataFrame]) -> None:
    """Save all structured raw tables into data/raw/<season>/."""
    season_dir = raw_season_dir(season)
    season_dir.mkdir(parents=True, exist_ok=True)

    for table_name in TABLE_NAMES:
        output_path = raw_season_file(season, table_name)
        save_dataframe(season_tables[table_name], output_path)

