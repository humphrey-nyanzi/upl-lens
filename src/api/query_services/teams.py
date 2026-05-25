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
            SUM(COALESCE(goals_for, 0))::integer AS goals_for,
            SUM(COALESCE(goals_against, 0))::integer AS goals_against,
            SUM(wins)::integer AS wins,
            SUM(draws)::integer AS draws,
            SUM(losses)::integer AS losses
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

