"""Unit tests for hosted/local operations log sync helpers."""

from __future__ import annotations

from pathlib import Path

from scripts.data_platform.verify_operations_log_sync import (
    OperationsEvidence,
    _comparison_payload,
    _parse_github_log,
)


def test_parse_github_log_extracts_hosted_operations_summary() -> None:
    """GitHub job logs should become comparable hosted operations evidence."""

    log_text = "\n".join(
        [
            "update-current-season\tRun update\t2026-05-23T07:02:57Z   Season: 2025-26",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z   Mode: full",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z   Raw verification: completed",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z   Staging rebuild: completed",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z   Staging verification: passed without error-level validation issues",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z   Remaining failed matches: 0",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z Raw rows processed by Postgres loader:",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z   matches        210",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z   events         2858",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z Staging row counts:",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z   staging.matches    2025_26: 210",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z   staging.events     2025_26: 2858",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z Validation summary for run_id=staging-test:",
            "update-current-season\tRun update\t2026-05-23T07:02:57Z   info    man_of_match_quality         staging.matches    1",
        ]
    )

    evidence = _parse_github_log(log_text, source="test-log", run_id="123")

    assert evidence.season == "2025-26"
    assert evidence.raw_verification == "completed"
    assert evidence.staging_verification == "passed without error-level validation issues"
    assert evidence.remaining_failed_matches == 0
    assert evidence.raw_loader_rows == {"matches": 210, "events": 2858}
    assert evidence.staging_rows == {"matches": 210, "events": 2858}
    assert evidence.validation_issue_counts == {"info": 1}
    assert evidence.run_id == "123"


def _evidence(
    source: str,
    *,
    raw_matches: int = 210,
    staging_matches: int = 210,
    raw_csv_matches: int = 220,
) -> OperationsEvidence:
    """Build a small comparable evidence object."""

    return OperationsEvidence(
        source=source,
        season="2025-26",
        mode="full",
        source_refresh="fresh live-source refresh",
        migrations="skipped",
        raw_verification="completed",
        staging_rebuild="completed",
        staging_verification="passed without error-level validation issues",
        remaining_failed_matches=0,
        raw_csv_rows={"matches": raw_csv_matches},
        raw_loader_rows={"matches": raw_matches},
        staging_rows={"matches": staging_matches},
        validation_issue_counts={},
        summary_path=str(Path("summary.json")),
        run_id="123" if source == "hosted" else None,
    )


def test_comparison_payload_reports_in_sync_core_counts() -> None:
    """Matching loaded/staging evidence should be in sync."""

    payload = _comparison_payload(_evidence("hosted"), _evidence("local"))

    assert payload["status"] == "in_sync"
    assert payload["mismatch_count"] == 0


def test_comparison_payload_flags_loaded_row_drift() -> None:
    """Loaded raw and staging count drift should fail the sync check."""

    payload = _comparison_payload(
        _evidence("hosted", raw_matches=210, staging_matches=210),
        _evidence("local", raw_matches=209, staging_matches=209),
    )

    assert payload["status"] == "out_of_sync"
    assert "raw_loader_rows.matches: hosted=210, local=209" in payload["mismatches"]
    assert "staging_rows.matches: hosted=210, local=209" in payload["mismatches"]


def test_comparison_payload_treats_raw_artifact_drift_as_warning_by_default() -> None:
    """Raw CSV drift should warn unless strict artifact comparison is requested."""

    payload = _comparison_payload(
        _evidence("hosted", raw_csv_matches=220),
        _evidence("local", raw_csv_matches=221),
    )

    assert payload["status"] == "warning"
    assert payload["mismatch_count"] == 0
    assert "raw_csv_rows.matches: hosted=220, local=221" in payload["warnings"]
