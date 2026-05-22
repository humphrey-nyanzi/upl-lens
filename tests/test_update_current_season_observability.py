"""Unit tests for current-season operations logging helpers."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from scripts.data_platform.update_current_season import (
    _extract_raw_load_counts,
    _run_summary_payload,
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


def test_staging_verification_status_detects_passing_log() -> None:
    """A known passing staging-verification line should become a clear status."""

    log_path = FakeLogPath(
        "[ok] Staging verification finished without error-level validation issues."
    )

    assert _staging_verification_status(log_path) == "passed without error-level validation issues"


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
    assert payload["step_logs"]["scrape_current_season"].endswith("scrape.log")
