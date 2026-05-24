"""Unit tests for high-risk staging parsing and normalization helpers."""

from __future__ import annotations

from datetime import date

import pandas as pd

from src import config
from src.db.staging_loader import (
    _has_error_level_issues,
    _is_forfeit_text,
    _normalize_goal_type,
    _normalize_team,
    _parse_minute,
    _season_date_anomaly_reason,
    _validate_scoreline_timeline_goal_consistency,
    _standardize_label,
)


def test_parse_minute_handles_regular_penalty_annotation() -> None:
    """Penalty annotations should not prevent numeric minute parsing."""

    parsed = _parse_minute("56 (P)")

    assert parsed["event_minute_text"] == "56 (P)"
    assert parsed["minute_base"] == 56
    assert parsed["minute_added"] == 0
    assert parsed["minute_total"] == 56
    assert parsed["is_added_time"] is False
    assert parsed["minute_period"] == "46-60"
    assert parsed["minute_annotation"] == "penalty"
    assert parsed["minute_parse_failed"] is False


def test_parse_minute_handles_added_time_apostrophe() -> None:
    """Added-time values should keep base and added minutes separate."""

    parsed = _parse_minute("45+2'")

    assert parsed["minute_base"] == 45
    assert parsed["minute_added"] == 2
    assert parsed["minute_total"] == 47
    assert parsed["is_added_time"] is True
    assert parsed["minute_period"] == "46-60"


def test_parse_minute_handles_own_goal_annotation() -> None:
    """Own-goal hints in the source minute text should be preserved."""

    parsed = _parse_minute("90 OG")

    assert parsed["minute_base"] == 90
    assert parsed["minute_total"] == 90
    assert parsed["minute_period"] == "76-90"
    assert parsed["minute_annotation"] == "own_goal"


def test_parse_minute_marks_unparseable_text_without_crashing() -> None:
    """Bad source minute text should become a validation concern, not a crash."""

    parsed = _parse_minute("second half")

    assert parsed["event_minute_text"] == "second half"
    assert parsed["minute_total"] is None
    assert parsed["minute_parse_failed"] is True


def test_parse_minute_treats_blank_values_as_unknown_not_failed() -> None:
    """Blank source minutes are incomplete data, not parser failures."""

    parsed = _parse_minute(pd.NA)

    assert parsed["event_minute_text"] is None
    assert parsed["minute_total"] is None
    assert parsed["minute_parse_failed"] is False


def test_goal_type_prefers_minute_annotations() -> None:
    """Penalty and own-goal annotations should standardize goal type."""

    assert _normalize_goal_type(None, "penalty") == config.GOAL_TYPE_PENALTY
    assert _normalize_goal_type(None, "own_goal") == config.GOAL_TYPE_OWN_GOAL
    assert _normalize_goal_type("regular", None) == config.GOAL_TYPE_REGULAR


def test_standardize_label_and_team_name_normalization() -> None:
    """Common labels and corrected team names should normalize consistently."""

    assert _standardize_label("Yellow Card") == "yellow_card"
    assert _standardize_label("  Red   Card  ") == "red_card"
    assert _normalize_team("kcca") == "KCCA FC"
    assert _normalize_team("Ondupraka FC") == "Onduparaka FC"


def test_error_level_validation_issues_block_staging_writes() -> None:
    """Error-level validation issues should stop before FK-breaking inserts."""

    assert _has_error_level_issues(pd.DataFrame(columns=["severity"])) is False
    assert _has_error_level_issues(pd.DataFrame([{"severity": "warning"}])) is False
    assert _has_error_level_issues(pd.DataFrame([{"severity": "error"}])) is True


def test_scoreline_timeline_goal_mismatch_is_flagged_as_warning() -> None:
    """Forfeit/admin scorelines should be visible without blocking staging."""

    staging_tables = {
        "matches": pd.DataFrame(
            [
                {
                    "match_id": 1,
                    "season": "2025_26",
                    "home_team": "Kitara FC",
                    "away_team": "Vipers SC",
                    "total_goals": 3,
                }
            ]
        ),
        "events": pd.DataFrame(
            columns=["match_id", "event_type"]
        ),
    }

    issues = _validate_scoreline_timeline_goal_consistency(staging_tables, "test-run")

    assert len(issues) == 1
    assert issues[0]["severity"] == "warning"
    assert issues[0]["check_name"] == "scoreline_timeline_goal_mismatch"
    assert issues[0]["issue_value"] == "scoreline_goals=3; timeline_goals=0"


def test_forfeit_text_detection_uses_source_notice_language() -> None:
    """Forfeit/admin source notices should become a stable staging flag."""

    assert _is_forfeit_text("Police FC lose the match by forfeiture.") is True
    assert _is_forfeit_text("The club failed to turn up for the match.") is True
    assert _is_forfeit_text("Failure to honour Match pending FUFA Disciplinary Panel Verdict.") is True
    assert _is_forfeit_text("Pilsner Man of the Match: Jane Doe") is False


def test_season_date_anomaly_flags_cross_season_source_rows() -> None:
    """A match dated long after its source season should be marked unsafe."""

    reason = _season_date_anomaly_reason("2019_20", date(2021, 5, 18))

    assert reason is not None
    assert reason.startswith("match_date_outside_season_window")
    assert _season_date_anomaly_reason("2020_21", date(2021, 5, 18)) is None
