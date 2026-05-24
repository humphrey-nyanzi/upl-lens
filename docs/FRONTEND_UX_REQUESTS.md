# Frontend UX Requests

This is the editable source of truth for proposed UI and UX improvements.

Use this document before implementation. A human user, designer, developer, or
AI agent can add requests here in normal language. The request does not need to
know the exact React component, CSS selector, endpoint, or chart library.

After a request is approved and implemented, move the durable decision into
[UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md) and add a short implementation note
to this file.

## Core Rule

This document can describe desired UI and UX changes, but it does not approve
implementation by itself.

An AI agent should only implement requests whose status is:

```text
approved
```

Draft, idea, and discussion notes should be treated as planning material only.

## Status Labels

Use these statuses:

| Status | Meaning |
|--------|---------|
| `idea` | A rough thought. Not ready for implementation. |
| `draft` | Clear enough to discuss, but still not approved. |
| `needs_review` | Ready for human review or prioritization. |
| `approved` | Approved for the next implementation pass. |
| `implemented` | Built and verified. Move lasting decisions to `UI_UX_GUIDELINES.md`. |
| `rejected` | Do not implement unless revived later. |

## How To Add A Request

Copy this template under the relevant section.

```text
### Request: Short Name

Status: idea

Area:

Current behavior:

Desired behavior:

Reason:

Data/API needs:

Visual/UX notes:

Mobile behavior:

Accessibility notes:

Out of scope:

Approval notes:

Implementation notes:
```

You can leave fields blank if you are not sure. The point is to capture the
product intent clearly enough that a future agent can ask fewer questions.

## AI Agent Instructions

When asked to work on frontend improvements, an AI agent should:

1. Read `AGENTS.md`.
2. Read [START_HERE.md](START_HERE.md).
3. Read this file.
4. Read [UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md).
5. Inspect `frontend/src/`, `api/`, and `src/api/` only enough to understand
   the affected product surface.
6. Implement only requests marked `approved`, unless the user explicitly says to
   work on a different status.
7. Keep React dependent on FastAPI JSON. Do not make React read CSV files,
   notebooks, or exported notebook images.
8. If new data is needed, prefer a thin FastAPI endpoint and query/service logic
   under `src/api/`.
9. After implementation, update the request status, implementation notes, and
   any durable guideline in [UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md).
10. Run `npm run build` for frontend changes and any relevant backend/API tests
    if endpoints changed.

## Product-Level Direction

Use this section for broad product intent that affects many screens.

When a request affects a specific feature insight, also check that feature's
`product_plan.md`. Feature-specific product changes should stay traceable to
the feature package, while app-wide UX and design rules belong here.

For app-wide product identity, audience, content priority, and the difference
between official-site duplication and football intelligence, use
[PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md) before approving major redesign
requests.

### Request: Adopt Mobile-First Redesign Mentality

Status: implemented

Area: product direction, mobile UX

Current behavior:

```text
The current app has responsive CSS, but the mobile experience is still poor
enough that users on phones may struggle to understand or use the product.
Desktop layout appears to be the stronger mental model.
```

Desired behavior:

```text
Future frontend redesign work should start from the phone viewport first, then
enhance for tablet and desktop. The app should be designed with the assumption
that many first-time UPL users will open it on a mobile device.

For each product-facing screen, the implementation agent should decide:

- what the core mobile task is
- what content must appear first
- what can collapse, stack, or move lower on the page
- which controls must remain reachable without excessive scrolling
- whether wide tables should become stacked cards, reduced-column tables, or
  horizontally scrollable tables
```

Reason:

```text
The primary audience is a stats-interested UPL fan, and many users will browse
on phones. If the mobile experience fails, the product fails its public-facing
purpose even if the desktop dashboard looks good.
```

Data/API needs:

```text
No new API data is required for this rule. It is a design and implementation
constraint that applies to all frontend slices.
```

Visual/UX notes:

```text
Mobile should not feel like a squeezed desktop dashboard. Prioritize readable
football insight, clear hierarchy, simple controls, and charts/tables that fit
the phone workflow.
```

Mobile behavior:

```text
Design mobile first. Verify at mobile width before considering the slice done.
Important text, controls, charts, cards, and status/caveat messages must not
overlap, truncate awkwardly, or require desktop-sized assumptions.
```

Accessibility notes:

```text
Keep tap targets large enough, labels visible, contrast readable, and controls
keyboard/screen-reader friendly where practical.
```

Out of scope:

```text
Do not build a separate mobile app.
Do not hide important caveats or data-quality status just to make mobile shorter.
Do not solve every future page in this request; apply the rule to the approved
slice being implemented.
```

Approval notes:

```text
Approved by the user on 2026-05-25 before the first redesign slice. The user
explicitly called out that mobile responsiveness is currently terrible and that
future work needs a mobile-first-before-computer mentality.
```

Implementation notes:

```text
Implemented in the League Intelligence Overview v1 redesign. The frontend CSS
now starts from a single-column phone layout and enhances to tablet/desktop
breakpoints. The overview header, season control, summary cards, featured
insight, exploratory previews, evidence panels, and methodology panel are all
designed to stack cleanly before widening.
```

### Request: Make The App Feel Like A Football Intelligence Workspace

Status: draft

Area: product direction

Current behavior:

```text
The app proves the API-to-React path with a League Overview screen, but it still
feels like a pilot dashboard.
```

Desired behavior:

```text
The app should feel like a compact football analysis workspace where a user can
scan the league, select a season, inspect matches, compare teams, and understand
key patterns.
```

Reason:

```text
The project should be the intelligence layer above the official website, not a
copy of match pages.
```

Data/API needs:

```text
Use existing endpoints first. Add endpoints only when a planned view proves the
need.
```

Visual/UX notes:

```text
Prioritize dense but readable layouts, clear filters, useful tables, and
football-specific language.
```

Out of scope:

```text
Do not turn the app into a marketing landing page.
```

### Request: Audit Current Frontend Before Redesign

Status: implemented

Area: product direction

Current behavior:

```text
The current frontend proves the production path, but the team has not yet
written a structured UX audit of what works, what feels pilot-like, and what
blocks real use.
```

Desired behavior:

```text
Before major React redesign work, an agent should audit the current frontend and
write a short findings summary. The audit should identify:

- what is already useful
- what feels unfinished or placeholder-like
- where navigation is unclear
- where loading, empty, or error states need improvement
- which visible UI issues matter most before adding new features
- which changes need API support and which can be frontend-only
```

Reason:

```text
The first redesign should be deliberate. An audit prevents us from jumping
straight into styling or endpoint work without understanding the current product
surface.
```

Data/API needs:

```text
No new endpoint should be added during the audit. The agent should only inspect
current API client usage and list possible future data needs.
```

Visual/UX notes:

```text
The audit should be practical and product-focused, not a general design essay.
```

Mobile behavior:

```text
Check whether the current layout remains usable at mobile widths.
```

Accessibility notes:

```text
Check obvious label, contrast, and keyboard-navigation concerns, but do not
perform a full accessibility audit unless requested.
```

Out of scope:

```text
Do not implement redesign changes during the audit.
Do not rewrite the app structure during the audit.
```

Approval notes:

```text
Audit requested by the user and completed as a documentation-only pass. No
frontend code was changed.
```

Implementation notes:

```text
Audit findings from the current frontend:

What already works:

- The frontend follows the correct production path: React calls FastAPI JSON and
  does not read CSV files, notebooks, or exported chart images.
- The League Overview gives a useful first screen with season selection,
  headline metrics, API/database health, date range, staging run context, goal
  timing, recent matches, event breakdown, and team records.
- The API client is small and understandable.
- The TypeScript response types mirror the current API shapes.
- The overview endpoint is used correctly for season-wide counts instead of
  forcing React to derive every summary from paged event rows.
- The current CSS already supports desktop, tablet, and mobile breakpoints.
- The error panel already mentions the hosted API and browser-extension blocking
  case, which is useful for the deployed free-tier setup.

What still feels pilot-like:

- `frontend/src/App.tsx` holds the whole product in one file, including data
  loading, formatting helpers, layout, charts, match rows, and empty states.
- Navigation is still mostly placeholder-based. Future sections appear in the
  sidebar and future panel, but they do not represent real product workflows
  yet.
- There is no route/page structure for Match Explorer, Team Profile, or
  Discipline Dashboard.
- Recent Matches is useful, but it is not yet a searchable/filterable Match
  Explorer.
- Goal Timing is displayed, but not yet an explorer with filters or comparison
  behavior.
- The teams table is useful, but team rows do not lead to a profile or detail
  view.
- The UI has no icon system yet, even though future tool/filter controls would
  benefit from one.

What blocks real use:

- Users cannot search or filter matches beyond the global season selector.
- Users cannot click into a match, team, or official.
- Users cannot compare teams directly.
- The app does not yet explain source-data caveats near the affected views.
- Loading and error state handling is global, so one failed season request can
  flatten the whole page instead of showing section-level recovery.
- Empty states are present but generic.

Real data/API needs discovered by the audit:

- Match Explorer can start with the existing `/matches` endpoint.
- The current frontend client does not expose all useful query options that the
  API already supports, such as `team`, `match_day`, `event_type`, and `offset`.
- Match detail will eventually need either `/matches/{match_id}` plus existing
  event filters or a dedicated match-detail client method.
- Team Profile will need a team-specific summary endpoint/client method before
  it becomes useful.
- Discipline Dashboard should wait for a validated Feature 2 or SQL exploration
  before the UI is built.

Recommended first approval order:

1. Approve "Map Frontend Data Needs Before Adding Endpoints" as a working rule.
2. Approve "Improve Loading Empty Error And Cold-Start States" if we want a
   low-risk polish pass first.
3. Approve "Improve Navigation And Product Structure" before adding multiple
   pages.
4. Approve "Build Match Explorer As First Real Product Slice" as the first major
   product expansion.
5. Keep "Plan Discipline Dashboard As Next Feature-Led Product Area" as a draft
   until Research & Football Intelligence validates the discipline metric.
```
```

### Request: Map Frontend Data Needs Before Adding Endpoints

Status: implemented

Area: product direction

Current behavior:

```text
The frontend already uses several API endpoints, but future product ideas could
tempt agents to add backend endpoints before the UI need is clear.
```

Desired behavior:

```text
Before adding any new API endpoint for frontend work, the agent should map:

- the user workflow
- the visible UI component
- the exact data shape needed
- whether an existing endpoint can support the slice
- whether the data should come from a direct query or a future analytics view
```

Reason:

```text
This keeps the backend thin and prevents overbuilding. The UI should prove the
need before new endpoints are added.
```

Data/API needs:

```text
Use existing endpoints first. Add endpoints only when the planned UI cannot be
served cleanly by the current API.
```

Visual/UX notes:

```text
The data map should describe what the user sees, not just database fields.
```

Mobile behavior:

```text
If the data shape creates a wide table, note whether mobile should use stacked
cards, horizontal scrolling, or a reduced column set.
```

Accessibility notes:

```text
If the data is charted, note whether values also need a table or text fallback.
```

Out of scope:

```text
Do not add speculative endpoints.
Do not move stable metric logic into React just because it is faster.
```

Approval notes:

```text
Approved on 2026-05-25 as a guardrail for the first redesign slice. The current
API already exposes useful data, so the next agent should map and use existing
endpoint capabilities before adding new backend routes.
```

Implementation notes:

```text
Implemented for the League Intelligence Overview v1 slice. Data mapping result:

- Product header and data status use existing `/health` and `/seasons`.
- Summary cards use existing `/seasons/{season}/overview`.
- Featured Goal Timing preview uses existing `/insights/goal-timing`.
- Team signal preview uses existing `/teams`.
- Recent match evidence uses existing `/matches`.
- Event coverage preview uses the existing overview event breakdown.

No new FastAPI endpoints or response-shape changes were needed for this slice.
```

## Navigation And Information Architecture

Use this section for sidebar, tabs, page structure, routes, and how users move
around the app.

### Request: Improve Navigation And Product Structure

Status: draft

Area: navigation

Current behavior:

```text
The current sidebar lists League Overview and Goal Timing as usable sections,
with future pages shown as disabled placeholders.
```

Desired behavior:

```text
Move toward a clearer app structure with sections for:

- League Overview
- Goal Timing Explorer
- Match Explorer
- Team Profile
- Discipline Dashboard

Navigation should communicate which sections are live, which are planned, and
which are not ready yet.
```

Reason:

```text
The app should feel like a product users can browse, not a single dashboard with
placeholder links.
```

Data/API needs:

```text
No new data is required just to improve navigation. Data needs should be mapped
when each section becomes active.
```

Visual/UX notes:

```text
Navigation should stay compact and analytical. Avoid marketing-style hero
navigation or decorative page intros.
```

Mobile behavior:

```text
Mobile navigation should remain usable without taking over the whole screen.
```

Accessibility notes:

```text
Disabled or future links should not behave like active links unless they lead to
a clear placeholder state.
```

Out of scope:

```text
Do not build every page in one pass.
Do not add routes that pretend unfinished sections are complete.
```

Approval notes:

```text
Audit recommendation: keep this draft until the user approves whether the next
UI change should introduce real routing/pages or remain a single-page workspace
with stronger sections.
```

Implementation notes:

```text
Audit note: the current sidebar uses anchor links and disabled future links.
This is fine for the pilot, but a real Match Explorer or Team Profile will need
a clearer navigation pattern.
```

## League Overview

Use this section for the home/overview screen, summary cards, season selector,
league totals, recent matches, and event breakdowns.

### Request: Redesign League Intelligence Overview V1

Status: implemented

Area: league overview

Current behavior:

```text
The current League Overview proves the API-to-React path, but it still feels
like a pilot dashboard. It does not yet introduce the product clearly enough as
an independent UPL football intelligence platform, and its mobile experience is
not strong enough for the likely audience.
```

Desired behavior:

```text
Redesign the first screen into a polished, mobile-first League Intelligence
Overview that immediately communicates:

"This product helps users understand the Uganda Premier League through
statistical insight beyond ordinary fixtures, results, and tables."

The overview should lead with curated analytical value, then offer clear paths
to deeper exploration.

It should include:

1. A clear product header
   - Product name: UPL Match Intelligence.
   - Short positioning line focused on statistical insight from UPL match data.
   - Season selector and data freshness/status close to the header.

2. Analytical summary cards
   - Use meaningful football signals, not generic decorative stats.
   - Good candidates include matches covered, goals recorded, teams tracked,
     goal timing signal, event coverage, and data-quality status.

3. Featured Insight preview
   - Treat Goal Timing as the current flagship insight.
   - Show the core question, a compact chart or summary, and a clear "dig
     deeper" action.
   - Keep caveats near the insight when added-time exclusions, missing events,
     or other limitations affect interpretation.

4. Explore The Numbers preview
   - Show the next major product areas without pretending unfinished sections
     are complete.
   - Good preview areas include Team Analytical Summaries, Match/Event Explorer,
     and Discipline Dashboard.

5. Trust and methodology strip
   - Show last updated or data freshness information when available.
   - Show data source, API/database health, caveat/methodology link, and a clear
     route to contact/about information when available.
```

Reason:

```text
The first redesign slice should establish the product identity before adding
new deep features. Users should understand within a few seconds that this is a
UPL analytics/intelligence product, not a fixtures site, generic standings page,
or developer portfolio landing page.
```

Data/API needs:

```text
Use existing endpoints first, especially the current season overview, goal
timing insight, health/status, recent matches, teams, and events data already
available to the frontend.

Before adding any endpoint, follow the approved "Map Frontend Data Needs Before
Adding Endpoints" request. Add backend work only if the visible UI cannot be
served cleanly from existing API data.
```

Visual/UX notes:

```text
The design should feel modern, global-sports-analytics, clean, and credible.
It should not look like a marketing landing page, generic admin template, or
copy of the official UPL site.

Use the product model from PRODUCT_STRATEGY.md:

- curated insight first
- dashboard-style drilldowns second
- technical portfolio value quiet and secondary

Keep labels football-readable. Avoid raw database language in visible UI.
```

Mobile behavior:

```text
Design this screen mobile first.

At phone width:

- The product header, season selector, and data status should remain readable.
- Summary cards should stack cleanly.
- The featured insight should be understandable without horizontal squeezing.
- Charts should keep labels and values legible.
- Wide tables should be avoided above the fold; use compact cards, reduced
  columns, or horizontal scrolling only where genuinely tabular.
- Caveats and data freshness should not disappear.
```

Accessibility notes:

```text
Use semantic headings and labelled controls. Do not rely on color alone for
health, caveat, success, warning, or card/status meanings. Keep contrast and
tap targets suitable for mobile.
```

Out of scope:

```text
Do not build a full Match Explorer in this slice.
Do not build a full Discipline Dashboard in this slice.
Do not build player profile pages.
Do not add monetization, account/login flows, or social sharing tools.
Do not duplicate official-site fixtures/results as the main feature.
Do not redesign every future page at once.
```

Approval notes:

```text
Approved by the user on 2026-05-25 as the first redesign slice after the
product strategy discussion. The goal is to make the first screen communicate
the app's football intelligence identity and work properly on mobile.
```

Implementation notes:

```text
Implemented as a mobile-first overview redesign using existing API data only.
The first screen now leads with the UPL Match Intelligence product identity,
season/data controls, analytical summary cards, Goal Timing as the featured
insight, Explore The Numbers previews, team/event evidence panels, recent match
context, and a Trust and Methodology panel. Full Match Explorer, Discipline
Dashboard, Team Profile, React Router, and new backend endpoints remain out of
scope.
```

### Request: League Overview Placeholder

Status: idea

Area: league overview

Current behavior:

Desired behavior:

Reason:

Data/API needs:

Visual/UX notes:

Mobile behavior:

Accessibility notes:

Out of scope:

Approval notes:

Implementation notes:

## Goal Timing Explorer

Use this section for Feature 1 goal timing UI changes.

### Request: Goal Timing Placeholder

Status: idea

Area: goal timing

Current behavior:

Desired behavior:

Reason:

Data/API needs:

Visual/UX notes:

Mobile behavior:

Accessibility notes:

Out of scope:

Approval notes:

Implementation notes:

## Match Explorer

Use this section for match search, filters, match rows, match detail pages,
timelines, lineups, officials, and stats.

### Request: Build Match Explorer As First Real Product Slice

Status: draft

Area: match explorer

Current behavior:

```text
The League Overview shows recent matches, but there is no dedicated match
browsing workflow yet.
```

Desired behavior:

```text
Build Match Explorer as the first real product expansion after the audit. It
should let users browse and filter matches in a season, then eventually inspect
one match in more detail.

Initial useful controls could include:

- season
- team
- match day
- result type
- event type where relevant
```

Reason:

```text
Match Explorer turns the app from a summary dashboard into something a user can
actually browse. It is also a natural bridge to team profiles, timelines,
officials, and discipline.
```

Data/API needs:

```text
Start with existing `/matches` data. Only add or extend endpoints if the UI
needs match detail, timelines, lineups, officials, or stats that are not already
available cleanly.
```

Visual/UX notes:

```text
Use a dense, filterable list or table. Scorelines, dates, teams, venues, and
result labels should be easy to scan.
```

Mobile behavior:

```text
On mobile, match rows may stack into compact cards instead of forcing every
column into a table.
```

Accessibility notes:

```text
Filters need clear labels. Match rows should keep team names and scores readable
without relying on color alone.
```

Out of scope:

```text
Do not build full player pages in this slice.
Do not build every possible match statistic in the first version.
Do not make React read raw CSV files or notebooks.
```

Approval notes:

```text
Draft recommendation. Needs human approval before implementation.
```

Implementation notes:

```text
Audit note: this is the best first major product expansion. It can begin with
existing `/matches` data and frontend-side controls only if the data volume
stays small enough, then graduate to API-backed filters when needed.
```

## Team Profile

Use this section for team pages, team comparison, results summaries, discipline,
goal timing profiles, home/away splits, and player usage.

### Request: Team Profile Placeholder

Status: idea

Area: team profile

Current behavior:

Desired behavior:

Reason:

Data/API needs:

Visual/UX notes:

Mobile behavior:

Accessibility notes:

Out of scope:

Approval notes:

Implementation notes:

## Discipline Dashboard

Use this section for yellow/red cards, card timing, red-card impact, team
discipline, and official card rates.

### Request: Plan Discipline Dashboard As Next Feature-Led Product Area

Status: draft

Area: discipline dashboard

Current behavior:

```text
The overview shows card totals, but there is no dedicated discipline analysis
surface yet.
```

Desired behavior:

```text
Treat Discipline Dashboard as the likely next feature-led product area after
the first Match Explorer/navigation work. It should be backed by notebook or SQL
validation before becoming a polished dashboard section.

Possible first questions:

- Which teams collect the most yellow/red cards?
- Which teams have the highest cards per match?
- When do cards happen during matches?
- Which officials are associated with higher card counts?
```

Reason:

```text
Discipline is one of the clearest ways this project can provide insight beyond
the official website, but it should be research-backed before UI polish.
```

Data/API needs:

```text
Likely sources include `staging.events`, `staging.matches`, and later an
`analytics.*` view if the metric becomes stable or reused.
```

Visual/UX notes:

```text
Prefer comparison tables and simple charts over decorative cards. Make yellow
and red card meanings obvious without relying on color alone.
```

Mobile behavior:

```text
Prioritize a small set of readable comparisons on mobile.
```

Accessibility notes:

```text
Card colors should be paired with labels or icons so meaning is not color-only.
```

Out of scope:

```text
Do not build this before the metric is validated in a feature package or clear
SQL exploration.
Do not infer causation from cards without careful caveats.
```

Approval notes:

```text
Draft recommendation. Should connect to a future Feature 2 package before
implementation.
```

Implementation notes:

```text
Audit note: the overview already shows total cards, so discipline has a visible
entry point. It should still wait for Research & Football Intelligence to define
the metric and caveats before becoming a dashboard.
```

## Visual System

Use this section for color, typography, spacing, density, chart style, and data
visualization direction.

### Request: Visual System Placeholder

Status: idea

Area: visual system

Current behavior:

Desired behavior:

Reason:

Data/API needs:

Visual/UX notes:

Mobile behavior:

Accessibility notes:

Out of scope:

Approval notes:

Implementation notes:

## Iconography

Use this section for icons in navigation, buttons, filters, status indicators,
tables, and chart controls.

### Request: Iconography Placeholder

Status: idea

Area: iconography

Current behavior:

Desired behavior:

Reason:

Data/API needs:

Visual/UX notes:

Mobile behavior:

Accessibility notes:

Out of scope:

Approval notes:

Implementation notes:

## UX States

Use this section for loading states, empty states, API offline states, validation
warnings, free-tier cold starts, and blocked browser-extension cases.

### Request: Improve Loading Empty Error And Cold-Start States

Status: draft

Area: UX states

Current behavior:

```text
The app has an API offline panel and loading labels, but the states are still
basic and tied to the pilot layout.
```

Desired behavior:

```text
Improve the states users see when:

- the hosted Render API is waking up from a free-tier cold start
- the API is unreachable
- a browser extension blocks the hosted API request
- the selected season has no returned rows
- a section is planned but not yet built
- data exists but caveats affect interpretation
```

Reason:

```text
The public app runs on free-tier infrastructure, so users need calm, useful
feedback instead of confusing failure states.
```

Data/API needs:

```text
Use `/health/live` and `/health` where appropriate. Do not add a new endpoint
unless the UI cannot explain the state with current health responses.
```

Visual/UX notes:

```text
States should be concise, helpful, and visually integrated with the analytical
workspace. Avoid large warning blocks unless the issue blocks the page.
```

Mobile behavior:

```text
Messages should wrap cleanly and avoid pushing primary controls too far down the
page.
```

Accessibility notes:

```text
Error states should use clear text and appropriate alert semantics where they
describe a failed action or unavailable data.
```

Out of scope:

```text
Do not hide real errors.
Do not blame the user for source-data gaps or backend cold starts.
```

Approval notes:

```text
Audit recommendation: good low-risk polish candidate before major page work,
especially because the deployed API can cold-start on Render.
```

Implementation notes:

```text
Audit note: current error handling is helpful but global. Future work should
separate initial API availability, season data loading, section empty states,
and user-triggered refresh failures.
```

## Copy, Labels, And Caveats

Use this section for wording, football language, metric explanations, caveats,
and labels shown in the app.

### Request: Copy Placeholder

Status: idea

Area: copy and caveats

Current behavior:

Desired behavior:

Reason:

Data/API needs:

Visual/UX notes:

Mobile behavior:

Accessibility notes:

Out of scope:

Approval notes:

Implementation notes:

## Approved Implementation Queue

Move approved requests here when they are ready for the next implementation
pass.

```text
1. none currently. The 2026-05-25 overview redesign requests were implemented.
```

## Implementation History

After an approved request is implemented, add a short entry here.

### 2026-05-22

- Request: Audit Current Frontend Before Redesign
- What changed: Added the audit findings directly to this request document.
- Backend/API: No backend changes. Audit noted that existing endpoint filters
  should be mapped before adding new endpoints.
- Frontend: No frontend code changes. Audit reviewed `frontend/src/App.tsx`,
  `frontend/src/styles.css`, `frontend/src/api/client.ts`, and
  `frontend/src/api/types.ts`.
- Guideline updates: None yet. No durable UI/UX decisions were approved.
- Verification: Documentation-only change; checked with `git diff --check`.

### 2026-05-25

- Request: Adopt Mobile-First Redesign Mentality
- Request: Map Frontend Data Needs Before Adding Endpoints
- Request: Redesign League Intelligence Overview V1
- What changed: Reworked the first screen into a mobile-first League
  Intelligence Overview focused on product identity, curated Goal Timing
  insight, exploratory previews, supporting evidence, and trust/methodology.
- Backend/API: No backend changes. The slice used existing health, seasons,
  overview, goal timing, matches, and teams data.
- Frontend: Replaced the pilot dashboard layout in `frontend/src/App.tsx` and
  rewrote `frontend/src/styles.css` with mobile-first layout rules.
- Guideline updates: Added durable mobile-first and League Intelligence Overview
  v1 decisions to `UI_UX_GUIDELINES.md`.
- Verification: Ran `npm run build` and rendered desktop/mobile browser checks.

### YYYY-MM-DD

- Request:
- What changed:
- Backend/API:
- Frontend:
- Guideline updates:
- Verification:
