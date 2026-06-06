"""Match list and match-detail queries."""

from __future__ import annotations

from typing import Any

from src.api.intelligence import (
    build_key_moments,
    build_score_progression,
    enrich_match_intelligence,
    summarize_event_phases,
)
from src.db.connection import get_api_psycopg_connection
from src.api.query_services.common import DEFAULT_LIMIT, _fetch_all, _fetch_one, _team_like, clamp_pagination


_MATCH_INTELLIGENCE_SORTS: dict[str, str] = {
    "latest": "match_date DESC NULLS LAST, match_id DESC",
    "interest": "(COALESCE(total_goals, 0) * 2 + late_goal_count * 5 + final_15_goal_count * 3 + red_card_count * 4 + yellow_card_count) DESC, match_date DESC NULLS LAST",
    "goals": "total_goals DESC NULLS LAST, match_date DESC NULLS LAST",
    "events": "event_count DESC, match_date DESC NULLS LAST",
    "cards": "(yellow_card_count + red_card_count) DESC, red_card_count DESC, match_date DESC NULLS LAST",
    "late_drama": "late_goal_count DESC, final_15_goal_count DESC, match_date DESC NULLS LAST",
}


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
            timeline_status,
            timeline_issue_count,
            timeline_note,
            scoreline_goal_count,
            timeline_goal_count,
            stats_assist_count,
            timeline_assist_count,
            stats_yellow_card_count,
            timeline_yellow_card_count,
            stats_red_card_count,
            timeline_red_card_count,
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


def list_match_intelligence(
    season: str | None = None,
    team: str | None = None,
    match_day: int | None = None,
    signal: str | None = None,
    sort: str = "interest",
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return match rows with backend-computed intelligence signals."""

    safe_limit, safe_offset = clamp_pagination(limit, offset)
    order_by = _MATCH_INTELLIGENCE_SORTS.get(sort, _MATCH_INTELLIGENCE_SORTS["interest"])
    rows = _fetch_all(
        f"""
        WITH event_summary AS (
            SELECT
                match_id,
                COUNT(*)::integer AS event_count,
                COUNT(*) FILTER (WHERE event_type IN ('goal', 'own_goal', 'penalty_goal'))::integer AS goal_count,
                COUNT(*) FILTER (WHERE event_type = 'yellow_card')::integer AS yellow_card_count,
                COUNT(*) FILTER (WHERE event_type = 'red_card')::integer AS red_card_count,
                COUNT(*) FILTER (
                    WHERE event_type IN ('goal', 'own_goal', 'penalty_goal')
                        AND minute_total >= 75
                )::integer AS late_goal_count,
                COUNT(*) FILTER (
                    WHERE event_type IN ('goal', 'own_goal', 'penalty_goal')
                        AND minute_total >= 76
                )::integer AS final_15_goal_count
            FROM staging.events
            GROUP BY match_id
        ),
        base_rows AS (
            SELECT
                matches.match_id,
                matches.season,
                matches.match_day,
                matches.match_date,
                matches.match_time,
                matches.home_team,
                matches.away_team,
                matches.home_score,
                matches.away_score,
                matches.total_goals,
                matches.result,
                matches.winner_team,
                matches.ground_name,
                matches.timeline_status,
                matches.timeline_note,
                matches.is_administrative_result,
                matches.administrative_note,
                matches.is_source_anomaly,
                matches.source_anomaly_reason,
                COALESCE(event_summary.event_count, 0)::integer AS event_count,
                COALESCE(event_summary.goal_count, 0)::integer AS goal_count,
                COALESCE(event_summary.yellow_card_count, 0)::integer AS yellow_card_count,
                COALESCE(event_summary.red_card_count, 0)::integer AS red_card_count,
                COALESCE(event_summary.late_goal_count, 0)::integer AS late_goal_count,
                COALESCE(event_summary.final_15_goal_count, 0)::integer AS final_15_goal_count
            FROM staging.matches AS matches
            LEFT JOIN event_summary
                ON event_summary.match_id = matches.match_id
            WHERE (%(season)s::text IS NULL OR matches.season = %(season)s::text)
                AND (
                    %(team_like)s::text IS NULL
                    OR matches.home_team ILIKE %(team_like)s::text
                    OR matches.away_team ILIKE %(team_like)s::text
                )
                AND (%(match_day)s::integer IS NULL OR matches.match_day = %(match_day)s::integer)
                AND matches.is_source_anomaly IS NOT TRUE
        )
        SELECT *
        FROM base_rows
        ORDER BY {order_by}
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
    enriched = [enrich_match_intelligence(row) for row in rows]
    if signal:
        enriched = [row for row in enriched if any(label["key"] == signal for label in row["signal_labels"])]
    return enriched


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
                timeline_status,
                timeline_issue_count,
                timeline_note,
                scoreline_goal_count,
                timeline_goal_count,
                stats_assist_count,
                timeline_assist_count,
                stats_yellow_card_count,
                timeline_yellow_card_count,
                stats_red_card_count,
                timeline_red_card_count,
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
        event_counts = {
            "event_count": len(match["events"]),
            "goal_count": sum(1 for event in match["events"] if event.get("event_type") in {"goal", "own_goal", "penalty_goal"}),
            "yellow_card_count": sum(1 for event in match["events"] if event.get("event_type") == "yellow_card"),
            "red_card_count": sum(1 for event in match["events"] if event.get("event_type") == "red_card"),
            "late_goal_count": sum(
                1
                for event in match["events"]
                if event.get("event_type") in {"goal", "own_goal", "penalty_goal"} and (event.get("minute_total") or 0) >= 75
            ),
            "final_15_goal_count": sum(
                1
                for event in match["events"]
                if event.get("event_type") in {"goal", "own_goal", "penalty_goal"} and (event.get("minute_total") or 0) >= 76
            ),
        }
        match_intelligence = enrich_match_intelligence({**match, **event_counts})
        match["intelligence_summary"] = _build_match_intelligence_detail(match_intelligence, match["events"])
        match["key_moments"] = build_key_moments(match, match["events"])
        match["event_phase_summary"] = summarize_event_phases(match["events"])
        match["score_progression"] = build_score_progression(match, match["events"])
    return match


def _build_match_intelligence_detail(row: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    goals = row.get("goal_count") or 0
    red_cards = row.get("red_card_count") or 0
    late_goals = row.get("late_goal_count") or 0
    scoring_pattern = None
    if goals >= 5:
        scoring_pattern = "Goal-heavy match"
    elif goals >= 3:
        scoring_pattern = "High-scoring match"
    elif goals == 0:
        scoring_pattern = "Low-scoring or goalless match"

    phase_rows = summarize_event_phases(events)
    decisive_phase = None
    if phase_rows:
        top_phase = max(phase_rows, key=lambda phase: (phase["goals"], phase["total_events"]))
        if top_phase["goals"] > 0:
            decisive_phase = top_phase["phase"]

    discipline_pattern = None
    if red_cards:
        discipline_pattern = "Red-card match"
    elif (row.get("yellow_card_count") or 0) >= 5:
        discipline_pattern = "High-card match"

    evidence_quality = "complete" if row.get("timeline_status") == "complete" else row.get("timeline_status") or "unknown"
    summary_text = _match_summary_text(row, scoring_pattern, discipline_pattern, late_goals)
    return {
        "primary_signal": row.get("primary_signal"),
        "signal_labels": row.get("signal_labels", []),
        "interest_score": row.get("interest_score", 0),
        "scoring_pattern": scoring_pattern,
        "decisive_phase": decisive_phase,
        "discipline_pattern": discipline_pattern,
        "evidence_quality": evidence_quality,
        "summary_text": summary_text,
    }


def _match_summary_text(
    row: dict[str, Any],
    scoring_pattern: str | None,
    discipline_pattern: str | None,
    late_goals: int,
) -> str | None:
    fragments: list[str] = []
    if scoring_pattern:
        fragments.append(scoring_pattern.lower())
    if late_goals:
        fragments.append("late scoring")
    if discipline_pattern:
        fragments.append(discipline_pattern.lower())
    if row.get("data_quality_note"):
        fragments.append("data caveat")
    if not fragments:
        return None
    return "This match is flagged for " + ", ".join(fragments) + "."

