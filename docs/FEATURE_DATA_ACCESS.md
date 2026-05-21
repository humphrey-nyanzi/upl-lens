# Feature Data Access

This guide explains which data sources feature notebooks should use during Phase
6 research.

The short version:

```text
Default notebook source: staging.*
Debug source-data issues: raw.*
Legacy comparison only: raw CSV / processed CSV
Promoted reusable metrics: analytics.*
```

For rules on when to create an `analytics.*` view, see
`docs/ANALYTICS_VIEW_CONVENTIONS.md`.

## Why `staging.*` Is The Default

Most feature research should start from cleaned Postgres tables:

```text
staging.matches
staging.events
staging.lineups
staging.staff
staging.officials
staging.stats
```

These tables are already cleaned and normalized enough for app-facing work. They
also match the production route:

```text
Postgres -> FastAPI -> React
```

Using `staging.*` in notebooks reduces the risk that a notebook proves a finding
on old CSV logic that the app cannot reproduce.

## Does Reading `staging.*` Modify Production Data?

No. A normal query like this only reads data:

```sql
SELECT *
FROM staging.events
WHERE season = '2025_26';
```

The risk is not reading. The risk is accidentally running write statements such
as:

```text
UPDATE
DELETE
INSERT
DROP
TRUNCATE
CREATE
ALTER
GRANT
REVOKE
```

For that reason, notebooks should use a read-only database role where possible,
and should use the helper in `src.research`.

## Recommended Notebook Helper

Use:

```python
from src.research import read_sql

events = read_sql(
    """
    SELECT
        match_id,
        season,
        event_type,
        minute_total,
        team_name
    FROM staging.events
    WHERE season = :season
    """,
    {"season": "2025_26"},
)
```

The helper:

- returns a pandas DataFrame
- blocks obvious write statements
- runs the transaction as read-only
- reuses the project's existing `.env` database settings

## Data Source Decision Guide

Use `staging.*` when:

- exploring team, match, event, discipline, official, lineup, or stats features
- building a metric that could become an API endpoint
- comparing seasons using cleaned fields
- making charts intended for the app

Use `raw.*` when:

- checking whether the scraper captured a source field correctly
- debugging missing data
- investigating why staging has a strange value
- planning a staging improvement

Use raw or processed CSV files when:

- reproducing the original Feature 1 legacy analysis
- comparing old notebook results to the new Postgres pipeline
- the data has not been loaded into Postgres yet

Use `analytics.*` when:

- a metric has become stable
- multiple endpoints or dashboard components need the same logic
- the query is complex enough to deserve a named, versioned database view

Use `docs/FEATURE_REGISTRY.md` to record which production source a promoted
feature uses. That makes it easier to see whether a feature is backed by a
direct `staging.*` query or by a reusable `analytics.*` object.

## Read-Only Research Role

For local or hosted Postgres, create a read-only research user using:

```text
database/permissions/002_create_upl_research_reader.sql
```

This role should be allowed to `SELECT` from:

```text
raw.*
staging.*
analytics.*
```

It should not be allowed to insert, update, delete, truncate, or alter tables.

After creating the role, use its credentials in your local `.env` while working
in notebooks if you want the strongest guardrail.

## AI Agent Rules

When promoting a notebook feature, an AI agent should check:

- Did the notebook use `staging.*` or explain why it did not?
- If it used `raw.*`, was that for source-data debugging?
- If it used CSV files, is there a plan to reproduce the result from Postgres?
- Are caveats written in `research_brief.md`?
- Are product changes written in `product_plan.md`?
- Does the final feature still follow `Postgres -> FastAPI -> React`?

If the notebook proves something using CSVs only, the AI agent should not promote
the feature blindly. It should first map the analysis to `staging.*` or propose
the missing staging/analytics work.
