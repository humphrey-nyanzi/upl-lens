"""Postgres query helpers for the read-first FastAPI backend.

The API starts from the cleaned `staging.*` tables because Phase 2 made those
tables the trusted application-facing layer. Route modules should stay thin and
call these helpers instead of embedding SQL in endpoint functions.
"""

from __future__ import annotations

from typing import Any

from psycopg.rows import dict_row

from src.db.connection import get_psycopg_connection, test_database_connection


DEFAULT_LIMIT = 50
MAX_LIMIT = 200


def clamp_pagination(limit: int, offset: int) -> tuple[int, int]:
    """Return safe pagination values for list endpoints."""

    safe_limit = max(1, min(limit, MAX_LIMIT))
    safe_offset = max(0, offset)
    return safe_limit, safe_offset


def _team_like(team: str | None) -> str | None:
    """Return a case-insensitive pattern for simple team-name filtering."""

    if team is None or not team.strip():
        return None
    return f"%{team.strip()}%"


def _fetch_all(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Run a read query and return dictionaries ready for Pydantic models."""

    with get_psycopg_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, params or {})
            return [dict(row) for row in cursor.fetchall()]


def _fetch_one(query: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Run a read query and return one dictionary, or None when no row exists."""

    with get_psycopg_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, params or {})
            row = cursor.fetchone()
            return None if row is None else dict(row)


def get_health_status() -> dict[str, Any]:
    """Return API and database health details."""

    database_name, postgres_version = test_database_connection()
    latest_run = _fetch_one(
        """
        SELECT run_id, completed_at
        FROM staging.validation_runs
        ORDER BY completed_at DESC
        LIMIT 1;
        """
    )
    return {
        "status": "ok",
        "api": "ok",
        "database": "ok",
        "database_name": database_name,
        "postgres_version": postgres_version,
        "latest_staging_run_id": None if latest_run is None else latest_run["run_id"],
        "latest_staging_completed_at": None if latest_run is None else latest_run["completed_at"],
    }


def list_seasons() -> list[dict[str, Any]]:
    """Return season-level availability from `staging.matches`."""

    return _fetch_all(
        """
        WITH match_counts AS (
            SELECT
                season,
                COUNT(*) AS match_count,
                MIN(match_date) AS first_match_date,
                MAX(match_date) AS last_match_date
            FROM staging.matches
            GROUP BY season
        ),
        team_rows AS (
            SELECT season, home_team AS team_name
            FROM staging.matches
            WHERE home_team IS NOT NULL
            UNION
            SELECT season, away_team AS team_name
            FROM staging.matches
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


def get_season_overview(season: str) -> dict[str, Any] | None:
    """Return one season-level dashboard summary from staging tables.

    This is the first API shape built specifically for the React overview. It
    lets Postgres do season-wide counting once, instead of forcing the browser
    to page through every match and event row.
    """

    overview = _fetch_one(
        """
        WITH match_totals AS (
            SELECT
                season,
                COUNT(*) AS match_count,
                COALESCE(SUM(COALESCE(total_goals, 0)), 0) AS goal_count,
                MIN(match_date) AS first_match_date,
                MAX(match_date) AS latest_match_date
            FROM staging.matches
            WHERE season = %(season)s::text
            GROUP BY season
        ),
        team_rows AS (
            SELECT home_team AS team_name
            FROM staging.matches
            WHERE season = %(season)s::text
                AND home_team IS NOT NULL
            UNION
            SELECT away_team AS team_name
            FROM staging.matches
            WHERE season = %(season)s::text
                AND away_team IS NOT NULL
        ),
        team_totals AS (
            SELECT COUNT(DISTINCT team_name) AS team_count
            FROM team_rows
        )
        SELECT
            match_totals.season,
            match_totals.match_count,
            COALESCE(team_totals.team_count, 0) AS team_count,
            match_totals.goal_count,
            match_totals.first_match_date,
            match_totals.latest_match_date
        FROM match_totals
        CROSS JOIN team_totals;
        """,
        {"season": season},
    )
    if overview is None:
        return None

    event_counts = _fetch_all(
        """
        SELECT
            COALESCE(event_type, 'other') AS event_type,
            COUNT(*) AS count
        FROM staging.events
        WHERE season = %(season)s::text
        GROUP BY COALESCE(event_type, 'other')
        ORDER BY count DESC, event_type;
        """,
        {"season": season},
    )
    counts_by_type = {row["event_type"]: row["count"] for row in event_counts}

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


def list_matches(
    season: str | None = None,
    team: str | None = None,
    match_day: int | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return matches with optional season, team, and match-day filters."""

    safe_limit, safe_offset = clamp_pagination(limit, offset)
    return _fetch_all(
        """
        SELECT
            match_id,
            season,
            match_day,
            match_date,
            match_time,
            league,
            home_team,
            away_team,
            home_score,
            away_score,
            total_goals,
            result,
            winner_team,
            ground_name,
            match_url
        FROM staging.matches
        WHERE (%(season)s::text IS NULL OR season = %(season)s::text)
            AND (
                %(team_like)s::text IS NULL
                OR home_team ILIKE %(team_like)s::text
                OR away_team ILIKE %(team_like)s::text
            )
            AND (%(match_day)s::integer IS NULL OR match_day = %(match_day)s::integer)
        ORDER BY match_date NULLS LAST, match_id
        LIMIT %(limit)s OFFSET %(offset)s;
        """,
        {
            "season": season,
            "team_like": _team_like(team),
            "match_day": match_day,
            "limit": safe_limit,
            "offset": safe_offset,
        },
    )


def get_match(match_id: int) -> dict[str, Any] | None:
    """Return one match with its event timeline, officials, and stats."""

    match = _fetch_one(
        """
        SELECT
            match_id,
            season,
            match_day,
            match_date,
            match_time,
            league,
            home_team,
            away_team,
            home_score,
            away_score,
            total_goals,
            goal_difference,
            result,
            winner_team,
            ground_name,
            ground_address,
            man_of_the_match,
            man_of_the_match_team,
            has_timeline,
            has_lineups,
            has_officials,
            has_stats,
            match_url
        FROM staging.matches
        WHERE match_id = %(match_id)s;
        """,
        {"match_id": match_id},
    )
    if match is None:
        return None

    match["events"] = _fetch_all(
        """
        SELECT
            event_row_key,
            match_id,
            season,
            match_day,
            event_index,
            event_type,
            event_minute_text,
            minute_total,
            minute_period,
            team_side,
            team_name,
            player_name,
            goal_type,
            sub_out_player_name,
            sub_in_player_name
        FROM staging.events
        WHERE match_id = %(match_id)s
        ORDER BY event_index NULLS LAST, event_row_key;
        """,
        {"match_id": match_id},
    )
    match["officials"] = _fetch_all(
        """
        SELECT
            official_row_key,
            match_id,
            season,
            match_day,
            role,
            official_name
        FROM staging.officials
        WHERE match_id = %(match_id)s
        ORDER BY role, official_name;
        """,
        {"match_id": match_id},
    )
    match["stats"] = _fetch_all(
        """
        SELECT
            stat_row_key,
            match_id,
            season,
            match_day,
            statistic_name,
            home_value,
            away_value
        FROM staging.stats
        WHERE match_id = %(match_id)s
        ORDER BY statistic_name;
        """,
        {"match_id": match_id},
    )
    return match


def list_teams(
    season: str | None = None,
    team: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return teams derived from match home/away rows."""

    safe_limit, safe_offset = clamp_pagination(limit, offset)
    return _fetch_all(
        """
        WITH team_matches AS (
            SELECT
                season,
                home_team AS team_name,
                match_id,
                home_score AS goals_for,
                away_score AS goals_against,
                CASE WHEN result = 'home_win' THEN 1 ELSE 0 END AS wins,
                CASE WHEN result = 'draw' THEN 1 ELSE 0 END AS draws,
                CASE WHEN result = 'away_win' THEN 1 ELSE 0 END AS losses
            FROM staging.matches
            WHERE home_team IS NOT NULL
            UNION ALL
            SELECT
                season,
                away_team AS team_name,
                match_id,
                away_score AS goals_for,
                home_score AS goals_against,
                CASE WHEN result = 'away_win' THEN 1 ELSE 0 END AS wins,
                CASE WHEN result = 'draw' THEN 1 ELSE 0 END AS draws,
                CASE WHEN result = 'home_win' THEN 1 ELSE 0 END AS losses
            FROM staging.matches
            WHERE away_team IS NOT NULL
        )
        SELECT
            team_name,
            COUNT(DISTINCT season) AS seasons_played,
            COUNT(*) AS matches_played,
            SUM(COALESCE(goals_for, 0)) AS goals_for,
            SUM(COALESCE(goals_against, 0)) AS goals_against,
            SUM(wins) AS wins,
            SUM(draws) AS draws,
            SUM(losses) AS losses
        FROM team_matches
        WHERE (%(season)s::text IS NULL OR season = %(season)s::text)
            AND (%(team_like)s::text IS NULL OR team_name ILIKE %(team_like)s::text)
        GROUP BY team_name
        ORDER BY team_name
        LIMIT %(limit)s OFFSET %(offset)s;
        """,
        {
            "season": season,
            "team_like": _team_like(team),
            "limit": safe_limit,
            "offset": safe_offset,
        },
    )


def list_events(
    season: str | None = None,
    team: str | None = None,
    match_day: int | None = None,
    event_type: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return cleaned event timeline rows with practical filters."""

    safe_limit, safe_offset = clamp_pagination(limit, offset)
    return _fetch_all(
        """
        SELECT
            event_row_key,
            match_id,
            season,
            match_day,
            event_index,
            event_type,
            event_minute_text,
            minute_total,
            minute_period,
            team_side,
            team_name,
            player_name,
            goal_type,
            sub_out_player_name,
            sub_in_player_name
        FROM staging.events
        WHERE (%(season)s::text IS NULL OR season = %(season)s::text)
            AND (%(team_like)s::text IS NULL OR team_name ILIKE %(team_like)s::text)
            AND (%(match_day)s::integer IS NULL OR match_day = %(match_day)s::integer)
            AND (%(event_type)s::text IS NULL OR event_type = %(event_type)s::text)
        ORDER BY season, match_day NULLS LAST, match_id, event_index NULLS LAST
        LIMIT %(limit)s OFFSET %(offset)s;
        """,
        {
            "season": season,
            "team_like": _team_like(team),
            "match_day": match_day,
            "event_type": event_type,
            "limit": safe_limit,
            "offset": safe_offset,
        },
    )


def list_officials(
    season: str | None = None,
    match_day: int | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return official assignments with season and match-day filters."""

    safe_limit, safe_offset = clamp_pagination(limit, offset)
    return _fetch_all(
        """
        SELECT
            official_row_key,
            match_id,
            season,
            match_day,
            role,
            official_name
        FROM staging.officials
        WHERE (%(season)s::text IS NULL OR season = %(season)s::text)
            AND (%(match_day)s::integer IS NULL OR match_day = %(match_day)s::integer)
        ORDER BY season, match_day NULLS LAST, match_id, role, official_name
        LIMIT %(limit)s OFFSET %(offset)s;
        """,
        {
            "season": season,
            "match_day": match_day,
            "limit": safe_limit,
            "offset": safe_offset,
        },
    )
