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

export type SeasonOverviewResponse = {
  season: string;
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
  ground_name: string | null;
  match_url: string;
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
};
