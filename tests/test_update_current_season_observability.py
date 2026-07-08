"""Unit tests for current-season operations logging helpers."""

from __future__ import annotations

import json
import sys
import shutil
from io import StringIO
from pathlib import Path

from scripts.data_platform import update_current_season as updater
from scripts.data_platform.update_current_season import (
    OperationsStepError,
    _extract_event_type_counts,
    _extract_raw_load_counts,
    _extract_staging_row_counts,
    _failed_run_summary_payload,
    _failure_evidence_payload,
    _run_summary_payload,
    _run_step,
    _staging_verification_status,
)


class FakeLogPath:
    """Small in-memory stand-in for the Path methods these helpers need."""

    def __init__(self, text: str, *, exists: bool = True) -> None:
        self.text = text
        self._exists = exists

    def exists(self) -> bool:
        return self._exists

    def open(self, *args, **kwargs):
        return StringIO(self.text)

    def read_text(self, *args, **kwargs) -> str:
        return self.text


def test_extract_raw_load_counts_reads_loader_log() -> None:
    """The final summary should reuse row counts printed by the raw loader."""

    log_path = FakeLogPath(
        "\n".join(
            [
                "Raw load summary:",
                "  matches: 199 in-season rows processed",
                "  events: 2813 in-season rows processed",
                "  lineups: 6100 in-season rows processed",
            ]
        )
    )

    assert _extract_raw_load_counts(log_path) == {
        "matches": 199,
        "events": 2813,
        "lineups": 6100,
    }


def test_extract_staging_row_counts_reads_build_log() -> None:
    """The final summary should expose staging rows written by the rebuild."""

    log_path = FakeLogPath(
        "\n".join(
            [
                "[ok] Staging rebuild finished.",
                "  staging.matches: 199 rows",
                "  staging.events: 2813 rows",
            ]
        )
    )

    assert _extract_staging_row_counts(log_path) == {
        "matches": 199,
        "events": 2813,
    }


def test_extract_event_type_counts_reads_staging_verification_log() -> None:
    """The final summary should expose event-type totals used by the UI."""

    log_path = FakeLogPath(
        "\n".join(
            [
                "Event type counts:",
                "  2025_26  goal             496",
                "  2025_26  yellow_card      729",
                "",
                "Validation summary for run_id=staging-test:",
            ]
        )
    )

    assert _extract_event_type_counts(log_path) == {
        "goal": 496,
        "yellow_card": 729,
    }


def test_staging_verification_status_detects_passing_log() -> None:
    """A known passing staging-verification line should become a clear status."""

    log_path = FakeLogPath(
        "[ok] Staging verification finished without error-level validation issues."
    )

    assert (
        _staging_verification_status(log_path)
        == "passed without error-level validation issues"
    )


def test_run_summary_payload_keeps_operational_decisions_visible() -> None:
    """The JSON payload should expose the choices that matter during debugging."""

    step_log = Path("outputs/automation/2025_26/scrape.log")

    payload = _run_summary_payload(
        season="2025-26",
        mode="full",
        use_cache=False,
        skip_migrations=True,
        failed_count=2,
        step_logs={"scrape_current_season": step_log},
        raw_verification_ran=True,
        staging_verification_ran=False,
    )

    assert payload["season"] == "2025-26"
    assert payload["mode"] == "full"
    assert payload["source"] == "fresh live-source refresh"
    assert payload["migrations"] == "skipped"
    assert payload["raw_verification"] == "completed"
    assert payload["staging_verification"] == "skipped"
    assert payload["remaining_failed_matches"] == 2
    assert "staging_rows" in payload
    assert "staging_event_type_counts" in payload
    assert payload["step_logs"]["scrape_current_season"].endswith("scrape.log")


def test_failed_run_summary_identifies_failed_stage_and_artifacts(
    monkeypatch,
) -> None:
    """Failed summaries should show where the pipeline stopped and what remains."""

    test_root = Path("outputs/test_artifacts/update_current_season_observability")
    if test_root.exists():
        shutil.rmtree(test_root)

    raw_dir = test_root / "data" / "raw" / "2025_26"
    raw_dir.mkdir(parents=True)
    matches_path = raw_dir / "matches.csv"
    matches_path.write_text("match_id,season\n1,2025-26\n", encoding="utf-8")
    log_dir = test_root / "outputs" / "automation" / "2025_26"
    completed_log = log_dir / "scrape.log"
    raw_load_log = log_dir / "raw-load.log"

    try:
        raw_counts = {
            table_name: None for table_name in updater.RAW_TABLE_FILE_PREFIXES
        }
        raw_counts["matches"] = 1
        raw_counts["failed_matches"] = 0

        monkeypatch.setattr(updater, "_raw_csv_counts", lambda season: raw_counts)
        monkeypatch.setattr(updater, "raw_season_dir", lambda season: raw_dir)
        monkeypatch.setattr(
            updater,
            "raw_season_file",
            lambda season, table_name: raw_dir / f"{table_name}.csv",
        )
        monkeypatch.setattr(
            updater,
            "raw_season_failed_matches_file",
            lambda season: raw_dir / "failed_matches.csv",
        )
        source_report = raw_dir / "source_preflight.json"
        source_report.write_text(
            json.dumps(
                {
                    "source_url": "https://upl.co.ug/calendar/2025-26-fixtures-results/",
                    "observed_link_count": 240,
                    "minimum_link_count": 1,
                    "expected_match_count": 240,
                    "failure_reason": None,
                }
            ),
            encoding="utf-8",
        )
        raw_load_report = raw_dir / "raw_load_safety.json"
        raw_load_report.write_text(
            json.dumps(
                {
                    "failure_reason": "incoming match set would remove or substitute existing hosted matches",
                    "expected_match_rows": 240,
                    "incoming_match_rows": 216,
                    "incoming_distinct_match_urls": 216,
                    "duplicate_match_rows": 0,
                    "existing_match_rows": 240,
                    "missing_existing_match_url_count": 24,
                    "missing_existing_match_url_sample": [
                        "https://upl.co.ug/event/216/"
                    ],
                    "override_enabled": False,
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(
            updater,
            "raw_season_source_preflight_file",
            lambda season: source_report,
        )
        monkeypatch.setattr(
            updater,
            "raw_season_load_safety_file",
            lambda season: raw_load_report,
        )

        payload = _failed_run_summary_payload(
            season="2025-26",
            mode="full",
            use_cache=False,
            skip_migrations=True,
            skip_raw_load=False,
            skip_raw_verification=False,
            skip_staging_verification=False,
            step_logs={
                "scrape_current_season": completed_log,
            },
            log_dir=log_dir,
            failed_stage="load_raw_to_postgres",
            failed_stage_log=raw_load_log,
            exit_code=1,
            failure_reason="unsafe raw load blocked",
        )

        assert payload["status"] == "failed"
        assert payload["failed_stage"] == "load_raw_to_postgres"
        assert payload["exit_code"] == 1
        assert payload["raw_load"] == "failed"
        assert payload["raw_verification"] == "not_started"
        assert payload["staging_rebuild"] == "not_started"
        evidence = payload["failure_evidence"]
        assert evidence["observed_link_count"] == 240
        assert evidence["expected_match_count"] == 240
        assert evidence["incoming_match_count"] == 216
        assert evidence["incoming_distinct_match_count"] == 216
        assert evidence["duplicate_match_rows"] == 0
        assert evidence["existing_hosted_count"] == 240
        assert evidence["missing_existing_match_url_count"] == 24
        assert evidence["missing_existing_match_url_sample"] == [
            "https://upl.co.ug/event/216/"
        ]
        assert evidence["override_enabled"] is False
        assert evidence["database_write_stages_skipped"] == [
            "raw",
            "staging",
            "analytics",
        ]
        assert payload["partial_artifacts"]["raw_season_dir_exists"] is True
        assert payload["partial_artifacts"]["raw_files"]["matches"]["exists"] is True
        assert payload["partial_artifacts"]["raw_files"]["matches"]["row_count"] == 1
        assert (
            payload["partial_artifacts"]["completed_step_logs"]["scrape_current_season"]
            .replace("\\", "/")
            .endswith("scrape.log")
        )
    finally:
        if test_root.exists():
            shutil.rmtree(test_root)


def test_source_failure_ignores_stale_raw_loader_evidence(
    monkeypatch, tmp_path
) -> None:
    """A failed preflight must not inherit an older loader failure report."""

    source_report = tmp_path / "source.json"
    source_report.write_text(
        json.dumps(
            {
                "source_url": "https://upl.co.ug/calendar/2025-26-fixtures-results/",
                "failure_reason": "unexpected_calendar_structure",
                "observed_link_count": 3,
                "minimum_link_count": 1,
                "expected_match_count": 3,
            }
        ),
        encoding="utf-8",
    )
    stale_raw_report = tmp_path / "raw.json"
    stale_raw_report.write_text(
        json.dumps(
            {
                "failure_reason": "stale loader failure",
                "incoming_match_rows": 216,
                "existing_match_rows": 200,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        updater,
        "raw_season_source_preflight_file",
        lambda season: source_report,
    )
    monkeypatch.setattr(
        updater,
        "raw_season_load_safety_file",
        lambda season: stale_raw_report,
    )

    evidence = _failure_evidence_payload(
        season="2025-26",
        step_logs={},
        failed_stage="scrape_current_season",
    )

    assert evidence["failure_reason"] == "unexpected_calendar_structure"
    assert evidence["incoming_match_count"] is None
    assert evidence["existing_hosted_count"] is None
    assert evidence["database_write_stages_skipped"] == ["raw", "staging", "analytics"]


def test_run_step_raises_structured_error_on_failed_command() -> None:
    """A failed stage should preserve its name, log path, and process exit code."""

    log_dir = Path("outputs/test_artifacts/update_current_season_run_step")
    if log_dir.exists():
        shutil.rmtree(log_dir)

    try:
        _run_step(
            "intentional_failure",
            [sys.executable, "-c", "print('boom'); raise SystemExit(7)"],
            log_dir,
        )
    except OperationsStepError as error:
        assert error.step_name == "intentional_failure"
        assert error.exit_code == 7
        assert error.log_path.exists()
        assert "boom" in error.log_path.read_text(encoding="utf-8")
    else:
        raise AssertionError("Expected OperationsStepError")
    finally:
        if log_dir.exists():
            shutil.rmtree(log_dir)
