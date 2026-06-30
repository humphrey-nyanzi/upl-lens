"""Tests for raw-loader destructive-write safety checks."""

from __future__ import annotations

import json
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


class ExistingUrlCursor:
    """Cursor fake for the hosted identity query."""

    def __init__(self) -> None:
        self.statement = ""
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def execute(self, statement, params) -> None:
        self.statement = statement
        self.params = params

    def fetchall(self):
        return [(" https://upl.co.ug/event/1/ ",), ("https://upl.co.ug/event/2/",)]


class ExistingUrlConnection:
    """Connection fake exposing the identity-query cursor."""

    def __init__(self) -> None:
        self.read_cursor = ExistingUrlCursor()

    def cursor(self):
        return self.read_cursor


def test_existing_season_urls_are_queried_as_distinct_identities() -> None:
    """The loader should read the hosted identity set before deletion."""

    connection = ExistingUrlConnection()

    urls = raw_loader._existing_season_match_urls(connection, "2025-26")

    assert urls == {
        "https://upl.co.ug/event/1/",
        "https://upl.co.ug/event/2/",
    }
    assert "SELECT DISTINCT BTRIM(match_url)" in connection.read_cursor.statement
    assert connection.read_cursor.params == ("2025_26",)


def _match_urls(count: int) -> list[str]:
    return [f"https://upl.co.ug/event/{index}/" for index in range(count)]


def _run_loader_boundary(
    monkeypatch,
    tmp_path: Path,
    *,
    incoming_urls: list[str],
    existing_urls: set[str],
    source_urls: set[str] | None = None,
    expected_count: int = 208,
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
    rows = [{"season": season, "match_url": url} for url in incoming_urls]
    validated_source_urls = (
        source_urls if source_urls is not None else set(incoming_urls)
    )
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
            validated_source_urls,
        ),
    )
    monkeypatch.setattr(
        raw_loader,
        "_existing_season_match_urls",
        lambda _connection, _season: existing_urls,
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
            incoming_match_urls=set(),
            duplicate_match_rows=0,
            existing_match_urls=set(_match_urls(208)),
            expected_match_rows=208,
            source_contract_valid=True,
            incoming_urls_match_source=True,
            allow_unsafe_season_reload=False,
        )

    assert "no in-season rows" in str(error.value)


def test_fresh_host_partial_input_never_reaches_delete(monkeypatch, tmp_path) -> None:
    """The trusted baseline protects an empty hosted database."""

    connection = FakeConnection()
    deleted_tables: list[str] = []
    with pytest.raises(RawSeasonLoadSafetyError) as error:
        _run_loader_boundary(
            monkeypatch,
            tmp_path,
            incoming_urls=_match_urls(20),
            existing_urls=set(),
            connection=connection,
            deleted_tables=deleted_tables,
        )

    assert "trusted season baseline" in str(error.value)
    assert deleted_tables == []
    assert connection.commit_count == 0


def test_existing_host_shrinkage_blocks_before_delete(monkeypatch, tmp_path) -> None:
    """A tolerated source count cannot authorize deleting hosted identities."""

    connection = FakeConnection()
    deleted_tables: list[str] = []
    with pytest.raises(RawSeasonLoadSafetyError) as error:
        _run_loader_boundary(
            monkeypatch,
            tmp_path,
            incoming_urls=_match_urls(188),
            existing_urls=set(_match_urls(208)),
            connection=connection,
            deleted_tables=deleted_tables,
        )

    assert "remove or substitute existing hosted matches" in str(error.value)
    assert error.value.report.incoming_distinct_match_urls == 188
    assert error.value.report.existing_match_rows == 208
    assert error.value.report.missing_existing_match_url_count == 20
    assert len(error.value.report.missing_existing_match_url_sample) == 10
    assert deleted_tables == []
    assert connection.commit_count == 0

    payload = json.loads(
        (tmp_path / "raw_load_safety.json").read_text(encoding="utf-8")
    )
    assert payload["incoming_distinct_match_urls"] == 188
    assert payload["existing_match_rows"] == 208
    assert payload["missing_existing_match_url_count"] == 20
    assert len(payload["missing_existing_match_url_sample"]) == 10
    assert payload["database_write_stages_skipped"] == ["raw", "staging", "analytics"]


def test_equal_count_substitution_blocks_before_delete(monkeypatch, tmp_path) -> None:
    """Equal counts cannot hide replacement of one hosted match identity."""

    existing_urls = set(_match_urls(208))
    incoming_urls = _match_urls(207) + ["https://upl.co.ug/event/replacement/"]
    connection = FakeConnection()
    deleted_tables: list[str] = []

    with pytest.raises(RawSeasonLoadSafetyError) as error:
        _run_loader_boundary(
            monkeypatch,
            tmp_path,
            incoming_urls=incoming_urls,
            existing_urls=existing_urls,
            source_urls=set(incoming_urls),
            connection=connection,
            deleted_tables=deleted_tables,
        )

    assert error.value.report.incoming_distinct_match_urls == 208
    assert error.value.report.existing_match_rows == 208
    assert error.value.report.missing_existing_match_url_count == 1
    assert (
        "https://upl.co.ug/event/207/"
        in error.value.report.missing_existing_match_url_sample
    )
    assert deleted_tables == []
    assert connection.commit_count == 0


def test_incoming_superset_preserves_existing_urls_and_proceeds(
    monkeypatch, tmp_path
) -> None:
    """Routine loading may add matches when all hosted identities remain present."""

    incoming_urls = _match_urls(209)
    connection, deleted_tables = _run_loader_boundary(
        monkeypatch,
        tmp_path,
        incoming_urls=incoming_urls,
        existing_urls=set(_match_urls(208)),
        source_urls=set(incoming_urls),
    )

    assert set(deleted_tables) == set(raw_loader.RAW_TABLE_CONFIGS)
    assert connection.commit_count == 1


def test_loader_rejects_self_declared_ten_match_contract(monkeypatch, tmp_path) -> None:
    """The loader independently compares reports with reviewed config."""

    report_path = tmp_path / "source.json"
    report_path.write_text(
        json.dumps(
            {
                "status": "passed",
                "target_season": "2025-26",
                "source_url": "https://upl.co.ug/calendar/2025-26-fixtures-results/",
                "source_structure_valid": True,
                "expected_match_count": 10,
                "observed_link_count": 10,
                "minimum_link_count": 10,
                "baseline_version": "2026-06-29",
                "match_urls": _match_urls(10),
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        raw_loader,
        "raw_season_source_preflight_file",
        lambda season: report_path,
    )

    expected, _, valid, urls = raw_loader._read_source_preflight_contract("2025-26")

    assert expected == 208
    assert valid is False
    assert len(urls) == 10


def test_duplicate_inflation_never_reaches_delete_or_commit(
    monkeypatch, tmp_path
) -> None:
    """Repeated copies of one valid URL cannot satisfy the count threshold."""

    connection = FakeConnection()
    deleted_tables: list[str] = []
    with pytest.raises(RawSeasonLoadSafetyError) as error:
        _run_loader_boundary(
            monkeypatch,
            tmp_path,
            incoming_urls=["https://upl.co.ug/event/0/"] * 188,
            existing_urls=set(),
            source_urls={"https://upl.co.ug/event/0/"},
            connection=connection,
            deleted_tables=deleted_tables,
        )

    assert "duplicate match records" in str(error.value)
    assert error.value.report.incoming_distinct_match_urls == 1
    assert error.value.report.duplicate_match_rows == 187
    assert deleted_tables == []
    assert connection.commit_count == 0


def test_valid_fresh_host_input_reaches_delete_and_commit(
    monkeypatch, tmp_path
) -> None:
    """A validated fresh season can enter the destructive write section."""

    connection, deleted_tables = _run_loader_boundary(
        monkeypatch,
        tmp_path,
        incoming_urls=_match_urls(208),
        existing_urls=set(),
    )

    assert set(deleted_tables) == set(raw_loader.RAW_TABLE_CONFIGS)
    assert connection.commit_count == 1


def test_named_admin_override_deliberately_permits_reviewed_shrinkage(
    monkeypatch, tmp_path
) -> None:
    """The admin-only override remains the intentional removal boundary."""

    connection, deleted_tables = _run_loader_boundary(
        monkeypatch,
        tmp_path,
        incoming_urls=_match_urls(188),
        existing_urls=set(_match_urls(208)),
        override=True,
    )

    assert set(deleted_tables) == set(raw_loader.RAW_TABLE_CONFIGS)
    assert connection.commit_count == 1
