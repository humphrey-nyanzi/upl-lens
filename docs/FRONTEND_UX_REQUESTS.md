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

### Request: UPL Lens Public Launch Frontend Redesign (Master Request)

Status: approved

Area: frontend redesign, launch

Request:

This is the master approved request that authorizes the frontend redesign and
public launch under the UPL Lens brand. It supersedes prior mockup-only
requests and consolidates high-level decisions and approved surface rules.

Why it matters:

The redesign and relaunch unify product naming, visual identity, and the
approved high-fidelity decisions listed in `docs/FRONTEND_DESIGN_SYSTEM.md`.

Clarifications for launch (binding for this approved request):

- Editorial Light is the default theme for UPL Lens. Implement the light token
  set as the launch baseline.
- Dark mode is an optional future variant and is not required for launch.
- The sidebar must show only one visible support link: "About". Methodology
  and data notes must be accessible from About, not as a separate top-level
  navigation item.
- No export button on public pages by default.
- No official club logos embedded; use team-initial badges with stable seeded
  palettes.

Data/API needs:

Map existing frontend data requirements to current FastAPI endpoints. Any new
data need must be proposed as a separate request with `Data/API needs` filled
out and approved before implementation.

Mobile/accessibility notes:

Follow existing accessibility principles in the design system. Mobile-first
layouts are required; desktop enhancements allowed when they preserve
accessibility.

Out of scope:

- Directly changing backend data models
- Adding CSV or notebook data sources to the frontend

Approval notes:

Approved as the canonical redesign and launch request for UPL Lens. Use this
file for ticket-level details, but move durable decisions into
`docs/FRONTEND_DESIGN_SYSTEM.md` and the UPL Lens start file.



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

### Request: Reorganize Overview Cards into Single Horizontal Row

Status: approved

Area: League Overview layout

Request:

Reorganize the featured insight card, league leaders card, and recent matches card into a single horizontal row layout. The featured insight card should take up 60% of the width, while the league leaders and recent matches cards share the remaining 40%. There should be no blank space underneath the featured insights card.

Why it matters:

This creates a more compact, dashboard-like first viewport that uses horizontal space efficiently and eliminates vertical gaps that make the page feel sparse.

Implementation requirements:

- Place featured insight, league leaders, and recent matches cards in one horizontal row
- Featured insight card: 60% width
- League leaders and recent matches cards: share 40% (20% each or stacked vertically within the 40% column)
- No blank space underneath the featured insights card
- Maintain responsive behavior on mobile (stack vertically on small screens)

Data/API needs:

None - uses existing data.

Mobile/accessibility notes:

On mobile screens, cards should stack vertically to maintain readability.

Out of scope:

None.

Approval notes:

Approved by user for immediate implementation.

### Request: Hero Section Background Image Integration

Status: approved

Area: League Overview hero section

Request:

Make the hero section image a background image of the entire hero section, with the text "understand the premier league" etc appearing on the left side within the image area, and the footballer visible on the right with no text overlaying him.

Why it matters:

This creates a more integrated, cohesive hero section where the image and text feel like part of the same design rather than two separate containers.

Implementation requirements:

- Use the hero image as a background image for the hero section
- Position text on the left side within the image area
- Ensure the footballer on the right remains visible with no text overlay
- Maintain readability of text against the background
- Ensure responsive behavior on mobile

Data/API needs:

None - uses existing image.

Mobile/accessibility notes:

Text must remain readable against the background image on all screen sizes. Consider overlay or gradient if needed for contrast.

Out of scope:

None.

Approval notes:

Approved by user for immediate implementation.

### Request: Redesign Overview Cards Layout and Styling

Status: approved

Area: League Overview main cards

Request:

Redesign the featured insight, recent matches, and league leaders cards to match the reference design with improved visual hierarchy, clearer data presentation, and more polished card styling.

Why it matters:

The current cards need better visual treatment to match the intended design direction with clearer metrics, better spacing, and more professional appearance.

Implementation requirements:

- Update Featured Insight card to show large metric (e.g., "41%") prominently with chart
- Update Recent Matches card to show compact result rows with team markers
- Update Team Signals card to show form guide with visual match history indicators
- Improve card styling with better borders, shadows, and spacing
- Ensure all cards maintain the 60%/40% horizontal layout
- Add appropriate buttons for "Explore", "View all", etc.

Data/API needs:

None - uses existing data.

Mobile/accessibility notes:

Cards should stack vertically on mobile while maintaining readability.

Out of scope:

None.

Approval notes:

Approved by user for immediate implementation.

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
