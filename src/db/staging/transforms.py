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


GOAL_EVENT_TYPES = {"goal", "own_goal", "penalty_goal"}
TIMELINE_STATUS_ADMINISTRATIVE = "administrative_result"
TIMELINE_STATUS_COMPLETE = "complete"
TIMELINE_STATUS_PARTIAL = "partial"
TIMELINE_STATUS_UNAVAILABLE = "unavailable"
TIMELINE_STATUS_UNKNOWN = "unknown"


def _sum_stat_values(home_value: object, away_value: object) -> int | None:
    """Return a whole-number total for source stats that represent event counts."""

    values = pd.to_numeric(pd.Series([home_value, away_value]), errors="coerce")
    if values.isna().any():
        return None
    return int(values.sum())


def _stat_count_by_match(stats: pd.DataFrame, statistic_name: str, output_column: str) -> pd.DataFrame:
    """Return one source-stat count column by match."""

    if stats.empty:
        return pd.DataFrame(columns=["match_id", output_column])

    normalized_name = stats["statistic_name"].fillna("").str.strip().str.casefold()
    selected = stats.loc[normalized_name == statistic_name.casefold(), ["match_id", "home_value", "away_value"]].copy()
    if selected.empty:
        return pd.DataFrame(columns=["match_id", output_column])

    selected[output_column] = [
        _sum_stat_values(home_value, away_value)
        for home_value, away_value in zip(selected["home_value"], selected["away_value"], strict=False)
    ]
    return selected.loc[:, ["match_id", output_column]]


def _event_count_by_match(events: pd.DataFrame, event_types: set[str], output_column: str) -> pd.DataFrame:
    """Return one parsed-timeline event count column by match."""

    if events.empty:
        return pd.DataFrame(columns=["match_id", output_column])

    selected = events.loc[events["event_type"].isin(event_types), ["match_id"]]
    if selected.empty:
        return pd.DataFrame(columns=["match_id", output_column])

    return selected.groupby("match_id").size().reset_index(name=output_column)


def _coerce_optional_count(value: object) -> int | None:
    """Convert a nullable count value to a Python int when present."""

    if pd.isna(value):
        return None
    return int(value)


def _timeline_coverage_note(row: pd.Series) -> str | None:
    """Build a concise reader-facing note for timeline coverage caveats."""

    if row["timeline_status"] == TIMELINE_STATUS_ADMINISTRATIVE:
        return "Administrative result; timeline events may not represent played match events."

    if row["timeline_status"] == TIMELINE_STATUS_UNAVAILABLE:
        return "Timeline unavailable from the source match page."

    if row["timeline_status"] != TIMELINE_STATUS_PARTIAL:
        return None

    issues: list[str] = []
    comparisons = (
        ("scoreline goals", "scoreline_goal_count", "timeline_goal_count"),
        ("source assists", "stats_assist_count", "timeline_assist_count"),
        ("source yellow cards", "stats_yellow_card_count", "timeline_yellow_card_count"),
        ("source red cards", "stats_red_card_count", "timeline_red_card_count"),
    )
    for label, source_column, timeline_column in comparisons:
        source_count = _coerce_optional_count(row.get(source_column))
        timeline_count = _coerce_optional_count(row.get(timeline_column))
        if source_count is None or timeline_count is None or source_count == timeline_count:
            continue
        issues.append(f"{label}={source_count}, parsed timeline={timeline_count}")

    if not issues:
        return "Timeline may be partial based on available source evidence."
    return f"Timeline is partial: {'; '.join(issues)}."


def _add_timeline_coverage_fields(
    matches: pd.DataFrame,
    events: pd.DataFrame,
    stats: pd.DataFrame,
) -> pd.DataFrame:
    """Add queryable timeline-completeness evidence to staged matches."""

    df = matches.copy()
    if df.empty:
        return pd.DataFrame(columns=list(STAGING_COLUMNS["matches"]))

    coverage_columns = (
        "timeline_status",
        "timeline_issue_count",
        "timeline_note",
        "scoreline_goal_count",
        "timeline_goal_count",
        "stats_assist_count",
        "timeline_assist_count",
        "stats_yellow_card_count",
        "timeline_yellow_card_count",
        "stats_red_card_count",
        "timeline_red_card_count",
    )
    df = df.drop(columns=list(coverage_columns), errors="ignore")

    count_frames = [
        _event_count_by_match(events, GOAL_EVENT_TYPES, "timeline_goal_count"),
        _event_count_by_match(events, {"assist"}, "timeline_assist_count"),
        _event_count_by_match(events, {"yellow_card"}, "timeline_yellow_card_count"),
        _event_count_by_match(events, {"red_card"}, "timeline_red_card_count"),
        _stat_count_by_match(stats, "Assists", "stats_assist_count"),
        _stat_count_by_match(stats, "Yellow Cards", "stats_yellow_card_count"),
        _stat_count_by_match(stats, "Red Cards", "stats_red_card_count"),
    ]

    df["scoreline_goal_count"] = df["total_goals"]
    for count_frame in count_frames:
        if count_frame.empty:
            continue
        df = df.merge(count_frame, on="match_id", how="left")

    timeline_columns = (
        "timeline_goal_count",
        "timeline_assist_count",
        "timeline_yellow_card_count",
        "timeline_red_card_count",
    )
    stats_columns = ("stats_assist_count", "stats_yellow_card_count", "stats_red_card_count")
    for column in timeline_columns:
        if column not in df.columns:
            df[column] = 0
        df[column] = df[column].fillna(0).astype("Int64")
    for column in stats_columns:
        if column not in df.columns:
            df[column] = pd.NA
        df[column] = df[column].astype("Int64")

    df["scoreline_goal_count"] = df["scoreline_goal_count"].astype("Int64")
    df["timeline_issue_count"] = 0

    goal_mismatch = df["scoreline_goal_count"].notna() & (df["scoreline_goal_count"] != df["timeline_goal_count"])
    assist_mismatch = df["stats_assist_count"].notna() & (df["stats_assist_count"] != df["timeline_assist_count"])
    yellow_mismatch = df["stats_yellow_card_count"].notna() & (
        df["stats_yellow_card_count"] != df["timeline_yellow_card_count"]
    )
    red_mismatch = df["stats_red_card_count"].notna() & (df["stats_red_card_count"] != df["timeline_red_card_count"])
    for mismatch in (goal_mismatch, assist_mismatch, yellow_mismatch, red_mismatch):
        df["timeline_issue_count"] += mismatch.astype(int)

    has_timeline = df["has_timeline"].fillna(False) | (df[list(timeline_columns)].sum(axis=1) > 0)
    is_admin = df["is_administrative_result"].fillna(False)

    df["timeline_status"] = TIMELINE_STATUS_COMPLETE
    df.loc[~has_timeline, "timeline_status"] = TIMELINE_STATUS_UNAVAILABLE
    df.loc[df["timeline_issue_count"] > 0, "timeline_status"] = TIMELINE_STATUS_PARTIAL
    df.loc[is_admin, "timeline_status"] = TIMELINE_STATUS_ADMINISTRATIVE
    df.loc[df["scoreline_goal_count"].isna(), "timeline_status"] = TIMELINE_STATUS_UNKNOWN
    df.loc[df["scoreline_goal_count"].isna() & ~has_timeline, "timeline_status"] = TIMELINE_STATUS_UNAVAILABLE

    df["timeline_note"] = df.apply(_timeline_coverage_note, axis=1)
    return df[list(STAGING_COLUMNS["matches"])]


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
    df["is_administrative_result"] = df["is_forfeit"]
    df["administrative_result_type"] = None
    df.loc[df["is_forfeit"], "administrative_result_type"] = "forfeit"
    df["administrative_note"] = None
    df.loc[df["is_forfeit"], "administrative_note"] = raw_man_of_the_match.map(_clean_text)
    df["played_on_pitch"] = ~df["is_administrative_result"]
    df["home_awarded_points"] = 0
    df["away_awarded_points"] = 0
    df.loc[df["result"] == "home_win", "home_awarded_points"] = 3
    df.loc[df["result"] == "away_win", "away_awarded_points"] = 3
    df.loc[df["result"] == "draw", ["home_awarded_points", "away_awarded_points"]] = 1
    df["timeline_status"] = TIMELINE_STATUS_UNKNOWN
    df["timeline_issue_count"] = 0
    df["timeline_note"] = None
    df["scoreline_goal_count"] = df["total_goals"]
    df["timeline_goal_count"] = 0
    df["stats_assist_count"] = pd.NA
    df["timeline_assist_count"] = 0
    df["stats_yellow_card_count"] = pd.NA
    df["timeline_yellow_card_count"] = 0
    df["stats_red_card_count"] = pd.NA
    df["timeline_red_card_count"] = 0
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

    staging_tables = {
        "matches": _clean_match_rows(raw_tables["matches"]),
        "events": _clean_event_rows(raw_tables["events"]),
        "lineups": _clean_team_person_table(raw_tables["lineups"], "lineups"),
        "staff": _clean_team_person_table(raw_tables["staff"], "staff"),
        "officials": _clean_official_rows(raw_tables["officials"]),
        "stats": _clean_stat_rows(raw_tables["stats"]),
    }
    staging_tables["matches"] = _add_timeline_coverage_fields(
        staging_tables["matches"],
        staging_tables["events"],
        staging_tables["stats"],
    )
    return staging_tables

