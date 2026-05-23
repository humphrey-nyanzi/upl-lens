# Analytics View Conventions

This guide explains when notebook logic should become a direct API query, an
`analytics.*` view, or a stored analytics table.

The beginner version:

```text
staging.* = cleaned source data
analytics.* = reusable derived insight layer
FastAPI = serves the result as JSON
React = displays the result
```

Do not put exploratory notebook variables directly into production. First decide
whether the metric should be reproduced by a query, a view, or a stored table.

## The Three Choices

### 1. Direct API Query

Use this when the feature is small and the logic is easy to understand.

Good fit:

- one endpoint uses the logic
- the query is short
- the metric is not yet reused elsewhere
- the calculation is cheap

Example:

```text
Goal Timing Feature 1 currently uses a direct query on staging.events.
```

This is okay because the first slice is narrow: selected season, regular-time
goals, 15-minute intervals.

### 2. Analytics SQL View

Use this when the metric becomes a stable product concept.

Good fit:

- multiple endpoints or dashboard panels may reuse it
- the query has meaningful business logic
- the metric should have a clear database name
- the result should always reflect the latest rebuilt staging data

Example:

```sql
CREATE OR REPLACE VIEW analytics.season_goal_summary AS
SELECT
    season,
    COUNT(*) AS matches_played,
    SUM(total_goals) AS total_goals,
    SUM(total_goals)::numeric / NULLIF(COUNT(*), 0) AS goals_per_match
FROM staging.matches
GROUP BY season;
```

A normal view does not store rows separately. It stores the SQL definition. When
FastAPI queries the view, Postgres calculates the result from the current
`staging.*` data.

### 3. Stored Analytics Table Or Materialized View

Use this later, only when a normal view is not enough.

Good fit:

- the query is expensive
- the metric needs snapshot history
- the result should be refreshed as part of the data pipeline
- the calculation cannot be expressed cleanly as a simple view

This project should prefer direct queries and normal views while the research
and product layers are still small. Stored analytics tables add maintenance
work, so they should be introduced only when there is a clear reason.

## Where Derived Metrics Belong

If a notebook creates a variable like `goals_per_match`, do not add it to
`staging.*` just because it is useful.

Use this rule:

```text
raw.*      = source-shaped scraped data
staging.*  = cleaned source facts
analytics.* = derived product metrics and summaries
```

Examples:

| Metric | Recommended Production Home | Why |
|--------|-----------------------------|-----|
| `minute_total` parsed from a source event | `staging.events` | It is cleaned source data needed by many features. |
| `goals_per_match` by season | `analytics.season_goal_summary` | It is a reusable derived metric. |
| `yellow_cards_per_match` by team and season | `analytics.team_discipline_summary` | It is a reusable analytical summary. |
| one-off count for a narrow panel | direct API query | It may not need a named database object yet. |
| expensive model output refreshed nightly | analytics table or materialized view | It may need stored results and refresh logic. |

## Naming Conventions

Use clear, boring names. The name should tell a future reader what one row
represents.

Recommended patterns:

```text
analytics.season_<topic>_summary
analytics.team_season_<topic>_summary
analytics.team_match_<topic>_summary
analytics.player_season_<topic>_summary
analytics.official_season_<topic>_summary
analytics.match_<topic>_summary
```

Examples:

```text
analytics.season_goal_summary
analytics.team_season_goal_timing_summary
analytics.team_season_discipline_summary
analytics.official_season_discipline_summary
analytics.match_timeline_summary
```

Avoid names that describe the chart instead of the data. For example,
`analytics.goal_timing_bar_chart` is less useful than
`analytics.team_season_goal_timing_summary`.

## Migration Rules

Create or update analytics views through database migrations.

Do not manually create production database objects as the source of truth. If a
view matters to the app, its definition should live in `database/migrations/`.

Migration files should:

- create the `analytics` schema if needed
- use `CREATE OR REPLACE VIEW` for normal views
- include clear column names
- avoid hardcoded seasons unless the feature is intentionally season-specific
- keep comments short and useful

Suggested file naming pattern:

```text
database/migrations/00X_create_analytics_<feature_name>.sql
```

Suggested view pattern:

```sql
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.<view_name> AS
SELECT
    ...
FROM staging.<table_name>
WHERE ...
GROUP BY ...;
```

## How Views Stay Updated

Normal analytics views stay current automatically because they read from
`staging.*` at query time.

The current update path is:

```text
scrape current season
  -> load raw.*
  -> rebuild staging.*
  -> FastAPI queries staging.* or analytics views
  -> React shows updated JSON
```

If a future feature uses a materialized view or stored analytics table, the
automation workflow must add a refresh step. Until then, normal views are the
lowest-maintenance option.

## Promotion Decision Checklist

Before promoting notebook logic, decide:

- Can the result be reproduced from Postgres?
- Does it use cleaned `staging.*` data where possible?
- Is this a one-endpoint calculation or a reusable product metric?
- Would a named `analytics.*` view make the logic easier to maintain?
- Does the SQL avoid hardcoded seasons, team names, or notebook-only files?
- Does the frontend still receive JSON from FastAPI instead of reading CSVs?

## AI Agent Rules

When implementing a feature promotion, an AI agent should:

- start with the feature's `research_brief.md` and `product_plan.md`
- choose direct query, analytics view, or stored table deliberately
- explain that choice in the implementation history
- use migrations for new `analytics.*` objects
- keep route handlers thin
- keep React dependent on API JSON only

The agent should not create analytics tables or materialized views just because
they sound more professional. Use the simplest production shape that keeps the
metric reproducible and maintainable.
