"""Match list and match-detail queries."""

from __future__ import annotations

from typing import Any

from src.db.connection import get_api_psycopg_connection
from src.api.query_services.common import DEFAULT_LIMIT, _fetch_all, _fetch_one, _team_like, clamp_pagination


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
            is_forfeit,
            is_administrative_result,
            administrative_result_type,
            administrative_note,
            played_on_pitch,
            home_awarded_points,
            away_awarded_points,
            is_source_anomaly,
            source_anomaly_reason,
            ground_name,
            match_url
        FROM staging.matches
        WHERE (%(season)s::text IS NULL OR season = %(season)s::text)
            AND is_source_anomaly IS NOT TRUE
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

    with get_api_psycopg_connection() as connection:
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
                is_forfeit,
                is_administrative_result,
                administrative_result_type,
                administrative_note,
                played_on_pitch,
                home_awarded_points,
                away_awarded_points,
                is_source_anomaly,
                source_anomaly_reason,
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
            connection=connection,
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
            connection=connection,
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
            connection=connection,
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
            connection=connection,
        )
    return match

