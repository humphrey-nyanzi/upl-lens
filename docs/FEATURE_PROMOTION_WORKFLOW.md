# Feature Promotion Workflow

This document explains how notebook experiments become production features in
UPL Match Intelligence.

The goal is to let the human researcher own the football logic while an AI agent
or engineer handles the production promotion and later implementation changes.

Related docs:

- `docs/RESEARCH_IDEAS.md` tracks rough football questions before they become
  formal feature packages.
- `docs/FEATURE_REGISTRY.md` tracks feature lifecycle status and where promoted
  features live.
- `docs/FEATURE_DATA_ACCESS.md` explains which data sources notebooks should
  use.
- `docs/ANALYTICS_VIEW_CONVENTIONS.md` explains when a metric should become a
  direct API query, an `analytics.*` view, or a stored analytics table.

## Core Rule

Notebook research is allowed to be exploratory. Product features must follow the
production path:

```text
Postgres staging/analytics
  -> FastAPI query/endpoint
  -> typed JSON
  -> React dashboard component
```

The React frontend must not read CSV files or notebook outputs directly.

## Standard Feature Package

Each feature lives under `notebooks/features/`:

```text
notebooks/features/
  feature_02_card_trends/
    README.md
    analysis.ipynb
    research_brief.md
    product_plan.md
    outputs/
```

Use the reusable template folder when starting a new feature:

```text
notebooks/features/_feature_template/
```

Copy it, rename the folder, and then start working.

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
- make matplotlib or seaborn charts
- try multiple definitions
- keep notes on failed attempts

The notebook can be messy while you are exploring. Before promotion, the final
sections should clearly state the chosen metric, final chart/table, and caveats.

### `research_brief.md`

This is the football-thinking file.

It should answer:

- What question are we answering?
- Why does it matter?
- What data did we use?
- What is the final finding?
- What are the metric definitions?
- What caveats should users know?
- What evidence in the notebook supports the finding?

Edit this file when the analysis or interpretation changes.

### `product_plan.md`

This is the single product/implementation handoff.

It has three jobs:

- **Promotion Plan**: what the first app version should do.
- **Change Requests**: what should change after the feature already exists.
- **Implementation History**: what has already been built and verified.

Edit this file when you want the app, API, UI, filters, copy, or behavior to
change.

You do not need to know the perfect endpoint, SQL view, or React component
structure. Write the desired product behavior clearly; the AI agent can choose
the clean technical shape while preserving the project architecture.

### `outputs/`

This folder can hold notebook exports or reference charts. These files are for
evidence and comparison only. The product dashboard should not depend on them.

## Human Workflow

1. Start with an idea in `docs/RESEARCH_IDEAS.md`.
2. Mark the idea `selected` when it is ready to become a feature package.
3. Copy the template folder.
4. Rename it with the next feature number and a short slug.
5. Add a row to `docs/FEATURE_REGISTRY.md` with status `researching`.
6. Work in `analysis.ipynb`.
7. Keep experimenting until the analysis has a useful final answer.
8. Fill in `research_brief.md`.
9. Fill in the **Promotion Plan** and readiness checklist in
   `product_plan.md`.
10. Update the registry status to `promotion_ready`.
11. Ask an AI agent to promote the feature.

Suggested first-promotion prompt:

```text
Promote notebooks/features/feature_02_card_trends into a product feature.

Read:
- docs/FEATURE_PROMOTION_WORKFLOW.md
- docs/FEATURE_DATA_ACCESS.md
- docs/FEATURE_REGISTRY.md
- docs/ANALYTICS_VIEW_CONVENTIONS.md
- notebooks/features/feature_02_card_trends/README.md
- notebooks/features/feature_02_card_trends/research_brief.md
- notebooks/features/feature_02_card_trends/product_plan.md
- notebooks/features/feature_02_card_trends/analysis.ipynb

Use research_brief.md and product_plan.md as the source of truth.
Keep the frontend API-only.
Use Postgres/FastAPI/React.
Do not make React read CSV files or notebook outputs.
Keep route handlers thin and put query logic in src/api/queries.py or an
appropriate query/service module.
Document how to run and verify the feature end to end.
After implementation, update product_plan.md implementation history and
docs/FEATURE_REGISTRY.md.
```

## Iterating On A Promoted Feature

After a feature exists in the app, do not create a new planning file. Add the
requested changes to the **Change Requests** section of `product_plan.md`.

Suggested change-request prompt:

```text
Implement the next ready change requests for notebooks/features/feature_01_goal_timing.

Read:
- docs/FEATURE_PROMOTION_WORKFLOW.md
- docs/FEATURE_DATA_ACCESS.md
- docs/FEATURE_REGISTRY.md
- docs/ANALYTICS_VIEW_CONVENTIONS.md
- notebooks/features/feature_01_goal_timing/research_brief.md
- notebooks/features/feature_01_goal_timing/product_plan.md

Use the Change Requests section of product_plan.md as the source of truth.
Preserve the architecture:
Postgres staging/analytics -> FastAPI -> JSON -> React.
After implementing, update the Implementation History section and the feature
registry if the source, endpoint, UI surface, or status changed.
```

## AI Agent Promotion Workflow

When asked to promote a feature, an AI agent should:

1. Read `AGENTS.md`, `.github/copilot-instructions.md`, and this workflow doc.
2. Read `docs/FEATURE_DATA_ACCESS.md`.
3. Read `docs/RESEARCH_IDEAS.md`.
4. Read `docs/FEATURE_REGISTRY.md` and
   `docs/ANALYTICS_VIEW_CONVENTIONS.md`.
5. Read the feature folder's `README.md`, `research_brief.md`, and
   `product_plan.md`.
6. Inspect the notebook only enough to understand the evidence and final metric.
7. Confirm whether the notebook used `staging.*`, `raw.*`, CSVs, or
   `analytics.*`, and map the result to a production-safe Postgres source.
8. Identify the production data source.
9. Decide whether to use a direct API query, an analytics SQL view, or a stored
   analytics table.
10. Add query logic in the backend query/service layer.
11. Add or extend a thin FastAPI route.
12. Add typed response models.
13. Add or extend a React client method and typed frontend response shape.
14. Add a responsive dashboard component.
15. Update docs, `product_plan.md` implementation history, and
    `docs/FEATURE_REGISTRY.md`.
16. Run relevant verification commands.

The AI agent should not:

- make React read CSV files
- make React parse notebooks or exported chart images
- promote a CSV-only analysis without mapping it back to Postgres
- promote every notebook idea at once
- ignore caveats from `research_brief.md`
- ignore out-of-scope notes from `product_plan.md`
- add a database migration when a query over existing staging data is enough
- hide business logic inside route handlers

## Promotion Decision Guide

Use a direct API query when:

- the feature is a small aggregation
- the query is easy to understand
- no reusable database object is needed yet

Use an analytics SQL view or migration when:

- multiple endpoints or dashboard panels will reuse the same logic
- the logic is complex enough that it should be versioned
- the feature needs a stable analytics contract

Use a stored analytics table or materialized view later when:

- a normal view becomes too slow
- the result needs snapshot history
- the data pipeline has an explicit refresh step for it

See `docs/ANALYTICS_VIEW_CONVENTIONS.md` for the full decision guide.

Keep the first promoted slice narrow. A good first slice usually has:

- one endpoint
- one chart or table
- one or two filters
- one clear caveat

## Current Feature Packages

```text
notebooks/features/_feature_template/
notebooks/features/feature_01_goal_timing/
```

Feature 1 has one promoted product slice:

```text
GET /insights/goal-timing?season=...
```

Ideas in a notebook are not considered product features until they are captured
in `research_brief.md`, described in `product_plan.md`, and served through
FastAPI to React.
