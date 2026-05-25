# Frontend UX Requests

This is the editable source of truth for proposed UI and UX improvements.

Use this file for requests that still need discussion, approval, or
implementation. Durable decisions from implemented work belong in
[UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md). Product positioning and audience
rules belong in [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md). The implementation
design reference for the current approved visual direction is
[FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md).

## Core Rule

This document can describe desired UI and UX changes, but it does not approve
implementation by itself.

An AI agent should only implement requests whose status is:

```text
approved
```

Draft, idea, and discussion notes are planning material only. Implemented
requests should stay short here; their lasting decisions should live in
[UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md).

## Status Labels

| Status | Meaning |
|--------|---------|
| `idea` | A rough thought. Not ready for implementation. |
| `draft` | Clear enough to discuss, but still not approved. |
| `needs_review` | Ready for human review or prioritization. |
| `approved` | Approved for the next implementation pass. |
| `implemented` | Built and verified. Durable decisions should be in `UI_UX_GUIDELINES.md`. |
| `rejected` | Do not implement unless revived later. |

## How To Add A Request

Add new requests under **Active Requests**, not under the implemented archive.

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
5. Read [UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md).
6. Read [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md) for visual
   system work.
7. Inspect `frontend/src/`, `api/`, and `src/api/` only enough to understand
   the affected product surface.
8. Implement only requests marked `approved`, unless the user explicitly says to
   work on a different status.
9. Keep React dependent on FastAPI JSON. Do not make React read CSV files,
   notebooks, or exported notebook images.
10. If new data is needed, prefer a thin FastAPI endpoint and query/service
    logic under `src/api/`.
11. After implementation, move durable UI/UX decisions to
    [UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md), then compress this file's
    implemented entry to one short statement.
12. Run `npm run build` for frontend changes and any relevant backend/API tests
    if endpoints changed.

## Active Requests

These requests came from the approved mockup direction and current product
strategy. They were approved by the user and implemented in the first
design-system rollout. Discipline remains a visual/planning placeholder until
Research & Football Intelligence validates the feature.

### Request: Implement App Shell Redesign

Status: implemented

Area: navigation, layout, visual system

Request: Redesign the app shell toward a desktop sidebar, top
control/search/filter bar, main analytical workspace, and mobile navigation
pattern grounded in the approved design system.

Why it matters: The shell is the foundation for making the app feel like a real
football intelligence workspace rather than a pilot dashboard.

Data/API needs: No new endpoint is required for shell layout. Existing health,
season, and overview data can support status and season controls.

Mobile/accessibility notes: Mobile should use a compact menu or bottom
navigation with clear selected states, keyboard-accessible controls, readable
contrast, and no hidden critical workflow.

Out of scope: Do not add fake navigation sections that do not have usable pages.
Do not build search unless the API/data workflow is mapped first.

Approval notes: Derived from the approved mockup direction. Needs review before
implementation because it changes global layout.

### Request: Implement Reusable Card And Panel System

Status: implemented

Area: components, visual system

Request: Create reusable card, panel, attention panel, KPI card, insight card,
ranking card, recent result card, and caveat/status surfaces using the design
system tokens.

Why it matters: The redesign should not be one-off CSS per page. Reusable
surfaces keep the product consistent as new pages are added.

Data/API needs: No new endpoint required.

Mobile/accessibility notes: Cards must stack cleanly on phones, avoid text
overlap, preserve focus states, and keep tap targets practical.

Out of scope: Do not redesign every page during the component foundation pass.

Approval notes: Derived from the approved mockup direction. Needs review to set
the first implementation slice.

### Request: Implement KPI Number System

Status: implemented

Area: numbers system, components, copy

Request: Standardize headline numbers so each KPI has a football-facing label,
dominant value, context line, and optional trend, rank, or caveat.

Why it matters: The product should win through figures that fans can understand
quickly and analysts can trust.

Data/API needs: Existing overview, team, match, and insight endpoints can power
the first version. New comparison or trend values should be proposed as API work
only when a page needs them.

Mobile/accessibility notes: On mobile, show the most important numbers first and
avoid grids that become too dense.

Out of scope: Do not invent new metrics in React without research or API
support.

Approval notes: Consolidates earlier approved number-system direction into a
build-ready request that still needs final implementation approval.

### Request: Implement Ranking And Top-Five Preview Pattern

Status: implemented

Area: rankings, data display, mobile UX

Request: Build a reusable top-five ranking pattern for teams, matches, players,
officials, or events where a compact leaderboard communicates the story better
than a full table.

Why it matters: Rankings are quick to scan, mobile-friendly, and more
fan-facing than dumping full tables first.

Data/API needs: Existing team and match data can support initial rankings.
Player, official, and discipline rankings may need future API work after
research validation.

Mobile/accessibility notes: Ranking rows need readable names, values, and rank
labels. Do not rely on color alone.

Out of scope: Do not remove full tables where full structured comparison is the
clearest interaction.

Approval notes: Derived from existing numbers/ranking direction and the mockup.
Needs review before component work.

### Request: Implement Chart And Heatmap Treatment

Status: implemented

Area: charts, goal timing, visual system

Request: Define and implement the first chart treatment, prioritizing a Goal
Timing heatmap-style panel with clear labels, legend, peak-zone text, and
accessible fallback values.

Why it matters: Goal Timing is the flagship insight, and the mockup makes the
heatmap the strongest visual proof of the product's football intelligence.

Data/API needs: Existing `/insights/goal-timing` supports the first version.
Team-specific or home/away heatmaps would require separate API planning.

Mobile/accessibility notes: Heatmap labels and legends must remain readable on
phones. Provide text values or a list fallback where needed.

Out of scope: Do not add decorative chart types. Do not use notebook-exported
images.

Approval notes: Derived from the approved mockup and Feature 1 direction. Needs
review before replacing current chart treatment.

### Request: Implement Mobile Navigation And Mobile Data Layouts

Status: implemented

Area: mobile UX, navigation, data display

Request: Formalize mobile navigation and data layout behavior for the redesigned
shell, KPI cards, rankings, charts, filters, tables, and caveats.

Why it matters: Mobile is a first-class product surface. The app must preserve
the analysis workflow rather than compressing desktop panels awkwardly.

Data/API needs: No new endpoint required.

Mobile/accessibility notes: This request is specifically about touch ergonomics,
readable contrast, focus states, short labels, and avoiding overlap.

Out of scope: Do not build a separate mobile app.

Approval notes: Derived from current mobile-first rules and the approved mockup.
Needs review before a global layout change.

### Request: Redesign League Overview Using Approved Visual System

Status: implemented

Area: League Overview, visual system, product structure

Request: Apply the design system to the League Overview with the app shell,
season/status controls, KPI cards, flagship Goal Timing preview, top teams,
recent results, and clear data notes.

Why it matters: The overview is the first ten seconds of the product. It should
make the football intelligence value obvious.

Data/API needs: Use existing health, seasons, overview, goal timing, teams, and
matches endpoints first. Propose API changes only if a visible component cannot
be powered cleanly.

Mobile/accessibility notes: The first mobile screen should prioritize season,
status, headline metrics, and the flagship insight.

Out of scope: Do not add unsupported search, players, news, or compare areas
just because the mockup includes them.

Approval notes: Needs review as the first page-level redesign after shell and
component foundations.

### Request: Redesign Goal Timing Explorer Using Approved Visual System

Status: implemented

Area: Goal Timing, featured insight

Request: Redesign Goal Timing as the flagship featured insight page with a
football question, headline finding, heatmap or chart panel, interpretation,
caveat, and drilldown path.

Why it matters: Goal Timing is the first promoted notebook-to-product feature
and should set the standard for future researched insights.

Data/API needs: Existing goal timing endpoint supports the base page. Team,
home/away, or period filters require separate API mapping before implementation.

Mobile/accessibility notes: The mobile view should show the main finding and
peak period before deeper chart detail.

Out of scope: Do not change the metric definition without updating the Feature 1
research/product docs.

Approval notes: Needs review after visual/component foundation.

### Request: Apply Design System To Match Explorer

Status: implemented

Area: Match Explorer, filters, cards

Request: Apply the visual system to Match Explorer with compact filters, result
summary KPIs, recent match cards, empty states, and future-ready drilldown
patterns.

Why it matters: Match Explorer is the first practical evidence surface for fans
who want to inspect scorelines and match patterns.

Data/API needs: Use existing `/matches` filters where possible. Pagination,
search, match detail, or richer timeline needs should be proposed separately.

Mobile/accessibility notes: Prefer stacked match cards and short filters on
phones. Avoid wide raw tables as the first view.

Out of scope: Do not build full match detail or timeline UI unless separately
approved.

Approval notes: Needs review. Should follow shell, components, overview, and
Goal Timing work.

### Request: Apply Design System To Team Insights

Status: implemented

Area: Team Insights, team profile, rankings

Request: Apply the visual system to Team Insights with top-five previews,
ranked team cards, scoring/defensive KPIs, and a future path to team profiles.

Why it matters: Team pages should feel analytical, not like basic club profile
pages.

Data/API needs: Existing `/teams` data supports initial summaries. Team profile
or split metrics may need `/teams/{team_id}/summary` or additional API work.

Mobile/accessibility notes: On mobile, prioritize top teams and strongest
signals before full lists.

Out of scope: Do not create player-heavy or scouting-style profiles without
validated data.

Approval notes: Needs review. Should follow reusable ranking/KPI components.

### Request: Standardize Loading Empty Error And Data Status States

Status: implemented

Area: UX states, reliability, trust

Request: Apply the visual system to skeleton loading, cold-start messaging,
empty states, API/data status indicators, caveats, and error panels.

Why it matters: The hosted API may cold-start, source data can have caveats, and
trust depends on clear states.

Data/API needs: Existing health and season metadata should be used first.
Additional validation-status detail should be proposed as API work if needed.

Mobile/accessibility notes: State messages should be readable, calm, and close
to the affected surface. Do not rely on color alone.

Out of scope: Do not hide limitations to make the UI look cleaner.

Approval notes: Needs review. Can be implemented alongside component foundation
or early page redesigns.

### Request: Plan Discipline Dashboard As Next Feature-Led Product Area

Status: implemented

Area: feature planning, discipline

Request: Plan the future Discipline Dashboard after research validates the
football questions, metrics, and caveats.

Why it matters: Discipline is a promising intelligence area, but it should come
from the feature-promotion workflow rather than UI guessing.

Data/API needs: Likely needs research queries over `staging.events`, then a
direct API query or `analytics.*` object if promoted.

Mobile/accessibility notes: Card totals, team comparisons, and top-five previews
may work better than wide tables.

Out of scope: Do not build this before the research/product plan is approved.

Approval notes: Keep as draft until Research & Football Intelligence validates
the feature.

## Recommended Implementation Order

Do not redesign every page at once.

Suggested order:

```text
1. Approve design tokens, app shell, and reusable component foundation.
2. Implement shell/tokens/components behind current API data.
3. Redesign League Overview.
4. Redesign Goal Timing Explorer.
5. Apply the system to Team Insights.
6. Apply the system to Match Explorer.
7. Plan and build Discipline Dashboard only after feature research promotion.
```

## Approved Implementation Queue

Move requests here only after the user explicitly approves them for a build
pass.

Current queue:

```text
none
```

## Needs Review Design Queue

Suggested review order:

```text
1. Implement App Shell Redesign
2. Implement Reusable Card And Panel System
3. Implement KPI Number System
4. Implement Ranking And Top-Five Preview Pattern
5. Implement Chart And Heatmap Treatment
6. Implement Mobile Navigation And Mobile Data Layouts
7. Redesign League Overview Using Approved Visual System
8. Redesign Goal Timing Explorer Using Approved Visual System
9. Apply Design System To Team Insights
10. Apply Design System To Match Explorer
11. Standardize Loading Empty Error And Data Status States
12. Plan Discipline Dashboard As Next Feature-Led Product Area
```

This queue is now implemented. Use it as the historical order for the first
mockup-aligned redesign pass.

## Implemented Archive

Implemented entries are intentionally short. Lasting decisions from these
requests should be recorded in [UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md) or
[FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md).

- Adopt Mobile-First Redesign Mentality: established mobile-first design as the
  default for product-facing frontend slices.
- Audit Current Frontend Before Redesign: captured the original frontend audit
  before the overview redesign.
- Map Frontend Data Needs Before Adding Endpoints: confirmed frontend redesigns
  should map data needs before adding API endpoints.
- Fix Sticky Anchor Offset On Mobile: removed the original mobile sticky-anchor
  problem by moving toward page-like navigation.
- Introduce Page-Based Navigation Structure: added lightweight page-based
  navigation for real product areas.
- Use Mobile Sandwich Menu For Primary Navigation: added compact mobile primary
  navigation.
- Redesign League Intelligence Overview V1: implemented the mobile-first League
  Intelligence Overview using existing API data.
- Define League Intelligence Front Page Template: implemented the overview as a
  front-page league intelligence surface.
- Define Featured Insight Page Template: implemented Goal Timing as a dedicated
  researched insight page.
- Define Explorer Page Template: implemented Match Explorer with moderate
  filters, summary context, and compact match cards.
- Define Team Summary Page Template: implemented Team Insights with ranked team
  cards and existing team data.
- Define Methodology And Data Notes Page Template: implemented a Data Notes page
  for source, freshness, coverage, and limitations.
- Define Corner Radius And Panel Treatment: moved the UI toward restrained
  panel/card treatment.
- Define Anti-Patterns To Avoid: recorded that the app should avoid generic
  dashboard, marketing-page, raw-table, and notebook-export patterns.
- Define UPL Match Intelligence Visual System: captured the approved mockup
  direction in `docs/FRONTEND_DESIGN_SYSTEM.md`.
- Define Fan-First Numbers System: folded number hierarchy guidance into
  `docs/FRONTEND_DESIGN_SYSTEM.md`.
- Define Rankings And Top-Five Preview Pattern: folded ranking guidance into
  `docs/FRONTEND_DESIGN_SYSTEM.md`.
- Define Chart And Visualization System: folded chart and heatmap guidance into
  `docs/FRONTEND_DESIGN_SYSTEM.md`.
- Define Interactive Filter Rules: folded filter guidance into
  `docs/FRONTEND_DESIGN_SYSTEM.md`.
- Define Mobile-First Data Display Rules: folded mobile adaptation guidance into
  `docs/FRONTEND_DESIGN_SYSTEM.md`.
- Use Skeleton Loading Before Error States: added skeleton-shaped loading states
  before confirmed errors.
- Improve Loading Empty Error And Cold-Start States: added reusable loading,
  empty, and error components for product pages.
- Make Overview Copy Fan-Facing And Remove Internal Product Language: changed
  overview language from internal product terms to public-facing football copy.
- Move Technical Trust Details To Methodology Data Notes Page: kept the overview
  lighter by moving source, freshness, and trust context to Data Notes.
