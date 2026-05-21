# Phase 5 Current-Season Automation

This note documents the working GitHub Actions setup for refreshing the current
UPL season.

Phase 5 has two different jobs:

- Routine refreshes update existing data rows.
- Admin migration runs change the database structure.

Keeping those jobs separate matters because the weekly workflow should use a
limited database role. It should not need permission to create schemas, alter
tables, or manage migrations.

## Routine Weekly Refresh

The routine workflow path is:

```text
GitHub Actions
  -> scrape current season from the live UPL source
  -> load raw CSV rows into Postgres raw.*
  -> verify raw row counts
  -> rebuild staging.*
  -> verify staging outputs
  -> upload raw files and automation logs as artifacts
```

The scheduled workflow uses:

```text
mode=full
apply_migrations=false
use_cache=false
```

In plain English:

- `mode=full` means the workflow updates Postgres and staging, not just
  artifacts.
- `apply_migrations=false` means schema changes are skipped.
- `use_cache=false` means the scraper refreshes from the live UPL website rather
  than trusting old cached HTML or checkpoint state.

The equivalent local command is:

```powershell
.venv\Scripts\python.exe scripts\data_platform\update_current_season.py --season 2025-26 --skip-migrations
```

## GitHub Repository Secrets

Full mode needs these repository secrets:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_SSLMODE
```

For Supabase pooler connections, `POSTGRES_USER` may need the project reference
suffix:

```text
upl_actions_loader.<project-ref>
```

The actual database role inside Postgres should still be:

```text
upl_actions_loader
```

The `<project-ref>` is the value in the Supabase project URL:

```text
https://<project-ref>.supabase.co
```

Use the SQL template at
`database/permissions/001_create_upl_actions_loader.sql` to create the loader
role from a secure Supabase SQL editor session. Replace the password placeholder
only in that secure session or in a temporary private copy. Do not commit real
passwords.

## Manual Workflow Run

From GitHub:

1. Open the repository's Actions tab.
2. Choose `Current season update`.
3. Click `Run workflow`.
4. Use:

```text
season=2025-26
mode=full
apply_migrations=false
use_cache=false
```

That is the normal safe rerun after a source-site refresh or a temporary failed
scrape.

## Admin Migration Run

Only use an admin-capable database credential when the schema has changed and
migrations need to run.

For a migration-capable manual run:

```text
mode=full
apply_migrations=true
use_cache=false
```

After the migration setup is complete, switch the GitHub secrets back to the
least-privilege loader role before relying on scheduled runs.

## Artifacts

The workflow uploads artifacts even when a run fails:

- `raw-season-<season>` contains the refreshed raw CSV files.
- `automation-logs-<season>` contains the step logs under `outputs/automation/`.

This is intentional. A failed database load can still leave useful scraped files
and logs for debugging.

## Troubleshooting

`ENOIDENTIFIER no tenant identifier provided`

The Supabase pooler did not know which project to route the connection to.
Usually this means `POSTGRES_USER` is missing the project reference suffix. For
pooler connections, use:

```text
upl_actions_loader.<project-ref>
```

`EAUTHQUERY user not found in the database`

The pooler reached the project, but Postgres could not find the role being used.
Check the role in the same Supabase project as the GitHub secrets:

```sql
SELECT rolname
FROM pg_roles
WHERE rolname = 'upl_actions_loader';
```

If that query returns no rows, rerun
`database/permissions/001_create_upl_actions_loader.sql` in the correct
Supabase project.

`permission denied for schema raw` or `permission denied for schema staging`

The connection works, but the loader role is missing data-refresh permissions.
Rerun the permissions SQL template as an admin user, then retry the workflow.

## Successful Run Checklist

A healthy routine run should show:

- The scraper found and processed the current season matches.
- The log says migrations were skipped.
- `load_raw_to_postgres` finished.
- `verify_raw_postgres_counts` finished.
- `build_staging_from_raw` finished.
- `verify_staging_outputs` finished without error-level validation issues.
- The final Phase 5 summary prints row counts and log paths.

