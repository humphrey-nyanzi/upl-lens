"""Unit tests for high-risk staging parsing and normalization helpers."""

from __future__ import annotations

from datetime import date

import pandas as pd

from src import config
from src.db.staging_loader import (
    _build_staging_tables,
    _has_error_level_issues,
    _clean_match_rows,
    _validate_fixture_completeness,
    _is_forfeit_text,
    _normalize_goal_type,
    _normalize_team,
    _parse_minute,
    _season_date_anomaly_reason,
    _validate_scoreline_timeline_goal_consistency,
    _validate_timeline_coverage,
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


def test_forfeit_match_rows_get_admin_result_fields() -> None:
    """Forfeits should carry explicit administrative-result and awarded-points fields."""

    raw_matches = pd.DataFrame(
        [
            {
                "match_id": 1,
                "match_url": "https://upl.co.ug/event/test/",
                "season": "2025-26",
                "date": "04/10/2025",
                "time": "15:00",
                "league": "Uganda Premier League",
                "match_day": 1,
                "home_team": "Kitara FC",
                "home_team_url": None,
                "away_team": "Vipers SC",
                "away_team_url": None,
                "ground_name": None,
                "ground_address": None,
                "man_of_the_match": "Vipers SC failed to turn up for the match.",
                "man_of_the_match_team": None,
                "home_score": 3,
                "away_score": 0,
                "home_first_half_goals": None,
                "away_first_half_goals": None,
                "home_second_half_goals": None,
                "away_second_half_goals": None,
                "has_timeline": False,
                "has_lineups": False,
                "has_officials": False,
                "has_stats": False,
                "ingested_at": pd.Timestamp("2026-01-01T00:00:00Z"),
            }
        ]
    )

    cleaned = _clean_match_rows(raw_matches)
    row = cleaned.iloc[0]

    assert bool(row["is_forfeit"]) is True
    assert bool(row["is_administrative_result"]) is True
    assert row["administrative_result_type"] == "forfeit"
    assert bool(row["played_on_pitch"]) is False
    assert row["home_awarded_points"] == 3
    assert row["away_awarded_points"] == 0


def _raw_match_fixture() -> dict[str, object]:
    """Return a minimal raw match row with all fields needed by staging."""

    return {
        "match_id": 31687,
        "match_url": "https://upl.co.ug/event/vipers-sc-vs-express-fc-12/",
        "season": "2025-26",
        "date": "21/05/2026",
        "time": "16:00",
        "league": "Uganda Premier League",
        "match_day": 30,
        "home_team": "Vipers SC",
        "home_team_url": None,
        "away_team": "Express FC",
        "away_team_url": None,
        "ground_name": "St Mary's Stadium",
        "ground_address": None,
        "man_of_the_match": None,
        "man_of_the_match_team": None,
        "home_score": 2,
        "away_score": 0,
        "home_first_half_goals": None,
        "away_first_half_goals": None,
        "home_second_half_goals": None,
        "away_second_half_goals": None,
        "has_timeline": True,
        "has_lineups": True,
        "has_officials": True,
        "has_stats": True,
        "ingested_at": pd.Timestamp("2026-05-21T18:00:00Z"),
    }


def _raw_event_fixture(event_index: int, event_type: str, team_side: str = config.SIDE_HOME) -> dict[str, object]:
    """Return a minimal raw event row for timeline coverage tests."""

    return {
        "event_row_key": f"31687-{event_index}",
        "match_id": 31687,
        "match_url": "https://upl.co.ug/event/vipers-sc-vs-express-fc-12/",
        "season": "2025-26",
        "date": "21/05/2026",
        "time": "16:00",
        "league": "Uganda Premier League",
        "match_day": 30,
        "home_team": "Vipers SC",
        "away_team": "Express FC",
        "event_index": event_index,
        "event_type": event_type,
        "event_minute": f"{20 + event_index}",
        "team_side": team_side,
        "player_name": f"Player {event_index}",
        "player_url": None,
        "goal_type": None,
        "sub_out_player_name": None,
        "sub_out_player_url": None,
        "sub_in_player_name": None,
        "sub_in_player_url": None,
        "ingested_at": pd.Timestamp("2026-05-21T18:00:00Z"),
    }


def _raw_stat_fixture(name: str, home_value: int, away_value: int) -> dict[str, object]:
    """Return a minimal raw stat row for timeline coverage tests."""

    safe_name = name.lower().replace(" ", "_")
    return {
        "stat_row_key": f"31687-{safe_name}",
        "match_id": 31687,
        "match_url": "https://upl.co.ug/event/vipers-sc-vs-express-fc-12/",
        "season": "2025-26",
        "match_day": 30,
        "home_team": "Vipers SC",
        "away_team": "Express FC",
        "statistic_name": name,
        "home_value": home_value,
        "away_value": away_value,
        "ingested_at": pd.Timestamp("2026-05-21T18:00:00Z"),
    }


def test_timeline_coverage_marks_missing_assists_and_cards_as_partial() -> None:
    """Stat evidence should make partial timelines explicit for the frontend."""

    staging_tables = _build_staging_tables(
        {
            "matches": pd.DataFrame([_raw_match_fixture()]),
            "events": pd.DataFrame(
                [
                    _raw_event_fixture(1, "Goal"),
                    _raw_event_fixture(2, "Goal"),
                ]
            ),
            "lineups": pd.DataFrame(),
            "staff": pd.DataFrame(),
            "officials": pd.DataFrame(),
            "stats": pd.DataFrame(
                [
                    _raw_stat_fixture("Assists", 1, 0),
                    _raw_stat_fixture("Yellow Cards", 0, 1),
                    _raw_stat_fixture("Red Cards", 0, 0),
                ]
            ),
        }
    )

    row = staging_tables["matches"].iloc[0]
    assert row["timeline_status"] == "partial"
    assert row["timeline_issue_count"] == 2
    assert row["scoreline_goal_count"] == 2
    assert row["timeline_goal_count"] == 2
    assert row["stats_assist_count"] == 1
    assert row["timeline_assist_count"] == 0
    assert row["stats_yellow_card_count"] == 1
    assert row["timeline_yellow_card_count"] == 0
    assert "source assists=1, parsed timeline=0" in row["timeline_note"]
    assert "source yellow cards=1, parsed timeline=0" in row["timeline_note"]

    issues = _validate_timeline_coverage(staging_tables, "test-run")
    assert len(issues) == 1
    assert issues[0]["check_name"] == "partial_timeline_coverage"
    assert issues[0]["severity"] == "warning"


def test_timeline_coverage_marks_matching_timeline_as_complete() -> None:
    """When scoreline, stats, and parsed events agree, the timeline is complete."""

    staging_tables = _build_staging_tables(
        {
            "matches": pd.DataFrame([_raw_match_fixture()]),
            "events": pd.DataFrame(
                [
                    _raw_event_fixture(1, "Goal"),
                    _raw_event_fixture(2, "Goal"),
                    _raw_event_fixture(3, "Assist"),
                    _raw_event_fixture(4, "Yellow Card", team_side=config.SIDE_AWAY),
                ]
            ),
            "lineups": pd.DataFrame(),
            "staff": pd.DataFrame(),
            "officials": pd.DataFrame(),
            "stats": pd.DataFrame(
                [
                    _raw_stat_fixture("Assists", 1, 0),
                    _raw_stat_fixture("Yellow Cards", 0, 1),
                    _raw_stat_fixture("Red Cards", 0, 0),
                ]
            ),
        }
    )

    row = staging_tables["matches"].iloc[0]
    assert row["timeline_status"] == "complete"
    assert row["timeline_issue_count"] == 0
    assert row["timeline_note"] is None


def test_fixture_completeness_warns_for_near_complete_missing_team_match() -> None:
    """Near-complete seasons should flag teams below expected fixture counts."""

    rows = []
    teams = ["A", "B", "C", "D"]
    match_id = 1
    for home in teams:
        for away in teams:
            if home == away or (home == "A" and away == "B"):
                continue
            rows.append(
                {
                    "match_id": match_id,
                    "season": "2025_26",
                    "home_team": home,
                    "away_team": away,
                    "is_source_anomaly": False,
                }
            )
            match_id += 1

    issues = _validate_fixture_completeness({"matches": pd.DataFrame(rows)}, "test-run")

    issue_values = [issue["issue_value"] for issue in issues]
    assert any("team=A; recorded=5; expected=6" in value for value in issue_values)
    assert any("team=B; recorded=5; expected=6" in value for value in issue_values)


def test_season_date_anomaly_flags_cross_season_source_rows() -> None:
    """A match dated long after its source season should be marked unsafe."""

    reason = _season_date_anomaly_reason("2019_20", date(2021, 5, 18))

    assert reason is not None
    assert reason.startswith("match_date_outside_season_window")
    assert _season_date_anomaly_reason("2020_21", date(2021, 5, 18)) is None
