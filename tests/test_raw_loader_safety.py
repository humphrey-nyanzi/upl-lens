"""Tests for raw-loader destructive-write safety checks."""

from __future__ import annotations

import pytest

from src.db.raw_loader import RawSeasonLoadSafetyError, _enforce_safe_raw_season_load


def test_safe_raw_season_load_blocks_zero_match_input() -> None:
    """Routine loading must not delete hosted rows after an empty scrape."""

    with pytest.raises(RawSeasonLoadSafetyError) as error:
        _enforce_safe_raw_season_load(
            season="2025-26",
            incoming_match_rows=0,
            existing_match_rows=210,
            allow_unsafe_season_reload=False,
        )

    assert "no in-season rows" in str(error.value)
    assert error.value.report.existing_match_rows == 210


def test_safe_raw_season_load_blocks_implausibly_small_input() -> None:
    """A tiny incoming scrape should not replace a larger hosted season."""

    with pytest.raises(RawSeasonLoadSafetyError) as error:
        _enforce_safe_raw_season_load(
            season="2025-26",
            incoming_match_rows=25,
            existing_match_rows=210,
            allow_unsafe_season_reload=False,
        )

    assert "much smaller" in str(error.value)


def test_safe_raw_season_load_accepts_plausible_input() -> None:
    """Normal routine reloads should pass when incoming counts are trustworthy."""

    report = _enforce_safe_raw_season_load(
        season="2025-26",
        incoming_match_rows=205,
        existing_match_rows=210,
        allow_unsafe_season_reload=False,
    )

    assert report.incoming_match_rows == 205
    assert report.existing_match_rows == 210


def test_safe_raw_season_load_allows_named_admin_override() -> None:
    """The explicit admin flag preserves an escape hatch for manual recovery."""

    report = _enforce_safe_raw_season_load(
        season="2025-26",
        incoming_match_rows=0,
        existing_match_rows=210,
        allow_unsafe_season_reload=True,
    )

    assert report.incoming_match_rows == 0
