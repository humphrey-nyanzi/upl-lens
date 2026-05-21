-- Read-only role template for the deployed FastAPI backend.
--
-- Run this manually with a Supabase/Postgres admin credential after the normal
-- schema migrations have already created staging and analytics tables/views.
-- Do not commit a real password. Replace the placeholder only inside the
-- Supabase SQL editor or another secure admin session.
--
-- Plain-English permission model:
-- - The public API should read cleaned product data.
-- - The public API should not write raw scrape rows, staging rows, migrations,
--   or validation records.
-- - GitHub Actions keeps using upl_actions_loader for scheduled data refreshes.

DO $$
DECLARE
    api_password TEXT := 'REPLACE_WITH_STRONG_PASSWORD';
BEGIN
    IF api_password = 'REPLACE_WITH_STRONG_PASSWORD' THEN
        RAISE EXCEPTION 'Replace api_password before running this template.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'upl_api_reader'
    ) THEN
        EXECUTE format(
            'CREATE ROLE upl_api_reader WITH LOGIN PASSWORD %L',
            api_password
        );
    END IF;
END
$$;

DO $$
BEGIN
    EXECUTE format(
        'GRANT CONNECT ON DATABASE %I TO upl_api_reader',
        current_database()
    );
END
$$;

GRANT USAGE ON SCHEMA staging TO upl_api_reader;
GRANT USAGE ON SCHEMA analytics TO upl_api_reader;

GRANT SELECT
ON ALL TABLES IN SCHEMA staging
TO upl_api_reader;

GRANT SELECT
ON ALL TABLES IN SCHEMA analytics
TO upl_api_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA staging
GRANT SELECT
ON TABLES
TO upl_api_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA analytics
GRANT SELECT
ON TABLES
TO upl_api_reader;
