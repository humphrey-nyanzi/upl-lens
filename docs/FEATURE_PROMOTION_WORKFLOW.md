# Feature Promotion Workflow

This document is the research playbook for the repository's Research &
Football Intelligence lane and the product surfaces that now ship as UPL
Lens.

It is the single source of truth for:

- research idea capture
- feature lifecycle status
- notebook package workflow
- notebook data-source rules
- promotion decisions for `staging.*` versus `analytics.*`
- how notebook findings become FastAPI and React product features

Use this doc with [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md) and
[PROJECT_ROADMAP.md](PROJECT_ROADMAP.md).

## Core Rule

Notebook research can be exploratory. Product features must follow the
production path:

```text
Postgres staging/analytics
  -> FastAPI query or endpoint
  -> typed JSON
  -> React dashboard component
```

React must not read CSV files, notebook outputs, exported notebook images, or
local database files directly.

Active research work should be tracked as GitHub Issues when it moves beyond a
quick note. Use the `Research / Football Intelligence` Issue template for
notebook-first questions, including discipline questions such as goal-scoring
patterns after red cards. This document owns the durable research lifecycle and
feature registry; Issues own active work, comments, handoffs, and owner review.

## Reading Order

When working in Research & Football Intelligence, read in this order:

1. [START_HERE.md](START_HERE.md)
2. [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md)
3. this workflow doc
4. the feature folder under `notebooks/features/`
5. [START_HERE.md](START_HERE.md) if you need recent repo context

## Feature Lifecycle

Use these statuses consistently for research ideas and feature packages.
These statuses describe the research feature itself. GitHub Project columns
describe active workflow state across all work areas.

| Status | Meaning | What usually happens next |
|--------|---------|---------------------------|
| `idea` | Interesting question, but not ready to work on yet. | Capture notes and leave it parked. |
| `candidate` | Plausible next research topic. Needs prioritization. | Compare it against other football questions. |
| `selected` | Chosen as the next feature package, but not created yet. | Copy the template and start a notebook package. |
| `researching` | Notebook work has started. | Keep experimenting in `analysis.ipynb`. |
| `validated` | Research produced a useful finding, metric, or chart. | Write `research_brief.md`. |
| `promotion_ready` | Ready for product planning and implementation. | Ask an AI agent or engineer to promote it. |
| `promoted` | The feature is available through FastAPI and React. | Track follow-up work in `product_plan.md`. |
| `needs_revision` | The feature exists, but the logic, caveats, data, or UI need review. | Add change requests before more implementation. |
| `parked` | Keep the idea, but do not work on it soon. | Leave it documented but inactive. |
| `rejected` | Do not pursue unless revived later. | Keep only as historical context. |

## Standard Feature Package

Each real research feature lives under `notebooks/features/`:

```text
notebooks/features/
  feature_02_card_trends/
    README.md
    analysis.ipynb
    research_brief.md
    product_plan.md
    outputs/
```

Use the template folder when starting a new feature:

```text
notebooks/features/_feature_template/
```

Example:

```powershell
Copy-Item -Recurse notebooks\features\_feature_template notebooks\features\feature_02_card_trends
```

## What Each File Does

### `analysis.ipynb`

This is the research lab.

Use it to:

- load data
- test SQL
- use pandas
- make charts
- try multiple metric definitions
- keep notes on failed attempts

The notebook can be messy while exploring. Before promotion, the final sections
should clearly show the chosen metric, final chart or table, and caveats.

### `research_brief.md`

This is the football-thinking file.

It should answer:

- What question are we answering?
- Why does it matter?
- What data did we use?
- What is the final finding?
- What are the metric definitions?
- What caveats should users know?
- What notebook evidence supports the finding?

### `product_plan.md`

This is the product and implementation handoff.

It has three jobs:

- Promotion plan: what the first app version should do
- Change requests: what should change after the feature already exists
- Implementation history: what has already been built and verified

### `outputs/`

This folder can hold notebook exports or reference charts. These files are
evidence only. The product dashboard should not depend on them.

## Notebook Data Access Rules

Use this rule:

```text
Default notebook source: staging.*
Debug source-data issues: raw.*
Legacy comparison only: CSV files
Promoted reusable metrics: analytics.*
```

### Why `staging.*` Is The Default

Most feature research should start from cleaned Postgres tables:

```text
staging.matches
staging.events
staging.lineups
staging.staff
staging.officials
staging.stats
```

These tables match the production path and reduce the risk that a notebook
proves something the app cannot reproduce later.

### Does Reading `staging.*` Modify Data?

No. Normal notebook queries are read-only.

The risk is accidentally running write statements such as:

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

Prefer a read-only research role and the helper in `src.research`.

### Recommended Notebook Helper

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

The helper returns a pandas DataFrame, blocks obvious write statements, runs the
transaction as read-only, and reuses the project's `.env` database settings.

### Data Source Decision Guide

Use `staging.*` when:

- exploring team, match, event, discipline, official, lineup, or stats features
- building a metric that could become an API endpoint
- comparing seasons using cleaned fields
- making charts intended for the app

Use `raw.*` when:

- checking whether the scraper captured a field correctly
- debugging missing data
- investigating strange staging values
- planning a staging improvement

Use CSV files only when:

- reproducing the original legacy analysis
- comparing old notebook results to the new Postgres pipeline
- the data has not been loaded into Postgres yet

Use `analytics.*` when:

- a metric has become stable
- multiple endpoints or components need the same logic
- the query is complex enough to deserve a named database contract

## Analytics Promotion Decisions

Use this rule:

```text
raw.*       = source-shaped scraped data
staging.*   = cleaned source facts
analytics.* = reusable derived product metrics and summaries
```

### Direct API Query

Use this when:

- the feature is small
- the logic is easy to understand
- one endpoint uses the logic
- the calculation is still narrow

Current example:

```text
Goal Timing Feature 1 uses a direct query on staging.events.
```

### Analytics SQL View

Use this when:

- multiple endpoints or panels may reuse the same logic
- the query has meaningful business logic
- the metric should have a stable database name
- the result should always reflect the latest staging rebuild

Create or update views through migrations in `database/migrations/`.

### Stored Analytics Table Or Materialized View

Use this later, only when:

- a normal view is too slow
- snapshot history is needed
- the refresh must be part of the pipeline
- the calculation cannot stay a normal view

This repo should prefer direct queries and normal views while the research and
product layers are still small.

### Naming Conventions

Use clear names that describe what one row represents:

```text
analytics.season_<topic>_summary
analytics.team_season_<topic>_summary
analytics.team_match_<topic>_summary
analytics.player_season_<topic>_summary
analytics.official_season_<topic>_summary
analytics.match_<topic>_summary
```

Avoid naming data objects after charts.

### Promotion Decision Checklist

Before promoting notebook logic, decide:

- Can the result be reproduced from Postgres?
- Does it use cleaned `staging.*` data where possible?
- Is this a one-endpoint calculation or a reusable product metric?
- Would a named `analytics.*` view make the logic easier to maintain?
- Does the SQL avoid hardcoded seasons, team names, or notebook-only files?
- Does the frontend still receive JSON from FastAPI instead of reading CSVs?

## Research Backlog

This section replaces the old separate research-backlog and feature-registry
docs.

### Priority Queue

```text
1. Card Trends And Discipline - candidate
2. Match Explorer Data Questions - candidate
3. Team Profiles And Home/Away Strength - idea
```

### Current Feature Table

| Feature | Status | Feature Package | Research Source | Production Source | API Endpoint | Frontend Surface | Notes |
|---------|--------|-----------------|-----------------|-------------------|--------------|------------------|-------|
| Feature 1 - Goal Timing | `promoted` | `notebooks/features/feature_01_goal_timing/` | `staging.events` via notebook and API query | direct query on `staging.events`; no `analytics.*` view yet | `GET /insights/goal-timing?season=...` | Goal Timing Explorer | First promoted research-to-product slice. Counts regular-time goal events by 15-minute interval and excludes added time. |
| Feature 2 - Card Trends And Discipline | `candidate` | none yet | likely `staging.events`, `staging.matches`, `staging.officials` | choose during promotion | none yet | Discipline Dashboard, Team Insights, League Overview insight card | Strong next candidate if card coverage is consistent enough across seasons. |
| Feature XX - Template | `idea` | `notebooks/features/_feature_template/` | `staging.*` by default | choose during promotion | none yet | none yet | Copy this package when starting a new experimental feature. |

### Active Research Ideas

#### Card Trends And Discipline

Status: `candidate`

Football question:

```text
Which teams are most disciplined or most card-prone, and how does discipline
change by season?
```

Why it matters:

```text
Discipline is easy for football users to understand, and card patterns are not
well summarized by individual official match pages.
```

Likely data:

```text
staging.events
staging.matches
staging.officials
```

Possible product surfaces:

```text
Discipline Dashboard
Team Profile discipline section
League Overview insight card
```

Key caveat:

```text
Confirm that card events are captured consistently enough across target seasons.
```

#### Dramatic Match Timelines

Status: `idea`

Football question:

```text
Which matches had the most dramatic timelines?
```

Why it matters:

```text
This could make Match Explorer more interesting than a fixture list.
```

Key caveat:

```text
Needs reliable goal ordering and match-state reconstruction.
```

#### Team Home And Away Strength

Status: `idea`

Football question:

```text
Which teams are strongest at home, and which are vulnerable away?
```

Why it matters:

```text
Home and away patterns fit naturally into team profiles and season comparison.
```

Key caveat:

```text
Check whether home and away fields are complete enough across target seasons.
```

#### Officials And Card Rates

Status: `idea`

Football question:

```text
Which officials are associated with the highest card rates?
```

Why it matters:

```text
Official patterns are rarely visible from basic match listings and could be a
useful intelligence layer.
```

Key caveat:

```text
Confirm which official role should count as the main referee and watch for
small-sample distortion.
```

## Human Workflow

1. Start with a `selected` or explicitly approved idea in this document.
2. Copy the notebook template folder.
3. Rename it with the next feature number and short slug.
4. Change the feature table row to `researching`.
5. Work in `analysis.ipynb`.
6. Write `research_brief.md`.
7. Fill in the promotion plan and readiness notes in `product_plan.md`.
8. Change the feature table row to `promotion_ready`.
9. Ask an AI agent to promote the feature.
10. After implementation, change the row to `promoted` or `needs_revision`.

## Suggested Promotion Prompt

```text
Promote notebooks/features/feature_02_card_trends into a product feature.

Read:
- docs/FEATURE_PROMOTION_WORKFLOW.md
- docs/PRODUCT_STRATEGY.md
- notebooks/features/feature_02_card_trends/README.md
- notebooks/features/feature_02_card_trends/research_brief.md
- notebooks/features/feature_02_card_trends/product_plan.md
- notebooks/features/feature_02_card_trends/analysis.ipynb

Use research_brief.md and product_plan.md as the source of truth.
Keep the frontend API-only.
Use Postgres/FastAPI/React.
Do not make React read CSV files or notebook outputs.
Keep route handlers thin and put query logic in src/api/query_services/ or an
appropriate query/service module.
Document how to run and verify the feature end to end.
After implementation, update product_plan.md implementation history and the
feature table in docs/FEATURE_PROMOTION_WORKFLOW.md.
```

## AI Agent Workflow

When asked to promote or modify a research feature, an AI agent should:

1. Read `AGENTS.md`, `.github/copilot-instructions.md`, and this workflow doc.
2. Read [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md).
3. Read the feature folder's `README.md`, `research_brief.md`, and
   `product_plan.md`.
4. Inspect the notebook only enough to understand the final metric and
   supporting evidence.
5. Confirm whether the notebook used `staging.*`, `raw.*`, CSVs, or
   `analytics.*`.
6. Identify the production-safe Postgres source.
7. Choose direct query, analytics view, or stored table deliberately.
8. Add query logic in the backend query/service layer.
9. Add or extend a thin FastAPI route.
10. Add typed response models and frontend response types.
11. Add a responsive dashboard component.
12. Update `product_plan.md`, this workflow doc's feature table, and any
    affected docs.
13. Run relevant verification commands.

The AI agent should not:

- make React read CSV files
- make React parse notebooks or exported chart images
- promote a CSV-only analysis without mapping it back to Postgres
- hide business logic inside route handlers
- add a database migration when a query over existing staging data is enough
- ignore caveats from `research_brief.md`

## Current Feature Packages

```text
notebooks/features/_feature_template/
notebooks/features/feature_01_goal_timing/
```

Ideas in notebooks are not considered product features until they are captured
in `research_brief.md`, described in `product_plan.md`, and served through
FastAPI to React.
