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
    file's implemented entry to one short note and remove the detailed
    description from active requests.
11. Run `npm run build` for frontend changes and any relevant backend or API
    verification if endpoints changed.

## Active Requests

These requests translate the approved mockup direction into specific frontend
work. The goal is one cohesive League Overview screen: compact, football-native,
dashboard-like, readable on mobile, and powered only by existing FastAPI JSON
unless a request explicitly says API work must be proposed separately.

### Request: Add Football-Native Visual Markers Without Fake Data

Status: implemented

Area: visual identity, team markers, sports-native UI

Request:

Introduce restrained football-native visual markers across Overview modules so
the page feels less like a generic dashboard and more like a UPL product, while
avoiding fake logos or unsupported data.

Why it matters:

The mockup feels sports-native partly because rankings and results include team
identity markers. The current app is credible but still visually generic in
some list modules.

Implementation requirements:

- Add a reusable marker style for teams and match rows.
- If real crest assets are unavailable, use stable initials, seeded color chips,
  or small neutral badge placeholders.
- Use markers in Top 5 Teams and Recent Matches first.
- Keep markers small; they should aid scanning, not decorate the page.
- Do not invent official crests.
- Do not use random icons that change between renders.
- Keep colors restrained and compatible with the dark sports palette.

Acceptance criteria:

- Team rows become easier to scan.
- The Overview feels more football-specific without pretending to have assets
  the project does not have.
- Markers work in both desktop and mobile row layouts.

Data/API needs:

Use existing team names. No backend change unless later real crest URLs become
available.

Mobile/accessibility notes:

Markers must not reduce label readability or tap target size. Text labels remain
the source of meaning.

Out of scope:

Do not scrape or add club crest assets in this request.

Approval notes:

Implemented in the frontend with reusable stable team markers, Top 5 team
markers, and recent-match home/away markers. No crest assets, fake logos, API
changes, or backend changes were added.



### Request: Refine Goal Timing Distribution Chart

Status: approved

Area: charts, Goal Timing, League Overview

Request:

Refine the existing Goal Timing distribution visualization into a premium football-intelligence chart rather than replacing it with a fake heatmap.

Why it matters:

The current chart structure is analytically correct, but the visual treatment still feels too generic. The chart should become a refined branded distribution chart that communicates timing patterns clearly while matching the approved visual direction.

Implementation requirements:

- Keep a bar-chart/distribution-chart structure.
- Use Recharts.
- Use six timing intervals:
  - 0–15
  - 16–30
  - 31–45
  - 46–60
  - 61–75
  - 76–90
- Use subdued green bars for regular intervals.
- Highlight the peak interval using gold/amber.
- Add subtle rounded bars.
- Use subdued gridlines.
- Keep chart height compact.
- Add a small annotation or label for the peak interval.
- Keep tooltip styling aligned with the design system.
- Keep legend and caveat close to the chart.
- Avoid excessive chart decoration.
- Avoid fake heatmap/grid systems.
- Avoid default Recharts styling.
- Ensure the chart remains highly readable on mobile.

Data/API needs:

Use existing Goal Timing API data.

Mobile/accessibility notes:

Labels and values must remain readable on smaller screens. Avoid overcrowded axes or tiny text.

Out of scope:

Do not redesign the full Goal Timing page in this request.

Approval notes:

Approved after identifying that the previous heatmap direction duplicated the timing dimension and weakened analytical clarity.

## Recommended Implementation Order

Use this order once requests are approved:

```text

```

## Implemented Archive

Implemented entries stay intentionally short.

- Mobile-first redesign mentality adopted as the default for product-facing
  frontend work.
- Convert Recent Matches Into Compact Result Rows
- Separate Overview Preview Detail From Explorer Detail
- Establish Overview First-Viewport Contract
- Rebuild KPI Row As Compact Football Scoreboard Cards
- Create Compact Overview Goal Timing Heatmap Preview
- Turn Top 5 Teams Into A Sports-Native Ranking Module
- Frontend data needs should be mapped before adding endpoints.
- Page-based product navigation replaced the older sticky-anchor pattern.
- Make Overview Main Grid A Balanced Dashboard Band
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
- The League Overview mockup acceptance checklist was added to the frontend
  design system.
- Recharts was adopted as the standard chart library, with reusable chart
  primitives and the Goal Timing chart converted first.
- Surface hierarchy and visual depth were refined with shared radius,
  elevation, border, and surface-variant rules.
- KPI and number cards were consolidated around the shared `KpiCard` component.

## Implementation Notes

The active requests above are intentionally written as design/build tickets.
They should be approved individually or in a named implementation batch before
code changes begin.

Future frontend work should either:

- come from a newly approved request in this file, or
- be explicitly requested by the user in chat

Do not reopen completed requests here unless the product direction changes or a
specific follow-up request is approved.
