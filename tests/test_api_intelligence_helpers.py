from __future__ import annotations

from src.api.intelligence import (
    bucket_goal_timing,
    build_match_signals,
    build_player_profile_labels,
    build_team_profile_labels,
    calculate_interest_score,
    classify_data_quality,
    safe_rate,
    slugify,
)


def test_safe_rate_returns_none_for_empty_denominator() -> None:
    assert safe_rate(3, 0) is None
    assert safe_rate(3, None) is None
    assert safe_rate(1, 4) == 0.25


def test_slugify_matches_api_style() -> None:
    assert slugify("Vipers SC") == "vipers-sc"
    assert slugify("  NEC / FC  ") == "nec-fc"


def test_classify_data_quality_warns_on_partial_timelines() -> None:
    status, note = classify_data_quality(
        match_count=10,
        timeline_complete_count=8,
        timeline_partial_count=2,
        timeline_unavailable_count=0,
    )

    assert status == "caution"
    assert note is not None


def test_match_signals_and_interest_score_prioritize_football_events() -> None:
    row = {
        "total_goals": 5,
        "yellow_card_count": 4,
        "red_card_count": 1,
        "late_goal_count": 1,
        "final_15_goal_count": 1,
        "event_count": 14,
        "timeline_status": "partial",
        "is_administrative_result": False,
        "is_source_anomaly": False,
    }

    signal_keys = [signal["key"] for signal in build_match_signals(row)]

    assert "goal_heavy" in signal_keys
    assert "late_drama" in signal_keys
    assert "red_card" in signal_keys
    assert "timeline_partial" in signal_keys
    assert calculate_interest_score(row) > 20


def test_goal_timing_bucket_uses_regular_time_goal_events() -> None:
    buckets = bucket_goal_timing(
        [
            {"event_type": "goal", "minute_total": 12},
            {"event_type": "penalty_goal", "minute_total": 78},
            {"event_type": "yellow_card", "minute_total": 80},
            {"event_type": "goal", "minute_total": 94},
        ]
    )

    assert buckets[0]["goals"] == 1
    assert buckets[-1]["goals"] == 1
    assert sum(bucket["goals"] for bucket in buckets) == 2


def test_team_and_player_labels_are_derived_from_rates() -> None:
    team_labels = build_team_profile_labels(
        {
            "goals_per_match": 2.0,
            "conceded_per_match": 0.7,
            "win_rate": 0.6,
            "points_per_match": 2.0,
            "administrative_matches": 0,
            "missing_matches": 0,
        }
    )
    player_labels = build_player_profile_labels(
        {
            "goals": 4,
            "assists": 3,
            "appearances": 8,
            "starts_share": 0.75,
            "substitutions_on": 0,
            "yellow_cards": 1,
            "red_cards": 0,
            "teams": ["Vipers SC"],
        }
    )

    assert {label["key"] for label in team_labels} >= {"strong_attack", "tight_defence"}
    assert {label["key"] for label in player_labels} >= {"goal_threat", "creator", "regular_starter"}
