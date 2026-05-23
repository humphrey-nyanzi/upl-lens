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
  ground_name: string | null;
  match_url: string;
};

export type TeamResponse = {
  team_name: string;
  seasons_played: number;
  matches_played: number;
  goals_for: number;
  goals_against: number;
  wins: number;
  draws: number;
  losses: number;
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
