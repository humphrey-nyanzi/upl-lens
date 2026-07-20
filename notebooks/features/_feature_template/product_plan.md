# Product Plan: Feature XX - Short Feature Name

This file is the single product/implementation handoff for the feature.

Use the **Promotion Plan** section before the feature exists in the app. Use the
**Change Requests** section after the feature has already been promoted and you
want to modify it.

You do not need to know the perfect endpoint or SQL design. Write the desired
product behavior clearly; the AI agent can choose the clean technical shape
while preserving the project architecture.

Feature lifecycle status:

```text
idea
```

Allowed statuses are documented in `docs/FEATURE_PROMOTION_WORKFLOW.md`.

## Promotion Plan

Use this section for the first product version.

### Desired Product Feature

Describe what the dashboard should let users understand or compare.

### Suggested Data Shape

Describe the rows or summary the product needs.

Example:

```text
one row per team per season
```

Useful fields:

```text
season
team_name
matches_played
yellow_cards
cards_per_match
```

### Production Source

Use Postgres-backed data for product features.

Likely source:

```text
staging.events
staging.matches
analytics.<view_name_if_needed>
```

If you are not sure, write what the notebook used and let the AI agent map it to
the right production source.

Default rule:

```text
feature notebooks explore with staging.*
promoted reusable metrics may move to analytics.*
raw.* is for source-data debugging
CSVs are for legacy comparison only
```

### Production Shape Decision

Choose one, or write "AI agent should decide" with a short reason.

```text
direct API query
analytics SQL view
stored analytics table or materialized view
AI agent should decide
```

Beginner guide:

- Use a direct API query for a small first slice.
- Use an `analytics.*` view when the metric is stable or reusable.
- Use a stored analytics table/materialized view only when a normal view is too
  slow or the result must be snapshotted.

See `docs/FEATURE_PROMOTION_WORKFLOW.md` before adding database objects.

### Desired Filters

List useful filters.

```text
season
team
home_away
```

### Suggested UI

Describe the component in normal product language.

- Page/panel:
- Chart type:
- Table columns:
- Empty state:
- Mobile behavior:

### Out Of Scope For First Version

List ideas that should not be included in the first promotion pass.

### Promotion Readiness Checklist

Before asking an AI agent to promote this feature, check these items.

```text
[ ] The notebook has a final metric, chart, or table worth promoting.
[ ] The metric is explained in plain English in research_brief.md.
[ ] The data source is staging.* or there is a clear reason it is not.
[ ] Any CSV-only result has a plan to reproduce it from Postgres.
[ ] The desired product behavior is described above.
[ ] The desired filters are listed.
[ ] The expected chart or table shape is described.
[ ] Known caveats are documented.
[ ] Out-of-scope ideas are listed so the first slice stays small.
```

## Change Requests

Use this section after the feature already exists in the app.

Write change requests in normal product language. You do not need to design the
endpoint or SQL yourself.

### Request 1

Status: draft

Current behavior:

Desired behavior:

Reason:

Out of scope:

### Example Request

Status: example

Current behavior:

```text
The dashboard shows one league-wide chart for the selected season.
```

Desired behavior:

```text
Add a team filter so users can compare one team's pattern against the league
average.
```

Reason:

```text
The league-wide chart is useful, but team-level patterns are more actionable.
```

Out of scope:

```text
Do not add player-level analysis in this request.
```

### Request 2

Status: draft

Current behavior:

Desired behavior:

Reason:

Out of scope:

## Implementation History

After an AI agent implements a promotion or change request, it should add a short
entry here.

### YYYY-MM-DD

- What changed:
- Backend/API:
- Data/analytics:
- Frontend:
- Verification:
