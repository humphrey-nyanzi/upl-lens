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
    file's implemented entry to one short note and remove the detailed description from active requests
11. Run `npm run build` for frontend changes and any relevant backend or API
    verification if endpoints changed.

## Active Requests


### Request: Build A Real Goal Timing Heatmap

Status: approved

Area: charts, Goal Timing, visual identity

Request:

Replace the current Goal Timing chart alias with a real branded heatmap component that becomes the signature visualization of UPL Match Intelligence.

Why it matters:

Goal Timing is the flagship insight. The current implementation uses a basic distribution bar chart, which does not match the approved mockup or the intended heatmap-led product identity.

Implementation requirements:

- Create a dedicated `GoalTimingHeatmap` component instead of wrapping `DistributionBarChart`.
- Show each timing interval as a heatmap cell.
- Use a green-to-gold intensity scale:
  - low values: muted dark green
  - medium values: football green
  - high/peak values: lime/gold highlight
- Clearly label the peak interval in text and visually.
- Include interval labels such as `0–15`, `16–30`, `31–45`, `46–60`, `61–75`, `76–90`.
- Include the value and percentage where space allows.
- Provide an accessible value list fallback below or near the heatmap.
- Keep the legend close to the chart.
- Keep added-time caveat close to the chart.
- Support dark and light mode tokens.
- Avoid decorative fake heatmaps that do not reflect actual values.

Data/API needs:

Use the existing Goal Timing API data. No backend changes unless the current payload lacks percentage values needed for display.

Mobile/accessibility notes:

On mobile, cells may stack into a 2-column or single-column layout if a full grid becomes unreadable. Do not rely on color alone; text values must remain available.

Out of scope:

Do not redesign the whole Goal Timing page yet. This request only creates the reusable heatmap and updates current Goal Timing usages.

Approval notes:

Approved because the heatmap is the visual anchor of the target mockup and should be fixed before broader page redesign.

### Request: Redesign League Overview To Match Approved Dashboard Structure

Status: approved

Area: League Overview, layout, dashboard composition

Request:

Redesign only the League Overview page using the approved hybrid mockup structure after the shared surface system and real Goal Timing Heatmap are implemented.

Why it matters:

League Overview is the first impression of the app. It should prove the visual direction before the same system is applied to other pages.

Target desktop structure:

```text
PageHero / League Status Panel
KPI Row
Main Dashboard Grid:
  Large Goal Timing Heatmap / Featured Insight
  Top 5 Teams
  Recent Results
Bottom Insight Strip:
  3 short insight cards
  View all insights action
```

Implementation requirements:

Use the available desktop width properly.
Avoid a narrow centered article-column layout.
Use a 2–3 column dashboard grid on desktop.
Make Goal Timing the largest and most visually important panel.
Place Top 5 Teams and Recent Results beside the main visual on desktop.
Make KPI cards compact and strongly number-led.
Add a bottom insight strip with short, football-readable insights.
Use the refined surface hierarchy from the design system.
Use reusable components, not page-specific one-off CSS.
Preserve existing API data only.
Do not add unsupported fake features.

Data/API needs:

Use existing overview, team, match, and goal timing data. If a desired insight is not supported by existing data, show only supported insights.

Mobile/accessibility notes:

Mobile order should be:

page title/status
KPI cards
Goal Timing featured insight
Top 5 Teams
Recent Results
insight strip/caveat

Out of scope:

Do not redesign Goal Timing Explorer, Match Explorer, Team Insights, or Data Notes in this request.

Approval notes:

Approved because this is the highest-impact page and should become the reference implementation for the rest of the frontend.


### Request: Standardize Chart Panel Treatment

Status: approved

Area: charts, components, design system

Request:

Create a polished reusable `ChartPanel` treatment for all analytical charts, including title, subtitle, chart body, legend, caveat, loading, and empty states.

Why it matters:

Recharts has been added, but charts still need product-level presentation. Without standardized chart panels, visual drift will continue.

Implementation requirements:

- Create or refine a `ChartPanel` component with:
  - eyebrow/section label
  - title
  - short explanation
  - chart slot
  - legend slot
  - caveat slot
  - optional action
- Use consistent spacing around charts.
- Use design tokens for colors, borders, radius, and text.
- Tooltips should use the app’s dark/light theme.
- Legends should be compact and near the chart.
- Empty chart states should be calm and useful.
- Avoid chart-specific CSS scattered across pages.

Data/API needs:

None.

Mobile/accessibility notes:

Chart panels must remain readable on mobile. If chart labels become unreadable, use simplified mobile labels or value lists.

Out of scope:

Do not add new chart types beyond current required primitives.

Approval notes:

Approved because the app now has a chart library but needs a consistent visual container system.

### Request: Redesign Top Five And Ranking Previews

Status: needs_review

Area: rankings, Team Insights, League Overview

Request:

Create a reusable ranking preview pattern for top-five lists, then apply it first to League Overview and later to Team Insights.

Why it matters:

The target mockup uses rankings as a major sports-native pattern. Current lists still feel like plain rows rather than designed analytical previews.

Implementation requirements:

- Create a `RankingPreviewCard` or `TopFiveCard` component.
- Each row should show:
  - rank
  - team/player label
  - value
  - optional context
- Values should align cleanly.
- Use compact visual hierarchy.
- Add a clear “View full table” or “Compare teams” action only when useful.
- Support green/gold accent for leader or selected metric.
- Avoid wide tables where a top-five preview is better.

Data/API needs:

Use existing team data first.

Mobile/accessibility notes:

Ranking cards should be mobile-first and easier to read than tables.

Out of scope:

Do not build full standings, compare tools, or unsupported player rankings yet.

Approval notes:

Needs review after League Overview redesign confirms the pattern.

### Request: Mobile Layout Polish Pass

Status: needs_review

Area: mobile UX, responsive design

Request:

After the League Overview desktop redesign is approved, run a dedicated mobile polish pass to make the app feel like a real mobile sports intelligence product.

Why it matters:

The approved mockup emphasizes mobile-first design. Mobile should not be a squeezed version of desktop.

Implementation requirements:

- Review all key pages at common mobile widths.
- Ensure KPI cards are readable.
- Ensure heatmap/chart labels remain readable.
- Prefer top-five cards over wide tables.
- Keep primary navigation reachable.
- Keep caveats close to affected data.
- Improve tap targets.
- Avoid horizontal overflow.
- Ensure text wraps cleanly.

Data/API needs:

None.

Mobile/accessibility notes:

This request is specifically about mobile UX.

Out of scope:

Do not add new data features.

Approval notes:

Needs review after League Overview and real heatmap are implemented.

## Approved Implementation Queue

1. Standardize Chart Panel Treatment
2. Build A Real Goal Timing Heatmap
3. Redesign League Overview To Match Approved Dashboard Structure
4. Review screenshots against approved mockup
5. Visual Cleanup Of App Shell And Navigation
6. Redesign Top Five And Ranking Previews
7. Mobile Layout Polish Pass
8. Then move to Goal Timing Explorer redesign

## Needs Review Queue



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
- Surface hierarchy and visual depth were refined with shared radius,
  elevation, border, and surface-variant rules.
- KPI and number cards were consolidated around the shared `KpiCard` component.

## Implementation Notes

The current approved frontend pass is complete enough to reset this file to a
planning state.

Future frontend work should either:

- come from a newly approved request in this file, or
- be explicitly requested by the user in chat

Do not reopen completed requests here unless the product direction changes or a
specific follow-up request is approved.
