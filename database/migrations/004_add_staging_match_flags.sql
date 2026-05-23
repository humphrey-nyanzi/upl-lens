ALTER TABLE staging.matches
ADD COLUMN IF NOT EXISTS is_forfeit BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_staging_matches_is_forfeit
ON staging.matches (is_forfeit);
