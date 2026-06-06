"""Historical season trend queries for the UPL Lens Trends page."""

from __future__ import annotations

from typing import Any

from src.api.intelligence import classify_data_quality, safe_rate
from src.api.query_services.common import _fetch_all


def get_season_trends() -> dict[str, Any]:
    """Return chart-ready season comparison rows from staging tables."""

    rows = _fetch_all(
        """
        WITH match_rows AS (
            SELECT *
            FROM staging.matches
        ),
        app_safe_matches AS (
            SELECT *
            FROM match_rows
            WHERE is_source_anomaly IS NOT TRUE
        ),
        team_rows AS (
            SELECT season, home_team AS team_name
            FROM app_safe_matches
            WHERE home_team IS NOT NULL
            UNION
            SELECT season, away_team AS team_name
            FROM app_safe_matches
            WHERE away_team IS NOT NULL
        ),
        team_counts AS (
            SELECT season, COUNT(DISTINCT team_name)::integer AS team_count
            FROM team_rows
            GROUP BY season
        ),
        match_agg AS (
            SELECT
                season,
                COUNT(*)::integer AS match_count,
                MIN(match_date) AS first_match_date,
                MAX(match_date) AS last_match_date,
                COALESCE(SUM(COALESCE(total_goals, 0)), 0)::integer AS scoreline_goal_count,
                COUNT(*) FILTER (WHERE result = 'home_win')::integer AS home_wins,
                COUNT(*) FILTER (WHERE result = 'away_win')::integer AS away_wins,
                COUNT(*) FILTER (WHERE result = 'draw')::integer AS draws,
                COUNT(*) FILTER (WHERE COALESCE(total_goals, 0) >= 3)::integer AS high_scoring_match_count,
                COUNT(*) FILTER (WHERE COALESCE(total_goals, 0) >= 5)::integer AS goal_heavy_match_count,
                COUNT(*) FILTER (WHERE timeline_status = 'complete')::integer AS timeline_complete_match_count,
                COUNT(*) FILTER (WHERE timeline_status = 'partial')::integer AS timeline_partial_match_count,
                COUNT(*) FILTER (WHERE timeline_status = 'unavailable')::integer AS timeline_unavailable_match_count,
                COUNT(*) FILTER (WHERE is_administrative_result IS TRUE)::integer AS administrative_result_count
            FROM app_safe_matches
            GROUP BY season
        ),
        event_counts AS (
            SELECT
                events.season,
                COUNT(*) FILTER (WHERE events.event_type IN ('goal', 'own_goal', 'penalty_goal'))::integer AS timeline_goal_count,
                COUNT(*) FILTER (WHERE events.event_type = 'yellow_card')::integer AS yellow_card_count,
                COUNT(*) FILTER (WHERE events.event_type = 'red_card')::integer AS red_card_count
            FROM staging.events AS events
            INNER JOIN app_safe_matches AS matches
                ON matches.match_id = events.match_id
            GROUP BY events.season
        ),
        anomaly_counts AS (
            SELECT season, COUNT(*)::integer AS source_anomaly_count
            FROM match_rows
            WHERE is_source_anomaly IS TRUE
            GROUP BY season
        )
        SELECT
            match_agg.season,
            match_agg.match_count,
            COALESCE(team_counts.team_count, 0)::integer AS team_count,
            match_agg.first_match_date,
            match_agg.last_match_date,
            match_agg.scoreline_goal_count,
            COALESCE(event_counts.timeline_goal_count, 0)::integer AS timeline_goal_count,
            COALESCE(event_counts.yellow_card_count, 0)::integer AS yellow_card_count,
            COALESCE(event_counts.red_card_count, 0)::integer AS red_card_count,
            match_agg.home_wins,
            match_agg.away_wins,
            match_agg.draws,
            match_agg.high_scoring_match_count,
            match_agg.goal_heavy_match_count,
            match_agg.timeline_complete_match_count,
            match_agg.timeline_partial_match_count,
            match_agg.timeline_unavailable_match_count,
            match_agg.administrative_result_count,
            COALESCE(anomaly_counts.source_anomaly_count, 0)::integer AS source_anomaly_count
        FROM match_agg
        LEFT JOIN team_counts
            ON team_counts.season = match_agg.season
        LEFT JOIN event_counts
            ON event_counts.season = match_agg.season
        LEFT JOIN anomaly_counts
            ON anomaly_counts.season = match_agg.season
        ORDER BY match_agg.season;
        """
    )

    seasons = [_shape_season_trend_row(row) for row in rows]
    total_matches = sum(row["match_count"] for row in seasons)
    total_scoreline_goals = sum(row["scoreline_goal_count"] for row in seasons)
    total_timeline_goals = sum(row["timeline_goal_count"] for row in seasons)
    total_cards = sum(row["total_card_count"] for row in seasons)
    summary = {
        "season_count": len(seasons),
        "total_matches": total_matches,
        "total_scoreline_goals": total_scoreline_goals,
        "total_timeline_goals": total_timeline_goals,
        "total_cards": total_cards,
        "average_goals_per_match": safe_rate(total_timeline_goals, total_matches),
        "average_cards_per_match": safe_rate(total_cards, total_matches),
        "earliest_season": seasons[0]["season"] if seasons else None,
        "latest_season": seasons[-1]["season"] if seasons else None,
    }
    return {"seasons": seasons, "summary": summary}


def _shape_season_trend_row(row: dict[str, Any]) -> dict[str, Any]:
    total_card_count = (row["yellow_card_count"] or 0) + (row["red_card_count"] or 0)
    status, note = classify_data_quality(
        match_count=row["match_count"],
        timeline_complete_count=row["timeline_complete_match_count"],
        timeline_partial_count=row["timeline_partial_match_count"],
        timeline_unavailable_count=row["timeline_unavailable_match_count"],
        administrative_result_count=row["administrative_result_count"],
        source_anomaly_count=row["source_anomaly_count"],
    )
    timeline_covered = row["timeline_complete_match_count"] + row["timeline_partial_match_count"]
    return {
        **row,
        "total_card_count": total_card_count,
        "goals_per_match": safe_rate(row["timeline_goal_count"], row["match_count"]),
        "cards_per_match": safe_rate(total_card_count, row["match_count"]),
        "home_win_share": safe_rate(row["home_wins"], row["match_count"]),
        "away_win_share": safe_rate(row["away_wins"], row["match_count"]),
        "draw_share": safe_rate(row["draws"], row["match_count"]),
        "high_scoring_match_share": safe_rate(row["high_scoring_match_count"], row["match_count"]),
        "goal_heavy_match_share": safe_rate(row["goal_heavy_match_count"], row["match_count"]),
        "timeline_coverage_share": safe_rate(timeline_covered, row["match_count"]),
        "data_quality_status": status,
        "data_quality_note": note,
    }
