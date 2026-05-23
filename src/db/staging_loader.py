"""Build cleaned staging tables from Postgres raw tables.

Phase 2 deliberately reads from `raw.*` in Postgres instead of going back to
CSV files. That makes Postgres the trusted boundary between scraping and
downstream modeling.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from json import dumps
from typing import Any, Callable

import pandas as pd
from sqlalchemy import text

from src import config
from src.cleaning import normalize_team_name
from src.db.connection import create_sqlalchemy_engine
from src.db.raw_loader import resolve_seasons
from src.db.settings import DatabaseSettings


RAW_TABLES = ("matches", "events", "lineups", "staff", "officials", "stats")

STAGING_RELOAD_ORDER = ("events", "lineups", "staff", "officials", "stats", "matches")
STAGING_INSERT_ORDER = ("matches", "events", "lineups", "staff", "officials", "stats")

RAW_REQUIRED_COLUMNS: dict[str, set[str]] = {
    "matches": {
        "match_id",
        "match_url",
        "season",
        "date",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
    },
    "events": {"event_row_key", "match_id", "season", "event_index", "event_type"},
    "lineups": {"lineup_row_key", "match_id", "season", "team_side", "team_name", "player_name"},
    "staff": {"staff_row_key", "match_id", "season", "team_side", "team_name", "person_name"},
    "officials": {"official_row_key", "match_id", "season", "role", "official_name"},
    "stats": {"stat_row_key", "match_id", "season", "statistic_name"},
}


@dataclass(frozen=True)
class StagingBuildResult:
    """Summary returned after rebuilding staging tables."""

    run_id: str
    seasons: list[str]
    row_counts: dict[str, int]
    issue_counts: dict[str, int]


@dataclass(frozen=True)
class StagingValidationError(Exception):
    """Raised after validation evidence is recorded for an unsafe staging build."""

    run_id: str
    seasons: list[str]
    issue_counts: dict[str, int]

    def __str__(self) -> str:
        return (
            "Staging validation found error-level issues before table writes. "
            f"Run ID: {self.run_id}."
        )


def _season_key_series(series: pd.Series) -> pd.Series:
    """Normalize season text so `2025/26`, `2025-26`, and `2025_26` compare equally."""

    return (
        series.astype("string")
        .str.strip()
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
    )


def _clean_text(value: Any) -> str | None:
    """Return stripped text or None for empty/null values."""

    if pd.isna(value):
        return None
    text_value = str(value).strip()
    return text_value or None


def _standardize_label(value: Any) -> str | None:
    """Normalize low-cardinality labels such as event types and squad roles."""

    text_value = _clean_text(value)
    if text_value is None:
        return None
    return re.sub(r"\s+", "_", text_value.lower())


def _normalize_team(value: Any) -> str | None:
    """Normalize team names with the shared project corrections."""

    text_value = _clean_text(value)
    if text_value is None:
        return None
    corrected = config.CLUB_NAME_CORRECTIONS.get(text_value, text_value)
    corrected = config.CLUB_NAME_CORRECTIONS.get(corrected.title(), corrected)
    normalized = normalize_team_name(corrected.lower())
    return config.CLUB_NAME_CORRECTIONS.get(normalized, normalized)


def _normalize_person(value: Any) -> str | None:
    """Trim person names while preserving the source spelling."""

    return _clean_text(value)


def _clean_person_name(value: Any) -> str | None:
    """Return a stricter person-name value for fields such as Man of the Match."""

    text_value = _clean_text(value)
    if text_value is None:
        return None
    cleaned = re.sub(r"^\(?\s*(?:gk|captain|capt)\s*\)?\s*", "", text_value, flags=re.IGNORECASE)
    cleaned = cleaned.replace("(", "").replace(")", "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .:-|")
    if not cleaned:
        return None
    if re.search(
        r"\b(match|coach|yellow|red|card|live|televised|turn up|circumstances|decision|forfeiture|fixture|notice)\b",
        cleaned,
        flags=re.IGNORECASE,
    ):
        return None
    return cleaned


def _team_matches_match(row: pd.Series, team_name: str | None) -> bool:
    """Return whether a team belongs to the match's home/away pair."""

    if team_name is None:
        return False
    return team_name in {row.get("home_team"), row.get("away_team")}


def _extract_man_of_match(row: pd.Series) -> tuple[str | None, str | None]:
    """Extract a strict Man of the Match name/team pair from raw match text.

    The UPL page excerpt often mixes broadcast notes, coach cards, forfeiture
    explanations, and the actual award. Staging keeps only the award when it can
    identify a likely person name and a team that played in the match.
    """

    raw_name = _clean_text(row.get("man_of_the_match"))
    raw_team = _normalize_team(row.get("man_of_the_match_team"))
    if raw_name is None:
        return None, None

    label_match = re.search(
        r"(?:pilsner\s+)?m\s*<?an\s*of\s*(?:the\s*)?(?:match|math)\s*:\s*(?P<body>.+)",
        raw_name,
        flags=re.IGNORECASE,
    )
    if label_match:
        body = label_match.group("body")
        parenthetical_teams = list(re.finditer(r"\((?P<team>[^()]*)\)", body))
        for team_match in reversed(parenthetical_teams):
            parsed_team = _normalize_team(team_match.group("team"))
            if not _team_matches_match(row, parsed_team):
                continue
            parsed_name = _clean_person_name(body[: team_match.start()])
            if parsed_name:
                return parsed_name, parsed_team

        # A few source rows omit the opening parenthesis before the team, e.g.
        # `Name Team FC)`. Use the home/away team names as anchors instead of
        # guessing arbitrary trailing words.
        for candidate_team in (row.get("home_team"), row.get("away_team")):
            if candidate_team and re.search(re.escape(str(candidate_team)), body, flags=re.IGNORECASE):
                parsed_name = _clean_person_name(
                    re.split(re.escape(str(candidate_team)), body, maxsplit=1, flags=re.IGNORECASE)[0]
                )
                if parsed_name:
                    return parsed_name, str(candidate_team)

    clean_name = _clean_person_name(raw_name)
    if clean_name and len(clean_name) <= 80:
        if _team_matches_match(row, raw_team):
            return clean_name, raw_team
        if raw_team is None:
            return clean_name, None

    return None, None


def _parse_dates(series: pd.Series) -> pd.Series:
    """Parse UPL dates with day-first ordering.

    Historical source files use day-first dates. Invalid dates become null and
    are logged by validation instead of crashing the whole build.
    """

    return pd.to_datetime(series, dayfirst=True, errors="coerce").dt.date


def _is_forfeit_text(value: Any) -> bool:
    """Return whether source text clearly describes a forfeited match."""

    text_value = _clean_text(value)
    if text_value is None:
        return False
    return bool(
        re.search(
            r"\b(forfeit|forfeiture|failed to turn up|failure to honour|walkover|walk over)\b",
            text_value,
            flags=re.IGNORECASE,
        )
    )


def _minute_period(minute_total: int | None) -> str | None:
    """Bucket a match minute into a simple analysis interval."""

    if minute_total is None:
        return None
    if minute_total <= 15:
        return "0-15"
    if minute_total <= 30:
        return "16-30"
    if minute_total <= 45:
        return "31-45"
    if minute_total <= 60:
        return "46-60"
    if minute_total <= 75:
        return "61-75"
    if minute_total <= 90:
        return "76-90"
    return "90+"


def _parse_minute(value: Any) -> dict[str, Any]:
    """Parse event minute text into numeric pieces.

    Handles normal minutes (`56`), added time (`45+2`), apostrophes, empty
    strings, and inline annotations such as `56 (P)` or `90 OG`.
    """

    text_value = _clean_text(value)
    if text_value is None:
        return {
            "event_minute_text": None,
            "minute_base": None,
            "minute_added": None,
            "minute_total": None,
            "is_added_time": False,
            "minute_period": None,
            "minute_annotation": None,
            "minute_parse_failed": False,
        }

    annotation_parts: list[str] = []
    normalized = text_value.replace("'", "").strip()
    if re.search(r"\(\s*p\s*\)|\bpen\b", normalized, flags=re.IGNORECASE):
        annotation_parts.append("penalty")
    if re.search(r"\bog\b", normalized, flags=re.IGNORECASE):
        annotation_parts.append("own_goal")

    minute_text = re.sub(r"\(\s*p\s*\)", "", normalized, flags=re.IGNORECASE)
    minute_text = re.sub(r"\bpen\b", "", minute_text, flags=re.IGNORECASE)
    minute_text = re.sub(r"\bog\b", "", minute_text, flags=re.IGNORECASE).strip()
    match = re.search(r"(?P<base>\d{1,3})(?:\s*\+\s*(?P<added>\d{1,2}))?", minute_text)
    if match is None:
        return {
            "event_minute_text": text_value,
            "minute_base": None,
            "minute_added": None,
            "minute_total": None,
            "is_added_time": False,
            "minute_period": None,
            "minute_annotation": ",".join(annotation_parts) or None,
            "minute_parse_failed": True,
        }

    base_minute = int(match.group("base"))
    added_minute = int(match.group("added") or 0)
    total_minute = base_minute + added_minute
    return {
        "event_minute_text": text_value,
        "minute_base": base_minute,
        "minute_added": added_minute,
        "minute_total": total_minute,
        "is_added_time": added_minute > 0,
        "minute_period": _minute_period(total_minute),
        "minute_annotation": ",".join(annotation_parts) or None,
        "minute_parse_failed": False,
    }


def _normalize_goal_type(raw_goal_type: Any, minute_annotation: Any) -> str | None:
    """Standardize goal type and preserve penalty/own-goal hints from minute text."""

    goal_type = _clean_text(raw_goal_type)
    annotation = _clean_text(minute_annotation)
    if annotation == "penalty":
        return config.GOAL_TYPE_PENALTY
    if annotation == "own_goal":
        return config.GOAL_TYPE_OWN_GOAL
    if annotation == "penalty,own_goal":
        return config.GOAL_TYPE_PENALTY
    if goal_type is None:
        return None
    normalized = goal_type.replace("_", " ").title()
    if normalized.lower() == "own goal":
        return config.GOAL_TYPE_OWN_GOAL
    if normalized.lower() == "penalty":
        return config.GOAL_TYPE_PENALTY
    return normalized


def _team_from_side(row: pd.Series) -> str | None:
    """Resolve the actual team name for an event from its home/away side."""

    if row.get("team_side") == config.SIDE_HOME:
        return row.get("home_team")
    if row.get("team_side") == config.SIDE_AWAY:
        return row.get("away_team")
    return None


def _read_raw_table(connection, table_name: str, seasons: list[str]) -> pd.DataFrame:
    """Read a season slice from one raw table."""

    if table_name not in RAW_TABLES:
        raise ValueError(f"Unsupported raw table: {table_name}")

    query = text(
        f"""
        SELECT *
        FROM raw.{table_name}
        WHERE REPLACE(REPLACE(season, '-', '_'), '/', '_') = ANY(:seasons)
        """
    )
    return pd.read_sql_query(query, connection, params={"seasons": seasons})


ProgressCallback = Callable[[str], None]


def _read_raw_tables(
    connection,
    seasons: list[str],
    progress: ProgressCallback | None = None,
) -> dict[str, pd.DataFrame]:
    """Read all raw tables needed by the staging build."""

    raw_tables: dict[str, pd.DataFrame] = {}
    for table_name in RAW_TABLES:
        if progress:
            progress(f"Reading raw.{table_name}")
        table_df = _read_raw_table(connection, table_name, seasons)
        raw_tables[table_name] = table_df
        if progress:
            progress(f"Read raw.{table_name}: {len(table_df)} rows")
    return raw_tables


def _discover_raw_database_seasons(connection) -> list[str]:
    """Discover seasons from `raw.matches` inside Postgres."""

    rows = connection.execute(
        text(
            """
            SELECT DISTINCT REPLACE(REPLACE(season, '-', '_'), '/', '_') AS season_key
            FROM raw.matches
            WHERE season IS NOT NULL AND BTRIM(season) <> ''
            ORDER BY season_key;
            """
        )
    ).fetchall()
    return [str(row[0]) for row in rows]


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


STAGING_COLUMNS: dict[str, tuple[str, ...]] = {
    "matches": (
        "match_id",
        "match_url",
        "source_season",
        "season",
        "match_date",
        "match_time",
        "league",
        "match_day",
        "home_team",
        "home_team_url",
        "away_team",
        "away_team_url",
        "ground_name",
        "ground_address",
        "man_of_the_match",
        "man_of_the_match_team",
        "home_score",
        "away_score",
        "total_goals",
        "goal_difference",
        "result",
        "winner_team",
        "is_forfeit",
        "home_first_half_goals",
        "away_first_half_goals",
        "home_second_half_goals",
        "away_second_half_goals",
        "has_timeline",
        "has_lineups",
        "has_officials",
        "has_stats",
        "raw_ingested_at",
    ),
    "events": (
        "event_row_key",
        "match_id",
        "match_url",
        "source_season",
        "season",
        "match_date",
        "match_time",
        "league",
        "match_day",
        "home_team",
        "away_team",
        "event_index",
        "event_type",
        "event_minute_text",
        "minute_base",
        "minute_added",
        "minute_total",
        "is_added_time",
        "minute_period",
        "team_side",
        "team_name",
        "player_name",
        "player_url",
        "goal_type",
        "sub_out_player_name",
        "sub_out_player_url",
        "sub_in_player_name",
        "sub_in_player_url",
        "is_goal",
        "is_yellow_card",
        "is_red_card",
        "is_substitution",
        "raw_ingested_at",
    ),
    "lineups": (
        "lineup_row_key",
        "match_id",
        "match_url",
        "source_season",
        "season",
        "match_day",
        "home_team",
        "away_team",
        "team_name",
        "team_side",
        "squad_role",
        "shirt_number",
        "player_name",
        "player_url",
        "player_position",
        "is_player_of_match",
        "swap_badge_type",
        "linked_player_name",
        "linked_shirt_number",
        "raw_ingested_at",
    ),
    "staff": (
        "staff_row_key",
        "match_id",
        "match_url",
        "source_season",
        "season",
        "match_day",
        "home_team",
        "away_team",
        "team_name",
        "team_side",
        "role",
        "person_name",
        "person_url",
        "raw_ingested_at",
    ),
    "officials": (
        "official_row_key",
        "match_id",
        "match_url",
        "source_season",
        "season",
        "match_day",
        "home_team",
        "away_team",
        "role",
        "official_name",
        "raw_ingested_at",
    ),
    "stats": (
        "stat_row_key",
        "match_id",
        "match_url",
        "source_season",
        "season",
        "match_day",
        "home_team",
        "away_team",
        "statistic_name",
        "home_value",
        "away_value",
        "raw_ingested_at",
    ),
}


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


def _issue(
    run_id: str,
    severity: str,
    check_name: str,
    schema_name: str,
    table_name: str,
    issue_message: str,
    season: Any = None,
    match_id: Any = None,
    row_key: Any = None,
    column_name: str | None = None,
    issue_value: Any = None,
) -> dict[str, Any]:
    """Create one validation issue row."""

    return {
        "run_id": run_id,
        "severity": severity,
        "check_name": check_name,
        "schema_name": schema_name,
        "table_name": table_name,
        "season": _clean_text(season),
        "match_id": int(match_id) if pd.notna(match_id) else None,
        "row_key": _clean_text(row_key),
        "column_name": column_name,
        "issue_message": issue_message,
        "issue_value": _clean_text(issue_value),
    }


def _validate_required_columns(raw_tables: dict[str, pd.DataFrame], run_id: str) -> list[dict[str, Any]]:
    """Check that expected raw columns are available before transformation."""

    issues: list[dict[str, Any]] = []
    for table_name, required_columns in RAW_REQUIRED_COLUMNS.items():
        missing_columns = sorted(required_columns.difference(raw_tables[table_name].columns))
        for column_name in missing_columns:
            issues.append(
                _issue(
                    run_id=run_id,
                    severity="error",
                    check_name="required_columns",
                    schema_name="raw",
                    table_name=table_name,
                    column_name=column_name,
                    issue_message="Required raw column is missing.",
                )
            )
    return issues


def _validate_raw_season_consistency(
    raw_tables: dict[str, pd.DataFrame],
    seasons: list[str],
    run_id: str,
) -> list[dict[str, Any]]:
    """Confirm raw season values match the requested season slice."""

    expected_seasons = set(seasons)
    issues: list[dict[str, Any]] = []
    for table_name, df in raw_tables.items():
        if df.empty or "season" not in df.columns:
            continue
        normalized = _season_key_series(df["season"])
        bad_rows = df.loc[~normalized.isin(expected_seasons)]
        for _, row in bad_rows.head(200).iterrows():
            issues.append(
                _issue(
                    run_id=run_id,
                    severity="error",
                    check_name="season_consistency",
                    schema_name="raw",
                    table_name=table_name,
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get(f"{table_name[:-1]}_row_key"),
                    column_name="season",
                    issue_message="Raw row season does not match the requested staging season slice.",
                    issue_value=row.get("season"),
                )
            )
    return issues


def _validate_duplicates(staging_tables: dict[str, pd.DataFrame], run_id: str) -> list[dict[str, Any]]:
    """Log duplicate risks in natural keys used for staging tables."""

    duplicate_rules = {
        "matches": ["match_id"],
        "events": ["match_id", "event_index"],
        "lineups": ["lineup_row_key"],
        "staff": ["staff_row_key"],
        "officials": ["official_row_key"],
        "stats": ["match_id", "statistic_name"],
    }
    issues: list[dict[str, Any]] = []
    for table_name, key_columns in duplicate_rules.items():
        df = staging_tables[table_name]
        if df.empty:
            continue
        duplicate_rows = df.loc[df.duplicated(subset=key_columns, keep=False)]
        for _, row in duplicate_rows.head(200).iterrows():
            issues.append(
                _issue(
                    run_id=run_id,
                    severity="error",
                    check_name="duplicate_risk",
                    schema_name="staging",
                    table_name=table_name,
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get(f"{table_name[:-1]}_row_key"),
                    issue_message=f"Duplicate natural key risk on columns: {', '.join(key_columns)}.",
                    issue_value=" | ".join(str(row.get(column)) for column in key_columns),
                )
            )
    return issues


def _validate_key_fields(staging_tables: dict[str, pd.DataFrame], run_id: str) -> list[dict[str, Any]]:
    """Validate core IDs, match references, dates, sides, and minute parsing."""

    issues: list[dict[str, Any]] = []
    matches = staging_tables["matches"]
    match_ids = set(matches["match_id"].dropna().astype(int)) if not matches.empty else set()

    if not matches.empty:
        for column_name in ("match_id", "match_url", "season"):
            missing_rows = matches.loc[matches[column_name].isna()]
            for _, row in missing_rows.head(200).iterrows():
                issues.append(
                    _issue(
                        run_id,
                        "error",
                        "key_field_quality",
                        "staging",
                        "matches",
                        f"Required match field `{column_name}` is missing after cleaning.",
                        season=row.get("season"),
                        match_id=row.get("match_id"),
                        column_name=column_name,
                    )
                )
        for column_name in ("home_team", "away_team"):
            missing_rows = matches.loc[matches[column_name].isna()]
            for _, row in missing_rows.head(200).iterrows():
                issues.append(
                    _issue(
                        run_id,
                        "warning",
                        "missing_team_player_values",
                        "staging",
                        "matches",
                        f"Match is missing `{column_name}` after cleaning.",
                        season=row.get("season"),
                        match_id=row.get("match_id"),
                        column_name=column_name,
                    )
                )
        invalid_dates = matches.loc[matches["match_date"].isna()]
        for _, row in invalid_dates.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "key_field_quality",
                    "staging",
                    "matches",
                    "Match date could not be parsed with day-first parsing.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    column_name="match_date",
                    issue_value=row.get("match_date"),
                )
            )

    for table_name in ("events", "lineups", "staff", "officials", "stats"):
        df = staging_tables[table_name]
        if df.empty:
            continue
        missing_match = df.loc[~df["match_id"].isin(match_ids)]
        for _, row in missing_match.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "error",
                    "key_field_quality",
                    "staging",
                    table_name,
                    "Row references a match_id that is not present in staging.matches.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get(f"{table_name[:-1]}_row_key"),
                    column_name="match_id",
                    issue_value=row.get("match_id"),
                )
            )

    events = staging_tables["events"]
    if not events.empty:
        bad_sides = events.loc[events["team_side"].notna() & ~events["team_side"].isin({config.SIDE_HOME, config.SIDE_AWAY})]
        for _, row in bad_sides.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "key_field_quality",
                    "staging",
                    "events",
                    "Event team_side is not home or away.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get("event_row_key"),
                    column_name="team_side",
                    issue_value=row.get("team_side"),
                )
            )

        missing_minute = events.loc[events["event_minute_text"].isna()]
        for _, row in missing_minute.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "info",
                    "key_field_quality",
                    "staging",
                    "events",
                    "Event minute is blank in the source and is marked unknown.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get("event_row_key"),
                    column_name="event_minute_text",
                )
            )

        failed_minutes = events.loc[events["event_minute_text"].notna() & events["minute_total"].isna()]
        for _, row in failed_minutes.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "key_field_quality",
                    "staging",
                    "events",
                    "Event minute text could not be parsed into a numeric minute.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get("event_row_key"),
                    column_name="event_minute_text",
                    issue_value=row.get("event_minute_text"),
                )
            )

    return issues


def _validate_missing_team_player_values(
    staging_tables: dict[str, pd.DataFrame],
    run_id: str,
) -> list[dict[str, Any]]:
    """Check missing team/player values where they matter for analysis."""

    issues: list[dict[str, Any]] = []
    events = staging_tables["events"]
    if not events.empty:
        player_event_mask = events["event_type"].isin({"goal", "yellow_card", "red_card"})
        player_missing = events.loc[player_event_mask & events["player_name"].isna()]
        for _, row in player_missing.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "missing_team_player_values",
                    "staging",
                    "events",
                    "Goal/card event is missing player_name.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get("event_row_key"),
                    column_name="player_name",
                )
            )
        team_missing = events.loc[events["event_type"].notna() & events["team_name"].isna()]
        for _, row in team_missing.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "missing_team_player_values",
                    "staging",
                    "events",
                    "Event is missing a resolvable team name.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get("event_row_key"),
                    column_name="team_name",
                    issue_value=row.get("team_side"),
                )
            )

    for table_name, person_column in (("lineups", "player_name"), ("staff", "person_name")):
        df = staging_tables[table_name]
        if df.empty:
            continue
        missing_team = df.loc[df["team_name"].isna()]
        for _, row in missing_team.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "missing_team_player_values",
                    "staging",
                    table_name,
                    "Row is missing team_name.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get(f"{table_name[:-1]}_row_key"),
                    column_name="team_name",
                )
            )
        missing_person = df.loc[df[person_column].isna()]
        for _, row in missing_person.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "missing_team_player_values",
                    "staging",
                    table_name,
                    f"Row is missing {person_column}.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get(f"{table_name[:-1]}_row_key"),
                    column_name=person_column,
                )
            )

    officials = staging_tables["officials"]
    if not officials.empty:
        missing_official = officials.loc[officials["official_name"].isna()]
        for _, row in missing_official.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "missing_team_player_values",
                    "staging",
                    "officials",
                    "Official assignment is missing official_name.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get("official_row_key"),
                    column_name="official_name",
                )
            )

    return issues


def _validate_man_of_match_quality(
    raw_tables: dict[str, pd.DataFrame],
    staging_tables: dict[str, pd.DataFrame],
    run_id: str,
) -> list[dict[str, Any]]:
    """Validate Man of the Match extraction without failing historical rebuilds."""

    issues: list[dict[str, Any]] = []
    matches = staging_tables["matches"]
    if matches.empty:
        return issues

    motm_with_no_team = matches.loc[
        matches["man_of_the_match"].notna() & matches["man_of_the_match_team"].isna()
    ]
    for _, row in motm_with_no_team.head(200).iterrows():
        issues.append(
            _issue(
                run_id,
                "warning",
                "man_of_match_quality",
                "staging",
                "matches",
                "Man of the Match name was kept, but no valid team could be confirmed.",
                season=row.get("season"),
                match_id=row.get("match_id"),
                column_name="man_of_the_match_team",
                issue_value=row.get("man_of_the_match"),
            )
        )

    motm_bad_team = matches.loc[
        matches["man_of_the_match_team"].notna()
        & (matches["man_of_the_match_team"] != matches["home_team"])
        & (matches["man_of_the_match_team"] != matches["away_team"])
    ]
    for _, row in motm_bad_team.head(200).iterrows():
        issues.append(
            _issue(
                run_id,
                "error",
                "man_of_match_quality",
                "staging",
                "matches",
                "Man of the Match team is not one of the two teams in the match.",
                season=row.get("season"),
                match_id=row.get("match_id"),
                column_name="man_of_the_match_team",
                issue_value=row.get("man_of_the_match_team"),
            )
        )

    raw_matches = raw_tables["matches"]
    if raw_matches.empty:
        return issues

    compare_columns = ["match_id", "man_of_the_match"]
    raw_motm = raw_matches.loc[:, compare_columns].rename(columns={"man_of_the_match": "raw_man_of_the_match"})
    motm_compare = raw_motm.merge(
        matches.loc[:, ["match_id", "season", "man_of_the_match"]],
        on="match_id",
        how="left",
    )
    raw_had_text = motm_compare["raw_man_of_the_match"].map(_clean_text).notna()
    staging_missing = motm_compare["man_of_the_match"].isna()
    for _, row in motm_compare.loc[raw_had_text & staging_missing].head(200).iterrows():
        issues.append(
            _issue(
                run_id,
                "info",
                "man_of_match_quality",
                "staging",
                "matches",
                "Raw Man of the Match text was not accepted as a strict player/team award.",
                season=row.get("season"),
                match_id=row.get("match_id"),
                column_name="man_of_the_match",
                issue_value=row.get("raw_man_of_the_match"),
            )
        )

    return issues


def _validate_scoreline_timeline_goal_consistency(
    staging_tables: dict[str, pd.DataFrame],
    run_id: str,
) -> list[dict[str, Any]]:
    """Flag matches where official scoreline goals differ from timeline goals.

    Administrative results and forfeits can make the match score say 3-0 even
    when the match timeline has fewer actual goal events. That is valid source
    behavior, but analytical features should know about it and use timeline
    goals when they mean actual scored goals.
    """

    issues: list[dict[str, Any]] = []
    matches = staging_tables["matches"]
    events = staging_tables["events"]
    if matches.empty:
        return issues

    if events.empty:
        event_goal_counts = pd.DataFrame(columns=["match_id", "timeline_goal_count"])
    else:
        goal_events = events.loc[events["event_type"].isin({"goal", "own_goal", "penalty_goal"})]
        event_goal_counts = (
            goal_events.groupby("match_id")
            .size()
            .reset_index(name="timeline_goal_count")
        )

    compare = matches.loc[
        matches["total_goals"].notna(),
        ["match_id", "season", "home_team", "away_team", "total_goals"],
    ].merge(event_goal_counts, on="match_id", how="left")
    compare["timeline_goal_count"] = compare["timeline_goal_count"].fillna(0).astype(int)
    compare["scoreline_goal_count"] = compare["total_goals"].astype(int)
    mismatches = compare.loc[compare["scoreline_goal_count"] != compare["timeline_goal_count"]]

    for _, row in mismatches.head(200).iterrows():
        issue_value = (
            f"scoreline_goals={row['scoreline_goal_count']}; "
            f"timeline_goals={row['timeline_goal_count']}"
        )
        issues.append(
            _issue(
                run_id,
                "warning",
                "scoreline_timeline_goal_mismatch",
                "staging",
                "matches",
                (
                    "Scoreline goals differ from timeline goal events. "
                    "Treat as a possible forfeit/admin result or source timeline gap; "
                    "use timeline goals for actual-goals analytics."
                ),
                season=row.get("season"),
                match_id=row.get("match_id"),
                column_name="total_goals",
                issue_value=issue_value,
            )
        )

    return issues


def _validate_staging_tables(
    raw_tables: dict[str, pd.DataFrame],
    staging_tables: dict[str, pd.DataFrame],
    seasons: list[str],
    run_id: str,
) -> pd.DataFrame:
    """Run Phase 2 validation checks and return issue rows."""

    issues: list[dict[str, Any]] = []
    issues.extend(_validate_required_columns(raw_tables, run_id))
    issues.extend(_validate_raw_season_consistency(raw_tables, seasons, run_id))
    issues.extend(_validate_duplicates(staging_tables, run_id))
    issues.extend(_validate_key_fields(staging_tables, run_id))
    issues.extend(_validate_missing_team_player_values(staging_tables, run_id))
    issues.extend(_validate_man_of_match_quality(raw_tables, staging_tables, run_id))
    issues.extend(_validate_scoreline_timeline_goal_consistency(staging_tables, run_id))
    return pd.DataFrame(issues)


def _delete_staging_season_rows(
    connection,
    seasons: list[str],
    progress: ProgressCallback | None = None,
) -> None:
    """Delete requested seasons from staging tables before inserting rebuilt rows."""

    for table_name in STAGING_RELOAD_ORDER:
        if progress:
            progress(f"Deleting old staging.{table_name} rows")
        connection.execute(
            text(f"DELETE FROM staging.{table_name} WHERE season = ANY(:seasons)"),
            {"seasons": seasons},
        )
        if progress:
            progress(f"Deleted old staging.{table_name} rows")


def _write_staging_tables(
    connection,
    staging_tables: dict[str, pd.DataFrame],
    progress: ProgressCallback | None = None,
) -> dict[str, int]:
    """Append cleaned rows into staging tables and return row counts."""

    row_counts: dict[str, int] = {}
    for table_name in STAGING_INSERT_ORDER:
        table_df = staging_tables[table_name]
        row_counts[table_name] = len(table_df)
        if table_df.empty:
            if progress:
                progress(f"Skipping staging.{table_name}: 0 rows")
            continue
        if progress:
            progress(f"Writing staging.{table_name}: {len(table_df)} rows")
        table_df.to_sql(
            table_name,
            connection,
            schema="staging",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )
        if progress:
            progress(f"Wrote staging.{table_name}: {len(table_df)} rows")
    return row_counts


def _write_validation_issues(
    connection,
    issues_df: pd.DataFrame,
    progress: ProgressCallback | None = None,
) -> dict[str, int]:
    """Append validation issues and summarize counts by severity."""

    if issues_df.empty:
        if progress:
            progress("No validation issues to write")
        return {}
    if progress:
        progress(f"Writing staging.validation_issues: {len(issues_df)} rows")
    issues_df.to_sql(
        "validation_issues",
        connection,
        schema="staging",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )
    if progress:
        progress(f"Wrote staging.validation_issues: {len(issues_df)} rows")
    return issues_df["severity"].value_counts().sort_index().to_dict()


def _write_validation_run(
    connection,
    run_id: str,
    seasons: list[str],
    row_counts: dict[str, int],
    issue_counts: dict[str, int],
    progress: ProgressCallback | None = None,
) -> None:
    """Record every staging build, including runs with no validation issues."""

    if progress:
        progress("Recording staging.validation_runs row")
    connection.execute(
        text(
            """
            INSERT INTO staging.validation_runs (run_id, seasons, row_counts, issue_counts)
            VALUES (:run_id, :seasons, CAST(:row_counts AS JSONB), CAST(:issue_counts AS JSONB))
            ON CONFLICT (run_id) DO UPDATE
            SET seasons = EXCLUDED.seasons,
                row_counts = EXCLUDED.row_counts,
                issue_counts = EXCLUDED.issue_counts,
                completed_at = NOW();
            """
        ),
        {
            "run_id": run_id,
            "seasons": ", ".join(seasons),
            "row_counts": dumps(row_counts),
            "issue_counts": dumps(issue_counts),
        },
    )
    if progress:
        progress("Recorded staging.validation_runs row")


def _has_error_level_issues(issues_df: pd.DataFrame) -> bool:
    """Return whether validation found issues that should block staging writes."""

    if issues_df.empty or "severity" not in issues_df.columns:
        return False
    return bool((issues_df["severity"] == "error").any())


def _configure_staging_session(connection, progress: ProgressCallback | None = None) -> None:
    """Set database timeouts so hosted rebuilds fail clearly instead of hanging.

    `lock_timeout` protects against waiting forever behind another database
    session. `statement_timeout` keeps a single slow SQL statement inside the
    GitHub Actions job timeout so the real failure can reach the logs.
    """

    if progress:
        progress("Configuring database statement and lock timeouts")
    connection.execute(text("SET LOCAL lock_timeout = '30s';"))
    connection.execute(text("SET LOCAL statement_timeout = '20min';"))


def build_staging_from_raw(
    seasons: list[str] | None = None,
    settings: DatabaseSettings | None = None,
    progress: ProgressCallback | None = None,
) -> StagingBuildResult:
    """Rebuild Phase 2 staging tables from Postgres raw tables.

    Parameters
    ----------
    seasons : list[str] | None, optional
        Season keys to rebuild. If omitted, the pipeline uses all discovered
        raw season folders.
    settings : DatabaseSettings | None, optional
        Preloaded database settings.
    progress : Callable[[str], None] | None, optional
        Callback used by scripts and automation to expose long-running rebuild
        stages in logs.

    Returns
    -------
    StagingBuildResult
        Rebuild run ID, row counts, and validation issue counts.
    """

    run_id = f"staging-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    if progress:
        progress(f"Created staging run_id={run_id}")
        progress("Creating SQLAlchemy engine")
    engine = create_sqlalchemy_engine(settings=settings)
    validation_error: StagingValidationError | None = None

    with engine.begin() as connection:
        _configure_staging_session(connection, progress)
        if progress:
            progress("Resolving target seasons")
        season_names = resolve_seasons(seasons) if seasons else _discover_raw_database_seasons(connection)
        if progress:
            progress(f"Target seasons: {', '.join(season_names)}")
        raw_tables = _read_raw_tables(connection, season_names, progress)
        if progress:
            progress("Transforming raw tables into staging tables")
        staging_tables = _build_staging_tables(raw_tables)
        if progress:
            for table_name, table_df in staging_tables.items():
                progress(f"Prepared staging.{table_name}: {len(table_df)} rows")
            progress("Running staging validation checks")
        validation_issues = _validate_staging_tables(raw_tables, staging_tables, season_names, run_id)
        if progress:
            progress(f"Prepared validation issues: {len(validation_issues)} rows")

        if _has_error_level_issues(validation_issues):
            if progress:
                progress("Validation found error-level issues; recording evidence before staging writes")
            row_counts = {table_name: 0 for table_name in STAGING_INSERT_ORDER}
            issue_counts = _write_validation_issues(connection, validation_issues, progress)
            _write_validation_run(connection, run_id, season_names, row_counts, issue_counts, progress)
            validation_error = StagingValidationError(
                run_id=run_id,
                seasons=season_names,
                issue_counts=issue_counts,
            )
            if progress:
                progress("Skipping staging table writes because validation errors were recorded")
        else:
            _delete_staging_season_rows(connection, season_names, progress)
            row_counts = _write_staging_tables(connection, staging_tables, progress)
            issue_counts = _write_validation_issues(connection, validation_issues, progress)
            _write_validation_run(connection, run_id, season_names, row_counts, issue_counts, progress)

    if progress:
        progress("Disposing SQLAlchemy engine")
    engine.dispose()

    if validation_error is not None:
        raise validation_error

    return StagingBuildResult(
        run_id=run_id,
        seasons=season_names,
        row_counts=row_counts,
        issue_counts=issue_counts,
    )
