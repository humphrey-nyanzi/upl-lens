"""Team summary queries backed by stored analytics tables."""

from __future__ import annotations

from typing import Any

from src.api.intelligence import (
    bucket_goal_timing,
    build_match_signals,
    build_team_profile_labels,
    safe_rate,
    slugify,
)
from src.api.query_services.common import DEFAULT_LIMIT, _fetch_all, _team_like, clamp_pagination


def list_teams(
    season: str | None = None,
    team: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return teams from the stored analytics summary table."""

    safe_limit, safe_offset = clamp_pagination(limit, offset)
    rows = _fetch_all(
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
    return [_enrich_team_summary(row) for row in rows]


def get_team_profile(team_slug: str, season: str | None = None) -> dict[str, Any] | None:
    """Return one team profile with split records, form, events, and caveats."""

    summary = _find_team_summary_by_slug(team_slug, season=season)
    if summary is None:
        return None

    team_name = summary["team_name"]
    matches = _fetch_all(
        """
        SELECT
            match_id,
            season,
            match_day,
            match_date,
            home_team,
            away_team,
            home_score,
            away_score,
            total_goals,
            result,
            winner_team,
            timeline_status,
            is_administrative_result,
            is_source_anomaly
        FROM staging.matches
        WHERE (%(season)s::text IS NULL OR season = %(season)s::text)
            AND is_source_anomaly IS NOT TRUE
            AND (home_team = %(team_name)s::text OR away_team = %(team_name)s::text)
        ORDER BY match_date DESC NULLS LAST, match_id DESC
        LIMIT 500;
        """,
        {"season": season, "team_name": team_name},
    )
    events = _fetch_all(
        """
        SELECT
            event_type,
            minute_total,
            team_name,
            team_side
        FROM staging.events AS events
        JOIN staging.matches AS matches
            ON matches.match_id = events.match_id
        WHERE (%(season)s::text IS NULL OR events.season = %(season)s::text)
            AND events.team_name = %(team_name)s::text
            AND matches.is_source_anomaly IS NOT TRUE;
        """,
        {"season": season, "team_name": team_name},
    )

    event_summary = _team_event_summary(events)
    data_quality = _team_data_quality(summary)
    return {
        **summary,
        "season": season,
        "home_record": _split_record(matches, team_name, "home"),
        "away_record": _split_record(matches, team_name, "away"),
        "form": [_shape_form_match(match, team_name) for match in matches[:5]],
        "recent_matches": [_shape_team_match(match, team_name) for match in matches[:10]],
        "event_summary": event_summary,
        "goal_timing": bucket_goal_timing(events),
        "discipline_summary": {
            "yellow_cards": event_summary["yellow_cards"],
            "red_cards": event_summary["red_cards"],
            "cards_per_match": safe_rate(event_summary["yellow_cards"] + event_summary["red_cards"], summary["played_matches"]),
        },
        "data_quality": data_quality,
    }


def _find_team_summary_by_slug(team_slug: str, season: str | None = None) -> dict[str, Any] | None:
    for row in list_teams(season=season, limit=500, offset=0):
        if row["team_slug"] == team_slug:
            return row
    return None


def _enrich_team_summary(row: dict[str, Any]) -> dict[str, Any]:
    goal_difference = row["goals_for"] - row["goals_against"]
    played_matches = row["played_matches"] or row["matches_played"]
    enriched = {
        **row,
        "team_slug": slugify(row["team_name"]),
        "goal_difference": goal_difference,
        "goals_per_match": safe_rate(row["goals_for"], played_matches),
        "conceded_per_match": safe_rate(row["goals_against"], played_matches),
        "win_rate": safe_rate(row["wins"], played_matches),
        "points_per_match": safe_rate(row["official_points"], played_matches),
    }
    enriched["profile_labels"] = build_team_profile_labels(enriched)
    return enriched


def _team_event_summary(events: list[dict[str, Any]]) -> dict[str, int]:
    goals = sum(1 for event in events if event["event_type"] in {"goal", "own_goal", "penalty_goal"})
    yellow_cards = sum(1 for event in events if event["event_type"] == "yellow_card")
    red_cards = sum(1 for event in events if event["event_type"] == "red_card")
    substitutions = sum(1 for event in events if event["event_type"] == "substitution")
    assists = sum(1 for event in events if event["event_type"] == "assist")
    return {
        "goals": goals,
        "assists": assists,
        "yellow_cards": yellow_cards,
        "red_cards": red_cards,
        "substitutions": substitutions,
        "events_total": len(events),
    }


def _team_data_quality(summary: dict[str, Any]) -> dict[str, Any]:
    total_matches = summary["matches_played"]
    administrative_matches = summary["administrative_matches"]
    missing_matches = summary["missing_matches"]
    covered = max(summary["played_matches"] - administrative_matches, 0)
    note = None
    if administrative_matches or missing_matches:
        note = "Administrative or missing matches affect this team profile."
    return {
        "timeline_coverage_matches": covered,
        "total_matches": total_matches,
        "timeline_coverage_share": safe_rate(covered, total_matches),
        "administrative_matches": administrative_matches,
        "missing_matches": missing_matches,
        "note": note,
    }


def _split_record(matches: list[dict[str, Any]], team_name: str, side: str) -> dict[str, int]:
    side_matches = [match for match in matches if match.get(f"{side}_team") == team_name]
    record = {"matches": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "points": 0}
    for match in side_matches:
        result = _team_result(match, team_name)
        goals_for, goals_against = _team_goals(match, team_name)
        record["matches"] += 1
        record["goals_for"] += goals_for
        record["goals_against"] += goals_against
        if result == "W":
            record["wins"] += 1
            record["points"] += 3
        elif result == "D":
            record["draws"] += 1
            record["points"] += 1
        elif result == "L":
            record["losses"] += 1
    return record


def _shape_form_match(match: dict[str, Any], team_name: str) -> dict[str, Any]:
    home_away = "home" if match["home_team"] == team_name else "away"
    return {
        "match_id": match["match_id"],
        "match_date": match["match_date"],
        "opponent": match["away_team"] if home_away == "home" else match["home_team"],
        "home_away": home_away,
        "result": _team_result(match, team_name),
        "scoreline": _scoreline(match),
    }


def _shape_team_match(match: dict[str, Any], team_name: str) -> dict[str, Any]:
    home_away = "home" if match["home_team"] == team_name else "away"
    signals = [signal["label"] for signal in build_match_signals(match)]
    return {
        "match_id": match["match_id"],
        "match_date": match["match_date"],
        "match_day": match["match_day"],
        "opponent": match["away_team"] if home_away == "home" else match["home_team"],
        "home_away": home_away,
        "home_team": match["home_team"],
        "away_team": match["away_team"],
        "home_score": match["home_score"],
        "away_score": match["away_score"],
        "result_for_team": _team_result(match, team_name),
        "total_goals": match["total_goals"],
        "timeline_status": match["timeline_status"],
        "signal_labels": signals,
    }


def _team_result(match: dict[str, Any], team_name: str) -> str:
    if match.get("home_score") is None or match.get("away_score") is None:
        return "N/A"
    if match.get("home_score") == match.get("away_score"):
        return "D"
    if match.get("winner_team") == team_name:
        return "W"
    return "L"


def _team_goals(match: dict[str, Any], team_name: str) -> tuple[int, int]:
    home_score = match.get("home_score") or 0
    away_score = match.get("away_score") or 0
    if match.get("home_team") == team_name:
        return home_score, away_score
    return away_score, home_score


def _scoreline(match: dict[str, Any]) -> str | None:
    if match.get("home_score") is None or match.get("away_score") is None:
        return None
    return f"{match['home_score']}-{match['away_score']}"

