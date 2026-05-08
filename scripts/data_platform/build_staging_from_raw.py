"""Build cleaned staging tables from Postgres raw tables.

Usage examples
--------------
python scripts/data_platform/build_staging_from_raw.py
python scripts/data_platform/build_staging_from_raw.py --season 2025-26
python scripts/data_platform/build_staging_from_raw.py --season 2024-25 --season 2025-26
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.staging_loader import build_staging_from_raw


def parse_args() -> argparse.Namespace:
    """Parse command-line options for the staging build."""

    parser = argparse.ArgumentParser(
        description="Rebuild Postgres staging tables from Postgres raw tables."
    )
    parser.add_argument(
        "--season",
        action="append",
        dest="seasons",
        help="Season to rebuild, for example 2025-26. Repeat the flag for multiple seasons.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the repeatable raw-to-staging pipeline and print a summary."""

    args = parse_args()
    result = build_staging_from_raw(seasons=args.seasons)

    print("UPL Match Intelligence - Build Staging From Raw Postgres Tables")
    print(f"Run ID: {result.run_id}")
    print(f"Target seasons: {', '.join(result.seasons)}")

    print("\n[ok] Staging rebuild finished.")
    for table_name, row_count in result.row_counts.items():
        print(f"  staging.{table_name}: {row_count} rows")

    if result.issue_counts:
        print("\nValidation issues logged to staging.validation_issues:")
        for severity, issue_count in result.issue_counts.items():
            print(f"  {severity}: {issue_count}")
        print("\nReview issues with:")
        print(
            "  SELECT severity, check_name, table_name, COUNT(*) "
            "FROM staging.validation_issues "
            f"WHERE run_id = '{result.run_id}' "
            "GROUP BY severity, check_name, table_name "
            "ORDER BY severity, check_name, table_name;"
        )
    else:
        print("\n[ok] No validation issues were logged for this run.")

    print("\n[ok] Re-running this command is safe for the same season slice.")


if __name__ == "__main__":
    main()
