"""Database write helpers for staging tables and validation evidence."""

from __future__ import annotations

from json import dumps

import pandas as pd
from sqlalchemy import text

from src.db.staging.constants import STAGING_INSERT_ORDER, STAGING_RELOAD_ORDER
from src.db.staging.models import ProgressCallback


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

