"""Load season-scoped raw UPL CSV outputs into Postgres.

Usage examples
--------------
python scripts/data_platform/load_raw_to_postgres.py
python scripts/data_platform/load_raw_to_postgres.py --season 2025-26
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
    return parser.parse_args()


def main() -> None:
    """Run idempotent raw-table ingestion and print row counts."""

    args = parse_args()
    target_seasons = args.seasons or discover_available_seasons()

    print("UPL Match Intelligence - Load Raw CSVs To Postgres")
    print(f"Target seasons: {', '.join(target_seasons)}")

    load_counts = load_raw_seasons_to_postgres(seasons=args.seasons)

    print("\n[ok] Raw ingestion finished.")
    for season, table_counts in load_counts.items():
        print(f"  Season {season}:")
        for table_name, row_count in table_counts.items():
            print(f"    {table_name}: {row_count} in-season rows processed")

    print("\n[ok] Re-running this command is safe because each table uses upserts.")
    print("[ok] Rows whose `season` value does not match the folder season are skipped.")


if __name__ == "__main__":
    main()
