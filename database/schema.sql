-- UPL Match Intelligence database foundation
--
-- This file mirrors the current Phase 1 migration in a single readable place.
-- You can inspect it to understand the intended database structure, while the
-- actual setup command should run the migration files through the migration
-- runner so schema changes stay versioned.

\i migrations/001_create_raw_schema.sql
\i migrations/002_create_staging_foundation.sql
\i migrations/003_create_staging_validation_runs.sql
\i migrations/004_add_staging_match_flags.sql
