"""Event timeline list queries."""

from __future__ import annotations

from typing import Any

from src.api.query_services.common import DEFAULT_LIMIT, _fetch_all, _team_like, clamp_pagination


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
            events.event_row_key,
            events.match_id,
            events.season,
            events.match_day,
            events.event_index,
            events.event_type,
            events.event_minute_text,
            events.minute_total,
            events.minute_period,
            events.team_side,
            events.team_name,
            events.player_name,
            events.goal_type,
            events.sub_out_player_name,
            events.sub_in_player_name
        FROM staging.events AS events
        INNER JOIN staging.matches AS matches
            ON matches.match_id = events.match_id
        WHERE (%(season)s::text IS NULL OR events.season = %(season)s::text)
            AND matches.is_source_anomaly IS NOT TRUE
            AND (%(team_like)s::text IS NULL OR events.team_name ILIKE %(team_like)s::text)
            AND (%(match_day)s::integer IS NULL OR events.match_day = %(match_day)s::integer)
            AND (%(event_type)s::text IS NULL OR events.event_type = %(event_type)s::text)
        ORDER BY events.season, events.match_day NULLS LAST, events.match_id, events.event_index NULLS LAST
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

