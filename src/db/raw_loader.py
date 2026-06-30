"""Load season-scoped raw CSV outputs into Postgres raw tables.

The loader is intentionally conservative:

- it only targets the `raw` schema in Phase 1
- it reads the scraper CSVs as the source of truth
- it uses upserts so rerunning the same season does not duplicate rows
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from psycopg import sql

from src.config import (
    MIN_CALENDAR_MATCH_LINKS,
    MIN_RAW_SEASON_MATCH_RATIO,
    MIN_RAW_SEASON_MATCH_ROWS,
    MIN_RAW_SEASON_SOURCE_RATIO,
    RAW_TABLE_FILE_PREFIXES,
    TRUSTED_SEASON_CALENDAR_BASELINES,
    UPL_CALENDAR_URL,
    raw_season_dir,
    raw_season_failed_matches_file,
    raw_season_file,
    raw_season_load_safety_file,
    raw_season_source_preflight_file,
    season_key,
)
from src.db.connection import get_psycopg_connection
from src.db.settings import DatabaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def _to_int(value: str) -> int | None:
    """Convert a CSV value to an integer when possible.

    The historical raw files contain a small number of visually similar values
    such as `o` instead of `0`, and em dashes where a numeric split was not
    captured. We normalize those specific cases so existing season CSVs can be
    loaded without manual repair, while still raising on truly unexpected text.
    """

    text = value.strip()
    if text == "":
        return None
    if text in {"—", "–", "-"}:
        return None
    if text in {"o", "O"}:
        return 0
    return int(text)


def _to_bool(value: str) -> bool | None:
    """Convert a scraper boolean string into a Python boolean."""

    text = value.strip().lower()
    if text == "":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError(f"Cannot convert boolean value: {value!r}")


def _to_timestamp(value: str) -> datetime | None:
    """Convert an ISO timestamp string to a timezone-aware datetime."""

    text = value.strip()
    if text == "":
        return None
    return datetime.fromisoformat(text)


def _clean_text(value: str) -> str | None:
    """Normalize empty strings to None for nullable database columns."""

    text = value.strip()
    return text or None


def _fingerprint(*parts: Any) -> str:
    """Build a deterministic row key from stable identifying fields.

    The child raw tables do not always have one natural single-column key in the
    CSV files. A stable fingerprint gives us a repeatable conflict target for
    idempotent upserts.
    """

    normalized_parts = ["" if part is None else str(part).strip() for part in parts]
    joined = "||".join(normalized_parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RawSeasonSafetyReport:
    """Counts and source evidence used to authorize a raw season reload."""

    season: str
    source_url: str
    incoming_match_rows: int
    incoming_distinct_match_urls: int
    duplicate_match_rows: int
    existing_match_rows: int
    missing_existing_match_url_count: int
    missing_existing_match_url_sample: tuple[str, ...]
    expected_match_rows: int
    minimum_match_rows: int
    minimum_source_ratio: float
    minimum_existing_ratio: float
    source_contract_valid: bool
    incoming_urls_match_source: bool
    override_enabled: bool

    @property
    def minimum_source_rows(self) -> int:
        """Return the season-aware floor derived from the validated calendar."""

        return math.ceil(self.expected_match_rows * self.minimum_source_ratio)


class RawSeasonLoadSafetyError(RuntimeError):
    """Raised before a raw season reload would delete trustworthy hosted rows."""

    def __init__(self, report: RawSeasonSafetyReport, reason: str) -> None:
        self.report = report
        self.reason = reason
        super().__init__(
            "Unsafe raw season reload blocked for "
            f"{report.season}: {reason} "
            f"(source={report.source_url}, incoming rows={report.incoming_match_rows}, "
            f"distinct match URLs={report.incoming_distinct_match_urls}, "
            f"duplicate match rows={report.duplicate_match_rows}, "
            f"existing raw matches={report.existing_match_rows}, "
            f"missing existing URLs={report.missing_existing_match_url_count}, "
            f"expected matches={report.expected_match_rows}, "
            f"minimum source matches={report.minimum_source_rows}, "
            f"minimum fixed matches={report.minimum_match_rows}, "
            f"minimum existing ratio={report.minimum_existing_ratio:.0%}, "
            f"override enabled={report.override_enabled})."
        )


@dataclass(frozen=True)
class RawTableConfig:
    """Configuration for loading one raw CSV file into one raw database table."""

    table_name: str
    database_columns: list[str]
    conflict_columns: list[str]
    season_column: str = "season"


RAW_TABLE_CONFIGS: dict[str, RawTableConfig] = {
    "matches": RawTableConfig(
        table_name="matches",
        database_columns=[
            "match_id",
            "match_url",
            "source_page_title",
            "date",
            "time",
            "league",
            "season",
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
            "home_first_half_goals",
            "away_first_half_goals",
            "home_second_half_goals",
            "away_second_half_goals",
            "has_timeline",
            "has_lineups",
            "has_officials",
            "has_stats",
            "source_file",
        ],
        conflict_columns=["match_id"],
    ),
    "events": RawTableConfig(
        table_name="events",
        database_columns=[
            "event_row_key",
            "match_id",
            "match_url",
            "date",
            "time",
            "league",
            "season",
            "match_day",
            "home_team",
            "away_team",
            "event_index",
            "event_type",
            "event_minute",
            "team_side",
            "player_name",
            "player_url",
            "goal_type",
            "sub_out_player_name",
            "sub_out_player_url",
            "sub_in_player_name",
            "sub_in_player_url",
            "source_file",
        ],
        conflict_columns=["event_row_key"],
    ),
    "lineups": RawTableConfig(
        table_name="lineups",
        database_columns=[
            "lineup_row_key",
            "match_id",
            "match_url",
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
            "source_file",
        ],
        conflict_columns=["lineup_row_key"],
    ),
    "staff": RawTableConfig(
        table_name="staff",
        database_columns=[
            "staff_row_key",
            "match_id",
            "match_url",
            "season",
            "match_day",
            "home_team",
            "away_team",
            "team_name",
            "team_side",
            "role",
            "person_name",
            "person_url",
            "source_file",
        ],
        conflict_columns=["staff_row_key"],
    ),
    "officials": RawTableConfig(
        table_name="officials",
        database_columns=[
            "official_row_key",
            "match_id",
            "match_url",
            "season",
            "match_day",
            "home_team",
            "away_team",
            "role",
            "official_name",
            "source_file",
        ],
        conflict_columns=["official_row_key"],
    ),
    "stats": RawTableConfig(
        table_name="stats",
        database_columns=[
            "stat_row_key",
            "match_id",
            "match_url",
            "season",
            "match_day",
            "home_team",
            "away_team",
            "statistic_name",
            "home_value",
            "away_value",
            "source_file",
        ],
        conflict_columns=["stat_row_key"],
    ),
    "failed_matches": RawTableConfig(
        table_name="failed_matches",
        database_columns=[
            "failed_match_row_key",
            "match_url",
            "season",
            "attempt_count",
            "last_error",
            "last_attempt_at_utc",
            "source_file",
        ],
        conflict_columns=["failed_match_row_key"],
    ),
}


def discover_available_seasons() -> list[str]:
    """Return season folder names from `data/raw/` in sorted order."""

    seasons = [
        item.name
        for item in RAW_DIR.iterdir()
        if item.is_dir() and item.name != "Goal_scraper_V1_data"
    ]
    return sorted(seasons)


def resolve_seasons(requested_seasons: list[str] | None) -> list[str]:
    """Normalize requested seasons or fall back to all available season folders."""

    if not requested_seasons:
        return discover_available_seasons()
    return [season_key(season) for season in requested_seasons]


def _read_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    """Read a CSV file into a list of dictionary rows."""

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def row_matches_expected_season(row: dict[str, str], expected_season: str) -> bool:
    """Return whether a CSV row belongs to the season folder being loaded.

    The raw files should be season-scoped. Some historical files currently
    contain leaked rows from `2025/26`, so ingestion and verification need a
    shared rule for what counts as a valid in-folder row.
    """

    row_season = row.get("season", "")
    if row_season is None:
        return False
    return season_key(row_season.strip()) == season_key(expected_season)


def _prepare_match_row(row: dict[str, str], source_file: Path) -> dict[str, Any]:
    """Convert one raw match CSV row into database-ready values."""

    return {
        "match_id": _to_int(row["match_id"]),
        "match_url": _clean_text(row["match_url"]),
        "source_page_title": _clean_text(row["source_page_title"]),
        "date": _clean_text(row["date"]),
        "time": _clean_text(row["time"]),
        "league": _clean_text(row["league"]),
        "season": _clean_text(row["season"]),
        "match_day": _to_int(row["match_day"]),
        "home_team": _clean_text(row["home_team"]),
        "home_team_url": _clean_text(row["home_team_url"]),
        "away_team": _clean_text(row["away_team"]),
        "away_team_url": _clean_text(row["away_team_url"]),
        "ground_name": _clean_text(row["ground_name"]),
        "ground_address": _clean_text(row["ground_address"]),
        "man_of_the_match": _clean_text(row["man_of_the_match"]),
        "man_of_the_match_team": _clean_text(row["man_of_the_match_team"]),
        "home_score": _to_int(row["home_score"]),
        "away_score": _to_int(row["away_score"]),
        "home_first_half_goals": _to_int(row["home_first_half_goals"]),
        "away_first_half_goals": _to_int(row["away_first_half_goals"]),
        "home_second_half_goals": _to_int(row["home_second_half_goals"]),
        "away_second_half_goals": _to_int(row["away_second_half_goals"]),
        "has_timeline": _to_bool(row["has_timeline"]),
        "has_lineups": _to_bool(row["has_lineups"]),
        "has_officials": _to_bool(row["has_officials"]),
        "has_stats": _to_bool(row["has_stats"]),
        "source_file": str(source_file),
    }


def _prepare_event_row(row: dict[str, str], source_file: Path) -> dict[str, Any]:
    """Convert one raw event CSV row into database-ready values."""

    match_id = _to_int(row["match_id"])
    event_index = _to_int(row["event_index"])
    return {
        "event_row_key": _fingerprint(match_id, event_index),
        "match_id": match_id,
        "match_url": _clean_text(row["match_url"]),
        "date": _clean_text(row["date"]),
        "time": _clean_text(row["time"]),
        "league": _clean_text(row["league"]),
        "season": _clean_text(row["season"]),
        "match_day": _to_int(row["match_day"]),
        "home_team": _clean_text(row["home_team"]),
        "away_team": _clean_text(row["away_team"]),
        "event_index": event_index,
        "event_type": _clean_text(row["event_type"]),
        "event_minute": _clean_text(row["event_minute"]),
        "team_side": _clean_text(row["team_side"]),
        "player_name": _clean_text(row["player_name"]),
        "player_url": _clean_text(row["player_url"]),
        "goal_type": _clean_text(row["goal_type"]),
        "sub_out_player_name": _clean_text(row["sub_out_player_name"]),
        "sub_out_player_url": _clean_text(row["sub_out_player_url"]),
        "sub_in_player_name": _clean_text(row["sub_in_player_name"]),
        "sub_in_player_url": _clean_text(row["sub_in_player_url"]),
        "source_file": str(source_file),
    }


def _prepare_lineup_row(row: dict[str, str], source_file: Path) -> dict[str, Any]:
    """Convert one raw lineup CSV row into database-ready values."""

    match_id = _to_int(row["match_id"])
    team_side = _clean_text(row["team_side"])
    squad_role = _clean_text(row["squad_role"])
    shirt_number = _to_int(row["shirt_number"])
    player_name = _clean_text(row["player_name"])
    linked_player_name = _clean_text(row["linked_player_name"])
    swap_badge_type = _clean_text(row["swap_badge_type"])

    return {
        "lineup_row_key": _fingerprint(
            match_id,
            team_side,
            squad_role,
            shirt_number,
            player_name,
            linked_player_name,
            swap_badge_type,
        ),
        "match_id": match_id,
        "match_url": _clean_text(row["match_url"]),
        "season": _clean_text(row["season"]),
        "match_day": _to_int(row["match_day"]),
        "home_team": _clean_text(row["home_team"]),
        "away_team": _clean_text(row["away_team"]),
        "team_name": _clean_text(row["team_name"]),
        "team_side": team_side,
        "squad_role": squad_role,
        "shirt_number": shirt_number,
        "player_name": player_name,
        "player_url": _clean_text(row["player_url"]),
        "player_position": _clean_text(row["player_position"]),
        "is_player_of_match": _to_bool(row["is_player_of_match"]),
        "swap_badge_type": swap_badge_type,
        "linked_player_name": linked_player_name,
        "linked_shirt_number": _to_int(row["linked_shirt_number"]),
        "source_file": str(source_file),
    }


def _prepare_staff_row(row: dict[str, str], source_file: Path) -> dict[str, Any]:
    """Convert one raw staff CSV row into database-ready values."""

    match_id = _to_int(row["match_id"])
    team_side = _clean_text(row["team_side"])
    role = _clean_text(row["role"])
    person_name = _clean_text(row["person_name"])

    return {
        "staff_row_key": _fingerprint(match_id, team_side, role, person_name),
        "match_id": match_id,
        "match_url": _clean_text(row["match_url"]),
        "season": _clean_text(row["season"]),
        "match_day": _to_int(row["match_day"]),
        "home_team": _clean_text(row["home_team"]),
        "away_team": _clean_text(row["away_team"]),
        "team_name": _clean_text(row["team_name"]),
        "team_side": team_side,
        "role": role,
        "person_name": person_name,
        "person_url": _clean_text(row["person_url"]),
        "source_file": str(source_file),
    }


def _prepare_official_row(row: dict[str, str], source_file: Path) -> dict[str, Any]:
    """Convert one raw official CSV row into database-ready values."""

    match_id = _to_int(row["match_id"])
    role = _clean_text(row["role"])
    official_name = _clean_text(row["official_name"])

    return {
        "official_row_key": _fingerprint(match_id, role, official_name),
        "match_id": match_id,
        "match_url": _clean_text(row["match_url"]),
        "season": _clean_text(row["season"]),
        "match_day": _to_int(row["match_day"]),
        "home_team": _clean_text(row["home_team"]),
        "away_team": _clean_text(row["away_team"]),
        "role": role,
        "official_name": official_name,
        "source_file": str(source_file),
    }


def _prepare_stat_row(row: dict[str, str], source_file: Path) -> dict[str, Any]:
    """Convert one raw stat CSV row into database-ready values."""

    match_id = _to_int(row["match_id"])
    statistic_name = _clean_text(row["statistic_name"])

    return {
        "stat_row_key": _fingerprint(match_id, statistic_name),
        "match_id": match_id,
        "match_url": _clean_text(row["match_url"]),
        "season": _clean_text(row["season"]),
        "match_day": _to_int(row["match_day"]),
        "home_team": _clean_text(row["home_team"]),
        "away_team": _clean_text(row["away_team"]),
        "statistic_name": statistic_name,
        "home_value": _clean_text(row["home_value"]),
        "away_value": _clean_text(row["away_value"]),
        "source_file": str(source_file),
    }


def _prepare_failed_match_row(row: dict[str, str], source_file: Path) -> dict[str, Any]:
    """Convert one failed-match CSV row into database-ready values."""

    season = _clean_text(row["season"])
    match_url = _clean_text(row["match_url"])

    return {
        "failed_match_row_key": _fingerprint(season, match_url),
        "match_url": match_url,
        "season": season,
        "attempt_count": _to_int(row["attempt_count"]),
        "last_error": _clean_text(row["last_error"]),
        "last_attempt_at_utc": _to_timestamp(row["last_attempt_at_utc"]),
        "source_file": str(source_file),
    }


ROW_PREPARERS = {
    "matches": _prepare_match_row,
    "events": _prepare_event_row,
    "lineups": _prepare_lineup_row,
    "staff": _prepare_staff_row,
    "officials": _prepare_official_row,
    "stats": _prepare_stat_row,
    "failed_matches": _prepare_failed_match_row,
}


def _build_upsert_statement(config: RawTableConfig) -> sql.SQL:
    """Construct an `INSERT ... ON CONFLICT DO UPDATE` statement."""

    insert_columns = [sql.Identifier(column) for column in config.database_columns]
    placeholders = sql.SQL(", ").join(
        sql.Placeholder(column) for column in config.database_columns
    )

    update_columns = [
        column
        for column in config.database_columns
        if column not in config.conflict_columns
    ]
    update_assignments = sql.SQL(", ").join(
        sql.SQL("{column} = EXCLUDED.{column}").format(column=sql.Identifier(column))
        for column in update_columns
    )

    return sql.SQL("""
        INSERT INTO raw.{table_name} ({columns})
        VALUES ({values})
        ON CONFLICT ({conflict_columns}) DO UPDATE
        SET {update_assignments},
            ingested_at = NOW();
        """).format(
        table_name=sql.Identifier(config.table_name),
        columns=sql.SQL(", ").join(insert_columns),
        values=placeholders,
        conflict_columns=sql.SQL(", ").join(
            sql.Identifier(column) for column in config.conflict_columns
        ),
        update_assignments=update_assignments,
    )


def _season_table_paths(season: str) -> dict[str, Path]:
    """Return the expected CSV path for each raw table in one season folder."""

    return {
        **{
            table_name: raw_season_file(season, table_name)
            for table_name in RAW_TABLE_FILE_PREFIXES
        },
        "failed_matches": raw_season_failed_matches_file(season),
    }


def season_table_paths(season: str) -> dict[str, Path]:
    """Public wrapper that returns the raw CSV paths for one season.

    This is used by verification tooling so both ingestion and validation rely
    on the same season-folder conventions.
    """

    return _season_table_paths(season)


def _upsert_rows(connection, table_key: str, rows: list[dict[str, Any]]) -> int:
    """Upsert a prepared batch of rows into one raw table."""

    if not rows:
        return 0

    config = RAW_TABLE_CONFIGS[table_key]
    statement = _build_upsert_statement(config)

    with connection.cursor() as cursor:
        cursor.executemany(statement, rows)

    return len(rows)


def _read_source_preflight_contract(
    season: str,
) -> tuple[int, str, bool, set[str]]:
    """Validate scraper evidence against the version-controlled season baseline."""

    expected_source_url = UPL_CALENDAR_URL.format(season=season)
    trusted_baseline = TRUSTED_SEASON_CALENDAR_BASELINES.get(season_key(season))
    trusted_expected_rows = (
        int(trusted_baseline["expected_match_count"]) if trusted_baseline else 0
    )
    trusted_minimum_rows = (
        max(
            MIN_CALENDAR_MATCH_LINKS,
            math.ceil(trusted_expected_rows * MIN_RAW_SEASON_SOURCE_RATIO),
        )
        if trusted_expected_rows > 0
        else MIN_CALENDAR_MATCH_LINKS
    )
    report_path = raw_season_source_preflight_file(season)
    if not report_path.exists():
        return trusted_expected_rows, expected_source_url, False, set()

    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        match_urls = payload.get("match_urls")
        reported_expected_rows = int(payload.get("expected_match_count", 0))
        observed_link_count = int(payload.get("observed_link_count", 0))
        reported_minimum_rows = int(payload.get("minimum_link_count", 0))
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return trusted_expected_rows, expected_source_url, False, set()

    source_url = str(payload.get("source_url") or expected_source_url)
    source_urls = set(match_urls) if isinstance(match_urls, list) else set()
    contract_valid = (
        trusted_baseline is not None
        and payload.get("status") == "passed"
        and season_key(str(payload.get("target_season", ""))) == season_key(season)
        and source_url == expected_source_url
        and payload.get("source_structure_valid") is True
        and reported_expected_rows == trusted_expected_rows
        and reported_minimum_rows == trusted_minimum_rows
        and observed_link_count == len(source_urls)
        and observed_link_count >= trusted_minimum_rows
        and str(payload.get("baseline_version")) == str(trusted_baseline["version"])
    )
    return trusted_expected_rows, source_url, contract_valid, source_urls


def _write_raw_load_safety_artifact(
    report: RawSeasonSafetyReport,
    *,
    status: str,
    failure_reason: str | None,
) -> Path:
    """Persist the raw-loader decision before any destructive write begins."""

    report_path = raw_season_load_safety_file(report.season)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": status,
        "failure_reason": failure_reason,
        **asdict(report),
        "minimum_source_rows": report.minimum_source_rows,
        "database_write_stages_skipped": (
            ["raw", "staging", "analytics"] if status == "blocked" else []
        ),
    }
    report_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"[raw-load-safety] Report: {report_path}")
    return report_path


def _existing_season_match_urls(connection, season: str) -> set[str]:
    """Return distinct nonblank hosted match URLs for one normalized season."""

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT BTRIM(match_url)
            FROM raw.matches
            WHERE REPLACE(REPLACE(season, '-', '_'), '/', '_') = %s
              AND NULLIF(BTRIM(match_url), '') IS NOT NULL;
            """,
            (season_key(season),),
        )
        rows = cursor.fetchall()
    return {str(row[0]).strip() for row in rows if row and str(row[0]).strip()}


def _enforce_safe_raw_season_load(
    *,
    season: str,
    source_url: str,
    incoming_match_rows: int,
    incoming_match_urls: set[str],
    duplicate_match_rows: int,
    existing_match_urls: set[str],
    expected_match_rows: int,
    source_contract_valid: bool,
    incoming_urls_match_source: bool,
    allow_unsafe_season_reload: bool,
    minimum_match_rows: int = MIN_RAW_SEASON_MATCH_ROWS,
    minimum_source_ratio: float = MIN_RAW_SEASON_SOURCE_RATIO,
    minimum_existing_ratio: float = MIN_RAW_SEASON_MATCH_RATIO,
) -> RawSeasonSafetyReport:
    """Block unsafe raw loads before any season rows are deleted."""

    missing_existing_urls = sorted(existing_match_urls - incoming_match_urls)
    report = RawSeasonSafetyReport(
        season=season,
        source_url=source_url,
        incoming_match_rows=incoming_match_rows,
        incoming_distinct_match_urls=len(incoming_match_urls),
        duplicate_match_rows=duplicate_match_rows,
        existing_match_rows=len(existing_match_urls),
        missing_existing_match_url_count=len(missing_existing_urls),
        missing_existing_match_url_sample=tuple(missing_existing_urls[:10]),
        expected_match_rows=expected_match_rows,
        minimum_match_rows=minimum_match_rows,
        minimum_source_ratio=minimum_source_ratio,
        minimum_existing_ratio=minimum_existing_ratio,
        source_contract_valid=source_contract_valid,
        incoming_urls_match_source=incoming_urls_match_source,
        override_enabled=allow_unsafe_season_reload,
    )
    if allow_unsafe_season_reload:
        return report

    if not incoming_match_urls:
        raise RawSeasonLoadSafetyError(
            report, "incoming match CSV has no in-season rows"
        )

    if duplicate_match_rows > 0:
        raise RawSeasonLoadSafetyError(
            report,
            "incoming match CSV contains duplicate match records",
        )

    if not source_contract_valid:
        raise RawSeasonLoadSafetyError(
            report,
            "source evidence does not match the trusted season baseline",
        )

    if not incoming_urls_match_source:
        raise RawSeasonLoadSafetyError(
            report,
            "incoming match URLs are not contained in the validated source calendar",
        )

    if len(incoming_match_urls) < minimum_match_rows:
        raise RawSeasonLoadSafetyError(
            report,
            "incoming match CSV is below the minimum trusted match count",
        )

    if len(incoming_match_urls) < report.minimum_source_rows:
        raise RawSeasonLoadSafetyError(
            report,
            "incoming distinct match URLs are below the trusted season baseline",
        )

    if missing_existing_urls:
        raise RawSeasonLoadSafetyError(
            report,
            "incoming match set would remove or substitute existing hosted matches",
        )

    if existing_match_urls:
        minimum_from_existing = math.ceil(
            len(existing_match_urls) * minimum_existing_ratio
        )
        if len(incoming_match_urls) < minimum_from_existing:
            raise RawSeasonLoadSafetyError(
                report,
                "incoming match CSV is much smaller than existing hosted raw data",
            )

    return report


def _delete_existing_season_rows(connection, table_key: str, season: str) -> None:
    """Delete one season slice from a raw table before reloading it.

    This keeps ingestion idempotent in a stronger sense than plain upserts:
    rerunning a season removes stale rows that may have been loaded earlier from
    contaminated CSV files, then inserts the current valid in-season rows.
    """

    config = RAW_TABLE_CONFIGS[table_key]
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("""
                DELETE FROM raw.{table_name}
                WHERE REPLACE(REPLACE({season_column}, '-', '_'), '/', '_') = %s;
                """).format(
                table_name=sql.Identifier(config.table_name),
                season_column=sql.Identifier(config.season_column),
            ),
            (season_key(season),),
        )


def load_raw_seasons_to_postgres(
    seasons: list[str] | None = None,
    settings: DatabaseSettings | None = None,
    *,
    allow_unsafe_season_reload: bool = False,
) -> dict[str, dict[str, int]]:
    """Load one or more season folders into the Postgres `raw` schema.

    Parameters
    ----------
    seasons : list[str] | None, optional
        Seasons such as `["2025-26", "2024_25"]`. If omitted, all detected
        season folders are loaded.
    settings : DatabaseSettings | None, optional
        Preloaded database settings object.
    allow_unsafe_season_reload : bool, optional
        Admin recovery override that permits empty or low-confidence season
        CSVs to delete/reload hosted raw rows. Routine automation should leave
        this disabled.

    Returns
    -------
    dict[str, dict[str, int]]
        Row counts loaded per season and per table.
    """

    season_names = resolve_seasons(seasons)
    season_counts: dict[str, dict[str, int]] = {}

    with get_psycopg_connection(settings=settings) as connection:
        for season in season_names:
            season_dir = raw_season_dir(season)
            if not season_dir.exists():
                raise FileNotFoundError(f"Season folder not found: {season_dir}")

            table_paths = _season_table_paths(season)
            match_rows = _read_csv_rows(table_paths["matches"])
            matching_match_rows = [
                row for row in match_rows if row_matches_expected_season(row, season)
            ]
            expected_rows, source_url, contract_valid, source_urls = (
                _read_source_preflight_contract(season)
            )
            incoming_url_values = [
                str(row.get("match_url", "")).strip()
                for row in matching_match_rows
                if str(row.get("match_url", "")).strip()
            ]
            incoming_urls = set(incoming_url_values)
            duplicate_match_rows = len(incoming_url_values) - len(incoming_urls)
            incoming_urls_match_source = (
                bool(source_urls) and incoming_urls <= source_urls
            )
            existing_urls = _existing_season_match_urls(connection, season)
            try:
                safety_report = _enforce_safe_raw_season_load(
                    season=season,
                    source_url=source_url,
                    incoming_match_rows=len(matching_match_rows),
                    incoming_match_urls=incoming_urls,
                    duplicate_match_rows=duplicate_match_rows,
                    existing_match_urls=existing_urls,
                    expected_match_rows=expected_rows,
                    source_contract_valid=contract_valid,
                    incoming_urls_match_source=incoming_urls_match_source,
                    allow_unsafe_season_reload=allow_unsafe_season_reload,
                )
            except RawSeasonLoadSafetyError as error:
                _write_raw_load_safety_artifact(
                    error.report,
                    status="blocked",
                    failure_reason=error.reason,
                )
                raise

            _write_raw_load_safety_artifact(
                safety_report,
                status="override" if allow_unsafe_season_reload else "passed",
                failure_reason=None,
            )
            print(
                "[ok] Raw season safety check passed: "
                f"season={season} incoming_rows={safety_report.incoming_match_rows} "
                f"distinct_match_urls={safety_report.incoming_distinct_match_urls} "
                f"expected_matches={safety_report.expected_match_rows} "
                f"existing_matches={safety_report.existing_match_rows} "
                f"override_enabled={safety_report.override_enabled}"
            )

            table_counts: dict[str, int] = {}
            for table_key, csv_path in table_paths.items():
                rows = (
                    match_rows if table_key == "matches" else _read_csv_rows(csv_path)
                )
                matching_rows = [
                    row for row in rows if row_matches_expected_season(row, season)
                ]
                _delete_existing_season_rows(connection, table_key, season)
                prepared_rows = [
                    ROW_PREPARERS[table_key](row, csv_path) for row in matching_rows
                ]
                table_counts[table_key] = _upsert_rows(
                    connection, table_key, prepared_rows
                )

            season_counts[season] = table_counts

        connection.commit()

    return season_counts
