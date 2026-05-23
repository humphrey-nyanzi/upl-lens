CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.matches (
    match_id BIGINT PRIMARY KEY,
    match_url TEXT NOT NULL,
    source_season TEXT,
    season TEXT NOT NULL,
    match_date DATE,
    match_time TEXT,
    league TEXT,
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
    total_goals INTEGER,
    goal_difference INTEGER,
    result TEXT,
    winner_team TEXT,
    is_forfeit BOOLEAN NOT NULL DEFAULT FALSE,
    home_first_half_goals INTEGER,
    away_first_half_goals INTEGER,
    home_second_half_goals INTEGER,
    away_second_half_goals INTEGER,
    has_timeline BOOLEAN,
    has_lineups BOOLEAN,
    has_officials BOOLEAN,
    has_stats BOOLEAN,
    raw_ingested_at TIMESTAMPTZ,
    staged_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_staging_matches_season ON staging.matches (season);
CREATE INDEX IF NOT EXISTS idx_staging_matches_date ON staging.matches (match_date);
CREATE INDEX IF NOT EXISTS idx_staging_matches_match_day ON staging.matches (match_day);
CREATE INDEX IF NOT EXISTS idx_staging_matches_home_team ON staging.matches (home_team);
CREATE INDEX IF NOT EXISTS idx_staging_matches_away_team ON staging.matches (away_team);

CREATE TABLE IF NOT EXISTS staging.events (
    event_row_key TEXT PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES staging.matches (match_id) ON DELETE CASCADE,
    match_url TEXT,
    source_season TEXT,
    season TEXT NOT NULL,
    match_date DATE,
    match_time TEXT,
    league TEXT,
    match_day INTEGER,
    home_team TEXT,
    away_team TEXT,
    event_index INTEGER,
    event_type TEXT,
    event_minute_text TEXT,
    minute_base INTEGER,
    minute_added INTEGER,
    minute_total INTEGER,
    is_added_time BOOLEAN,
    minute_period TEXT,
    team_side TEXT,
    team_name TEXT,
    player_name TEXT,
    player_url TEXT,
    goal_type TEXT,
    sub_out_player_name TEXT,
    sub_out_player_url TEXT,
    sub_in_player_name TEXT,
    sub_in_player_url TEXT,
    is_goal BOOLEAN NOT NULL DEFAULT FALSE,
    is_yellow_card BOOLEAN NOT NULL DEFAULT FALSE,
    is_red_card BOOLEAN NOT NULL DEFAULT FALSE,
    is_substitution BOOLEAN NOT NULL DEFAULT FALSE,
    raw_ingested_at TIMESTAMPTZ,
    staged_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_staging_events_match_event UNIQUE (match_id, event_index)
);

CREATE INDEX IF NOT EXISTS idx_staging_events_season ON staging.events (season);
CREATE INDEX IF NOT EXISTS idx_staging_events_match_id ON staging.events (match_id);
CREATE INDEX IF NOT EXISTS idx_staging_events_type ON staging.events (event_type);
CREATE INDEX IF NOT EXISTS idx_staging_events_minute_total ON staging.events (minute_total);
CREATE INDEX IF NOT EXISTS idx_staging_events_team_name ON staging.events (team_name);
CREATE INDEX IF NOT EXISTS idx_staging_events_player_name ON staging.events (player_name);

CREATE TABLE IF NOT EXISTS staging.lineups (
    lineup_row_key TEXT PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES staging.matches (match_id) ON DELETE CASCADE,
    match_url TEXT,
    source_season TEXT,
    season TEXT NOT NULL,
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
    raw_ingested_at TIMESTAMPTZ,
    staged_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_staging_lineups_season ON staging.lineups (season);
CREATE INDEX IF NOT EXISTS idx_staging_lineups_match_id ON staging.lineups (match_id);
CREATE INDEX IF NOT EXISTS idx_staging_lineups_team_name ON staging.lineups (team_name);
CREATE INDEX IF NOT EXISTS idx_staging_lineups_player_name ON staging.lineups (player_name);

CREATE TABLE IF NOT EXISTS staging.staff (
    staff_row_key TEXT PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES staging.matches (match_id) ON DELETE CASCADE,
    match_url TEXT,
    source_season TEXT,
    season TEXT NOT NULL,
    match_day INTEGER,
    home_team TEXT,
    away_team TEXT,
    team_name TEXT,
    team_side TEXT,
    role TEXT,
    person_name TEXT,
    person_url TEXT,
    raw_ingested_at TIMESTAMPTZ,
    staged_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_staging_staff_season ON staging.staff (season);
CREATE INDEX IF NOT EXISTS idx_staging_staff_match_id ON staging.staff (match_id);
CREATE INDEX IF NOT EXISTS idx_staging_staff_team_name ON staging.staff (team_name);
CREATE INDEX IF NOT EXISTS idx_staging_staff_person_name ON staging.staff (person_name);

CREATE TABLE IF NOT EXISTS staging.officials (
    official_row_key TEXT PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES staging.matches (match_id) ON DELETE CASCADE,
    match_url TEXT,
    source_season TEXT,
    season TEXT NOT NULL,
    match_day INTEGER,
    home_team TEXT,
    away_team TEXT,
    role TEXT,
    official_name TEXT,
    raw_ingested_at TIMESTAMPTZ,
    staged_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_staging_officials_season ON staging.officials (season);
CREATE INDEX IF NOT EXISTS idx_staging_officials_match_id ON staging.officials (match_id);
CREATE INDEX IF NOT EXISTS idx_staging_officials_name ON staging.officials (official_name);

CREATE TABLE IF NOT EXISTS staging.stats (
    stat_row_key TEXT PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES staging.matches (match_id) ON DELETE CASCADE,
    match_url TEXT,
    source_season TEXT,
    season TEXT NOT NULL,
    match_day INTEGER,
    home_team TEXT,
    away_team TEXT,
    statistic_name TEXT,
    home_value TEXT,
    away_value TEXT,
    raw_ingested_at TIMESTAMPTZ,
    staged_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_staging_stats_match_stat UNIQUE (match_id, statistic_name)
);

CREATE INDEX IF NOT EXISTS idx_staging_stats_season ON staging.stats (season);
CREATE INDEX IF NOT EXISTS idx_staging_stats_match_id ON staging.stats (match_id);
CREATE INDEX IF NOT EXISTS idx_staging_stats_statistic_name ON staging.stats (statistic_name);

CREATE TABLE IF NOT EXISTS staging.validation_issues (
    issue_id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    check_name TEXT NOT NULL,
    schema_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    season TEXT,
    match_id BIGINT,
    row_key TEXT,
    column_name TEXT,
    issue_message TEXT NOT NULL,
    issue_value TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_staging_validation_run ON staging.validation_issues (run_id);
CREATE INDEX IF NOT EXISTS idx_staging_validation_severity ON staging.validation_issues (severity);
CREATE INDEX IF NOT EXISTS idx_staging_validation_table ON staging.validation_issues (schema_name, table_name);
CREATE INDEX IF NOT EXISTS idx_staging_validation_season ON staging.validation_issues (season);
