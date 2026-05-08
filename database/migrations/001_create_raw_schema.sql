CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS raw.matches (
    match_id BIGINT PRIMARY KEY,
    match_url TEXT NOT NULL,
    source_page_title TEXT,
    date TEXT,
    time TEXT,
    league TEXT,
    season TEXT,
    match_day INTEGER,
    home_team TEXT,
    home_team_url TEXT,
    away_team TEXT,
    away_team_url TEXT,
    ground_name TEXT,
    ground_address TEXT,
    man_of_the_match TEXT,
    man_of_the_match_team TEXT,
    home_score INTEGER,
    away_score INTEGER,
    home_first_half_goals INTEGER,
    away_first_half_goals INTEGER,
    home_second_half_goals INTEGER,
    away_second_half_goals INTEGER,
    has_timeline BOOLEAN,
    has_lineups BOOLEAN,
    has_officials BOOLEAN,
    has_stats BOOLEAN,
    source_file TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_matches_season ON raw.matches (season);
CREATE INDEX IF NOT EXISTS idx_raw_matches_match_day ON raw.matches (match_day);
CREATE INDEX IF NOT EXISTS idx_raw_matches_date ON raw.matches (date);
CREATE INDEX IF NOT EXISTS idx_raw_matches_home_team ON raw.matches (home_team);
CREATE INDEX IF NOT EXISTS idx_raw_matches_away_team ON raw.matches (away_team);

CREATE TABLE IF NOT EXISTS raw.events (
    event_row_key TEXT PRIMARY KEY,
    match_id BIGINT NOT NULL,
    match_url TEXT,
    date TEXT,
    time TEXT,
    league TEXT,
    season TEXT,
    match_day INTEGER,
    home_team TEXT,
    away_team TEXT,
    event_index INTEGER,
    event_type TEXT,
    event_minute TEXT,
    team_side TEXT,
    player_name TEXT,
    player_url TEXT,
    goal_type TEXT,
    sub_out_player_name TEXT,
    sub_out_player_url TEXT,
    sub_in_player_name TEXT,
    sub_in_player_url TEXT,
    source_file TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_raw_events_match_event UNIQUE (match_id, event_index)
);

CREATE INDEX IF NOT EXISTS idx_raw_events_season ON raw.events (season);
CREATE INDEX IF NOT EXISTS idx_raw_events_match_id ON raw.events (match_id);
CREATE INDEX IF NOT EXISTS idx_raw_events_event_type ON raw.events (event_type);
CREATE INDEX IF NOT EXISTS idx_raw_events_team_side ON raw.events (team_side);
CREATE INDEX IF NOT EXISTS idx_raw_events_player_name ON raw.events (player_name);

CREATE TABLE IF NOT EXISTS raw.lineups (
    lineup_row_key TEXT PRIMARY KEY,
    match_id BIGINT NOT NULL,
    match_url TEXT,
    season TEXT,
    match_day INTEGER,
    home_team TEXT,
    away_team TEXT,
    team_name TEXT,
    team_side TEXT,
    squad_role TEXT,
    shirt_number INTEGER,
    player_name TEXT,
    player_url TEXT,
    player_position TEXT,
    is_player_of_match BOOLEAN,
    swap_badge_type TEXT,
    linked_player_name TEXT,
    linked_shirt_number INTEGER,
    source_file TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_raw_lineups_natural_key
    ON raw.lineups (lineup_row_key);
CREATE INDEX IF NOT EXISTS idx_raw_lineups_season ON raw.lineups (season);
CREATE INDEX IF NOT EXISTS idx_raw_lineups_match_id ON raw.lineups (match_id);
CREATE INDEX IF NOT EXISTS idx_raw_lineups_team_name ON raw.lineups (team_name);
CREATE INDEX IF NOT EXISTS idx_raw_lineups_player_name ON raw.lineups (player_name);

CREATE TABLE IF NOT EXISTS raw.staff (
    staff_row_key TEXT PRIMARY KEY,
    match_id BIGINT NOT NULL,
    match_url TEXT,
    season TEXT,
    match_day INTEGER,
    home_team TEXT,
    away_team TEXT,
    team_name TEXT,
    team_side TEXT,
    role TEXT,
    person_name TEXT,
    person_url TEXT,
    source_file TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_staff_season ON raw.staff (season);
CREATE INDEX IF NOT EXISTS idx_raw_staff_match_id ON raw.staff (match_id);
CREATE INDEX IF NOT EXISTS idx_raw_staff_team_name ON raw.staff (team_name);
CREATE INDEX IF NOT EXISTS idx_raw_staff_person_name ON raw.staff (person_name);

CREATE TABLE IF NOT EXISTS raw.officials (
    official_row_key TEXT PRIMARY KEY,
    match_id BIGINT NOT NULL,
    match_url TEXT,
    season TEXT,
    match_day INTEGER,
    home_team TEXT,
    away_team TEXT,
    role TEXT,
    official_name TEXT,
    source_file TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_officials_season ON raw.officials (season);
CREATE INDEX IF NOT EXISTS idx_raw_officials_match_id ON raw.officials (match_id);
CREATE INDEX IF NOT EXISTS idx_raw_officials_role ON raw.officials (role);
CREATE INDEX IF NOT EXISTS idx_raw_officials_name ON raw.officials (official_name);

CREATE TABLE IF NOT EXISTS raw.stats (
    stat_row_key TEXT PRIMARY KEY,
    match_id BIGINT NOT NULL,
    match_url TEXT,
    season TEXT,
    match_day INTEGER,
    home_team TEXT,
    away_team TEXT,
    statistic_name TEXT,
    home_value TEXT,
    away_value TEXT,
    source_file TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_raw_stats_match_stat UNIQUE (match_id, statistic_name)
);

CREATE INDEX IF NOT EXISTS idx_raw_stats_season ON raw.stats (season);
CREATE INDEX IF NOT EXISTS idx_raw_stats_match_id ON raw.stats (match_id);
CREATE INDEX IF NOT EXISTS idx_raw_stats_statistic_name ON raw.stats (statistic_name);

CREATE TABLE IF NOT EXISTS raw.failed_matches (
    failed_match_row_key TEXT PRIMARY KEY,
    match_url TEXT NOT NULL,
    season TEXT NOT NULL,
    attempt_count INTEGER,
    last_error TEXT,
    last_attempt_at_utc TIMESTAMPTZ,
    source_file TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_raw_failed_matches_season_url UNIQUE (season, match_url)
);

CREATE INDEX IF NOT EXISTS idx_raw_failed_matches_season ON raw.failed_matches (season);
CREATE INDEX IF NOT EXISTS idx_raw_failed_matches_attempted_at ON raw.failed_matches (last_attempt_at_utc);
