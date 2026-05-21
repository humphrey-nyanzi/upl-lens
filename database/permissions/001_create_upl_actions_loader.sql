-- Least-privilege role template for routine GitHub Actions updates.
--
-- Run this manually with a Supabase/Postgres admin credential after the normal
-- schema migrations have already created app_meta, raw, and staging tables.
-- Do not commit a real password. Replace the placeholder only inside the
-- Supabase SQL editor or another secure admin session.

DO $$
DECLARE
    loader_password TEXT := 'REPLACE_WITH_STRONG_PASSWORD';
BEGIN
    IF loader_password = 'REPLACE_WITH_STRONG_PASSWORD' THEN
        RAISE EXCEPTION 'Replace loader_password before running this template.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'upl_actions_loader'
    ) THEN
        EXECUTE format(
            'CREATE ROLE upl_actions_loader WITH LOGIN PASSWORD %L',
            loader_password
        );
    END IF;
END
$$;

DO $$
BEGIN
    EXECUTE format(
        'GRANT CONNECT ON DATABASE %I TO upl_actions_loader',
        current_database()
    );
END
$$;

GRANT USAGE ON SCHEMA raw TO upl_actions_loader;
GRANT USAGE ON SCHEMA staging TO upl_actions_loader;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA raw
TO upl_actions_loader;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA staging
TO upl_actions_loader;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA staging
TO upl_actions_loader;

ALTER DEFAULT PRIVILEGES IN SCHEMA raw
GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLES
TO upl_actions_loader;

ALTER DEFAULT PRIVILEGES IN SCHEMA staging
GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLES
TO upl_actions_loader;

ALTER DEFAULT PRIVILEGES IN SCHEMA staging
GRANT USAGE, SELECT
ON SEQUENCES
TO upl_actions_loader;
