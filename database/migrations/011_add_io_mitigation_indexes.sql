-- Reduce hosted Supabase Disk IO by matching indexes to repeated API and
-- automation filters. These indexes are additive and do not change table data.

CREATE INDEX IF NOT EXISTS idx_raw_matches_season_key_order
    ON raw.matches ((REPLACE(REPLACE(season, '-', '_'), '/', '_')), match_day, date, match_id);

CREATE INDEX IF NOT EXISTS idx_raw_events_season_key_match
    ON raw.events ((REPLACE(REPLACE(season, '-', '_'), '/', '_')), match_id, event_type);

CREATE INDEX IF NOT EXISTS idx_raw_lineups_season_key_match
    ON raw.lineups ((REPLACE(REPLACE(season, '-', '_'), '/', '_')), match_id);

CREATE INDEX IF NOT EXISTS idx_raw_staff_season_key_match
    ON raw.staff ((REPLACE(REPLACE(season, '-', '_'), '/', '_')), match_id);

CREATE INDEX IF NOT EXISTS idx_raw_officials_season_key_match
    ON raw.officials ((REPLACE(REPLACE(season, '-', '_'), '/', '_')), match_id);

CREATE INDEX IF NOT EXISTS idx_raw_stats_season_key_match
    ON raw.stats ((REPLACE(REPLACE(season, '-', '_'), '/', '_')), match_id);

CREATE INDEX IF NOT EXISTS idx_raw_failed_matches_season_key_url
    ON raw.failed_matches ((REPLACE(REPLACE(season, '-', '_'), '/', '_')), match_url);

CREATE INDEX IF NOT EXISTS idx_staging_matches_app_safe_season_date
    ON staging.matches (season, match_date DESC, match_id DESC)
    WHERE is_source_anomaly IS NOT TRUE;

CREATE INDEX IF NOT EXISTS idx_staging_matches_app_safe_season_match_day
    ON staging.matches (season, match_day, match_id)
    WHERE is_source_anomaly IS NOT TRUE;

CREATE INDEX IF NOT EXISTS idx_staging_events_season_match_type
    ON staging.events (season, match_id, event_type);

CREATE INDEX IF NOT EXISTS idx_staging_lineups_season_player_match
    ON staging.lineups (season, player_name, match_id)
    WHERE player_name IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_staging_events_season_player_match
    ON staging.events (season, player_name, match_id)
    WHERE player_name IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_staging_events_season_sub_in_match
    ON staging.events (season, sub_in_player_name, match_id)
    WHERE sub_in_player_name IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_staging_events_season_sub_out_match
    ON staging.events (season, sub_out_player_name, match_id)
    WHERE sub_out_player_name IS NOT NULL;
