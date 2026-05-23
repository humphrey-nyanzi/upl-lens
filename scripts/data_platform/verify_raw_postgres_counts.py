"""Compare raw CSV row counts to Postgres raw-table row counts.

Usage examples
--------------
python scripts/data_platform/verify_raw_postgres_counts.py
python scripts/data_platform/verify_raw_postgres_counts.py --season 2025-26
python scripts/data_platform/verify_raw_postgres_counts.py --season 2024-25 --season 2025-26
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import season_key
from src.db.connection import get_psycopg_connection
from src.db.raw_loader import (
    discover_available_seasons,
    resolve_seasons,
    row_matches_expected_season,
    season_table_paths,
)


RAW_TABLES = (
    "matches",
    "events",
    "lineups",
    "staff",
    "officials",
    "stats",
    "failed_matches",
)


def parse_args() -> argparse.Namespace:
    """Parse command-line options for raw count verification."""

    parser = argparse.ArgumentParser(
        description="Compare season CSV row counts to Postgres raw-table row counts."
    )
    parser.add_argument(
        "--season",
        action="append",
        dest="seasons",
        help="Season to verify, for example 2025-26. Repeat the flag to verify multiple seasons.",
    )
    return parser.parse_args()


def _count_csv_rows(csv_path: Path, expected_season: str) -> tuple[int, int]:
    """Count valid and cross-season rows in one CSV file.

    Returns
    -------
    tuple[int, int]
        `(valid_rows, contaminated_rows)` for the target season folder.
    """

    valid_rows = 0
    contaminated_rows = 0
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row_matches_expected_season(row, expected_season):
                valid_rows += 1
            else:
                contaminated_rows += 1
    return valid_rows, contaminated_rows


def _csv_counts_by_season(seasons: list[str]) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]]]:
    """Return valid and contaminated CSV row counts for each season and table."""

    valid_counts: dict[str, dict[str, int]] = {}
    contaminated_counts: dict[str, dict[str, int]] = {}
    for season in seasons:
        table_counts: dict[str, int] = {}
        spill_counts: dict[str, int] = {}
        for table_name, csv_path in season_table_paths(season).items():
            valid_rows, contaminated_rows = _count_csv_rows(csv_path, season)
            table_counts[table_name] = valid_rows
            spill_counts[table_name] = contaminated_rows
        valid_counts[season] = table_counts
        contaminated_counts[season] = spill_counts
    return valid_counts, contaminated_counts


def _database_counts_by_season(seasons: list[str]) -> dict[str, dict[str, int]]:
    """Return Postgres row counts normalized to season-folder keys.

    The raw tables preserve the scraped season text. That means a season might
    appear as `2025/26` in most tables and `2025-26` in `failed_matches`.
    Normalizing both to `2025_26` keeps the verification stable.
    """

    counts = {
        season: {table_name: 0 for table_name in RAW_TABLES}
        for season in seasons
    }

    with get_psycopg_connection() as connection:
        with connection.cursor() as cursor:
            for table_name in RAW_TABLES:
                cursor.execute(
                    f"SELECT season, COUNT(*) FROM raw.{table_name} GROUP BY season;"
                )
                for db_season, row_count in cursor.fetchall():
                    normalized_season = season_key(str(db_season))
                    if normalized_season in counts:
                        counts[normalized_season][table_name] = int(row_count)

    return counts


def _print_results(
    seasons: list[str],
    csv_counts: dict[str, dict[str, int]],
    contaminated_counts: dict[str, dict[str, int]],
    database_counts: dict[str, dict[str, int]],
) -> bool:
    """Print a comparison table and return whether loaded counts match.

    Cross-season spill rows are reported as warnings, not failures. The raw
    loader intentionally skips those rows, so the unsafe condition is a mismatch
    between valid in-season CSV rows and rows loaded into Postgres.
    """

    all_match = True
    found_spill_rows = False

    for season in seasons:
        print(f"\nSeason {season}:")
        for table_name in RAW_TABLES:
            csv_count = csv_counts[season][table_name]
            contaminated_count = contaminated_counts[season][table_name]
            db_count = database_counts[season][table_name]
            status = "ok" if csv_count == db_count else "mismatch"
            if contaminated_count:
                found_spill_rows = True
            print(
                f"  {table_name:<14} csv_valid={csv_count:<6} db={db_count:<6} "
                f"spill={contaminated_count:<4} status={status}"
            )
            if csv_count != db_count:
                all_match = False

    if found_spill_rows:
        print(
            "\n[warning] Some season folders contain cross-season spill rows. "
            "The raw loader skipped them; review only if the spill pattern looks unexpected."
        )

    return all_match


def main() -> None:
    """Run the CSV-versus-Postgres row-count verification."""

    args = parse_args()
    target_seasons = resolve_seasons(args.seasons) if args.seasons else discover_available_seasons()

    print("UPL Match Intelligence - Verify Raw CSV Counts Against Postgres")
    print(f"Target seasons: {', '.join(target_seasons)}")

    csv_counts, contaminated_counts = _csv_counts_by_season(target_seasons)
    database_counts = _database_counts_by_season(target_seasons)
    all_match = _print_results(target_seasons, csv_counts, contaminated_counts, database_counts)

    if all_match:
        print("\n[ok] Valid in-season CSV counts match the Postgres raw tables.")
        return

    print("\n[error] One or more raw tables have count mismatches.")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
