"""Tests for raw-loader destructive-write safety checks."""

from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path

import pytest

from src.db import raw_loader
from src.db.raw_loader import RawSeasonLoadSafetyError, _enforce_safe_raw_season_load


class FakeConnection:
    """Minimal transaction boundary for loader integration tests."""

    def __init__(self) -> None:
        self.commit_count = 0

    def commit(self) -> None:
        self.commit_count += 1


def _match_rows(count: int, season: str = "2025-26") -> list[dict[str, str]]:
    return [
        {"season": season, "match_url": f"https://upl.co.ug/event/{index}/"}
        for index in range(count)
    ]


def _run_loader_boundary(
    monkeypatch,
    tmp_path: Path,
    *,
    incoming_count: int,
    existing_count: int,
    expected_count: int,
    contract_valid: bool = True,
    override: bool = False,
    connection: FakeConnection | None = None,
    deleted_tables: list[str] | None = None,
) -> tuple[FakeConnection, list[str]]:
    season = "2025-26"
    season_dir = tmp_path / "raw" / "2025_26"
    season_dir.mkdir(parents=True)
    table_paths = {
        table_name: season_dir / f"{table_name}.csv"
        for table_name in raw_loader.RAW_TABLE_CONFIGS
    }
    rows = _match_rows(incoming_count, season)
    source_urls = {row["match_url"] for row in _match_rows(expected_count, season)}
    connection = connection or FakeConnection()
    deleted_tables = deleted_tables if deleted_tables is not None else []

    monkeypatch.setattr(raw_loader, "raw_season_dir", lambda _season: season_dir)
    monkeypatch.setattr(raw_loader, "_season_table_paths", lambda _season: table_paths)
    monkeypatch.setattr(
        raw_loader,
        "_read_csv_rows",
        lambda path: rows if path == table_paths["matches"] else [],
    )
    monkeypatch.setattr(
        raw_loader,
        "_read_source_preflight_contract",
        lambda _season: (
            expected_count,
            "https://upl.co.ug/calendar/2025-26-fixtures-results/",
            contract_valid,
            source_urls,
        ),
    )
    monkeypatch.setattr(
        raw_loader,
        "_count_existing_season_matches",
        lambda _connection, _season: existing_count,
    )
    monkeypatch.setattr(
        raw_loader,
        "_delete_existing_season_rows",
        lambda _connection, table_name, _season: deleted_tables.append(table_name),
    )
    monkeypatch.setattr(
        raw_loader, "_upsert_rows", lambda _connection, _table, values: len(values)
    )
    monkeypatch.setattr(
        raw_loader,
        "get_psycopg_connection",
        lambda settings=None: nullcontext(connection),
    )
    monkeypatch.setattr(
        raw_loader,
        "raw_season_load_safety_file",
        lambda _season: tmp_path / "raw_load_safety.json",
    )
    for table_name in raw_loader.ROW_PREPARERS:
        monkeypatch.setitem(
            raw_loader.ROW_PREPARERS, table_name, lambda row, _path: row
        )

    raw_loader.load_raw_seasons_to_postgres(
        [season],
        allow_unsafe_season_reload=override,
    )
    return connection, deleted_tables


def test_safe_raw_season_load_blocks_zero_match_input() -> None:
    """Routine loading must reject an empty season."""

    with pytest.raises(RawSeasonLoadSafetyError) as error:
        _enforce_safe_raw_season_load(
            season="2025-26",
            source_url="https://upl.co.ug/calendar/2025-26-fixtures-results/",
            incoming_match_rows=0,
            existing_match_rows=210,
            expected_match_rows=210,
            source_contract_valid=True,
            incoming_urls_match_source=True,
            allow_unsafe_season_reload=False,
        )

    assert "no in-season rows" in str(error.value)


def test_fresh_host_partial_input_never_reaches_delete(monkeypatch, tmp_path) -> None:
    """A source-derived expectation protects an empty hosted database."""

    connection = FakeConnection()
    deleted_tables: list[str] = []
    with pytest.raises(RawSeasonLoadSafetyError) as error:
        _run_loader_boundary(
            monkeypatch,
            tmp_path,
            incoming_count=20,
            existing_count=0,
            expected_count=200,
            connection=connection,
            deleted_tables=deleted_tables,
        )

    assert "source-calendar expectation" in str(error.value)
    assert deleted_tables == []
    assert connection.commit_count == 0
    payload = (tmp_path / "raw_load_safety.json").read_text(encoding="utf-8")
    assert '"existing_match_rows": 0' in payload
    assert '"database_write_stages_skipped"' in payload


def test_existing_host_ratio_rejection_preserves_transaction(
    monkeypatch, tmp_path
) -> None:
    """The hosted-row ratio blocks delete before transaction mutation."""

    connection = FakeConnection()
    deleted_tables: list[str] = []
    with pytest.raises(RawSeasonLoadSafetyError) as error:
        _run_loader_boundary(
            monkeypatch,
            tmp_path,
            incoming_count=30,
            existing_count=100,
            expected_count=30,
            connection=connection,
            deleted_tables=deleted_tables,
        )

    assert "much smaller than existing" in str(error.value)
    assert deleted_tables == []
    assert connection.commit_count == 0


def test_valid_input_reaches_delete_and_commit(monkeypatch, tmp_path) -> None:
    """A validated complete season can enter the destructive write section."""

    connection, deleted_tables = _run_loader_boundary(
        monkeypatch,
        tmp_path,
        incoming_count=20,
        existing_count=0,
        expected_count=20,
    )

    assert set(deleted_tables) == set(raw_loader.RAW_TABLE_CONFIGS)
    assert connection.commit_count == 1


def test_named_admin_override_explicitly_allows_recovery(monkeypatch, tmp_path) -> None:
    """The admin-only override remains available outside routine orchestration."""

    connection, deleted_tables = _run_loader_boundary(
        monkeypatch,
        tmp_path,
        incoming_count=0,
        existing_count=210,
        expected_count=0,
        contract_valid=False,
        override=True,
    )

    assert set(deleted_tables) == set(raw_loader.RAW_TABLE_CONFIGS)
    assert connection.commit_count == 1
