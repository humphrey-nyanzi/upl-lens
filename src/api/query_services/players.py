"""Player summary queries derived from cleaned lineup and event data."""

from __future__ import annotations

from typing import Any, Literal

from src.api.query_services.common import DEFAULT_LIMIT, _fetch_all, clamp_pagination


PlayerSort = Literal["goals", "assists", "appearances", "starts", "cards", "name"]

_PLAYER_SLUG_SQL = "trim(both '-' from regexp_replace(lower(trim(%s)), '[^a-z0-9]+', '-', 'g'))"
_SORT_COLUMNS: dict[str, str] = {
    "goals": "goals DESC, assists DESC, appearances DESC, player_name",
    "assists": "assists DESC, goals DESC, appearances DESC, player_name",
    "appearances": "appearances DESC, starts DESC, goals DESC, player_name",
    "starts": "starts DESC, appearances DESC, goals DESC, player_name",
    "cards": "(yellow_cards + red_cards) DESC, red_cards DESC, player_name",
    "name": "player_name",
}


def _safe_sort(sort: str | None) -> str:
    """Return a whitelisted ORDER BY expression for player rankings."""

    return _SORT_COLUMNS.get(sort or "goals", _SORT_COLUMNS["goals"])


def list_players(
    season: str | None = None,
    player: str | None = None,
    player_slug: str | None = None,
    sort: PlayerSort = "goals",
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return player rankings from staging lineups and events."""

    safe_limit, safe_offset = clamp_pagination(limit, offset)
    player_like = f"%{player.strip()}%" if player is not None and player.strip() else None
    order_by = _safe_sort(sort)

    return _fetch_all(
        f"""
        WITH lineup_rows AS (
            SELECT
                {_PLAYER_SLUG_SQL % "lineups.player_name"} AS player_slug,
                lineups.player_name,
                lineups.team_name,
                lineups.season,
                lineups.match_id,
                lineups.squad_role,
                lineups.is_player_of_match
            FROM staging.lineups AS lineups
            JOIN staging.matches AS matches
                ON matches.match_id = lineups.match_id
            WHERE lineups.player_name IS NOT NULL
                AND (%(season)s::text IS NULL OR lineups.season = %(season)s::text)
                AND (%(player_like)s::text IS NULL OR lineups.player_name ILIKE %(player_like)s::text)
                AND matches.is_source_anomaly IS NOT TRUE
        ),
        event_rows AS (
            SELECT
                {_PLAYER_SLUG_SQL % "events.player_name"} AS player_slug,
                events.player_name,
                events.team_name,
                events.season,
                events.match_id,
                events.event_type,
                events.goal_type,
                NULL::text AS substitution_direction
            FROM staging.events AS events
            JOIN staging.matches AS matches
                ON matches.match_id = events.match_id
            WHERE events.player_name IS NOT NULL
                AND (%(season)s::text IS NULL OR events.season = %(season)s::text)
                AND (%(player_like)s::text IS NULL OR events.player_name ILIKE %(player_like)s::text)
                AND matches.is_source_anomaly IS NOT TRUE
            UNION ALL
            SELECT
                {_PLAYER_SLUG_SQL % "events.sub_in_player_name"} AS player_slug,
                events.sub_in_player_name AS player_name,
                events.team_name,
                events.season,
                events.match_id,
                events.event_type,
                events.goal_type,
                'on'::text AS substitution_direction
            FROM staging.events AS events
            JOIN staging.matches AS matches
                ON matches.match_id = events.match_id
            WHERE events.sub_in_player_name IS NOT NULL
                AND (%(season)s::text IS NULL OR events.season = %(season)s::text)
                AND (%(player_like)s::text IS NULL OR events.sub_in_player_name ILIKE %(player_like)s::text)
                AND matches.is_source_anomaly IS NOT TRUE
            UNION ALL
            SELECT
                {_PLAYER_SLUG_SQL % "events.sub_out_player_name"} AS player_slug,
                events.sub_out_player_name AS player_name,
                events.team_name,
                events.season,
                events.match_id,
                events.event_type,
                events.goal_type,
                'off'::text AS substitution_direction
            FROM staging.events AS events
            JOIN staging.matches AS matches
                ON matches.match_id = events.match_id
            WHERE events.sub_out_player_name IS NOT NULL
                AND (%(season)s::text IS NULL OR events.season = %(season)s::text)
                AND (%(player_like)s::text IS NULL OR events.sub_out_player_name ILIKE %(player_like)s::text)
                AND matches.is_source_anomaly IS NOT TRUE
        ),
        lineup_summary AS (
            SELECT
                player_slug,
                MAX(player_name) AS player_name,
                COUNT(DISTINCT season)::integer AS seasons_played,
                COUNT(DISTINCT match_id)::integer AS appearances,
                COUNT(DISTINCT match_id) FILTER (WHERE squad_role = 'starting_xi')::integer AS starts,
                COUNT(DISTINCT match_id) FILTER (WHERE squad_role = 'bench')::integer AS bench_listings,
                COUNT(*) FILTER (WHERE is_player_of_match IS TRUE)::integer AS player_of_match_awards
            FROM lineup_rows
            WHERE player_slug <> ''
            GROUP BY player_slug
        ),
        event_summary AS (
            SELECT
                player_slug,
                MAX(player_name) AS player_name,
                COUNT(*) FILTER (
                    WHERE event_type = 'goal'
                        AND lower(COALESCE(goal_type, '')) NOT LIKE '%%own%%'
                )::integer AS goals,
                COUNT(*) FILTER (WHERE event_type = 'assist')::integer AS assists,
                COUNT(*) FILTER (WHERE event_type = 'yellow_card')::integer AS yellow_cards,
                COUNT(*) FILTER (WHERE event_type = 'red_card')::integer AS red_cards,
                COUNT(*) FILTER (WHERE substitution_direction = 'on')::integer AS substitutions_on,
                COUNT(*) FILTER (WHERE substitution_direction = 'off')::integer AS substitutions_off
            FROM event_rows
            WHERE player_slug <> ''
            GROUP BY player_slug
        ),
        player_teams AS (
            SELECT player_slug, team_name, COUNT(DISTINCT match_id) AS match_count
            FROM (
                SELECT player_slug, team_name, match_id FROM lineup_rows
                UNION ALL
                SELECT player_slug, team_name, match_id FROM event_rows
            ) AS player_team_rows
            WHERE player_slug <> '' AND team_name IS NOT NULL
            GROUP BY player_slug, team_name
        ),
        team_summary AS (
            SELECT
                player_slug,
                ARRAY_AGG(team_name ORDER BY team_name) AS teams,
                (ARRAY_AGG(team_name ORDER BY match_count DESC, team_name))[1] AS primary_team
            FROM player_teams
            GROUP BY player_slug
        ),
        combined AS (
            SELECT
                COALESCE(lineup_summary.player_slug, event_summary.player_slug) AS player_slug,
                COALESCE(lineup_summary.player_name, event_summary.player_name) AS player_name,
                COALESCE(team_summary.primary_team, NULL) AS primary_team,
                COALESCE(team_summary.teams, ARRAY[]::text[]) AS teams,
                COALESCE(lineup_summary.seasons_played, 0) AS seasons_played,
                COALESCE(lineup_summary.appearances, 0) AS appearances,
                COALESCE(lineup_summary.starts, 0) AS starts,
                COALESCE(lineup_summary.bench_listings, 0) AS bench_listings,
                COALESCE(event_summary.goals, 0) AS goals,
                COALESCE(event_summary.assists, 0) AS assists,
                COALESCE(event_summary.yellow_cards, 0) AS yellow_cards,
                COALESCE(event_summary.red_cards, 0) AS red_cards,
                COALESCE(event_summary.substitutions_on, 0) AS substitutions_on,
                COALESCE(event_summary.substitutions_off, 0) AS substitutions_off,
                COALESCE(lineup_summary.player_of_match_awards, 0) AS player_of_match_awards
            FROM lineup_summary
            FULL OUTER JOIN event_summary
                ON event_summary.player_slug = lineup_summary.player_slug
            LEFT JOIN team_summary
                ON team_summary.player_slug = COALESCE(lineup_summary.player_slug, event_summary.player_slug)
        )
        SELECT *
        FROM combined
        WHERE (%(player_slug)s::text IS NULL OR player_slug = %(player_slug)s::text)
        ORDER BY {order_by}
        LIMIT %(limit)s OFFSET %(offset)s;
        """,
        {
            "season": season,
            "player_like": player_like,
            "player_slug": player_slug,
            "limit": safe_limit,
            "offset": safe_offset,
        },
    )


def get_player(player_slug: str, season: str | None = None) -> dict[str, Any] | None:
    """Return one player profile plus season and recent-match detail."""

    summary_rows = list_players(season=season, player_slug=player_slug, sort="name", limit=1, offset=0)
    summary = summary_rows[0] if summary_rows else None
    if summary is None:
        return None

    summary["season_breakdown"] = _get_player_seasons(player_slug, season=season)
    summary["recent_matches"] = _get_player_recent_matches(player_slug, season=season)
    return summary


def _get_player_seasons(player_slug: str, season: str | None = None) -> list[dict[str, Any]]:
    """Return per-season player rows for the profile view."""

    return _fetch_all(
        f"""
        WITH lineup_summary AS (
            SELECT
                {_PLAYER_SLUG_SQL % "lineups.player_name"} AS player_slug,
                lineups.season,
                ARRAY_AGG(DISTINCT lineups.team_name) FILTER (WHERE lineups.team_name IS NOT NULL) AS teams,
                COUNT(DISTINCT lineups.match_id)::integer AS appearances,
                COUNT(DISTINCT lineups.match_id) FILTER (WHERE lineups.squad_role = 'starting_xi')::integer AS starts,
                COUNT(DISTINCT lineups.match_id) FILTER (WHERE lineups.squad_role = 'bench')::integer AS bench_listings,
                COUNT(*) FILTER (WHERE lineups.is_player_of_match IS TRUE)::integer AS player_of_match_awards
            FROM staging.lineups AS lineups
            JOIN staging.matches AS matches
                ON matches.match_id = lineups.match_id
            WHERE lineups.player_name IS NOT NULL
                AND (%(season)s::text IS NULL OR lineups.season = %(season)s::text)
                AND matches.is_source_anomaly IS NOT TRUE
            GROUP BY {_PLAYER_SLUG_SQL % "lineups.player_name"}, lineups.season
        ),
        event_rows AS (
            SELECT
                {_PLAYER_SLUG_SQL % "events.player_name"} AS player_slug,
                events.season,
                events.event_type,
                events.goal_type,
                NULL::text AS substitution_direction
            FROM staging.events AS events
            JOIN staging.matches AS matches
                ON matches.match_id = events.match_id
            WHERE events.player_name IS NOT NULL
                AND (%(season)s::text IS NULL OR events.season = %(season)s::text)
                AND matches.is_source_anomaly IS NOT TRUE
            UNION ALL
            SELECT
                {_PLAYER_SLUG_SQL % "events.sub_in_player_name"} AS player_slug,
                events.season,
                events.event_type,
                events.goal_type,
                'on'::text AS substitution_direction
            FROM staging.events AS events
            JOIN staging.matches AS matches
                ON matches.match_id = events.match_id
            WHERE events.sub_in_player_name IS NOT NULL
                AND (%(season)s::text IS NULL OR events.season = %(season)s::text)
                AND matches.is_source_anomaly IS NOT TRUE
            UNION ALL
            SELECT
                {_PLAYER_SLUG_SQL % "events.sub_out_player_name"} AS player_slug,
                events.season,
                events.event_type,
                events.goal_type,
                'off'::text AS substitution_direction
            FROM staging.events AS events
            JOIN staging.matches AS matches
                ON matches.match_id = events.match_id
            WHERE events.sub_out_player_name IS NOT NULL
                AND (%(season)s::text IS NULL OR events.season = %(season)s::text)
                AND matches.is_source_anomaly IS NOT TRUE
        ),
        event_summary AS (
            SELECT
                player_slug,
                season,
                COUNT(*) FILTER (
                    WHERE event_type = 'goal'
                        AND lower(COALESCE(goal_type, '')) NOT LIKE '%%own%%'
                )::integer AS goals,
                COUNT(*) FILTER (WHERE event_type = 'assist')::integer AS assists,
                COUNT(*) FILTER (WHERE event_type = 'yellow_card')::integer AS yellow_cards,
                COUNT(*) FILTER (WHERE event_type = 'red_card')::integer AS red_cards,
                COUNT(*) FILTER (WHERE substitution_direction = 'on')::integer AS substitutions_on,
                COUNT(*) FILTER (WHERE substitution_direction = 'off')::integer AS substitutions_off
            FROM event_rows
            WHERE player_slug <> ''
            GROUP BY player_slug, season
        )
        SELECT
            COALESCE(lineup_summary.season, event_summary.season) AS season,
            COALESCE(lineup_summary.teams, ARRAY[]::text[]) AS teams,
            COALESCE(lineup_summary.appearances, 0) AS appearances,
            COALESCE(lineup_summary.starts, 0) AS starts,
            COALESCE(lineup_summary.bench_listings, 0) AS bench_listings,
            COALESCE(event_summary.goals, 0) AS goals,
            COALESCE(event_summary.assists, 0) AS assists,
            COALESCE(event_summary.yellow_cards, 0) AS yellow_cards,
            COALESCE(event_summary.red_cards, 0) AS red_cards,
            COALESCE(event_summary.substitutions_on, 0) AS substitutions_on,
            COALESCE(event_summary.substitutions_off, 0) AS substitutions_off,
            COALESCE(lineup_summary.player_of_match_awards, 0) AS player_of_match_awards
        FROM lineup_summary
        FULL OUTER JOIN event_summary
            ON event_summary.player_slug = lineup_summary.player_slug
            AND event_summary.season = lineup_summary.season
        WHERE COALESCE(lineup_summary.player_slug, event_summary.player_slug) = %(player_slug)s
        ORDER BY season DESC;
        """,
        {"player_slug": player_slug, "season": season},
    )


def _get_player_recent_matches(player_slug: str, season: str | None = None) -> list[dict[str, Any]]:
    """Return recent matches where the player appears in a lineup or event."""

    return _fetch_all(
        f"""
        WITH player_matches AS (
            SELECT
                {_PLAYER_SLUG_SQL % "lineups.player_name"} AS player_slug,
                lineups.match_id,
                lineups.team_name,
                lineups.squad_role
            FROM staging.lineups AS lineups
            WHERE lineups.player_name IS NOT NULL
            UNION
            SELECT
                {_PLAYER_SLUG_SQL % "events.player_name"} AS player_slug,
                events.match_id,
                events.team_name,
                NULL::text AS squad_role
            FROM staging.events AS events
            WHERE events.player_name IS NOT NULL
        ),
        event_counts AS (
            SELECT
                events.match_id,
                {_PLAYER_SLUG_SQL % "events.player_name"} AS player_slug,
                COUNT(*) FILTER (
                    WHERE events.event_type = 'goal'
                        AND lower(COALESCE(events.goal_type, '')) NOT LIKE '%%own%%'
                )::integer AS goals,
                COUNT(*) FILTER (WHERE events.event_type = 'assist')::integer AS assists,
                COUNT(*) FILTER (WHERE events.event_type = 'yellow_card')::integer AS yellow_cards,
                COUNT(*) FILTER (WHERE events.event_type = 'red_card')::integer AS red_cards
            FROM staging.events AS events
            WHERE events.player_name IS NOT NULL
            GROUP BY events.match_id, {_PLAYER_SLUG_SQL % "events.player_name"}
        )
        SELECT DISTINCT ON (matches.match_id)
            matches.match_id,
            matches.season,
            matches.match_day,
            matches.match_date,
            matches.home_team,
            matches.away_team,
            matches.home_score,
            matches.away_score,
            player_matches.team_name,
            player_matches.squad_role,
            COALESCE(event_counts.goals, 0) AS goals,
            COALESCE(event_counts.assists, 0) AS assists,
            COALESCE(event_counts.yellow_cards, 0) AS yellow_cards,
            COALESCE(event_counts.red_cards, 0) AS red_cards
        FROM player_matches
        JOIN staging.matches AS matches
            ON matches.match_id = player_matches.match_id
        LEFT JOIN event_counts
            ON event_counts.match_id = player_matches.match_id
            AND event_counts.player_slug = player_matches.player_slug
        WHERE player_matches.player_slug = %(player_slug)s
            AND (%(season)s::text IS NULL OR matches.season = %(season)s::text)
            AND matches.is_source_anomaly IS NOT TRUE
        ORDER BY matches.match_id, matches.match_date DESC NULLS LAST
        LIMIT 12;
        """,
        {"player_slug": player_slug, "season": season},
    )
