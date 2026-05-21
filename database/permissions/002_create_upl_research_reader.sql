-- Read-only role template for notebook research.
--
-- Run this manually with a Supabase/Postgres admin credential after the normal
-- schema migrations have already created raw, staging, and analytics schemas.
-- Do not commit a real password. Replace the placeholder only inside the
-- Supabase SQL editor or another secure admin session.

DO $$
DECLARE
    reader_password TEXT := 'REPLACE_WITH_STRONG_PASSWORD';
BEGIN
    IF reader_password = 'REPLACE_WITH_STRONG_PASSWORD' THEN
        RAISE EXCEPTION 'Replace reader_password before running this template.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'upl_research_reader'
    ) THEN
        EXECUTE format(
            'CREATE ROLE upl_research_reader WITH LOGIN PASSWORD %L',
            reader_password
        );
    END IF;
END
$$;

DO $$
BEGIN
    EXECUTE format(
        'GRANT CONNECT ON DATABASE %I TO upl_research_reader',
        current_database()
    );
END
$$;

GRANT USAGE ON SCHEMA raw TO upl_research_reader;
GRANT USAGE ON SCHEMA staging TO upl_research_reader;
GRANT USAGE ON SCHEMA analytics TO upl_research_reader;

GRANT SELECT
ON ALL TABLES IN SCHEMA raw
TO upl_research_reader;

GRANT SELECT
ON ALL TABLES IN SCHEMA staging
TO upl_research_reader;

GRANT SELECT
ON ALL TABLES IN SCHEMA analytics
TO upl_research_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA raw
GRANT SELECT
ON TABLES
TO upl_research_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA staging
GRANT SELECT
ON TABLES
TO upl_research_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA analytics
GRANT SELECT
ON TABLES
TO upl_research_reader;
