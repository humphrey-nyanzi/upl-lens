"""Composed overview intelligence for the UPL Lens front page."""

from __future__ import annotations

from typing import Any

from src.api.intelligence import classify_data_quality, safe_rate
from src.api.query_services.matches import list_match_intelligence
from src.api.query_services.teams import list_teams
from src.api.query_services.trends import get_season_trends


def get_overview_intelligence(season: str | None = None) -> dict[str, Any] | None:
    """Return a compact editorial control-room summary for the overview page."""

    trends = get_season_trends()["seasons"]
    trend_row = _select_trend_row(trends, season)
    if trend_row is None:
        return None

    teams = list_teams(season=season, limit=500)
    signal_matches = list_match_intelligence(season=season, sort="interest", limit=6)
    status, note = classify_data_quality(
        match_count=trend_row["match_count"],
        timeline_complete_count=trend_row["timeline_complete_match_count"],
        timeline_partial_count=trend_row["timeline_partial_match_count"],
        timeline_unavailable_count=trend_row["timeline_unavailable_match_count"],
        administrative_result_count=trend_row["administrative_result_count"],
        source_anomaly_count=trend_row["source_anomaly_count"],
    )
    return {
        "season": trend_row["season"] if season is not None else None,
        "season_pulse": {
            "matches_covered": trend_row["match_count"],
            "teams_tracked": trend_row["team_count"],
            "goals_per_match": trend_row["goals_per_match"],
            "cards_per_match": trend_row["cards_per_match"],
            "timeline_coverage_share": trend_row["timeline_coverage_share"],
            "high_scoring_match_share": trend_row["high_scoring_match_share"],
        },
        "things_to_notice": _overview_notices(trend_row),
        "recent_signal_matches": signal_matches,
        "team_signals": _team_signals(teams),
        "data_quality": {
            "timeline_coverage_share": trend_row["timeline_coverage_share"],
            "administrative_result_count": trend_row["administrative_result_count"],
            "source_anomaly_count": trend_row["source_anomaly_count"],
            "status": status,
            "note": note,
        },
    }


def _select_trend_row(rows: list[dict[str, Any]], season: str | None) -> dict[str, Any] | None:
    if season is not None:
        return next((row for row in rows if row["season"] == season), None)
    return rows[-1] if rows else None


def _overview_notices(row: dict[str, Any]) -> list[dict[str, Any]]:
    notices: list[dict[str, Any]] = []
    if row["goals_per_match"] is not None:
        notices.append(
            {
                "key": "scoring_rate",
                "title": "Scoring rate",
                "text": f"Available timeline data shows {row['goals_per_match']} goals per match.",
                "tone": "neutral",
                "link_path": "/trends",
            }
        )
    if row["high_scoring_match_share"] is not None and row["high_scoring_match_share"] >= 0.35:
        notices.append(
            {
                "key": "high_scoring_share",
                "title": "High-scoring matches",
                "text": "At least one third of covered matches have three or more goals.",
                "tone": "positive",
                "link_path": "/matches",
            }
        )
    if (row["timeline_coverage_share"] or 0) < 1:
        notices.append(
            {
                "key": "timeline_caveat",
                "title": "Timeline caveat",
                "text": "Some matches have partial or unavailable timelines, so event-led views include caveats.",
                "tone": "warning",
                "link_path": "/methodology",
            }
        )
    return notices[:3]


def _team_signals(teams: list[dict[str, Any]]) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    if not teams:
        return signals

    top_attack = max(teams, key=lambda row: row["goals_for"])
    tight_defence = min(teams, key=lambda row: row["conceded_per_match"] if row["conceded_per_match"] is not None else 999)
    points_leader = max(teams, key=lambda row: row["official_points"])
    goal_diff_leader = max(teams, key=lambda row: row["goal_difference"])
    for row, signal, metric, label in [
        (points_leader, "Points leader", points_leader["official_points"], "points"),
        (top_attack, "Top attack", top_attack["goals_for"], "goals for"),
        (tight_defence, "Tightest defence", tight_defence["conceded_per_match"], "conceded per match"),
        (goal_diff_leader, "Goal-difference leader", goal_diff_leader["goal_difference"], "goal difference"),
    ]:
        signals.append(
            {
                "team_name": row["team_name"],
                "team_slug": row["team_slug"],
                "signal": signal,
                "metric_value": None if metric is None else round(metric, 4) if isinstance(metric, float) else metric,
                "metric_label": label,
            }
        )
    return signals

