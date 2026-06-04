"""Season overview and availability queries."""

from __future__ import annotations

from typing import Any

from src.db.connection import get_api_psycopg_connection
from src.api.query_services.common import _fetch_all, _fetch_one


def list_seasons() -> list[dict[str, Any]]:
    """Return season-level availability from `staging.matches`."""

    return _fetch_all(
        """
        WITH app_safe_matches AS (
            SELECT *
            FROM staging.matches
            WHERE is_source_anomaly IS NOT TRUE
        ),
        match_counts AS (
            SELECT
                season,
                COUNT(*) AS match_count,
                MIN(match_date) AS first_match_date,
                MAX(match_date) AS last_match_date
            FROM app_safe_matches
            GROUP BY season
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
            SELECT season, COUNT(DISTINCT team_name) AS team_count
            FROM team_rows
            GROUP BY season
        )
        SELECT
            m.season,
            m.match_count,
            m.first_match_date,
            m.last_match_date,
            COALESCE(t.team_count, 0) AS team_count
        FROM match_counts AS m
        LEFT JOIN team_counts AS t
            ON t.season = m.season
        ORDER BY m.season;
        """
    )


def _event_type_label(event_type: str | None) -> str:
    """Return a viewer-friendly event label for dashboard summaries."""

    labels = {
        "goal": "Goals",
        "own_goal": "Own goals",
        "penalty_goal": "Penalty goals",
        "assist": "Assists",
        "yellow_card": "Yellow cards",
        "red_card": "Red cards",
        "substitution": "Substitutions",
    }
    if event_type is None:
        return "Other events"
    return labels.get(event_type, event_type.replace("_", " ").title())


def get_season_overview(season: str | None = None) -> dict[str, Any] | None:
    """Return a scope-aware dashboard summary from staging tables.

    This is the first API shape built specifically for the React overview. It
    lets Postgres do season-wide counting once, instead of forcing the browser
    to page through every match and event row. When ``season`` is omitted, the
    response aggregates across every app-safe season currently available.
    """

    with get_api_psycopg_connection() as connection:
        overview = _fetch_one(
            """
            WITH app_safe_matches AS (
                SELECT *
                FROM staging.matches
                WHERE (%(season)s::text IS NULL OR season = %(season)s::text)
                    AND is_source_anomaly IS NOT TRUE
            ),
            match_totals AS (
                SELECT
                    COUNT(DISTINCT season) AS season_count,
                    COUNT(*) AS match_count,
                    COALESCE(SUM(COALESCE(total_goals, 0)), 0) AS scoreline_goal_count,
                    MIN(match_date) AS first_match_date,
                    MAX(match_date) AS latest_match_date
                FROM app_safe_matches
            ),
            team_rows AS (
                SELECT home_team AS team_name
                FROM app_safe_matches
                WHERE home_team IS NOT NULL
                UNION
                SELECT away_team AS team_name
                FROM app_safe_matches
                WHERE away_team IS NOT NULL
            ),
            team_totals AS (
                SELECT COUNT(DISTINCT team_name) AS team_count
                FROM team_rows
            )
            SELECT
                CASE
                    WHEN %(season)s::text IS NULL THEN 'all'
                    ELSE %(season)s::text
                END AS season,
                CASE
                    WHEN %(season)s::text IS NULL THEN 'all'
                    ELSE %(season)s::text
                END AS scope_key,
                COALESCE(match_totals.season_count, 0) AS season_count,
                match_totals.match_count,
                COALESCE(team_totals.team_count, 0) AS team_count,
                match_totals.scoreline_goal_count,
                match_totals.first_match_date,
                match_totals.latest_match_date
            FROM match_totals
            CROSS JOIN team_totals;
            """,
            {"season": season},
            connection=connection,
        )
        if overview is None:
            return None
        if season is not None and overview["season_count"] == 0:
            return None

        event_counts = _fetch_all(
            """
            SELECT
                COALESCE(event_type, 'other') AS event_type,
                COUNT(*) AS count
            FROM staging.events AS events
            INNER JOIN staging.matches AS matches
                ON matches.match_id = events.match_id
            WHERE (%(season)s::text IS NULL OR events.season = %(season)s::text)
                AND matches.is_source_anomaly IS NOT TRUE
            GROUP BY COALESCE(event_type, 'other')
            ORDER BY count DESC, event_type;
            """,
            {"season": season},
            connection=connection,
        )
    counts_by_type = {row["event_type"]: row["count"] for row in event_counts}
    timeline_goal_count = (
        counts_by_type.get("goal", 0)
        + counts_by_type.get("own_goal", 0)
        + counts_by_type.get("penalty_goal", 0)
    )

    overview["goal_count"] = timeline_goal_count
    overview["timeline_goal_count"] = timeline_goal_count
    overview["event_count"] = sum(counts_by_type.values())
    overview["yellow_card_count"] = counts_by_type.get("yellow_card", 0)
    overview["red_card_count"] = counts_by_type.get("red_card", 0)
    overview["event_breakdown"] = [
        {
            "event_type": row["event_type"],
            "label": _event_type_label(row["event_type"]),
            "count": row["count"],
        }
        for row in event_counts
    ]
    return overview

