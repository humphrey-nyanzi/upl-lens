"""Column contracts for structured UPL scraper outputs."""

from __future__ import annotations

TABLE_NAMES = ("matches", "events", "lineups", "staff", "officials", "stats")
FAILED_MATCH_COLUMNS = [
    "match_url",
    "season",
    "attempt_count",
    "last_error",
    "last_attempt_at_utc",
]

MATCH_COLUMNS = [
    "match_id",
    "match_url",
    "source_page_title",
    "date",
    "time",
    "league",
    "season",
    "match_day",
    "home_team",
    "home_team_url",
    "away_team",
    "away_team_url",
    "ground_name",
    "ground_address",
    "man_of_the_match",
    "man_of_the_match_team",
    "home_score",
    "away_score",
    "home_first_half_goals",
    "away_first_half_goals",
    "home_second_half_goals",
    "away_second_half_goals",
    "has_timeline",
    "has_lineups",
    "has_officials",
    "has_stats",
]

EVENT_COLUMNS = [
    "match_id",
    "match_url",
    "date",
    "time",
    "league",
    "season",
    "match_day",
    "home_team",
    "away_team",
    "event_index",
    "event_type",
    "event_minute",
    "team_side",
    "player_name",
    "player_url",
    "goal_type",
    "sub_out_player_name",
    "sub_out_player_url",
    "sub_in_player_name",
    "sub_in_player_url",
]

LINEUP_COLUMNS = [
    "match_id",
    "match_url",
    "season",
    "match_day",
    "home_team",
    "away_team",
    "team_name",
    "team_side",
    "squad_role",
    "shirt_number",
    "player_name",
    "player_url",
    "player_position",
    "is_player_of_match",
    "swap_badge_type",
    "linked_player_name",
    "linked_shirt_number",
]

STAFF_COLUMNS = [
    "match_id",
    "match_url",
    "season",
    "match_day",
    "home_team",
    "away_team",
    "team_name",
    "team_side",
    "role",
    "person_name",
    "person_url",
]

OFFICIAL_COLUMNS = [
    "match_id",
    "match_url",
    "season",
    "match_day",
    "home_team",
    "away_team",
    "role",
    "official_name",
]

STAT_COLUMNS = [
    "match_id",
    "match_url",
    "season",
    "match_day",
    "home_team",
    "away_team",
    "statistic_name",
    "home_value",
    "away_value",
]

TABLE_COLUMNS = {
    "matches": MATCH_COLUMNS,
    "events": EVENT_COLUMNS,
    "lineups": LINEUP_COLUMNS,
    "staff": STAFF_COLUMNS,
    "officials": OFFICIAL_COLUMNS,
    "stats": STAT_COLUMNS,
}

RAW_DATABASE_TABLE_COLUMNS = {
    "matches": MATCH_COLUMNS,
    "events": EVENT_COLUMNS,
    "lineups": LINEUP_COLUMNS,
    "staff": STAFF_COLUMNS,
    "officials": OFFICIAL_COLUMNS,
    "stats": STAT_COLUMNS,
}

LEGACY_GOAL_COLUMNS = [
    "Date",
    "Time",
    "League",
    "Season",
    "Match Day",
    "home_team",
    "away_team",
    "goal_minute",
    "team_side",
    "player_name",
    "goal_type",
]

