export type HealthResponse = {
  status: string;
  api: string;
  database: string;
  database_name: string;
  postgres_version: string;
  latest_staging_run_id: string | null;
  latest_staging_completed_at: string | null;
};

export type SeasonResponse = {
  season: string;
  match_count: number;
  first_match_date: string | null;
  last_match_date: string | null;
  team_count: number;
};

export type EventBreakdownItem = {
  event_type: string;
  label: string;
  count: number;
};

export type SignalTone = "positive" | "neutral" | "warning" | "risk";
export type DataQualityStatus = "good" | "caution" | "limited";
export type TeamHomeAway = "home" | "away";
export type TeamFormResult = "W" | "D" | "L" | "N/A";
export type MatchEventPhase = "first_half" | "second_half" | "final_15" | "added_time";

export type SeasonOverviewResponse = {
  season: string;
  scope_key: string;
  season_count: number;
  match_count: number;
  team_count: number;
  goal_count: number;
  timeline_goal_count: number;
  scoreline_goal_count: number;
  event_count: number;
  yellow_card_count: number;
  red_card_count: number;
  first_match_date: string | null;
  latest_match_date: string | null;
  event_breakdown: EventBreakdownItem[];
};

export type SeasonTrendRow = {
  season: string;
  match_count: number;
  team_count: number;
  first_match_date: string | null;
  last_match_date: string | null;
  scoreline_goal_count: number;
  timeline_goal_count: number;
  goals_per_match: number | null;
  yellow_card_count: number;
  red_card_count: number;
  total_card_count: number;
  cards_per_match: number | null;
  home_wins: number;
  away_wins: number;
  draws: number;
  home_win_share: number | null;
  away_win_share: number | null;
  draw_share: number | null;
  high_scoring_match_count: number;
  high_scoring_match_share: number | null;
  goal_heavy_match_count: number;
  goal_heavy_match_share: number | null;
  timeline_complete_match_count: number;
  timeline_partial_match_count: number;
  timeline_unavailable_match_count: number;
  timeline_coverage_share: number | null;
  administrative_result_count: number;
  source_anomaly_count: number;
  data_quality_status: DataQualityStatus;
  data_quality_note: string | null;
};

export type SeasonTrendsSummary = {
  season_count: number;
  total_matches: number;
  total_scoreline_goals: number;
  total_timeline_goals: number;
  total_cards: number;
  average_goals_per_match: number | null;
  average_cards_per_match: number | null;
  earliest_season: string | null;
  latest_season: string | null;
};

export type SeasonTrendsResponse = {
  seasons: SeasonTrendRow[];
  summary: SeasonTrendsSummary;
};

export type SeasonPulse = {
  matches_covered: number;
  teams_tracked: number;
  goals_per_match: number | null;
  cards_per_match: number | null;
  timeline_coverage_share: number | null;
  high_scoring_match_share: number | null;
};

export type OverviewNotice = {
  key: string;
  title: string;
  text: string;
  tone: SignalTone;
  link_path: string | null;
};

export type TeamSignalSummary = {
  team_name: string;
  team_slug: string;
  signal: string;
  metric_value: number | null;
  metric_label: string;
};

export type OverviewDataQuality = {
  timeline_coverage_share: number | null;
  administrative_result_count: number;
  source_anomaly_count: number;
  status: DataQualityStatus;
  note: string | null;
};

export type OverviewIntelligenceResponse = {
  season: string | null;
  season_pulse: SeasonPulse;
  things_to_notice: OverviewNotice[];
  recent_signal_matches: MatchIntelligenceSummary[];
  team_signals: TeamSignalSummary[];
  data_quality: OverviewDataQuality;
};

export type GoalTimingInterval = {
  interval: string;
  start_minute: number;
  end_minute: number;
  goals: number;
  share: number;
  rank: number | null;
};

export type GoalTimingInsightResponse = {
  season: string;
  scope_key: string;
  season_count: number;
  first_match_date: string | null;
  last_match_date: string | null;
  total_regular_time_goals: number;
  peak_interval: string | null;
  intervals: GoalTimingInterval[];
};

export type MatchSummary = {
  match_id: number;
  season: string;
  match_day: number | null;
  match_date: string | null;
  match_time: string | null;
  league: string | null;
  home_team: string | null;
  away_team: string | null;
  home_score: number | null;
  away_score: number | null;
  total_goals: number | null;
  result: string | null;
  winner_team: string | null;
  is_forfeit: boolean;
  is_administrative_result: boolean;
  administrative_result_type: string | null;
  administrative_note: string | null;
  played_on_pitch: boolean;
  home_awarded_points: number | null;
  away_awarded_points: number | null;
  is_source_anomaly: boolean;
  source_anomaly_reason: string | null;
  timeline_status: string | null;
  timeline_issue_count: number;
  timeline_note: string | null;
  scoreline_goal_count: number | null;
  timeline_goal_count: number | null;
  stats_assist_count: number | null;
  timeline_assist_count: number | null;
  stats_yellow_card_count: number | null;
  timeline_yellow_card_count: number | null;
  stats_red_card_count: number | null;
  timeline_red_card_count: number | null;
  ground_name: string | null;
  match_url: string;
};

export type MatchSignal = {
  key: string;
  label: string;
  tone: SignalTone;
};

export type MatchIntelligenceSummary = {
  match_id: number;
  season: string;
  match_day: number | null;
  match_date: string | null;
  match_time: string | null;
  home_team: string | null;
  away_team: string | null;
  home_score: number | null;
  away_score: number | null;
  total_goals: number | null;
  result: string | null;
  winner_team: string | null;
  ground_name: string | null;
  timeline_status: string | null;
  is_administrative_result: boolean;
  is_source_anomaly: boolean;
  source_anomaly_reason: string | null;
  event_count: number;
  goal_count: number;
  yellow_card_count: number;
  red_card_count: number;
  late_goal_count: number;
  final_15_goal_count: number;
  signal_labels: MatchSignal[];
  interest_score: number;
  primary_signal: string | null;
  data_quality_note: string | null;
};

export type MatchIntelligenceDetail = {
  primary_signal: string | null;
  signal_labels: MatchSignal[];
  interest_score: number;
  scoring_pattern: string | null;
  decisive_phase: string | null;
  discipline_pattern: string | null;
  evidence_quality: string;
  summary_text: string | null;
};

export type MatchKeyMoment = {
  minute: number | null;
  minute_text: string | null;
  event_type: string | null;
  team_name: string | null;
  player_name: string | null;
  label: string;
  reason: string;
};

export type MatchEventPhaseSummary = {
  phase: MatchEventPhase;
  goals: number;
  yellow_cards: number;
  red_cards: number;
  substitutions: number;
  total_events: number;
};

export type ScoreProgressionPoint = {
  minute: number | null;
  minute_text: string | null;
  home_score: number;
  away_score: number;
  scoring_team: string | null;
  event_type: string | null;
};

export type TeamProfileLabel = {
  key: string;
  label: string;
  tone: SignalTone;
  description: string;
};

export type TeamSplitRecord = {
  matches: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
  points: number;
};

export type TeamFormMatch = {
  match_id: number;
  match_date: string | null;
  opponent: string | null;
  home_away: TeamHomeAway;
  result: TeamFormResult;
  scoreline: string | null;
};

export type TeamProfileMatch = {
  match_id: number;
  match_date: string | null;
  match_day: number | null;
  opponent: string | null;
  home_away: TeamHomeAway;
  home_team: string | null;
  away_team: string | null;
  home_score: number | null;
  away_score: number | null;
  result_for_team: TeamFormResult;
  total_goals: number | null;
  timeline_status: string | null;
  signal_labels: string[];
};

export type TeamEventSummary = {
  goals: number;
  assists: number;
  yellow_cards: number;
  red_cards: number;
  substitutions: number;
  events_total: number;
};

export type TeamGoalTimingInterval = {
  interval: string;
  start_minute: number;
  end_minute: number;
  goals: number;
  share: number | null;
};

export type TeamDisciplineSummary = {
  yellow_cards: number;
  red_cards: number;
  cards_per_match: number | null;
};

export type TeamProfileDataQuality = {
  timeline_coverage_matches: number;
  total_matches: number;
  timeline_coverage_share: number | null;
  administrative_matches: number;
  missing_matches: number;
  note: string | null;
};

export type TeamResponse = {
  team_name: string;
  seasons_played: number;
  matches_played: number;
  played_matches: number;
  administrative_matches: number;
  expected_matches: number | null;
  missing_matches: number;
  goals_for: number;
  goals_against: number;
  wins: number;
  draws: number;
  losses: number;
  sporting_points: number;
  administrative_points: number;
  points_adjustment: number;
  official_points: number;
  points_note: string | null;
  goal_difference: number;
  goals_per_match: number | null;
  conceded_per_match: number | null;
  win_rate: number | null;
  points_per_match: number | null;
  team_slug: string | null;
  profile_labels: TeamProfileLabel[];
};

export type TeamProfileResponse = {
  team_name: string;
  team_slug: string;
  season: string | null;
  matches_played: number;
  played_matches: number;
  administrative_matches: number;
  missing_matches: number;
  wins: number;
  draws: number;
  losses: number;
  official_points: number;
  sporting_points: number;
  points_adjustment: number;
  points_note: string | null;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  goals_per_match: number | null;
  conceded_per_match: number | null;
  win_rate: number | null;
  home_record: TeamSplitRecord | null;
  away_record: TeamSplitRecord | null;
  form: TeamFormMatch[];
  recent_matches: TeamProfileMatch[];
  event_summary: TeamEventSummary;
  goal_timing: TeamGoalTimingInterval[];
  discipline_summary: TeamDisciplineSummary;
  profile_labels: TeamProfileLabel[];
  data_quality: TeamProfileDataQuality;
};

export type PlayerProfileLabel = {
  key: string;
  label: string;
  tone: SignalTone;
};

export type PlayerSummary = {
  player_slug: string;
  player_name: string;
  primary_team: string | null;
  teams: string[];
  seasons_played: number;
  appearances: number;
  starts: number;
  bench_listings: number;
  goals: number;
  assists: number;
  yellow_cards: number;
  red_cards: number;
  substitutions_on: number;
  substitutions_off: number;
  player_of_match_awards: number;
  goal_contributions: number;
  goals_per_appearance: number | null;
  goal_contributions_per_appearance: number | null;
  starts_share: number | null;
  cards: number;
  profile_labels: PlayerProfileLabel[];
};

export type PlayerLeaderboardRow = PlayerSummary;

export type PlayerLeaderboardsResponse = {
  season: string | null;
  goals: PlayerLeaderboardRow[];
  assists: PlayerLeaderboardRow[];
  appearances: PlayerLeaderboardRow[];
  starts: PlayerLeaderboardRow[];
  goal_contributions: PlayerLeaderboardRow[];
  cards: PlayerLeaderboardRow[];
  bench_impact: PlayerLeaderboardRow[];
  data_quality_note: string | null;
};

export type PlayerSeasonSummary = {
  season: string;
  teams: string[];
  appearances: number;
  starts: number;
  bench_listings: number;
  goals: number;
  assists: number;
  yellow_cards: number;
  red_cards: number;
  substitutions_on: number;
  substitutions_off: number;
  player_of_match_awards: number;
};

export type PlayerMatchItem = {
  match_id: number;
  season: string;
  match_day: number | null;
  match_date: string | null;
  home_team: string | null;
  away_team: string | null;
  home_score: number | null;
  away_score: number | null;
  team_name: string | null;
  squad_role: string | null;
  goals: number;
  assists: number;
  yellow_cards: number;
  red_cards: number;
};

export type PlayerDetailResponse = PlayerSummary & {
  season_breakdown: PlayerSeasonSummary[];
  recent_matches: PlayerMatchItem[];
  assists_per_appearance: number | null;
  cards_per_appearance: number | null;
  season_trend: PlayerSeasonTrendPoint[];
  data_quality_note: string | null;
};

export type PlayerSeasonTrendPoint = {
  season: string;
  appearances: number;
  starts: number;
  goals: number;
  assists: number;
  goal_contributions: number;
  yellow_cards: number;
  red_cards: number;
};

export type EventResponse = {
  event_row_key: string;
  match_id: number;
  season: string;
  match_day: number | null;
  event_index: number | null;
  event_type: string | null;
  event_minute_text: string | null;
  minute_total: number | null;
  minute_period: string | null;
  team_side: string | null;
  team_name: string | null;
  player_name: string | null;
  goal_type: string | null;
  sub_out_player_name: string | null;
  sub_in_player_name: string | null;
};

export type OfficialResponse = {
  official_row_key: string;
  match_id: number;
  season: string;
  match_day: number | null;
  role: string | null;
  official_name: string | null;
};

export type MatchStatResponse = {
  stat_row_key: string;
  match_id: number;
  season: string;
  match_day: number | null;
  statistic_name: string | null;
  home_value: string | null;
  away_value: string | null;
};

export type MatchDetailResponse = MatchSummary & {
  goal_difference: number | null;
  ground_address: string | null;
  man_of_the_match: string | null;
  man_of_the_match_team: string | null;
  has_timeline: boolean | null;
  has_lineups: boolean | null;
  has_officials: boolean | null;
  has_stats: boolean | null;
  events: EventResponse[];
  officials: OfficialResponse[];
  stats: MatchStatResponse[];
  intelligence_summary: MatchIntelligenceDetail | null;
  key_moments: MatchKeyMoment[];
  event_phase_summary: MatchEventPhaseSummary[];
  score_progression: ScoreProgressionPoint[];
};
