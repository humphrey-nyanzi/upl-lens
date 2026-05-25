# Frontend UX Requests

This is the editable source of truth for proposed UI and UX improvements.

Use this file for requests that still need discussion, approval, or
implementation. Durable decisions from implemented work belong in
[UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md). Product positioning and audience
rules belong in [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md).

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
6. Inspect `frontend/src/`, `api/`, and `src/api/` only enough to understand
   the affected product surface.
7. Implement only requests marked `approved`, unless the user explicitly says to
   work on a different status.
8. Keep React dependent on FastAPI JSON. Do not make React read CSV files,
   notebooks, or exported notebook images.
9. If new data is needed, prefer a thin FastAPI endpoint and query/service logic
   under `src/api/`.
10. After implementation, move durable UI/UX decisions to
    [UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md), then compress this file's
    implemented entry to one short statement.
11. Run `npm run build` for frontend changes and any relevant backend/API tests
    if endpoints changed.

## Active Requests

These are not approved yet. Discuss, refine, or approve them before
implementation.

### Request: Make The App Feel Like A Football Intelligence Workspace

Status: draft

Area: product direction

Request: Continue shaping the app into a compact football analysis workspace
where a user can scan the league, select a season, inspect matches, compare
teams, and understand validated insights.

Why it matters: The project should be an intelligence layer over UPL data, not a
generic dashboard or clone of the official website.

Data/API needs: No immediate endpoint requirement. This is a product direction
request that should guide future surfaces.

Mobile/accessibility notes: Mobile views should preserve the core analysis task
instead of merely squeezing desktop panels into one column.

Out of scope: Do not redesign every page from this broad request alone.

Approval notes: The user clarified on 2026-05-25 that the desired feel is clean,
easy to understand, data-rich, powerful, visually exciting, and like a modern
sports analytics site.

### Request: Define Fan-First Numbers System

Status: needs_review

Area: numbers system

Request: Define how headline numbers, totals, rankings, percentages, trends,
comparisons, and anomalies should appear across the app.

Why it matters: The app should win through figures, trends, charts, and
surprising stats that fans might not see elsewhere, while still giving analysts
reproducible numbers and clean drilldowns.

Data/API needs: No immediate endpoint requirement.

Mobile/accessibility notes: On mobile, show the most important numbers first.
Avoid grids that become too long or too dense.

Out of scope: Do not invent metrics without research or data support.

### Request: Define Rankings And Top-Five Preview Pattern

Status: needs_review

Area: numbers system, rankings

Request: Define a reusable pattern for rankings and top-five previews. When a
full table would be boring or too large, show the top five visually and let the
user click for more detail.

Why it matters: The user prefers minimizing tables, especially on mobile.

Data/API needs: Existing team, match, event, and future analytics data can
support many ranking previews. Some "view more" states may require pagination or
filters later.

Mobile/accessibility notes: Top-five lists should be readable on phones, with
clear labels and values.

Out of scope: Do not remove tables entirely where tabular detail is genuinely
the clearest view.

### Request: Define Chart And Visualization System

Status: needs_review

Area: chart system, visualizations

Request: Define chart rules for beautiful but simple, functional visualizations.

Why it matters: Charts should make the football story easier to understand and
should look consistent across pages.

Data/API needs: Chart choices should follow the available metric and product
question.

Mobile/accessibility notes: Charts must be legible on phones. If a chart cannot
work on mobile, use a simpler mobile version or a summary card.

Out of scope: Do not add animations or complex chart types just because they
look impressive.

### Request: Define Interactive Filter Rules

Status: needs_review

Area: filters, interaction design

Request: Define a moderate filtering system. Use only the filters that are
necessary for the page, such as season, team, result, home/away, or match
period.

Why it matters: The app should feel powerful, but not like a database tool.

Data/API needs: Use existing API filters where possible. Add backend filter
support only after the page workflow proves it is needed.

Mobile/accessibility notes: Filters should be easy to reach and understand on
phones.

### Request: Define Modern Visual Direction

Status: needs_review

Area: visual direction

Request: Define a durable visual direction for a modern sports analytics product.

Why it matters: The frontend should feel deliberate and exciting, without
becoming decorative or one-note.

Data/API needs: None.

Mobile/accessibility notes: Any visual direction must preserve mobile
readability and contrast.

### Request: Explore Dark And Light Theme Direction

Status: needs_review

Area: visual direction, theme

Request: Decide whether the app should stay light-workspace-first, move toward a
dark sports-analytics theme, or support both later.

Why it matters: Theme direction affects charts, contrast, screenshots, and brand
feel.

Data/API needs: None.

Mobile/accessibility notes: Contrast and readability should decide the theme,
not only aesthetics.

### Request: Define Mobile-First Data Display Rules

Status: needs_review

Area: mobile UX

Request: Define how tables, cards, rankings, charts, filters, and long content
should adapt on phones.

Why it matters: Mobile should be the default design constraint, not an afterthought.

Data/API needs: None immediately.

Mobile/accessibility notes: This request is specifically about mobile-first
readability and touch ergonomics.

### Request: Define Fan-Facing Interpretation Rules

Status: needs_review

Area: content design

Request: Define how the app explains numbers in football language without
turning each page into a long article.

Why it matters: The dashboard should be understandable to football fans and
credible to analysts.

Data/API needs: None immediately.

Mobile/accessibility notes: Short explanations should not crowd out the primary
metric on phones.

### Request: Plan Discipline Dashboard As Next Feature-Led Product Area

Status: draft

Area: feature planning, discipline

Request: Plan the future Discipline Dashboard after research validates the
football questions, metrics, and caveats.

Why it matters: Discipline is one of the most promising next intelligence areas,
but it should come from the feature-promotion workflow rather than UI guessing.

Data/API needs: Likely needs research queries over `staging.events`, then a
direct API query or `analytics.*` object if promoted.

Mobile/accessibility notes: Card totals, team comparisons, and top-five previews
may work better than wide tables.

Out of scope: Do not build this before the research/product plan is approved.

### Request: Future Placeholder Requests

Status: idea

Area: backlog

Request: Keep placeholders for future League Overview, Goal Timing, Team
Profile, visual system, iconography, and copy improvements only when they become
specific enough to act on.

Approval notes: These are not ready for implementation without a more specific
product surface.

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
1. Define Fan-First Numbers System
2. Define Rankings And Top-Five Preview Pattern
3. Define Chart And Visualization System
4. Define Interactive Filter Rules
5. Define Modern Visual Direction
6. Explore Dark And Light Theme Direction
7. Define Mobile-First Data Display Rules
8. Define Fan-Facing Interpretation Rules
9. Plan Discipline Dashboard As Next Feature-Led Product Area
```

Do not implement this queue directly. Each request should move to `approved`
only after user review.

## Implemented Archive

Implemented entries are intentionally short. Lasting decisions from these
requests should be recorded in [UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md).

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
- Use Skeleton Loading Before Error States: added skeleton-shaped loading states
  before confirmed errors.
- Improve Loading Empty Error And Cold-Start States: added reusable loading,
  empty, and error components for product pages.
- Make Overview Copy Fan-Facing And Remove Internal Product Language: changed
  overview language from internal product terms to public-facing football copy.
- Move Technical Trust Details To Methodology Data Notes Page: kept the overview
  lighter by moving source, freshness, and trust context to Data Notes.
