"""Load season-scoped raw UPL CSV outputs into Postgres.

Usage examples
--------------
python scripts/data_platform/load_raw_to_postgres.py --season 2025-26
python scripts/data_platform/load_raw_to_postgres.py --season 2025-26 --full-rebuild
python scripts/data_platform/load_raw_to_postgres.py --season 2024-25 --season 2025-26
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.raw_loader import discover_available_seasons, load_raw_seasons_to_postgres


def parse_args() -> argparse.Namespace:
    """Parse command-line options for raw ingestion."""

    parser = argparse.ArgumentParser(
        description="Load raw UPL season CSV files into the Postgres raw schema."
    )
    parser.add_argument(
        "--season",
        action="append",
        dest="seasons",
        help="Season to load, for example 2025-26. Repeat the flag to load multiple seasons.",
    )
    parser.add_argument(
        "--full-rebuild",
        action="store_true",
        help=(
            "Admin/backfill only: delete and reload the complete selected season. "
            "Without this flag, loading uses the scraper match-level refresh plan."
        ),
    )
    parser.add_argument(
        "--allow-unsafe-season-reload",
        action="store_true",
        help=(
            "Admin recovery only: permit empty or low-confidence CSV input to "
            "delete/reload hosted raw season rows. Do not use for routine refreshes."
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Run idempotent raw-table ingestion and print row counts."""

    args = parse_args()
    target_seasons = args.seasons or discover_available_seasons()

    print("UPL Lens - Load Raw CSVs To Postgres")
    print(f"Target seasons: {', '.join(target_seasons)}")

    load_counts = load_raw_seasons_to_postgres(
        seasons=args.seasons,
        full_rebuild=args.full_rebuild,
        allow_unsafe_season_reload=args.allow_unsafe_season_reload,
    )

    print("\n[ok] Raw ingestion finished.")
    for season, table_counts in load_counts.items():
        print(f"  Season {season}:")
        for table_name, row_count in table_counts.items():
            print(f"    {table_name}: {row_count} in-season rows processed")

    if args.full_rebuild:
        print("\n[ok] Admin full rebuild completed for the selected season slice.")
    else:
        print(
            "\n[ok] Routine load only processed match IDs from the scraper refresh plan."
        )
    print(
        "[ok] Rows whose `season` value does not match the folder season are skipped."
    )


if __name__ == "__main__":
    main()
