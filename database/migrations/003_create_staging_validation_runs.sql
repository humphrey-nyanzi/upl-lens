CREATE TABLE IF NOT EXISTS staging.validation_runs (
    run_id TEXT PRIMARY KEY,
    seasons TEXT NOT NULL,
    row_counts JSONB NOT NULL,
    issue_counts JSONB NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_staging_validation_runs_completed_at
    ON staging.validation_runs (completed_at);
