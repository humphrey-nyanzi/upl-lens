"""Raw-to-staging DataFrame transformations.

These functions keep data-shaping separate from database writes so parsing and
normalization rules can be tested without touching Postgres.
"""

from __future__ import annotations

import pandas as pd

from src.db.staging.constants import STAGING_COLUMNS
from src.db.staging.normalization import (
    _clean_text,
    _extract_man_of_match,
    _is_forfeit_text,
    _normalize_goal_type,
    _normalize_person,
    _normalize_team,
    _parse_dates,
    _parse_minute,
    _season_date_anomaly_reason,
    _season_key_series,
    _standardize_label,
    _team_from_side,
)


def _clean_match_rows(raw_matches: pd.DataFrame) -> pd.DataFrame:
    """Transform `raw.matches` into `staging.matches` rows."""

    df = raw_matches.copy()
    if df.empty:
        return pd.DataFrame(columns=list(STAGING_COLUMNS["matches"]))

    df["source_season"] = df["season"]
    df["season"] = _season_key_series(df["season"])
    df["match_date"] = _parse_dates(df["date"])
    df["match_time"] = df["time"].map(_clean_text)
    for column in ("home_team", "away_team", "man_of_the_match_team"):
        df[column] = df[column].map(_normalize_team)

    raw_man_of_the_match = df["man_of_the_match"].copy()
    df["is_forfeit"] = raw_man_of_the_match.map(_is_forfeit_text)
    df["source_anomaly_reason"] = [
        _season_date_anomaly_reason(season, match_date)
        for season, match_date in zip(df["season"], df["match_date"], strict=False)
    ]
    df["is_source_anomaly"] = df["source_anomaly_reason"].notna()
    motm_values = df.apply(_extract_man_of_match, axis=1)
    df["man_of_the_match"] = [name for name, _ in motm_values]
    df["man_of_the_match_team"] = [team for _, team in motm_values]

    df["home_score"] = pd.to_numeric(df["home_score"], errors="coerce").astype("Int64")
    df["away_score"] = pd.to_numeric(df["away_score"], errors="coerce").astype("Int64")
    df["total_goals"] = df["home_score"] + df["away_score"]
    df["goal_difference"] = df["home_score"] - df["away_score"]
    df["result"] = "draw"
    df.loc[df["goal_difference"] > 0, "result"] = "home_win"
    df.loc[df["goal_difference"] < 0, "result"] = "away_win"
    df["winner_team"] = None
    df.loc[df["result"] == "home_win", "winner_team"] = df["home_team"]
    df.loc[df["result"] == "away_win", "winner_team"] = df["away_team"]
    df["raw_ingested_at"] = df["ingested_at"]

    return df[list(STAGING_COLUMNS["matches"])]


def _clean_event_rows(raw_events: pd.DataFrame) -> pd.DataFrame:
    """Transform `raw.events` into parsed event rows."""

    df = raw_events.copy()
    if df.empty:
        return pd.DataFrame(columns=list(STAGING_COLUMNS["events"]))

    df["source_season"] = df["season"]
    df["season"] = _season_key_series(df["season"])
    df["match_date"] = _parse_dates(df["date"])
    df["match_time"] = df["time"].map(_clean_text)
    for column in ("home_team", "away_team"):
        df[column] = df[column].map(_normalize_team)

    df["event_type"] = df["event_type"].map(_standardize_label)
    df["team_side"] = df["team_side"].map(_standardize_label)
    df["player_name"] = df["player_name"].map(_normalize_person)
    df["sub_out_player_name"] = df["sub_out_player_name"].map(_normalize_person)
    df["sub_in_player_name"] = df["sub_in_player_name"].map(_normalize_person)

    minute_parts = pd.DataFrame([_parse_minute(value) for value in df["event_minute"]])
    df = pd.concat([df.reset_index(drop=True), minute_parts], axis=1)
    df["goal_type"] = [
        _normalize_goal_type(goal_type, annotation)
        for goal_type, annotation in zip(df["goal_type"], df["minute_annotation"], strict=False)
    ]
    df["team_name"] = df.apply(_team_from_side, axis=1)
    df["is_goal"] = df["event_type"] == "goal"
    df["is_yellow_card"] = df["event_type"] == "yellow_card"
    df["is_red_card"] = df["event_type"] == "red_card"
    df["is_substitution"] = df["event_type"] == "substitution"
    df["raw_ingested_at"] = df["ingested_at"]

    return df[list(STAGING_COLUMNS["events"])]


def _clean_team_person_table(raw_df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Clean lineups/staff tables that contain team and person fields."""

    df = raw_df.copy()
    if df.empty:
        return pd.DataFrame(columns=list(STAGING_COLUMNS[table_name]))

    df["source_season"] = df["season"]
    df["season"] = _season_key_series(df["season"])
    for column in ("home_team", "away_team", "team_name"):
        df[column] = df[column].map(_normalize_team)
    df["team_side"] = df["team_side"].map(_standardize_label)
    if "squad_role" in df.columns:
        df["squad_role"] = df["squad_role"].map(_standardize_label)
    if "role" in df.columns:
        df["role"] = df["role"].map(_clean_text)
    for column in ("player_name", "linked_player_name", "person_name"):
        if column in df.columns:
            df[column] = df[column].map(_normalize_person)
    df["raw_ingested_at"] = df["ingested_at"]

    return df[list(STAGING_COLUMNS[table_name])]


def _clean_official_rows(raw_officials: pd.DataFrame) -> pd.DataFrame:
    """Clean official assignment rows."""

    df = raw_officials.copy()
    if df.empty:
        return pd.DataFrame(columns=list(STAGING_COLUMNS["officials"]))

    df["source_season"] = df["season"]
    df["season"] = _season_key_series(df["season"])
    for column in ("home_team", "away_team"):
        df[column] = df[column].map(_normalize_team)
    df["role"] = df["role"].map(_clean_text)
    df["official_name"] = df["official_name"].map(_normalize_person)
    df["raw_ingested_at"] = df["ingested_at"]

    return df[list(STAGING_COLUMNS["officials"])]


def _clean_stat_rows(raw_stats: pd.DataFrame) -> pd.DataFrame:
    """Clean match statistic rows."""

    df = raw_stats.copy()
    if df.empty:
        return pd.DataFrame(columns=list(STAGING_COLUMNS["stats"]))

    df["source_season"] = df["season"]
    df["season"] = _season_key_series(df["season"])
    for column in ("home_team", "away_team"):
        df[column] = df[column].map(_normalize_team)
    df["statistic_name"] = df["statistic_name"].map(_clean_text)
    df["home_value"] = df["home_value"].map(_clean_text)
    df["away_value"] = df["away_value"].map(_clean_text)
    df["raw_ingested_at"] = df["ingested_at"]

    return df[list(STAGING_COLUMNS["stats"])]


def _build_staging_tables(raw_tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Apply all raw-to-staging transformations."""

    return {
        "matches": _clean_match_rows(raw_tables["matches"]),
        "events": _clean_event_rows(raw_tables["events"]),
        "lineups": _clean_team_person_table(raw_tables["lineups"], "lineups"),
        "staff": _clean_team_person_table(raw_tables["staff"], "staff"),
        "officials": _clean_official_rows(raw_tables["officials"]),
        "stats": _clean_stat_rows(raw_tables["stats"]),
    }

