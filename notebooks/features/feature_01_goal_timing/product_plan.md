# Product Plan: Feature 01 - Goal Timing

This file is the product/implementation handoff for Feature 1. Use the
**Promotion Plan** section to understand what was first promoted. Use the
**Change Requests** section to batch future modifications before asking an AI
agent to implement them.

Feature lifecycle status:

```text
promoted
```

This status is also tracked in `docs/FEATURE_REGISTRY.md`.

## Promotion Plan

### Desired Product Feature

Show regular-time goal distribution by 15-minute interval for a selected season.

The first version should help users quickly answer:

```text
Which phase of the match produced the most regular-time goals?
```

### Suggested Data Shape

One response per selected season.

Nested interval rows:

```text
interval
start_minute
end_minute
goals
share
rank
```

### Production Source

Current source:

```text
staging.events
```

No migration was needed for the first promoted slice because `staging.events`
already contains:

```text
season
event_type
minute_total
is_added_time
```

### Production Shape Decision

Current implementation:

```text
direct API query
```

Reason:

```text
The first promoted slice is a narrow season-level aggregation used by one panel.
If future change requests add team-level reuse, home/away splits, or multiple
goal-timing panels, promote the shared logic into an analytics.* view.
```

### Desired Filters

First version:

```text
season
```

Later possible filters:

```text
team
home_away
```

### Suggested UI

Page/panel:

```text
Goal Timing Explorer
```

Chart type:

- Horizontal interval bars.

Summary:

- Total regular-time goals.
- Peak interval.

Empty state:

- Show a short message when no goal timing insight is returned.

Mobile behavior:

- Stack interval rows vertically on small screens.

### Out Of Scope For First Version

- Team-level goal timing filters.
- Home/away split.
- Match drama score.
- Decisive Impact Score.
- Opponent Vulnerability Window.
- Goal Timing Shift Index trend panel.

### Promotion Readiness Checklist

```text
[x] The notebook has a final metric, chart, or table worth promoting.
[x] The metric is explained in plain English in research_brief.md.
[x] The data source is staging.* or there is a clear reason it is not.
[x] Any CSV-only result has a plan to reproduce it from Postgres.
[x] The desired product behavior is described above.
[x] The desired filters are listed.
[x] The expected chart or table shape is described.
[x] Known caveats are documented.
[x] Out-of-scope ideas are listed so the first slice stays small.
```

## Change Requests

Use this section for future edits after the promoted feature exists.

Write requests in normal product language. The AI agent should preserve the
architecture and choose the clean technical implementation.

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
The Goal Timing Explorer shows league-wide regular-time goal distribution for a
selected season.
```

Desired behavior:

```text
Add a team filter so a user can compare a selected team's goal timing profile
against the league-wide distribution.
```

Reason:

```text
The current feature answers a league question. Team profiles would make it
useful for comparing club behavior.
```

Out of scope:

```text
Do not add player-level timing or match drama score in this request.
```

## Implementation History

### 2026-05-21

- What changed: promoted the first season-level goal timing slice into the app.
- Backend/API: added `GET /insights/goal-timing?season=...`.
- Data/analytics: used a direct query on `staging.events`; no analytics view was
  needed for the first narrow slice.
- Frontend: added a Goal Timing Explorer panel to the React dashboard.
- Verification: Python compile check, route registration check, endpoint smoke
  check, and `npm run build`.
