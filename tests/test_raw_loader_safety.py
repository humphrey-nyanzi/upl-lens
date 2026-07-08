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


class DeleteCursor:
    """Cursor fake that records a match-scoped delete."""

    def __init__(self) -> None:
        self.statement = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def execute(self, statement, params) -> None:
        self.statement = statement
        self.params = params


class DeleteConnection:
    """Connection fake for affected-match delete SQL."""

    def __init__(self) -> None:
        self.delete_cursor = DeleteCursor()

    def cursor(self):
        return self.delete_cursor


def test_incremental_delete_targets_match_ids_not_a_season() -> None:
    """Routine deletion must be bounded to the plan's affected IDs."""
    connection = DeleteConnection()

    raw_loader._delete_affected_match_rows(
        connection,
        "events",
        season="2025-26",
        match_ids=frozenset({7}),
        match_urls=frozenset(),
    )

    assert connection.delete_cursor.params == ([7],)
    statement = str(connection.delete_cursor.statement)
    assert "match_id" in statement
    assert "season" not in statement


def test_failed_match_delete_is_scoped_to_the_target_season() -> None:
    """Calendar spill must not remove another season's failure record."""
    connection = DeleteConnection()
    match_url = "https://upl.co.ug/event/7/"

    raw_loader._delete_affected_match_rows(
        connection,
        "failed_matches",
        season="2025-26",
        match_ids=frozenset(),
        match_urls=frozenset({match_url}),
    )

    assert connection.delete_cursor.params == ([match_url], "2025_26")
    statement = str(connection.delete_cursor.statement)
    assert "match_url" in statement
    assert "season" in statement


def _match_urls(count: int) -> list[str]:
    return [f"https://upl.co.ug/event/{index}/" for index in range(count)]


def _run_loader_boundary(
    monkeypatch,
    tmp_path: Path,
    *,
    incoming_urls: list[str],
    existing_urls: set[str],
    source_urls: set[str] | None = None,
    expected_count: int = 240,
    contract_valid: bool = True,
    override: bool = False,
    connection: FakeConnection | None = None,
    deleted_tables: list[str] | None = None,
    full_rebuild: bool = True,
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
        full_rebuild=full_rebuild,
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
            existing_match_urls=set(_match_urls(240)),
            expected_match_rows=240,
            source_contract_valid=True,
            incoming_urls_match_source=True,
            allow_unsafe_season_reload=False,
        )

    assert "no in-season rows" in str(error.value)


def test_fresh_host_early_season_input_can_proceed(monkeypatch, tmp_path) -> None:
    """A new season may start with only the fixtures currently on the calendar."""

    connection, deleted_tables = _run_loader_boundary(
        monkeypatch,
        tmp_path,
        incoming_urls=_match_urls(8),
        existing_urls=set(),
    )

    assert set(deleted_tables) == set(raw_loader.RAW_TABLE_CONFIGS)
    assert connection.commit_count == 1


def test_input_above_league_maximum_blocks_before_delete(monkeypatch, tmp_path) -> None:
    """A source or CSV cannot authorize more than the 240-match UPL ceiling."""

    connection = FakeConnection()
    deleted_tables: list[str] = []
    with pytest.raises(RawSeasonLoadSafetyError) as error:
        _run_loader_boundary(
            monkeypatch,
            tmp_path,
            incoming_urls=_match_urls(raw_loader.UPL_MAX_SEASON_MATCH_COUNT + 1),
            existing_urls=set(),
            source_urls=set(_match_urls(raw_loader.UPL_MAX_SEASON_MATCH_COUNT + 1)),
            connection=connection,
            deleted_tables=deleted_tables,
        )

    assert "trusted season maximum" in str(error.value)
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
            incoming_urls=_match_urls(216),
            existing_urls=set(_match_urls(240)),
            connection=connection,
            deleted_tables=deleted_tables,
        )

    assert "remove or substitute existing hosted matches" in str(error.value)
    assert error.value.report.incoming_distinct_match_urls == 216
    assert error.value.report.existing_match_rows == 240
    assert error.value.report.missing_existing_match_url_count == 24
    assert len(error.value.report.missing_existing_match_url_sample) == 10
    assert deleted_tables == []
    assert connection.commit_count == 0

    payload = json.loads(
        (tmp_path / "raw_load_safety.json").read_text(encoding="utf-8")
    )
    assert payload["incoming_distinct_match_urls"] == 216
    assert payload["existing_match_rows"] == 240
    assert payload["missing_existing_match_url_count"] == 24
    assert len(payload["missing_existing_match_url_sample"]) == 10
    assert payload["database_write_stages_skipped"] == ["raw", "staging", "analytics"]


def test_equal_count_substitution_blocks_before_delete(monkeypatch, tmp_path) -> None:
    """Equal counts cannot hide replacement of one hosted match identity."""

    existing_urls = set(_match_urls(240))
    incoming_urls = _match_urls(239) + ["https://upl.co.ug/event/replacement/"]
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

    assert error.value.report.incoming_distinct_match_urls == 240
    assert error.value.report.existing_match_rows == 240
    assert error.value.report.missing_existing_match_url_count == 1
    assert (
        "https://upl.co.ug/event/239/"
        in error.value.report.missing_existing_match_url_sample
    )
    assert deleted_tables == []
    assert connection.commit_count == 0


def test_incoming_superset_preserves_existing_urls_and_proceeds(
    monkeypatch, tmp_path
) -> None:
    """Routine loading may add matches when all hosted identities remain present."""

    incoming_urls = _match_urls(240)
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
                "minimum_link_count": 1,
                "baseline_version": "2026-07-08",
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

    assert expected == 240
    assert valid is False
    assert len(urls) == 10


def test_loader_accepts_hyphenated_source_url_for_normalized_season(
    monkeypatch, tmp_path
) -> None:
    """Hosted runs pass normalized season keys while source URLs keep hyphens."""

    report_path = tmp_path / "source.json"
    report_path.write_text(
        json.dumps(
            {
                "status": "passed",
                "target_season": "2025-26",
                "source_url": "https://upl.co.ug/calendar/2025-26-fixtures-results/",
                "source_structure_valid": True,
                "expected_match_count": raw_loader.UPL_MAX_SEASON_MATCH_COUNT,
                "observed_link_count": raw_loader.UPL_MAX_SEASON_MATCH_COUNT,
                "minimum_link_count": 1,
                "baseline_version": "2026-07-08",
                "match_urls": _match_urls(raw_loader.UPL_MAX_SEASON_MATCH_COUNT),
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        raw_loader,
        "raw_season_source_preflight_file",
        lambda season: report_path,
    )

    expected, source_url, valid, urls = raw_loader._read_source_preflight_contract(
        "2025_26"
    )

    assert expected == raw_loader.UPL_MAX_SEASON_MATCH_COUNT
    assert source_url == "https://upl.co.ug/calendar/2025-26-fixtures-results/"
    assert valid is True
    assert len(urls) == raw_loader.UPL_MAX_SEASON_MATCH_COUNT


def test_loader_rejects_baseline_above_league_maximum(monkeypatch, tmp_path) -> None:
    """The loader should not trust a preflight contract above the UPL ceiling."""

    report_path = tmp_path / "source.json"
    over_maximum = raw_loader.UPL_MAX_SEASON_MATCH_COUNT + 1
    report_path.write_text(
        json.dumps(
            {
                "status": "passed",
                "target_season": "2025-26",
                "source_url": "https://upl.co.ug/calendar/2025-26-fixtures-results/",
                "source_structure_valid": True,
                "expected_match_count": over_maximum,
                "observed_link_count": raw_loader.UPL_MAX_SEASON_MATCH_COUNT,
                "minimum_link_count": 1,
                "baseline_version": "test-over-max",
                "match_urls": _match_urls(raw_loader.UPL_MAX_SEASON_MATCH_COUNT),
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setitem(
        raw_loader.TRUSTED_SEASON_CALENDAR_BASELINES,
        "2025_26",
        {
            "expected_match_count": over_maximum,
            "version": "test-over-max",
            "evidence": "intentional invalid test baseline",
        },
    )
    monkeypatch.setattr(
        raw_loader,
        "raw_season_source_preflight_file",
        lambda season: report_path,
    )

    expected, _, valid, urls = raw_loader._read_source_preflight_contract("2025-26")

    assert expected == over_maximum
    assert valid is False
    assert len(urls) == raw_loader.UPL_MAX_SEASON_MATCH_COUNT


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
            incoming_urls=["https://upl.co.ug/event/0/"] * 216,
            existing_urls=set(),
            source_urls={"https://upl.co.ug/event/0/"},
            connection=connection,
            deleted_tables=deleted_tables,
        )

    assert "duplicate match records" in str(error.value)
    assert error.value.report.incoming_distinct_match_urls == 1
    assert error.value.report.duplicate_match_rows == 215
    assert deleted_tables == []
    assert connection.commit_count == 0


def test_valid_fresh_host_input_reaches_delete_and_commit(
    monkeypatch, tmp_path
) -> None:
    """A validated fresh season can enter the destructive write section."""

    connection, deleted_tables = _run_loader_boundary(
        monkeypatch,
        tmp_path,
        incoming_urls=_match_urls(240),
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
        incoming_urls=_match_urls(216),
        existing_urls=set(_match_urls(240)),
        override=True,
    )

    assert set(deleted_tables) == set(raw_loader.RAW_TABLE_CONFIGS)
    assert connection.commit_count == 1


def _run_incremental_loader(
    monkeypatch,
    tmp_path: Path,
    *,
    incoming_count: int,
    existing_count: int,
    affected_match_ids: set[int],
    attempted_match_ids: set[int] | None = None,
    failed_match_ids: set[int] | None = None,
) -> tuple[FakeConnection, list[tuple[str, tuple[int, ...]]], dict[str, list[dict]]]:
    """Run routine loading with a match-level scraper plan."""
    season = "2025-26"
    season_dir = tmp_path / "raw" / "2025_26"
    season_dir.mkdir(parents=True)
    table_paths = {
        table_name: season_dir / f"{table_name}.csv"
        for table_name in raw_loader.RAW_TABLE_CONFIGS
    }
    match_rows = [
        {
            "match_id": str(match_id),
            "season": season,
            "match_url": f"https://upl.co.ug/event/{match_id}/",
        }
        for match_id in range(incoming_count)
    ]
    event_rows = [
        {
            "match_id": str(match_id),
            "season": season,
            "match_url": f"https://upl.co.ug/event/{match_id}/",
            "event_index": "1",
        }
        for match_id in affected_match_ids
    ]
    failed_match_rows = [
        {
            "season": season,
            "match_url": f"https://upl.co.ug/event/{match_id}/",
            "last_error": "temporary source failure",
        }
        for match_id in (failed_match_ids or set())
    ]
    rows_by_path = {
        table_paths["matches"]: match_rows,
        table_paths["events"]: event_rows,
        table_paths["failed_matches"]: failed_match_rows,
    }
    affected_urls = frozenset(
        f"https://upl.co.ug/event/{match_id}/" for match_id in affected_match_ids
    )
    attempted_urls = frozenset(
        f"https://upl.co.ug/event/{match_id}/"
        for match_id in (
            attempted_match_ids
            if attempted_match_ids is not None
            else affected_match_ids
        )
    )
    failed_urls = frozenset(
        f"https://upl.co.ug/event/{match_id}/"
        for match_id in (failed_match_ids or set())
    )
    plan = raw_loader.RawRefreshPlan(
        affected_match_ids=frozenset(affected_match_ids),
        affected_match_urls=affected_urls,
        attempted_match_urls=attempted_urls,
        failed_match_urls=failed_urls,
    )
    connection = FakeConnection()
    deleted: list[tuple[str, tuple[int, ...]]] = []
    upserted: dict[str, list[dict]] = {}

    monkeypatch.setattr(raw_loader, "raw_season_dir", lambda _season: season_dir)
    monkeypatch.setattr(raw_loader, "_season_table_paths", lambda _season: table_paths)
    monkeypatch.setattr(
        raw_loader, "_read_csv_rows", lambda path: rows_by_path.get(path, [])
    )
    monkeypatch.setattr(raw_loader, "_read_raw_refresh_plan", lambda _season: plan)
    monkeypatch.setattr(
        raw_loader,
        "_read_source_preflight_contract",
        lambda _season: (
            raw_loader.UPL_MAX_SEASON_MATCH_COUNT,
            "https://upl.co.ug/calendar/2025-26-fixtures-results/",
            True,
            set(_match_urls(incoming_count)),
        ),
    )
    monkeypatch.setattr(
        raw_loader,
        "_existing_season_match_urls",
        lambda _connection, _season: set(_match_urls(existing_count)),
    )
    monkeypatch.setattr(
        raw_loader,
        "_delete_existing_season_rows",
        lambda *_args, **_kwargs: pytest.fail("routine mode deleted a season slice"),
    )

    def capture_incremental_delete(
        _connection,
        table_key,
        *,
        season,
        match_ids,
        match_urls,
    ) -> None:
        deletes_failed_matches = table_key == "failed_matches" and bool(match_urls)
        deletes_match_rows = table_key != "failed_matches" and bool(match_ids)
        if deletes_failed_matches or deletes_match_rows:
            deleted.append((table_key, tuple(sorted(match_ids))))

    monkeypatch.setattr(
        raw_loader, "_delete_affected_match_rows", capture_incremental_delete
    )

    def capture_upsert(_connection, table_key, values) -> int:
        upserted[table_key] = list(values)
        return len(values)

    monkeypatch.setattr(raw_loader, "_upsert_rows", capture_upsert)
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

    raw_loader.load_raw_seasons_to_postgres([season])
    return connection, deleted, upserted


def test_routine_no_change_skips_all_raw_database_writes(monkeypatch, tmp_path) -> None:
    """A repeated no-change run should not touch hosted raw rows."""
    connection, deleted, upserted = _run_incremental_loader(
        monkeypatch,
        tmp_path,
        incoming_count=240,
        existing_count=240,
        affected_match_ids=set(),
    )

    assert deleted == []
    assert connection.commit_count == 0
    assert all(rows == [] for rows in upserted.values())


def test_routine_unchanged_recheck_skips_all_raw_database_writes(
    monkeypatch, tmp_path
) -> None:
    """Re-fetched but unchanged recent matches should not create a transaction."""
    connection, deleted, upserted = _run_incremental_loader(
        monkeypatch,
        tmp_path,
        incoming_count=240,
        existing_count=240,
        affected_match_ids=set(),
        attempted_match_ids={207},
    )

    assert deleted == []
    assert connection.commit_count == 0
    assert all(rows == [] for rows in upserted.values())


def test_routine_failed_recheck_replaces_failure_state(monkeypatch, tmp_path) -> None:
    """A current scrape failure should replace only its season-scoped record."""
    connection, deleted, upserted = _run_incremental_loader(
        monkeypatch,
        tmp_path,
        incoming_count=240,
        existing_count=240,
        affected_match_ids=set(),
        attempted_match_ids={207},
        failed_match_ids={207},
    )

    assert deleted == [("failed_matches", ())]
    assert connection.commit_count == 1
    assert [row["match_url"] for row in upserted["failed_matches"]] == [
        "https://upl.co.ug/event/207/"
    ]


def test_routine_new_match_only_mutates_the_new_match(monkeypatch, tmp_path) -> None:
    """Adding one fixture should leave all prior hosted match rows untouched."""
    connection, deleted, upserted = _run_incremental_loader(
        monkeypatch,
        tmp_path,
        incoming_count=240,
        existing_count=239,
        affected_match_ids={239},
    )

    assert connection.commit_count == 1
    assert {match_id for _, ids in deleted for match_id in ids} == {239}
    assert [row["match_id"] for row in upserted["matches"]] == ["239"]
    assert [row["match_id"] for row in upserted["events"]] == ["239"]


def test_routine_changed_match_replaces_only_that_match_children(
    monkeypatch, tmp_path
) -> None:
    """Refreshing one result should replace only its raw parent and child rows."""
    connection, deleted, upserted = _run_incremental_loader(
        monkeypatch,
        tmp_path,
        incoming_count=240,
        existing_count=240,
        affected_match_ids={7},
    )

    assert connection.commit_count == 1
    assert {match_id for _, ids in deleted for match_id in ids} == {7}
    assert [row["match_id"] for row in upserted["matches"]] == ["7"]
    assert [row["match_id"] for row in upserted["events"]] == ["7"]


def test_unsafe_override_requires_explicit_full_rebuild() -> None:
    """The destructive safety bypass cannot leak into routine loading."""
    with pytest.raises(ValueError, match="explicit full rebuild"):
        raw_loader.load_raw_seasons_to_postgres(
            ["2025-26"], allow_unsafe_season_reload=True
        )
