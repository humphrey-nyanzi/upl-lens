ALTER TABLE staging.matches
ADD COLUMN IF NOT EXISTS is_source_anomaly BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE staging.matches
ADD COLUMN IF NOT EXISTS source_anomaly_reason TEXT;

CREATE INDEX IF NOT EXISTS idx_staging_matches_source_anomaly
ON staging.matches (is_source_anomaly);
