"""Pydantic response models for the FastAPI backend."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ApiModel(BaseModel):
    """Base model that allows dict rows from Postgres to become JSON."""

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(ApiModel):
    status: str
    api: str
    database: str
    database_name: str
    postgres_version: str
    latest_staging_run_id: str | None = None
    latest_staging_completed_at: datetime | None = None


class SeasonResponse(ApiModel):
    season: str
    match_count: int
    first_match_date: date | None = None
    last_match_date: date | None = None
    team_count: int


class MatchSummary(ApiModel):
    match_id: int
    season: str
    match_day: int | None = None
    match_date: date | None = None
    match_time: str | None = None
    league: str | None = None
    home_team: str | None = None
    away_team: str | None = None
    home_score: int | None = None
    away_score: int | None = None
    total_goals: int | None = None
    result: str | None = None
    winner_team: str | None = None
    ground_name: str | None = None
    match_url: str


class EventResponse(ApiModel):
    event_row_key: str
    match_id: int
    season: str
    match_day: int | None = None
    event_index: int | None = None
    event_type: str | None = None
    event_minute_text: str | None = None
    minute_total: int | None = None
    minute_period: str | None = None
    team_side: str | None = None
    team_name: str | None = None
    player_name: str | None = None
    goal_type: str | None = None
    sub_out_player_name: str | None = None
    sub_in_player_name: str | None = None


class OfficialResponse(ApiModel):
    official_row_key: str
    match_id: int
    season: str
    match_day: int | None = None
    role: str | None = None
    official_name: str | None = None


class MatchStatResponse(ApiModel):
    stat_row_key: str
    match_id: int
    season: str
    match_day: int | None = None
    statistic_name: str | None = None
    home_value: str | None = None
    away_value: str | None = None


class MatchDetail(MatchSummary):
    goal_difference: int | None = None
    ground_address: str | None = None
    man_of_the_match: str | None = None
    man_of_the_match_team: str | None = None
    has_timeline: bool | None = None
    has_lineups: bool | None = None
    has_officials: bool | None = None
    has_stats: bool | None = None
    events: list[EventResponse]
    officials: list[OfficialResponse]
    stats: list[MatchStatResponse]


class TeamResponse(ApiModel):
    team_name: str
    seasons_played: int
    matches_played: int
    goals_for: int
    goals_against: int
    wins: int
    draws: int
    losses: int

