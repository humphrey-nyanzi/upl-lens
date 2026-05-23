"""Unit tests for raw CSV-to-Postgres count verification rules."""

from __future__ import annotations

from scripts.data_platform.verify_raw_postgres_counts import _print_results


def _counts(matches: int) -> dict[str, dict[str, int]]:
    """Build the minimum count shape needed by the raw verifier."""

    return {
        "2024_25": {
            "matches": matches,
            "events": 0,
            "lineups": 0,
            "staff": 0,
            "officials": 0,
            "stats": 0,
            "failed_matches": 0,
        }
    }


def test_raw_count_verification_allows_spill_when_valid_counts_match(capsys) -> None:
    """Cross-season rows should warn without blocking a correct raw load."""

    csv_counts = _counts(240)
    database_counts = _counts(240)
    spill_counts = _counts(10)
    spill_sources = {"2024_25": {"matches": {"2025/26": 10}}}

    assert _print_results(["2024_25"], csv_counts, spill_counts, database_counts, spill_sources) is True

    output = capsys.readouterr().out
    assert "spill=10" in output
    assert "[warning] Some season folders contain cross-season spill rows." in output
    assert "2024_25.matches: 2025/26=10" in output


def test_raw_count_verification_fails_when_valid_counts_do_not_match() -> None:
    """Actual count mismatches should still fail the operation."""

    csv_counts = _counts(240)
    database_counts = _counts(239)
    spill_counts = _counts(0)

    assert _print_results(["2024_25"], csv_counts, spill_counts, database_counts) is False
