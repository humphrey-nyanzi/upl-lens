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
4. Read [UPL_LENS_FRONTEND_START_HERE.md](UPL_LENS_FRONTEND_START_HERE.md) if
   the work affects the public UPL Lens frontend.
5. Read this file.
6. Read [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md).
7. Inspect `frontend/src/`, `api/`, and `src/api/` only enough to understand
   the affected product surface.
8. Implement only requests marked `approved`, unless the user explicitly says
   to work on a different status.
9. Keep React dependent on FastAPI JSON. Do not make React read CSV files,
   notebooks, or exported notebook images.
10. If new data is needed, prefer a thin FastAPI endpoint and query or service
   logic under `src/api/`.
11. After implementation, move durable behavior into
    [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md), then compress this
    file's implemented entry to one short note and remove the detailed
    description from active requests.
12. Run `npm run build` for frontend changes and any relevant backend or API
    verification if endpoints changed.

## UPL Lens Note

For the current relaunch, the `UPL_LENS_*` docs define launch-specific
frontend structure and editorial direction. This file still owns request
approval state and implementation queue decisions.

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

### Request: Add Cross-Season Aggregation and Fixed Featured-Insight Season Framing

Status: approved

Area: season selector, overview, insight framing, insight detail behavior

Request:

Extend season handling so users can choose an "All Seasons" option that
aggregates available data across seasons, while keeping featured insights on
the Overview page fixed to the scope of the research insight itself rather than
changing with the currently selected season. On the insight detail page, allow
season-level exploration where the underlying data supports it.

Why it matters:

The current season selector assumes a single active season context everywhere.
That is useful for operational comparison, but it breaks down when users want
league-wide or multi-season context and when featured research insights are
meant to summarize a longer time window.

Implementation requirements:

- Add an "All Seasons" selector option wherever the global season context is
  used for supported aggregated metrics.
- When "All Seasons" is selected, dashboard metrics should aggregate across the
  available seasons for that metric rather than showing one arbitrary season.
- The Overview featured insight should remain fixed to the insight's research
  scope even when the global season selector changes.
- The Overview featured insight must clearly label the season span or date span
  used for that insight, for example a single season or a five-season window.
- Clicking the featured insight should route to the insight detail page where
  users can explore season variation or compare seasons when the data supports
  it.
- Insight detail pages should support season toggles or selectors where
  technically and analytically appropriate.

Why now:

This request establishes a cleaner contract between global product context and
research-driven featured insights, which will matter more as the insight
library grows.

Data/API needs:

Likely requires backend/API support for reliable all-season aggregation and
possibly per-insight multi-season breakdowns. The frontend must continue to use
FastAPI JSON only.

Mobile/accessibility notes:

Season controls must remain understandable on small screens. Fixed featured
insight scope should be visible in copy, not implied only through charts.

Out of scope:

- Inventing unsupported multi-season metrics
- Forcing every insight to become a full comparison dashboard if the data does
  not support that level of exploration yet

Approval notes:

Approved by user as a season-model and insight-context refinement. Backend/API
needs should be proposed carefully during implementation rather than assumed.

### Request: Improve Insights Library Home and Insight Exploration Surfaces

Status: approved

Area: insights library, insight discovery, insight detail exploration

Request:

Improve the Insights library landing view so it feels intentional and useful,
with a clearer hierarchy between featured/current insights and older or smaller
insight entries. The current Insights home view should evolve into a better
editorial library surface rather than a sparse placeholder. Where possible,
insight detail views should also support richer exploration such as season
switching or comparison.

Why it matters:

The insights area is one of the strongest ways to show that UPL Lens is doing
more than reproducing match records. If the library home is weak, the product's
research and storytelling value is harder to see.

Implementation requirements:

- Redesign the Insights home view into a clearer editorial library layout.
- Consider a stronger featured/latest insight area near the top.
- Support a secondary grid, list, or patterned layout for prior insights below.
- Keep the page readable, compact, and aligned with the Editorial Light system.
- When an insight supports deeper exploration, its detail page should feel more
  like a focused mini-dashboard than a static article card.
- Season toggles or similar comparison controls may be added on supported
  insight pages.

Why now:

This helps convert the Insights area from a minimal route into a durable
product surface that can support future research promotion.

Data/API needs:

Likely limited for the library-home redesign itself. Insight detail exploration
may require additional endpoint support depending on the insight.

Mobile/accessibility notes:

The featured/latest insight treatment must stack cleanly on mobile and keep tap
targets obvious.

Out of scope:

- Inventing fake insight records
- Requiring every insight to use the same chart/control pattern regardless of
  data shape

Approval notes:

Approved by user as a substantive improvement to the Insights discovery and
exploration experience.

### Request: Expand the Trends Page Into a Real Multi-Visualization Exploration Surface

Status: approved

Area: trends, visualizations, season comparison, exploratory controls

Request:

Develop the Trends page into a much richer exploration surface with more charts
and visual summaries across seasons, halves, and other time-based patterns,
while preserving readability and avoiding visual overcrowding.

Why it matters:

Trends is currently underdeveloped relative to the product promise. A stronger
Trends page gives UPL Lens a clearer analytical identity and helps users move
from single-surface summaries into broader league pattern exploration.

Implementation requirements:

- Add more charts and visualizations to the Trends page.
- Prioritize trend questions that compare:
  - seasons
  - first half vs second half
  - other time-based or competition-pattern views already supported by data
- Provide toggles, filters, or compact controls where they improve exploration.
- Avoid overcramming the page; preserve whitespace, grouping, and scanability.
- Keep the page feeling like a public intelligence surface rather than a raw
  chart dump.

Why now:

This is one of the largest remaining product gaps in the public analytical
surface.

Data/API needs:

Likely requires checking which trend-ready aggregates already exist and whether
new FastAPI support is needed for comparison views.

Mobile/accessibility notes:

Trend controls and charts must degrade gracefully on smaller screens without
requiring horizontal scrolling where avoidable.

Out of scope:

- Adding charts with weak analytical value only to fill space
- Replacing the whole app with a dedicated BI-style trends dashboard

Approval notes:

Approved by user as a major product-surface enhancement for a later
implementation phase.

## Impeccable-Oriented Implementation Notes

Use this section to keep approved UPL Lens requests aligned with the local
`impeccable` skill expectations before implementation starts.

### Required pass order for substantial frontend work

For any meaningful UI batch, prefer this sequence:

```text
layout or adapt or optimize or harden or clarify
-> implement the actual fixes
-> polish
```

Notes:

- Use `layout` when the main problem is hierarchy, spacing, or report-like
  structure.
- Use `adapt` when the main problem is mobile behavior, touch sizing, bottom
  navigation, sidebar collapse, or breakpoint-specific interaction patterns.
- Use `optimize` when bundle size, heavy lazy chunks, route-entry cost, or
  overly expensive skeleton/loading systems are the primary issue.
- Use `harden` when interaction timing, keyboard flows, overflow, extreme data,
  missing states, or focus behavior are fragile.
- Use `clarify` when labels, empty states, utility copy, and section framing
  feel too utilitarian or ambiguous.
- End with `polish`, because impeccable treats alignment to the design system,
  state completeness, spacing consistency, and flow coherence as a required
  final pass rather than optional cleanup.

### Current impeccable backlog mapped into the approved request queue

1. Large async chunk optimization:
   - maps to: Improve Shared Loading States, Iconography, and Frontend Text
     Formatting
   - command family: `optimize` -> `polish`
   - implementation meaning: reduce route-entry or shared-chunk cost before
     adding more heavy UI systems

2. Touch sizing on compact links and chips:
   - maps to: Refine App Shell Navigation, Search, Brand, and Global Utility UI
     plus Improve Shared Loading States, Iconography, and Frontend Text
     Formatting
   - command family: `adapt` -> `polish`
   - implementation meaning: treat mobile and coarse-pointer ergonomics as a
     first-class product requirement, not a CSS afterthought

3. Detail-page editorial hierarchy:
   - maps to: future non-Overview detail page refinement work, especially
     Match, Team, and Player report surfaces
   - command family: `layout` -> `clarify` -> `polish`
   - implementation meaning: make these pages read like guided reports, not
     stacked records panels

4. Search popover blur-timeout fragility:
   - maps to: Refine App Shell Navigation, Search, Brand, and Global Utility UI
   - command family: `harden` -> `polish`
   - implementation meaning: remove timeout-dependent dismissal where it harms
     keyboard or assistive workflows

5. Utilitarian copy on non-Overview pages:
   - maps to: Improve Insights Library Home and Insight Exploration Surfaces,
     Expand the Trends Page Into a Real Multi-Visualization Exploration
     Surface, and later Match/Players explorer copy refinements
   - command family: `clarify` -> `polish`
   - implementation meaning: rewrite for calm editorial guidance without
     turning the app into marketing copy

### Request shaping rules for future implementation batches

Before implementing an approved request, tighten it into one of these batch
types:

- `global systems batch`
  - shared controls, iconography, skeletons, focus states, touch targets,
    shell/navigation behavior
- `overview report batch`
  - hero, scoreline presentation, featured summary framing, signal board
- `library/discovery batch`
  - insights home, search-result hierarchy, trends discovery surfaces
- `data-contract batch`
  - all-seasons aggregation, fixed insight scope across selectors, insight
    comparison controls that need API support
- `detail report batch`
  - Match Detail, Team Detail, and Player Detail hierarchy and narrative flow

This prevents mixing visual hierarchy, responsiveness, performance, copy, and
data-contract changes in one vague implementation pass.

### Impeccable acceptance expectations for UPL Lens

Substantial approved requests should be considered ready only when they satisfy
these expectations:

- mobile interaction targets are touch-safe where they behave like controls
- no important interaction depends on hover alone
- no timeout-driven focus/blur workaround is carrying a core interaction if a
  more robust approach is available
- typography and spacing reinforce hierarchy without falling back to generic
  card-grid repetition
- copy is plain, specific, and product-led rather than utilitarian filler or
  marketing language
- loading and empty states match the shape of the content without excessive
  performance cost
- changes align with the shared Editorial Light tokens and existing component
  vocabulary
- final implementation is suitable for a closing `polish` pass

## Recommended Implementation Order

Use this order once requests are approved:

```text
1. Refine Goal Timing Distribution Chart
2. Improve Insights Library Home and Insight Exploration Surfaces
3. Add Cross-Season Aggregation and Fixed Featured-Insight Season Framing
4. Expand the Trends Page Into a Real Multi-Visualization Exploration Surface

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
- Overview card composition, hero integration, and signal-board scoreline refinements were implemented.
- App shell navigation, search, brand, favicon, and global utility polish were implemented.
- Shared loading, iconography, and public-facing text formatting refinements were implemented.
- Public app workflows were reviewed against the source-record vs intelligence-layer philosophy.

## Implementation Notes

The active requests above are intentionally written as design/build tickets.
They should be approved individually or in a named implementation batch before
code changes begin.

Future frontend work should either:

- come from a newly approved request in this file, or
- be explicitly requested by the user in chat

Do not reopen completed requests here unless the product direction changes or a
specific follow-up request is approved.
