"""Database reads used by the staging rebuild."""

from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from src.db.staging.constants import RAW_TABLES
from src.db.staging.models import ProgressCallback


def _read_raw_table(connection, table_name: str, seasons: list[str]) -> pd.DataFrame:
    """Read a season slice from one raw table."""

    if table_name not in RAW_TABLES:
        raise ValueError(f"Unsupported raw table: {table_name}")

    query = text(
        f"""
        SELECT *
        FROM raw.{table_name}
        WHERE REPLACE(REPLACE(season, '-', '_'), '/', '_') = ANY(:seasons)
        """
    )
    return pd.read_sql_query(query, connection, params={"seasons": seasons})


def _read_raw_tables(
    connection,
    seasons: list[str],
    progress: ProgressCallback | None = None,
) -> dict[str, pd.DataFrame]:
    """Read all raw tables needed by the staging build."""

    raw_tables: dict[str, pd.DataFrame] = {}
    for table_name in RAW_TABLES:
        if progress:
            progress(f"Reading raw.{table_name}")
        table_df = _read_raw_table(connection, table_name, seasons)
        raw_tables[table_name] = table_df
        if progress:
            progress(f"Read raw.{table_name}: {len(table_df)} rows")
    return raw_tables


def _discover_raw_database_seasons(connection) -> list[str]:
    """Discover seasons from `raw.matches` inside Postgres."""

    rows = connection.execute(
        text(
            """
            SELECT DISTINCT REPLACE(REPLACE(season, '-', '_'), '/', '_') AS season_key
            FROM raw.matches
            WHERE season IS NOT NULL AND BTRIM(season) <> ''
            ORDER BY season_key;
            """
        )
    ).fetchall()
    return [str(row[0]) for row in rows]

