"""Tests for the staging schema relationship contract."""

from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAGING_MIGRATION = PROJECT_ROOT / "database" / "migrations" / "002_create_staging_foundation.sql"


def _table_block(sql: str, table_name: str) -> str:
    """Return the CREATE TABLE block for one staging table."""

    pattern = re.compile(
        rf"CREATE TABLE IF NOT EXISTS staging\.{table_name} \((.*?)\n\);",
        re.DOTALL,
    )
    match = pattern.search(sql)
    assert match is not None, f"Missing staging.{table_name} CREATE TABLE block"
    return match.group(1)


def test_staging_child_tables_reference_staging_matches() -> None:
    """App-safe staging child rows must be constrained to a parent match."""

    sql = STAGING_MIGRATION.read_text(encoding="utf-8")
    child_tables = ("events", "lineups", "staff", "officials", "stats")

    for table_name in child_tables:
        table_sql = _table_block(sql, table_name)
        assert "match_id BIGINT NOT NULL REFERENCES staging.matches (match_id) ON DELETE CASCADE" in table_sql


def test_staging_matches_has_forfeit_flag() -> None:
    """Forfeited/admin matches should have a stable staging flag for analysis."""

    sql = STAGING_MIGRATION.read_text(encoding="utf-8")
    matches_sql = _table_block(sql, "matches")

    assert "is_forfeit BOOLEAN NOT NULL DEFAULT FALSE" in matches_sql


def test_staging_matches_has_source_anomaly_flags() -> None:
    """Source anomalies should be queryable without deleting raw evidence."""

    sql = STAGING_MIGRATION.read_text(encoding="utf-8")
    matches_sql = _table_block(sql, "matches")

    assert "is_source_anomaly BOOLEAN NOT NULL DEFAULT FALSE" in matches_sql
    assert "source_anomaly_reason TEXT" in matches_sql


def test_raw_schema_stays_source_tolerant_without_match_foreign_keys() -> None:
    """Raw ingestion should remain looser than staging and avoid child-table FKs."""

    raw_sql = (PROJECT_ROOT / "database" / "migrations" / "001_create_raw_schema.sql").read_text(
        encoding="utf-8"
    )

    assert "REFERENCES staging.matches" not in raw_sql
    assert "REFERENCES raw.matches" not in raw_sql
