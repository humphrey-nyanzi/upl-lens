"""Health and database-readiness queries."""

from __future__ import annotations

from typing import Any

from src.db.connection import get_api_psycopg_connection
from src.api.query_services.common import _fetch_one


def get_health_status() -> dict[str, Any]:
    """Return API and database health details."""

    with get_api_psycopg_connection() as connection:
        database_row = _fetch_one(
            """
            SELECT
                current_database() AS database_name,
                version() AS postgres_version;
            """,
            connection=connection,
        )
        latest_run = _fetch_one(
            """
            SELECT run_id, completed_at
            FROM staging.validation_runs
            ORDER BY completed_at DESC
            LIMIT 1;
            """,
            connection=connection,
        )

    if database_row is None:
        raise RuntimeError("Postgres health query returned no database details.")

    return {
        "status": "ok",
        "api": "ok",
        "database": "ok",
        "database_name": database_row["database_name"],
        "postgres_version": database_row["postgres_version"],
        "latest_staging_run_id": None if latest_run is None else latest_run["run_id"],
        "latest_staging_completed_at": None if latest_run is None else latest_run["completed_at"],
    }

