"""Summarize staging row counts and validation issues.

Usage examples
--------------
python scripts/data_platform/verify_staging_outputs.py
python scripts/data_platform/verify_staging_outputs.py --season 2025-26
python scripts/data_platform/verify_staging_outputs.py --run-id staging-20260506T180815Z-069def2e
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from psycopg import sql

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import season_key
from src.db.connection import get_psycopg_connection


STAGING_TABLES = ("matches", "events", "lineups", "staff", "officials", "stats")


def parse_args() -> argparse.Namespace:
    """Parse command-line options for staging verification."""

    parser = argparse.ArgumentParser(
        description="Summarize Postgres staging tables and validation issues."
    )
    parser.add_argument(
        "--season",
        action="append",
        dest="seasons",
        help="Season to summarize, for example 2025-26. Repeat the flag for multiple seasons.",
    )
    parser.add_argument(
        "--run-id",
        help="Validation run ID to inspect. If omitted, the latest run is used.",
    )
    return parser.parse_args()


def _resolve_latest_run_id(cursor) -> str | None:
    """Return the most recent validation run ID, if any run has been logged."""

    cursor.execute(
        """
        SELECT run_id
        FROM staging.validation_runs
        ORDER BY completed_at DESC
        LIMIT 1;
        """
    )
    row = cursor.fetchone()
    return None if row is None else str(row[0])


def _print_row_counts(cursor, seasons: list[str] | None) -> None:
    """Print staging row counts by table and season."""

    print("\nStaging row counts:")
    for table_name in STAGING_TABLES:
        if seasons:
            cursor.execute(
                sql.SQL(
                    """
                    SELECT season, COUNT(*)
                    FROM staging.{table_name}
                    WHERE season = ANY(%s)
                    GROUP BY season
                    ORDER BY season;
                    """
                ).format(table_name=sql.Identifier(table_name)),
                (seasons,),
            )
        else:
            cursor.execute(
                sql.SQL(
                    """
                    SELECT season, COUNT(*)
                    FROM staging.{table_name}
                    GROUP BY season
                    ORDER BY season;
                    """
                ).format(table_name=sql.Identifier(table_name))
            )

        rows = cursor.fetchall()
        if not rows:
            print(f"  staging.{table_name}: 0 rows")
            continue
        for season, row_count in rows:
            print(f"  staging.{table_name:<10} {season}: {row_count}")


def _print_event_type_counts(cursor, seasons: list[str] | None) -> None:
    """Print event counts by event type for sync and dashboard sanity checks."""

    print("\nEvent type counts:")
    if seasons:
        cursor.execute(
            """
            SELECT season, COALESCE(event_type, 'other') AS event_type, COUNT(*)
            FROM staging.events
            WHERE season = ANY(%s)
            GROUP BY season, COALESCE(event_type, 'other')
            ORDER BY season, event_type;
            """,
            (seasons,),
        )
    else:
        cursor.execute(
            """
            SELECT season, COALESCE(event_type, 'other') AS event_type, COUNT(*)
            FROM staging.events
            GROUP BY season, COALESCE(event_type, 'other')
            ORDER BY season, event_type;
            """
        )

    rows = cursor.fetchall()
    if not rows:
        print("  no staging.events rows")
        return
    for season, event_type, row_count in rows:
        print(f"  {season:<8} {event_type:<16} {row_count}")


def _print_validation_summary(cursor, run_id: str | None) -> int:
    """Print validation issue counts and return the number of error issues."""

    if run_id is None:
        print("\nValidation issues: none logged yet.")
        return 0

    cursor.execute(
        """
        SELECT severity, check_name, table_name, COUNT(*)
        FROM staging.validation_issues
        WHERE run_id = %s
        GROUP BY severity, check_name, table_name
        ORDER BY severity, check_name, table_name;
        """,
        (run_id,),
    )
    rows = cursor.fetchall()
    print(f"\nValidation summary for run_id={run_id}:")
    if not rows:
        print("  no issues")
        return 0

    error_count = 0
    for severity, check_name, table_name, issue_count in rows:
        print(f"  {severity:<7} {check_name:<28} staging.{table_name:<10} {issue_count}")
        if severity == "error":
            error_count += int(issue_count)

    return error_count


def main() -> None:
    """Print staging verification output and fail if error-level issues exist."""

    args = parse_args()
    seasons = [season_key(season) for season in args.seasons] if args.seasons else None

    print("UPL Match Intelligence - Verify Staging Outputs")

    with get_psycopg_connection() as connection:
        with connection.cursor() as cursor:
            _print_row_counts(cursor, seasons)
            _print_event_type_counts(cursor, seasons)
            run_id = args.run_id or _resolve_latest_run_id(cursor)
            error_count = _print_validation_summary(cursor, run_id)

    if error_count:
        print("\n[error] Validation logged error-level issues. Inspect staging.validation_issues.")
        raise SystemExit(1)

    print("\n[ok] Staging verification finished without error-level validation issues.")


if __name__ == "__main__":
    main()
