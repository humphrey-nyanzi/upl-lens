"""Team summary queries backed by stored analytics tables."""

from __future__ import annotations

from typing import Any

from src.api.query_services.common import DEFAULT_LIMIT, _fetch_all, _team_like, clamp_pagination


def list_teams(
    season: str | None = None,
    team: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return teams from the stored analytics summary table."""

    safe_limit, safe_offset = clamp_pagination(limit, offset)
    return _fetch_all(
        """
        SELECT
            team_name,
            COUNT(DISTINCT season) AS seasons_played,
            SUM(matches_played)::integer AS matches_played,
            SUM(
                CASE
                    WHEN COALESCE(played_matches, 0) = 0 AND matches_played > 0
                    THEN matches_played
                    ELSE COALESCE(played_matches, 0)
                END
            )::integer AS played_matches,
            SUM(administrative_matches)::integer AS administrative_matches,
            SUM(expected_matches)::integer AS expected_matches,
            SUM(missing_matches)::integer AS missing_matches,
            SUM(COALESCE(goals_for, 0))::integer AS goals_for,
            SUM(COALESCE(goals_against, 0))::integer AS goals_against,
            SUM(wins)::integer AS wins,
            SUM(draws)::integer AS draws,
            SUM(losses)::integer AS losses,
            SUM(
                CASE
                    WHEN COALESCE(sporting_points, 0) = 0 AND (wins > 0 OR draws > 0)
                    THEN wins * 3 + draws
                    ELSE COALESCE(sporting_points, 0)
                END
            )::integer AS sporting_points,
            SUM(administrative_points)::integer AS administrative_points,
            SUM(points_adjustment)::integer AS points_adjustment,
            SUM(
                CASE
                    WHEN COALESCE(official_points, 0) = 0 AND (wins > 0 OR draws > 0)
                    THEN wins * 3 + draws + COALESCE(points_adjustment, 0)
                    ELSE COALESCE(official_points, 0)
                END
            )::integer AS official_points,
            NULLIF(STRING_AGG(points_note, ' ' ORDER BY season) FILTER (WHERE points_note IS NOT NULL), '') AS points_note
        FROM analytics.team_season_summary
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

