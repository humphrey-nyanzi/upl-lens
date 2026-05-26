# Frontend UX Requests

This is the editable source of truth for proposed UI and UX improvements.

Use this file for requests that still need discussion, approval, or
implementation. Durable approved frontend rules belong in
[FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md). Product positioning and
audience rules belong in [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md).

## Core Rule

This document can describe desired UI and UX changes, but it does not approve
implementation by itself.

An AI agent should only implement requests whose status is:

```text
approved
```

Implemented requests should stay short here. Their lasting rules should move
into [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md).

## Status Labels

| Status | Meaning |
|--------|---------|
| `idea` | A rough thought. Not ready for implementation. |
| `draft` | Clear enough to discuss, but still not approved. |
| `needs_review` | Ready for human review or prioritization. |
| `approved` | Approved for the next implementation pass. |
| `implemented` | Built and verified. Durable decisions should already be reflected in the design system. |
| `rejected` | Do not implement unless revived later. |

## How To Add A Request

Add new requests under **Active Requests**.

```text
### Request: Short Name

Status: idea

Area:

Request:

Why it matters:

Data/API needs:

Mobile/accessibility notes:

Out of scope:

Approval notes:
```

## AI Agent Instructions

When asked to work on frontend improvements, an AI agent should:

1. Read `AGENTS.md`.
2. Read [START_HERE.md](START_HERE.md).
3. Read [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md).
4. Read this file.
5. Read [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md).
6. Inspect `frontend/src/`, `api/`, and `src/api/` only enough to understand
   the affected product surface.
7. Implement only requests marked `approved`, unless the user explicitly says
   to work on a different status.
8. Keep React dependent on FastAPI JSON. Do not make React read CSV files,
   notebooks, or exported notebook images.
9. If new data is needed, prefer a thin FastAPI endpoint and query or service
   logic under `src/api/`.
10. After implementation, move durable behavior into
    [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md), then compress this
    file's implemented entry to one short note.
11. Run `npm run build` for frontend changes and any relevant backend or API
    verification if endpoints changed.

## Active Requests

Request: Adopt Standardized Chart System

Status: implemented
Area: charts, frontend infrastructure

Request

Adopt a standardized React chart library and reusable chart system for all future analytical visualizations.

Approved Library

Primary chart library:

Recharts
Why

The current frontend creates inconsistent handcrafted visualizations that do not match the approved football intelligence visual system.

The app now requires:

reusable chart primitives
responsive analytical visuals
mobile-friendly rendering
accessible labels/tooltips
consistent spacing and styling
reusable insight layouts
Rules
All charts must use reusable wrappers/components.
Charts should answer football questions.
Charts must integrate with the design token system.
Charts must support dark and light mode.
Charts must remain readable on mobile.
Chart colors must follow semantic tokens.
Avoid decorative gradients and unnecessary animation.
Avoid ad hoc CSS-only visualizations when a proper chart is needed.
Required Initial Chart Components

Create reusable components for:

GoalTimingHeatmap
RankingBarChart
TrendLineChart
DistributionBarChart
InsightChartCard
ChartLegend
ChartTooltip
ChartEmptyState
Design Rules
Charts should sit inside reusable ChartPanel containers.
Labels must use football-readable language.
Tooltips should be compact and readable.
Legends should remain close to the chart.
Caveats should remain near affected visuals.
Charts should prioritize readability over decoration.
Avoid heavy animation.
Avoid 3D effects.
Avoid neon styling.
Avoid generic BI aesthetics.
Out Of Scope
Do not introduce dozens of chart types immediately.
Do not recreate Tableau-style dashboards.
Do not use charts where rankings/cards/tables communicate better.

Implementation note:

Recharts is now the required chart library for frontend analytical
visualizations. The initial implementation adds reusable chart primitives and
converts the live Goal Timing visualization away from handcrafted CSS bars.
Build and visual verification are user-owned for this pass.

## Approved Implementation Queue

```text
none
```

## Needs Review Queue

```text
none
```

## Implemented Archive

Implemented entries stay intentionally short.

- Mobile-first redesign mentality adopted as the default for product-facing
  frontend work.
- Frontend data needs should be mapped before adding endpoints.
- Page-based product navigation replaced the older sticky-anchor pattern.
- Compact mobile primary navigation was introduced.
- League Overview V1 was redesigned using existing API data.
- Goal Timing was implemented as a dedicated featured insight page.
- Match Explorer was implemented as an explorer page with moderate filters and
  compact match cards.
- Team Insights was implemented as a team-summary page using existing team
  data.
- Methodology and Data Notes moved into a dedicated trust-focused page.
- The app shell was widened into a real dashboard workspace with sidebar and
  aligned top bar.
- Design tokens and reusable surface primitives were introduced.
- Shared typography and metric hierarchy were strengthened.
- Loading, empty, error, and cold-start states were improved.
- Visual acceptance criteria were added to the frontend review standard.
- Recharts was adopted as the standard chart library, with reusable chart
  primitives and the Goal Timing chart converted first.

## Implementation Notes

The current approved frontend pass is complete enough to reset this file to a
planning state.

Future frontend work should either:

- come from a newly approved request in this file, or
- be explicitly requested by the user in chat

Do not reopen completed requests here unless the product direction changes or a
specific follow-up request is approved.
