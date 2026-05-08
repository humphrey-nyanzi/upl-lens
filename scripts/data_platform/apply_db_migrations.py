"""Apply pending SQL migrations for the local Postgres database.

Usage
-----
python scripts/data_platform/apply_db_migrations.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.migrations import apply_pending_migrations


def main() -> None:
    """Apply pending migrations and print a beginner-friendly summary."""

    print("UPL Match Intelligence - Apply Postgres Migrations")
    results = apply_pending_migrations()

    if not results:
        print("[ok] No migration files were found.")
        return

    for result in results:
        status = "applied" if result.applied else "already applied"
        print(f"[ok] {result.filename}: {status}")


if __name__ == "__main__":
    main()
