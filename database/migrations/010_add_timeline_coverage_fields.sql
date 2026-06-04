ALTER TABLE staging.matches
    ADD COLUMN IF NOT EXISTS timeline_status TEXT NOT NULL DEFAULT 'unknown',
    ADD COLUMN IF NOT EXISTS timeline_issue_count INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS timeline_note TEXT,
    ADD COLUMN IF NOT EXISTS scoreline_goal_count INTEGER,
    ADD COLUMN IF NOT EXISTS timeline_goal_count INTEGER,
    ADD COLUMN IF NOT EXISTS stats_assist_count INTEGER,
    ADD COLUMN IF NOT EXISTS timeline_assist_count INTEGER,
    ADD COLUMN IF NOT EXISTS stats_yellow_card_count INTEGER,
    ADD COLUMN IF NOT EXISTS timeline_yellow_card_count INTEGER,
    ADD COLUMN IF NOT EXISTS stats_red_card_count INTEGER,
    ADD COLUMN IF NOT EXISTS timeline_red_card_count INTEGER;

CREATE INDEX IF NOT EXISTS idx_staging_matches_timeline_status
    ON staging.matches (timeline_status);
