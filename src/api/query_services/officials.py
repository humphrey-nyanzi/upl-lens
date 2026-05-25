"""Official assignment list queries."""

from __future__ import annotations

from typing import Any

from src.api.query_services.common import DEFAULT_LIMIT, _fetch_all, clamp_pagination


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
