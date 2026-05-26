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

### Request: Establish Overview First-Viewport Contract

Status: implemented

Area: League Overview, layout, visual hierarchy

Request:

Make the League Overview first viewport behave like the mockup: page header,
KPI row, top of the Goal Timing preview, Top 5 Teams, and Recent Matches should
all be visible or clearly beginning on standard desktop without requiring a long
scroll.

Why it matters:

The current Overview has the right ingredients but still feels vertically
stacked. The mockup feels like a control room because the user can understand the
page's purpose in one scan.

Implementation requirements:

- Treat the Overview as a dashboard surface, not an article page.
- Keep the page header compact and outside any oversized hero treatment.
- Keep KPI cards shallow enough to support the main grid appearing quickly.
- Ensure the main grid begins in the first viewport on desktop.
- Reduce vertical gaps between header, KPI row, and main grid.
- Keep Overview content width aligned with the top bar and sidebar shell.
- Use existing `AppShell`, `HeroSection`, `KpiCard`, `FeaturedInsight`,
  `TopFiveCard`, and `RecentMatchPanel` patterns where practical.
- Do not hide important content below decorative spacing.

Acceptance criteria:

- On desktop, the user can see the page title, KPI row, and the start of the
  Goal Timing/Top 5/Recent Matches area at once.
- The Overview does not feel like a set of full-width sections stacked down the
  page.
- The first viewport communicates "UPL football intelligence workspace" before
  the user scrolls.

Data/API needs:

None. Use current overview, goal timing, teams, and matches data.

Mobile/accessibility notes:

Mobile may still scroll naturally, but the order must remain: compact header,
KPIs, Goal Timing preview, Top 5 Teams, Recent Matches, insight strip.

Out of scope:

Do not redesign Goal Timing Explorer, Match Explorer, Team Insights, or Data
Notes as part of this request.

Approval notes:

Implemented after approval. The Overview page now has a scoped first-viewport
layout wrapper, tighter header/KPI spacing, shallower KPI cards, and a more
compact main grid so the dashboard modules begin sooner without changing API
contracts or redesigning other pages.

### Request: Convert Overview Header Into Compact Dashboard Header

Status: implemented

Area: League Overview, header, page composition

Request:

Replace any hero-like Overview header treatment with a compact dashboard header
that matches the mockup: title, one short fan-facing subtitle, and no large
status/coverage panel.

Why it matters:

The mockup gets to the analytical content quickly. A large hero makes the page
feel like a landing page instead of a practical league workspace.

Implementation requirements:

- Keep `League Overview` as the main title.
- Use one short sentence under the title.
- Keep season selection in the top bar only.
- Keep data status in the sidebar and Data Notes page.
- Do not show coverage window or selected-season details prominently in the
  Overview header.
- Reduce header padding on desktop and mobile.
- Keep the title visually strong but smaller than a marketing hero.
- Remove decorative hero-only effects that do not help scanning.

Acceptance criteria:

- The header feels like the start of a dashboard, not a banner.
- KPIs appear immediately after the header with minimal dead space.
- The header does not duplicate information already shown in the top bar or
  sidebar.

Data/API needs:

None.

Mobile/accessibility notes:

On mobile, the header should be short enough that the first KPI row begins early
on the screen.

Out of scope:

Do not remove the Data Notes page or sidebar data status.

Approval notes:

Needs review. This is a prerequisite for the Overview density target.

### Request: Rebuild KPI Row As Compact Football Scoreboard Cards

Status: implemented

Area: League Overview, KPI cards, metric hierarchy

Request:

Refine the Overview KPI row so it reads like the mockup's compact sports
scoreboard: four tight cards with a small icon/marker, football-native label,
dominant value, and short trend/context line.

Why it matters:

The current KPI cards are accurate but still feel too tall and partly
data-platform oriented. The mockup's KPIs are faster to scan and use less
vertical space.

Implementation requirements:

- Use exactly four Overview KPI cards on desktop.
- Keep all four cards in one row at desktop widths.
- Use shorter fan-facing labels, for example:
  - `Matches Played` or `Matches Covered`
  - `Goals Scored` or `Recorded Goals`
  - `Teams`
  - `Cards Logged`
- Avoid internal labels such as `Timeline goals` unless the wording is clearly
  explained in the card context.
- Put the primary number first visually.
- Keep supporting text to one short line where possible.
- Use icons or stable visual markers consistently; do not use random decorative
  symbols.
- Use green only for positive/status emphasis and gold only for the key/peak
  card.
- Keep card height close to the mockup's compact rhythm.

Acceptance criteria:

- KPIs are readable at a glance without making the first screen tall.
- Card labels sound like football product language, not database language.
- The row feels like one system, not four unrelated cards.

Data/API needs:

Use existing season overview data only.

Mobile/accessibility notes:

Mobile should use a readable two-column KPI grid. Values must not overflow or
force horizontal scrolling.

Out of scope:

Do not add new metrics or backend endpoints.

Approval notes:

Needs review. Implement after the compact header so the top of the Overview
matches the mockup rhythm.

### Request: Create Compact Overview Goal Timing Heatmap Preview

Status: implemented

Area: League Overview, Goal Timing preview, chart design

Request:

Create a compact Overview-specific Goal Timing preview that looks closer to the
mockup's heatmap panel. The Overview preview should show the scoring pattern
quickly, while the dedicated Goal Timing page can keep fuller values, caveats,
and explanation.

Why it matters:

The current Overview heatmap is readable but behaves like a full Goal Timing
Explorer embedded into the Overview. The mockup uses Goal Timing as a compact
signature visual, not a long detailed chart section.

Implementation requirements:

- Keep the existing detailed `GoalTimingHeatmap` available for the Goal Timing
  page.
- Add or configure an Overview variant such as `GoalTimingHeatmapPreview`.
- Use compact cells or a matrix-like chart treatment rather than large metric
  tiles.
- Keep the peak window visually gold/lime and labelled in nearby text.
- Show enough labels to understand the timing intervals without creating a
  long value table.
- Keep legend close to the chart and visually small.
- Hide, collapse, or shorten the full interval value list on Overview.
- Keep added-time caveat visible but compact.
- Make the Goal Timing panel the largest Overview panel, but not taller than the
  combined side column without purpose.
- Use design tokens for green/gold/neutral colors.

Acceptance criteria:

- Overview Goal Timing feels like a visual preview, not the full feature page.
- The chart area is recognizable as a heatmap-style football signal.
- The panel fits alongside Top 5 Teams and Recent Matches in a balanced desktop
  grid.

Data/API needs:

Use the existing Goal Timing API payload. Do not add backend work.

Mobile/accessibility notes:

Mobile may use two-column cells or a simplified stacked layout. A readable value
fallback must remain available near the chart or in the dedicated Goal Timing
page.

Out of scope:

Do not redesign the full Goal Timing Explorer page in this request.

Approval notes:

Implemented after approval. The Overview now uses a dedicated compact
GoalTiming heatmap preview instead of embedding the larger explorer-style
heatmap. The preview keeps the peak window, compact legend, and added-time
caveat visible while preserving the full detailed chart treatment for the Goal
Timing page.

### Request: Make Overview Main Grid A Balanced Dashboard Band

Status: implemented

Area: League Overview, grid composition

Request:

Refine the Overview main grid so Goal Timing, Top 5 Teams, and Recent Matches
read as one coordinated dashboard band rather than separate stacked sections.

Why it matters:

The mockup feels cohesive because the three main panels share height, spacing,
and alignment. The current version has the right panels, but the Goal Timing
panel dominates vertical space and pushes supporting context too far down.

Implementation requirements:

- Use a desktop grid where Goal Timing takes the larger left area.
- Stack Top 5 Teams and Recent Matches in the right column.
- Align panel tops and keep right-column panels visually connected.
- Set panel padding and internal gaps specifically for Overview density.
- Avoid making the Goal Timing preview taller than the right column unless the
  visual design clearly justifies it.
- Keep the bottom insight strip close enough to feel like part of the Overview,
  not a separate page section.
- Avoid nested-card visual clutter inside panels.
- Use reusable components, but allow Overview-specific compact variants.

Acceptance criteria:

- The main grid feels like one dashboard composition.
- Top 5 Teams and Recent Matches are visible beside Goal Timing on desktop.
- The user does not need to scroll through the entire heatmap detail before
  seeing Recent Matches or the insight strip.

Data/API needs:

Use existing Overview, teams, matches, and Goal Timing data.

Mobile/accessibility notes:

Mobile order should remain: Goal Timing preview, Top 5 Teams, Recent Matches.
The panels should stack cleanly with no horizontal overflow.

Out of scope:

Do not modify Match Explorer or Team Insights.

Approval notes:

Needs review. Implement after the compact Goal Timing preview is available.

### Request: Turn Top 5 Teams Into A Sports-Native Ranking Module

Status: implemented

Area: League Overview, rankings, football identity

Request:

Refine the Overview Top 5 Teams panel into a compact sports ranking module like
the mockup: rank, team identity marker, team name, primary value, and optional
short context.

Why it matters:

The current `TopFiveCard` is structurally useful, but the Overview ranking still
feels generic. The mockup reads like a football table preview.

Implementation requirements:

- Keep `TopFiveCard` or a similar reusable ranking component.
- Add a small team marker slot:
  - team badge if available later
  - stable initials or colored team chip if badges are not available
- Show rank, marker, team name, and points/value in one compact row.
- Keep context such as record/win rate secondary and short.
- Highlight the leader subtly with gold or active surface treatment.
- Add an optional action slot for `View full table` or `Compare teams`.
- Keep row heights compact enough for all five teams to fit in the panel.
- Avoid wide tables and repeated generic cards.

Acceptance criteria:

- The panel communicates "Top 5 Teams" in under two seconds.
- Values align cleanly on the right.
- The module feels football-native even without real club crest assets.

Data/API needs:

Use existing team data. Do not add player rankings or standings endpoints.

Mobile/accessibility notes:

Rows should wrap team names gracefully and preserve the right-aligned value. The
rank and marker should not crowd the label on narrow screens.

Out of scope:

Do not build full standings, player rankings, or a team comparison feature.

Approval notes:

Implemented after approval. The Top 5 Teams panel now uses compact ranking
rows with rank, stable initials marker, team name, secondary record/win-rate
context, right-aligned points, subtle leader emphasis, and a direct action into
team insights without adding data or backend work.

### Request: Convert Recent Matches Into Compact Result Rows

Status: implemented

Area: League Overview, recent results, match previews

Request:

Replace large Overview match cards with compact recent-result rows that match
the mockup's "Recent Results" treatment: date/context, teams, scoreline, and
result state in a tight scan-friendly format.

Why it matters:

Current match cards are readable but too large for the Overview side column.
The mockup uses results as supporting evidence, not as full match cards.

Implementation requirements:

- Keep the larger `MatchRow` treatment available for Match Explorer if useful.
- Create an Overview-specific compact result row or variant.
- Show date or matchday in a small muted label.
- Show both teams in a compact football-readable line.
- Show scoreline as the strongest element on the right.
- Show result state such as `Home win`, `Away win`, or `Draw` as compact
  metadata.
- Limit the number of rows so the panel height matches the Top 5 panel rhythm.
- Add an optional `View all matches` action only if it links to Match Explorer.
- Avoid multiline rows becoming tall unless team names genuinely require it.

Acceptance criteria:

- Recent Matches fits comfortably in the right column.
- The scoreline is instantly visible.
- The panel supports the Overview without competing with Goal Timing.

Data/API needs:

Use existing matches data only.

Mobile/accessibility notes:

Rows may stack scoreline below team names on very narrow screens, but they must
not overflow horizontally.

Out of scope:

Do not build match detail pages or timelines.

Approval notes:

Implemented after approval. The Overview now uses compact result rows for
Recent Matches with a small date/matchday label, tight team line, right-aligned
scoreline, compact result state, and a direct action into Match Explorer while
leaving the larger Match Explorer match-row treatment intact.

### Request: Compress Insight Strip Into A True Dashboard Footer

Status: implemented

Area: League Overview, insight strip, navigation

Request:

Refine the Overview insight strip so it behaves like the mockup's compact
bottom band: three short insight/action cards plus one clear action, all visually
connected to the main dashboard.

Why it matters:

The current insight strip is useful but too section-like. The mockup uses it as
a slim continuation of the dashboard, not a new large content block.

Implementation requirements:

- Keep exactly three short insight/action items on Overview.
- Use compact cards or rows with small icon/marker, title, and one short line.
- Keep copy football-facing and action-oriented.
- Keep the `View all insights` action visually aligned with the strip.
- Reduce vertical padding and card height.
- Avoid long paragraphs inside the strip.
- Avoid making the strip visually heavier than the main grid.
- Keep the strip close to the main grid.

Acceptance criteria:

- The strip reads as a quick next-step band.
- It does not require a large scroll after Recent Matches.
- It supports, rather than competes with, Goal Timing and Top 5 Teams.

Data/API needs:

None. Use current navigation actions and supported product areas.

Mobile/accessibility notes:

On mobile, the three items can stack, but each should remain short and tappable.

Out of scope:

Do not create new insight pages or unsupported features.

Approval notes:

Implemented after approval. The Overview insight strip now behaves like a
compact dashboard footer with three short action cards, small football-native
markers, reduced vertical padding, shorter copy, and an aligned `View all
insights` action. It uses existing supported routes only and does not introduce
new API/backend work.

### Request: Add Football-Native Visual Markers Without Fake Data

Status: needs_review

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

Needs review. This can be implemented alongside Top 5 and Recent Matches row
work.

### Request: Separate Overview Preview Detail From Explorer Detail

Status: implemented

Area: information architecture, Overview, Goal Timing, Match Explorer

Request:

Create a clear rule in the frontend implementation: Overview modules should
preview the most important signal, while dedicated pages should carry detailed
values, caveats, filters, and explanations.

Why it matters:

The current Overview sometimes includes too much detail from deeper pages,
especially around Goal Timing values and caveats. The mockup succeeds by
showing enough to invite exploration without turning the Overview into the full
analysis.

Implementation requirements:

- Audit Overview modules for details that belong on dedicated pages.
- Keep the strongest number, visual, or row set on Overview.
- Move longer value lists, long caveats, and interpretation text to the
  dedicated page or Data Notes when appropriate.
- Keep a compact caveat on Overview only when the caveat affects immediate
  interpretation.
- Provide action buttons into deeper pages where supported.
- Do not remove trust information entirely.

Acceptance criteria:

- Overview feels scannable.
- Dedicated pages remain the place for explanation and detail.
- Caveats remain visible but no longer dominate preview modules.

Data/API needs:

None.

Mobile/accessibility notes:

Mobile users should see the key signal before long explanatory text.

Out of scope:

Do not remove caveats from the product. Reposition or shorten them.

Approval notes:

Implemented after approval. The Overview Goal Timing card now treats the
heatmap as a compact preview: it keeps the peak window and immediate caveat
visible, removes full interval values from the Overview, and leaves detailed
values, method context, and interpretation on the dedicated Goal Timing page.


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
9. Add Football-Native Visual Markers Without Fake Data
11. Run screenshot review against the mockup on desktop and mobile
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
