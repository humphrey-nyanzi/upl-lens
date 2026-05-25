"""Postgres-backed change detection for incremental scraping."""

from __future__ import annotations

from typing import Any

from src.config import season_key
from src.db.connection import get_psycopg_connection
from src.scraping.upl.constants import RAW_DATABASE_TABLE_COLUMNS, TABLE_NAMES
from src.scraping.upl.models import PostgresScrapePlan


def _query_raw_table_rows(connection, table_name: str, season: str) -> list[dict[str, Any]]:
    """Read existing raw rows for one season from Postgres.

    The scraper CSVs do not include loader-only columns such as `source_file`
    or `ingested_at`, so this query exports only the columns the scraper itself
    writes. That lets skipped DB rows be preserved in the next raw CSV output.
    """

    columns = RAW_DATABASE_TABLE_COLUMNS[table_name]
    column_sql = ", ".join(columns)
    query = f"""
        SELECT {column_sql}
        FROM raw.{table_name}
        WHERE REPLACE(REPLACE(season, '-', '_'), '/', '_') = %s
        ORDER BY match_id;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (season_key(season),))
        column_names = [column.name for column in cursor.description]
        return [
            dict(zip(column_names, row, strict=True))
            for row in cursor.fetchall()
        ]


def _query_raw_match_refresh_state(connection, season: str) -> list[dict[str, Any]]:
    """Return match-level state used to choose what should be re-scraped."""

    query = """
        SELECT
            match_url,
            match_id,
            date,
            match_day,
            home_score,
            away_score,
            ingested_at
        FROM raw.matches
        WHERE REPLACE(REPLACE(season, '-', '_'), '/', '_') = %s
        ORDER BY match_day NULLS LAST, date NULLS LAST, match_id;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (season_key(season),))
        column_names = [column.name for column in cursor.description]
        return [
            dict(zip(column_names, row, strict=True))
            for row in cursor.fetchall()
        ]


def _query_failed_match_urls(connection, season: str) -> set[str]:
    """Return match URLs that failed in the previous raw Postgres state."""

    query = """
        SELECT match_url
        FROM raw.failed_matches
        WHERE REPLACE(REPLACE(season, '-', '_'), '/', '_') = %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (season_key(season),))
        return {str(row[0]) for row in cursor.fetchall() if row[0]}


def _load_existing_raw_tables_from_postgres(connection, season: str) -> dict[str, list[dict[str, Any]]]:
    """Export existing raw season rows so skipped matches remain in CSV output."""

    return {
        table_name: _query_raw_table_rows(connection, table_name, season)
        for table_name in TABLE_NAMES
    }


def _filter_existing_tables_to_calendar(
    existing_tables: dict[str, list[dict[str, Any]]],
    match_urls: list[str],
) -> dict[str, list[dict[str, Any]]]:
    """Keep only existing DB rows still present in the current source calendar."""

    calendar_urls = set(match_urls)
    return {
        table_name: [
            row for row in rows
            if row.get("match_url") in calendar_urls
        ]
        for table_name, rows in existing_tables.items()
    }


def _is_complete_match(row: dict[str, Any]) -> bool:
    """Return whether a raw match row looks played enough to skip safely."""

    return row.get("home_score") is not None and row.get("away_score") is not None


def _recent_completed_urls(
    match_rows: list[dict[str, Any]],
    *,
    limit: int,
) -> set[str]:
    """Choose recent completed matches as practical updated-data candidates.

    The UPL source pages do not expose a reliable last-modified field in the
    calendar. Rechecking a small tail of recent completed matches catches late
    lineup, stats, or result corrections without re-fetching the whole season.
    """

    if limit <= 0:
        return set()

    complete_rows = [row for row in match_rows if _is_complete_match(row) and row.get("match_url")]
    recent_rows = sorted(
        complete_rows,
        key=lambda row: (
            row.get("date") or "",
            row.get("match_day") or -1,
            row.get("match_id") or -1,
        ),
        reverse=True,
    )
    return {str(row["match_url"]) for row in recent_rows[:limit]}


def _build_postgres_scrape_plan(
    season: str,
    match_urls: list[str],
    *,
    recent_completed_limit: int,
) -> PostgresScrapePlan:
    """Build a Postgres-backed plan for incremental scraping."""

    with get_psycopg_connection() as connection:
        existing_tables = _filter_existing_tables_to_calendar(
            _load_existing_raw_tables_from_postgres(connection, season),
            match_urls,
        )
        match_rows = _query_raw_match_refresh_state(connection, season)
        failed_match_urls = _query_failed_match_urls(connection, season)
    complete_urls = {
        str(row["match_url"])
        for row in match_rows
        if row.get("match_url") and _is_complete_match(row)
    }
    incomplete_urls = {
        str(row["match_url"])
        for row in match_rows
        if row.get("match_url") and not _is_complete_match(row)
    }
    recent_urls = _recent_completed_urls(match_rows, limit=recent_completed_limit)
    existing_urls = complete_urls.union(incomplete_urls)
    pending_reasons: dict[str, str] = {}

    for url in match_urls:
        if url in failed_match_urls:
            pending_reasons[url] = "previously_failed"
        elif url not in existing_urls:
            pending_reasons[url] = "missing_from_postgres"
        elif url in incomplete_urls:
            pending_reasons[url] = "unplayed_or_incomplete"
        elif url in recent_urls:
            pending_reasons[url] = "recent_completed_refresh"

    return PostgresScrapePlan(
        existing_tables=existing_tables,
        skip_urls=set(match_urls).difference(pending_reasons),
        pending_reasons=pending_reasons,
        complete_match_count=len(complete_urls),
        incomplete_match_count=len(incomplete_urls),
        failed_match_count=len(failed_match_urls),
        recent_refresh_count=len(recent_urls),
    )

