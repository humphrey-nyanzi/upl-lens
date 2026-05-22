# Operations

This guide explains how routine data operations should be observed, tested, and
escalated after the initial launch build.

It belongs to the **Data Reliability & Operations** area described in
[START_HERE.md](START_HERE.md).

## What Operations Owns

Operations owns the path from source data refresh to app-safe database tables:

```text
scrape current season
  -> write raw season CSVs
  -> load raw.* Postgres tables
  -> verify raw counts
  -> rebuild staging.*
  -> verify staging outputs
  -> expose app-safe data through FastAPI
```

The normal orchestration command is:

```powershell
.venv\Scripts\python.exe scripts\data_platform\update_current_season.py --season 2025-26 --skip-migrations
```

Use `--skip-migrations` for routine refreshes because scheduled operations
should use a least-privilege loader role. Schema changes belong to a separate
admin/migration path.

## Logs And Run Summaries

Each operations run writes step logs under:

```text
outputs/automation/<season>/
```

Typical step logs include:

```text
<timestamp>_scrape_current_season.log
<timestamp>_load_raw_to_postgres.log
<timestamp>_verify_raw_postgres_counts.log
<timestamp>_build_staging_from_raw.log
<timestamp>_verify_staging_outputs.log
<timestamp>_run_summary.json
```

The step logs answer: **what happened inside this stage?**

The JSON run summary answers: **what was the final operational state?**

The run summary records:

- season
- mode
- source refresh behavior
- migration behavior
- raw verification status
- staging rebuild status
- staging verification status
- remaining failed matches
- raw CSV row counts
- raw loader row counts
- step-log paths

In GitHub Actions, upload both the raw files and `outputs/automation/` logs as
artifacts. A failed database step can still leave useful scraped files and logs
for debugging.

## Severity Ladder

Use this severity language consistently:

```text
INFO    Normal progress, such as loaded row counts.
WARNING Odd or incomplete, but not blocking.
ERROR   A stage failed or data quality is unsafe.
FATAL   The run cannot continue.
```

Examples:

- `INFO`: loaded 199 matches for the season.
- `WARNING`: a few match pages still need retry after a source timeout.
- `ERROR`: raw CSV counts do not match loaded Postgres row counts.
- `FATAL`: Postgres cannot be reached, or required credentials are missing.

## Escalation Ladder

Use this operational ladder:

```text
Level 0: Record only
Level 1: Warn in logs or summaries
Level 2: Record a validation issue
Level 3: Fail the automation run
Level 4: Require manual/admin intervention
```

Do not fail the whole pipeline for every source-data imperfection. Football
source pages can be incomplete. The key question is whether the public app would
publish structurally broken or misleading data.

Escalate to a failed run when:

- a required stage exits with an error
- raw loaded counts disagree with season CSV counts
- staging verification reports error-level validation issues
- remaining failed matches should block this specific run and
  `--fail-on-remaining-failed-matches` was requested

Escalate to manual/admin intervention when:

- routine automation needs schema-changing permissions
- a migration must be applied
- a database role or permission template must be changed
- secrets, passwords, or admin credentials may have been exposed

## Tests

The first unit-test foundation focuses on pure, high-risk logic that can break
football metrics without needing a live database:

- event-minute parsing
- event type and label normalization
- team-name normalization
- goal-type interpretation from minute annotations
- operations log-summary parsing
- JSON run-summary generation

Run the tests with:

```powershell
.venv\Scripts\python.exe -m pytest
```

These tests do not replace staging validation. They answer different questions:

```text
Unit tests: does our code behave correctly on known examples?
Validation: does today's real UPL data look safe and coherent?
```

## First Debugging Checks

When a routine update fails, check in this order:

1. Open the GitHub Actions job summary or local terminal output.
2. Open `outputs/automation/<season>/<timestamp>_run_summary.json`.
3. Open the log for the failed step.
4. If scraping failed, inspect the failed-match manifest in `data/raw/<season>/`.
5. If raw verification failed, compare raw CSV row counts with Postgres counts.
6. If staging verification failed, inspect `staging.validation_issues`.
7. If permissions failed, confirm the job is using the correct routine or admin
   database role for the task.

