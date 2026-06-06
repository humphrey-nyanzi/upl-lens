"""Reusable football-intelligence helpers for API response shaping."""

from __future__ import annotations

import re
from typing import Any, Literal


GOAL_EVENT_TYPES = {"goal", "own_goal", "penalty_goal"}
CARD_EVENT_TYPES = {"yellow_card", "red_card"}
Tone = Literal["positive", "neutral", "warning", "risk"]


def safe_rate(numerator: int | float | None, denominator: int | float | None) -> float | None:
    """Return a rounded rate, or ``None`` when the denominator is not usable."""

    if denominator in (None, 0):
        return None
    return round(float(numerator or 0) / float(denominator), 4)


def slugify(value: str | None) -> str:
    """Return the same simple lowercase dash slug used by API player queries."""

    if value is None:
        return ""
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-")


def _label(key: str, label: str, tone: Tone = "neutral", description: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"key": key, "label": label, "tone": tone}
    if description is not None:
        row["description"] = description
    return row


def classify_data_quality(
    match_count: int,
    timeline_complete_count: int,
    timeline_partial_count: int,
    timeline_unavailable_count: int,
    administrative_result_count: int = 0,
    source_anomaly_count: int = 0,
) -> tuple[str, str | None]:
    """Classify public data quality for a season/team comparison row."""

    if match_count <= 0:
        return "limited", "No app-safe matches are available for this scope."

    timeline_coverage_share = safe_rate(timeline_complete_count + timeline_partial_count, match_count) or 0
    caveat_count = timeline_partial_count + timeline_unavailable_count + administrative_result_count

    if timeline_coverage_share < 0.5:
        return "limited", "Timeline coverage is limited, so event-led comparisons should be read cautiously."
    if source_anomaly_count > 0:
        return "caution", "Some source anomalies were excluded from public aggregates."
    if caveat_count > 0:
        return "caution", "Some matches carry timeline or administrative caveats."
    return "good", None


def build_team_profile_labels(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Return viewer-friendly team archetype labels from summary metrics."""

    labels: list[dict[str, Any]] = []
    goals_per_match = row.get("goals_per_match")
    conceded_per_match = row.get("conceded_per_match")
    win_rate = row.get("win_rate")
    points_per_match = row.get("points_per_match")

    if goals_per_match is not None and goals_per_match >= 1.75:
        labels.append(_label("strong_attack", "Strong attack", "positive", "Scores at a high rate in this scope."))
    if conceded_per_match is not None and conceded_per_match <= 0.8:
        labels.append(_label("tight_defence", "Tight defence", "positive", "Concedes less than one goal per match."))
    if win_rate is not None and win_rate >= 0.5:
        labels.append(_label("results_team", "Results team", "positive", "Wins at least half of its matches."))
    if points_per_match is not None and points_per_match < 1:
        labels.append(_label("needs_results", "Needs results", "warning", "Points return is below one point per match."))
    if row.get("administrative_matches", 0) > 0 or row.get("missing_matches", 0) > 0:
        labels.append(_label("data_caveat", "Data caveat", "warning", "Administrative or missing matches affect the record."))
    return labels[:4]


def build_player_profile_labels(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Return football-readable player labels from contribution and lineup data."""

    labels: list[dict[str, Any]] = []
    if row.get("goals", 0) >= 3:
        labels.append(_label("goal_threat", "Goal threat", "positive"))
    if row.get("assists", 0) >= 3:
        labels.append(_label("creator", "Creator", "positive"))
    starts_share = row.get("starts_share")
    if starts_share is not None and starts_share >= 0.7:
        labels.append(_label("regular_starter", "Regular starter", "positive"))
    elif row.get("appearances", 0) >= 5:
        labels.append(_label("squad_regular", "Squad regular", "neutral"))
    if row.get("substitutions_on", 0) >= 3 and row.get("goals", 0) + row.get("assists", 0) > 0:
        labels.append(_label("bench_impact", "Bench impact", "positive"))
    if row.get("yellow_cards", 0) + row.get("red_cards", 0) >= 4:
        labels.append(_label("discipline_watch", "Discipline watch", "warning"))
    if len(row.get("teams") or []) > 1:
        labels.append(_label("multi_team_player", "Multi-team player", "neutral"))
    return labels[:5]


def build_match_signals(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the public signal chips for a match intelligence row."""

    labels: list[dict[str, Any]] = []
    total_goals = row.get("total_goals")
    card_count = (row.get("yellow_card_count") or 0) + (row.get("red_card_count") or 0)

    if total_goals is not None and total_goals >= 5:
        labels.append(_label("goal_heavy", "Goal-heavy", "positive"))
    elif total_goals is not None and total_goals >= 3:
        labels.append(_label("high_scoring", "High scoring", "positive"))
    if (row.get("late_goal_count") or 0) > 0:
        labels.append(_label("late_drama", "Late drama", "positive"))
    if (row.get("final_15_goal_count") or 0) > 0:
        labels.append(_label("final_15_goal", "Final-15 goal", "positive"))
    if (row.get("red_card_count") or 0) > 0:
        labels.append(_label("red_card", "Red card", "risk"))
    if card_count >= 5:
        labels.append(_label("discipline_signal", "Discipline signal", "warning"))

    timeline_status = row.get("timeline_status")
    if timeline_status == "complete":
        labels.append(_label("timeline_complete", "Timeline complete", "neutral"))
    elif timeline_status == "partial":
        labels.append(_label("timeline_partial", "Partial timeline", "warning"))
    elif timeline_status == "unavailable":
        labels.append(_label("timeline_unavailable", "Timeline unavailable", "warning"))
    if row.get("is_administrative_result"):
        labels.append(_label("administrative_result", "Administrative result", "risk"))
    if row.get("is_source_anomaly"):
        labels.append(_label("source_caveat", "Source caveat", "risk"))
    return labels


def calculate_interest_score(row: dict[str, Any]) -> int:
    """Score a match by useful public signals, not by raw recency."""

    score = 0
    total_goals = row.get("total_goals") or 0
    score += min(total_goals, 6) * 2
    score += (row.get("late_goal_count") or 0) * 5
    score += (row.get("final_15_goal_count") or 0) * 3
    score += (row.get("red_card_count") or 0) * 4
    score += min(row.get("yellow_card_count") or 0, 6)
    score += min(row.get("event_count") or 0, 20) // 4
    if row.get("timeline_status") == "complete":
        score += 2
    if row.get("timeline_status") in {"partial", "unavailable"}:
        score -= 1
    if row.get("is_administrative_result") or row.get("is_source_anomaly"):
        score -= 2
    return max(score, 0)


def enrich_match_intelligence(row: dict[str, Any]) -> dict[str, Any]:
    """Attach signal labels, score, primary signal, and caveat note to a match row."""

    enriched = dict(row)
    signals = build_match_signals(enriched)
    enriched["signal_labels"] = signals
    enriched["interest_score"] = calculate_interest_score(enriched)
    enriched["primary_signal"] = signals[0]["label"] if signals else None
    enriched["data_quality_note"] = _match_data_quality_note(enriched)
    return enriched


def _match_data_quality_note(row: dict[str, Any]) -> str | None:
    if row.get("is_source_anomaly"):
        return row.get("source_anomaly_reason") or "This source record has an anomaly."
    if row.get("is_administrative_result"):
        return row.get("administrative_note") or "This was recorded as an administrative result."
    if row.get("timeline_status") in {"partial", "unavailable"}:
        return row.get("timeline_note") or "Timeline evidence is incomplete for this match."
    return None


def bucket_goal_timing(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return six regular-time goal buckets for a team or match event set."""

    intervals = [
        ("0-15", 1, 15),
        ("16-30", 16, 30),
        ("31-45", 31, 45),
        ("46-60", 46, 60),
        ("61-75", 61, 75),
        ("76-90", 76, 90),
    ]
    rows = [{"interval": label, "start_minute": start, "end_minute": end, "goals": 0} for label, start, end in intervals]
    for event in events:
        minute = event.get("minute_total")
        if event.get("event_type") not in GOAL_EVENT_TYPES or minute is None or minute < 1 or minute > 90:
            continue
        for row in rows:
            if row["start_minute"] <= minute <= row["end_minute"]:
                row["goals"] += 1
                break
    total = sum(row["goals"] for row in rows)
    return [{**row, "share": safe_rate(row["goals"], total)} for row in rows]


def summarize_event_phases(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group match events into broad football phases for match briefs."""

    phase_order = ["first_half", "second_half", "final_15", "added_time"]
    rows = {
        phase: {"phase": phase, "goals": 0, "yellow_cards": 0, "red_cards": 0, "substitutions": 0, "total_events": 0}
        for phase in phase_order
    }
    for event in events:
        phase = _event_phase(event)
        event_type = event.get("event_type")
        rows[phase]["total_events"] += 1
        if event_type in GOAL_EVENT_TYPES:
            rows[phase]["goals"] += 1
        elif event_type == "yellow_card":
            rows[phase]["yellow_cards"] += 1
        elif event_type == "red_card":
            rows[phase]["red_cards"] += 1
        elif event_type == "substitution":
            rows[phase]["substitutions"] += 1
    return [rows[phase] for phase in phase_order]


def _event_phase(event: dict[str, Any]) -> str:
    minute = event.get("minute_total")
    minute_text = str(event.get("event_minute_text") or "")
    if "+" in minute_text:
        return "added_time"
    if minute is not None and minute >= 76:
        return "final_15"
    if minute is not None and minute >= 46:
        return "second_half"
    return "first_half"


def build_score_progression(match: dict[str, Any], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return score changes from goal events in timeline order."""

    home_score = 0
    away_score = 0
    points: list[dict[str, Any]] = []
    for event in _ordered_goal_events(events):
        team_side = event.get("team_side")
        if event.get("event_type") == "own_goal":
            if team_side == "home":
                away_score += 1
            elif team_side == "away":
                home_score += 1
        elif team_side == "home":
            home_score += 1
        elif team_side == "away":
            away_score += 1
        else:
            continue
        points.append(
            {
                "minute": event.get("minute_total"),
                "minute_text": event.get("event_minute_text"),
                "home_score": home_score,
                "away_score": away_score,
                "scoring_team": _scoring_team_name(match, event),
                "event_type": event.get("event_type"),
            }
        )
    return points


def build_key_moments(match: dict[str, Any], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return compact events that explain why a match matters."""

    moments: list[dict[str, Any]] = []
    goals = _ordered_goal_events(events)
    progression = build_score_progression(match, events)
    if goals:
        moments.append(_moment(goals[0], "First goal", "Opened the scoring."))
        if len(goals) > 1:
            moments.append(_moment(goals[-1], "Final goal", "Closed the scoring sequence."))

    previous_home = 0
    previous_away = 0
    for point, goal in zip(progression, goals, strict=False):
        home_score = point["home_score"]
        away_score = point["away_score"]
        if home_score == away_score and previous_home != previous_away:
            moments.append(_moment(goal, "Equaliser", "Brought the match level."))
        if _is_winning_goal(point, match):
            moments.append(_moment(goal, "Winning goal", "Set the final winning margin."))
        if goal.get("event_type") == "penalty_goal":
            moments.append(_moment(goal, "Penalty goal", "Scored from the penalty spot."))
        if goal.get("event_type") == "own_goal":
            moments.append(_moment(goal, "Own goal", "Changed the scoreline through an own goal."))
        if (goal.get("minute_total") or 0) >= 76:
            moments.append(_moment(goal, "Late goal", "Arrived in the final 15 minutes or later."))
        previous_home = home_score
        previous_away = away_score

    for event in events:
        if event.get("event_type") == "red_card":
            moments.append(_moment(event, "Red card", "A dismissal changed the match context."))

    if match.get("is_administrative_result"):
        moments.append(
            {
                "minute": None,
                "minute_text": None,
                "event_type": "administrative_result",
                "team_name": None,
                "player_name": None,
                "label": "Administrative result",
                "reason": match.get("administrative_note") or "The result was decided administratively.",
            }
        )
    if match.get("is_source_anomaly"):
        moments.append(
            {
                "minute": None,
                "minute_text": None,
                "event_type": "source_caveat",
                "team_name": None,
                "player_name": None,
                "label": "Source caveat",
                "reason": match.get("source_anomaly_reason") or "The source record carries an anomaly.",
            }
        )
    return _dedupe_moments(moments)[:8]


def _ordered_goal_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [event for event in events if event.get("event_type") in GOAL_EVENT_TYPES],
        key=lambda event: (event.get("minute_total") is None, event.get("minute_total") or 999, event.get("event_index") or 999),
    )


def _moment(event: dict[str, Any], label: str, reason: str) -> dict[str, Any]:
    return {
        "minute": event.get("minute_total"),
        "minute_text": event.get("event_minute_text"),
        "event_type": event.get("event_type"),
        "team_name": event.get("team_name"),
        "player_name": event.get("player_name"),
        "label": label,
        "reason": reason,
    }


def _dedupe_moments(moments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    unique: list[dict[str, Any]] = []
    for moment in moments:
        key = (moment.get("minute_text"), moment.get("event_type"), moment.get("team_name"), moment.get("label"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(moment)
    return unique


def _is_winning_goal(point: dict[str, Any], match: dict[str, Any]) -> bool:
    home_score = match.get("home_score")
    away_score = match.get("away_score")
    if home_score is None or away_score is None or home_score == away_score:
        return False
    return point["home_score"] == home_score and point["away_score"] == away_score


def _scoring_team_name(match: dict[str, Any], event: dict[str, Any]) -> str | None:
    if event.get("event_type") == "own_goal":
        if event.get("team_side") == "home":
            return match.get("away_team")
        if event.get("team_side") == "away":
            return match.get("home_team")
    return event.get("team_name")

