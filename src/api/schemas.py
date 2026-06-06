"""Pydantic response models for the FastAPI backend."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

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


class EventBreakdownItem(ApiModel):
    event_type: str
    label: str
    count: int


class GoalTimingInterval(ApiModel):
    interval: str
    start_minute: int
    end_minute: int
    goals: int
    share: float
    rank: int | None = None


class GoalTimingInsightResponse(ApiModel):
    season: str
    scope_key: str
    season_count: int
    first_match_date: date | None = None
    last_match_date: date | None = None
    total_regular_time_goals: int
    peak_interval: str | None = None
    intervals: list[GoalTimingInterval]


class SeasonOverviewResponse(ApiModel):
    season: str
    scope_key: str
    season_count: int
    match_count: int
    team_count: int
    goal_count: int
    timeline_goal_count: int
    scoreline_goal_count: int
    event_count: int
    yellow_card_count: int
    red_card_count: int
    first_match_date: date | None = None
    latest_match_date: date | None = None
    event_breakdown: list[EventBreakdownItem]


class SeasonTrendRow(ApiModel):
    season: str
    match_count: int
    team_count: int
    first_match_date: date | None = None
    last_match_date: date | None = None
    scoreline_goal_count: int
    timeline_goal_count: int
    goals_per_match: float | None = None
    yellow_card_count: int
    red_card_count: int
    total_card_count: int
    cards_per_match: float | None = None
    home_wins: int
    away_wins: int
    draws: int
    home_win_share: float | None = None
    away_win_share: float | None = None
    draw_share: float | None = None
    high_scoring_match_count: int
    high_scoring_match_share: float | None = None
    goal_heavy_match_count: int
    goal_heavy_match_share: float | None = None
    timeline_complete_match_count: int
    timeline_partial_match_count: int
    timeline_unavailable_match_count: int
    timeline_coverage_share: float | None = None
    administrative_result_count: int
    source_anomaly_count: int
    data_quality_status: Literal["good", "caution", "limited"]
    data_quality_note: str | None = None


class SeasonTrendsSummary(ApiModel):
    season_count: int
    total_matches: int
    total_scoreline_goals: int
    total_timeline_goals: int
    total_cards: int
    average_goals_per_match: float | None = None
    average_cards_per_match: float | None = None
    earliest_season: str | None = None
    latest_season: str | None = None


class SeasonTrendsResponse(ApiModel):
    seasons: list[SeasonTrendRow]
    summary: SeasonTrendsSummary


class SeasonPulse(ApiModel):
    matches_covered: int
    teams_tracked: int
    goals_per_match: float | None = None
    cards_per_match: float | None = None
    timeline_coverage_share: float | None = None
    high_scoring_match_share: float | None = None


class OverviewNotice(ApiModel):
    key: str
    title: str
    text: str
    tone: Literal["positive", "neutral", "warning", "risk"]
    link_path: str | None = None


class TeamSignalSummary(ApiModel):
    team_name: str
    team_slug: str
    signal: str
    metric_value: float | int | None = None
    metric_label: str


class OverviewDataQuality(ApiModel):
    timeline_coverage_share: float | None = None
    administrative_result_count: int
    source_anomaly_count: int
    status: Literal["good", "caution", "limited"]
    note: str | None = None


class OverviewIntelligenceResponse(ApiModel):
    season: str | None = None
    season_pulse: SeasonPulse
    things_to_notice: list[OverviewNotice]
    recent_signal_matches: list["MatchIntelligenceSummary"]
    team_signals: list[TeamSignalSummary]
    data_quality: OverviewDataQuality


class MatchSignal(ApiModel):
    key: str
    label: str
    tone: Literal["positive", "neutral", "warning", "risk"]


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
    is_forfeit: bool = False
    is_administrative_result: bool = False
    administrative_result_type: str | None = None
    administrative_note: str | None = None
    played_on_pitch: bool = True
    home_awarded_points: int | None = None
    away_awarded_points: int | None = None
    is_source_anomaly: bool = False
    source_anomaly_reason: str | None = None
    timeline_status: str | None = None
    timeline_issue_count: int = 0
    timeline_note: str | None = None
    scoreline_goal_count: int | None = None
    timeline_goal_count: int | None = None
    stats_assist_count: int | None = None
    timeline_assist_count: int | None = None
    stats_yellow_card_count: int | None = None
    timeline_yellow_card_count: int | None = None
    stats_red_card_count: int | None = None
    timeline_red_card_count: int | None = None
    ground_name: str | None = None
    match_url: str


class MatchIntelligenceSummary(ApiModel):
    match_id: int
    season: str
    match_day: int | None = None
    match_date: date | None = None
    match_time: str | None = None
    home_team: str | None = None
    away_team: str | None = None
    home_score: int | None = None
    away_score: int | None = None
    total_goals: int | None = None
    result: str | None = None
    winner_team: str | None = None
    ground_name: str | None = None
    timeline_status: str | None = None
    is_administrative_result: bool = False
    is_source_anomaly: bool = False
    source_anomaly_reason: str | None = None
    event_count: int
    goal_count: int
    yellow_card_count: int
    red_card_count: int
    late_goal_count: int
    final_15_goal_count: int
    signal_labels: list[MatchSignal]
    interest_score: int
    primary_signal: str | None = None
    data_quality_note: str | None = None


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


class MatchIntelligenceDetail(ApiModel):
    primary_signal: str | None = None
    signal_labels: list[MatchSignal]
    interest_score: int
    scoring_pattern: str | None = None
    decisive_phase: str | None = None
    discipline_pattern: str | None = None
    evidence_quality: str
    summary_text: str | None = None


class MatchKeyMoment(ApiModel):
    minute: int | None = None
    minute_text: str | None = None
    event_type: str | None = None
    team_name: str | None = None
    player_name: str | None = None
    label: str
    reason: str


class MatchEventPhaseSummary(ApiModel):
    phase: Literal["first_half", "second_half", "final_15", "added_time"]
    goals: int
    yellow_cards: int
    red_cards: int
    substitutions: int
    total_events: int


class ScoreProgressionPoint(ApiModel):
    minute: int | None = None
    minute_text: str | None = None
    home_score: int
    away_score: int
    scoring_team: str | None = None
    event_type: str | None = None


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
    intelligence_summary: MatchIntelligenceDetail | None = None
    key_moments: list[MatchKeyMoment] = []
    event_phase_summary: list[MatchEventPhaseSummary] = []
    score_progression: list[ScoreProgressionPoint] = []


class TeamProfileLabel(ApiModel):
    key: str
    label: str
    tone: Literal["positive", "neutral", "warning", "risk"]
    description: str


class TeamSplitRecord(ApiModel):
    matches: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int


class TeamFormMatch(ApiModel):
    match_id: int
    match_date: date | None = None
    opponent: str | None = None
    home_away: Literal["home", "away"]
    result: Literal["W", "D", "L", "N/A"]
    scoreline: str | None = None


class TeamProfileMatch(ApiModel):
    match_id: int
    match_date: date | None = None
    match_day: int | None = None
    opponent: str | None = None
    home_away: Literal["home", "away"]
    home_team: str | None = None
    away_team: str | None = None
    home_score: int | None = None
    away_score: int | None = None
    result_for_team: Literal["W", "D", "L", "N/A"]
    total_goals: int | None = None
    timeline_status: str | None = None
    signal_labels: list[str]


class TeamEventSummary(ApiModel):
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int
    substitutions: int
    events_total: int


class TeamGoalTimingInterval(ApiModel):
    interval: str
    start_minute: int
    end_minute: int
    goals: int
    share: float | None = None


class TeamDisciplineSummary(ApiModel):
    yellow_cards: int
    red_cards: int
    cards_per_match: float | None = None


class TeamProfileDataQuality(ApiModel):
    timeline_coverage_matches: int
    total_matches: int
    timeline_coverage_share: float | None = None
    administrative_matches: int
    missing_matches: int
    note: str | None = None


class TeamResponse(ApiModel):
    team_name: str
    seasons_played: int
    matches_played: int
    played_matches: int
    administrative_matches: int
    expected_matches: int | None = None
    missing_matches: int
    goals_for: int
    goals_against: int
    wins: int
    draws: int
    losses: int
    sporting_points: int
    administrative_points: int
    points_adjustment: int
    official_points: int
    points_note: str | None = None
    goal_difference: int
    goals_per_match: float | None = None
    conceded_per_match: float | None = None
    win_rate: float | None = None
    points_per_match: float | None = None
    team_slug: str | None = None
    profile_labels: list[TeamProfileLabel] = []


class TeamProfileResponse(ApiModel):
    team_name: str
    team_slug: str
    season: str | None = None
    matches_played: int
    played_matches: int
    administrative_matches: int
    missing_matches: int
    wins: int
    draws: int
    losses: int
    official_points: int
    sporting_points: int
    points_adjustment: int
    points_note: str | None = None
    goals_for: int
    goals_against: int
    goal_difference: int
    goals_per_match: float | None = None
    conceded_per_match: float | None = None
    win_rate: float | None = None
    home_record: TeamSplitRecord | None = None
    away_record: TeamSplitRecord | None = None
    form: list[TeamFormMatch]
    recent_matches: list[TeamProfileMatch]
    event_summary: TeamEventSummary
    goal_timing: list[TeamGoalTimingInterval]
    discipline_summary: TeamDisciplineSummary
    profile_labels: list[TeamProfileLabel]
    data_quality: TeamProfileDataQuality


class PlayerProfileLabel(ApiModel):
    key: str
    label: str
    tone: Literal["positive", "neutral", "warning", "risk"]


class PlayerSummary(ApiModel):
    player_slug: str
    player_name: str
    primary_team: str | None = None
    teams: list[str]
    seasons_played: int
    appearances: int
    starts: int
    bench_listings: int
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int
    substitutions_on: int
    substitutions_off: int
    player_of_match_awards: int
    goal_contributions: int = 0
    goals_per_appearance: float | None = None
    goal_contributions_per_appearance: float | None = None
    starts_share: float | None = None
    cards: int = 0
    profile_labels: list[PlayerProfileLabel] = []


class PlayerLeaderboardRow(PlayerSummary):
    pass


class PlayerLeaderboardsResponse(ApiModel):
    season: str | None = None
    goals: list[PlayerLeaderboardRow]
    assists: list[PlayerLeaderboardRow]
    appearances: list[PlayerLeaderboardRow]
    starts: list[PlayerLeaderboardRow]
    goal_contributions: list[PlayerLeaderboardRow]
    cards: list[PlayerLeaderboardRow]
    bench_impact: list[PlayerLeaderboardRow]
    data_quality_note: str | None = None


class PlayerSeasonSummary(ApiModel):
    season: str
    teams: list[str]
    appearances: int
    starts: int
    bench_listings: int
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int
    substitutions_on: int
    substitutions_off: int
    player_of_match_awards: int


class PlayerSeasonTrendPoint(ApiModel):
    season: str
    appearances: int
    starts: int
    goals: int
    assists: int
    goal_contributions: int
    yellow_cards: int
    red_cards: int


class PlayerMatchItem(ApiModel):
    match_id: int
    season: str
    match_day: int | None = None
    match_date: date | None = None
    home_team: str | None = None
    away_team: str | None = None
    home_score: int | None = None
    away_score: int | None = None
    team_name: str | None = None
    squad_role: str | None = None
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int


class PlayerDetail(PlayerSummary):
    season_breakdown: list[PlayerSeasonSummary]
    recent_matches: list[PlayerMatchItem]
    assists_per_appearance: float | None = None
    cards_per_appearance: float | None = None
    season_trend: list[PlayerSeasonTrendPoint] = []
    data_quality_note: str | None = None
