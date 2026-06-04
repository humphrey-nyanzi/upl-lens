# Frontend Design System

This document is the frontend playbook for the public product now known as
UPL Lens (frontend). It documents durable visual and UX rules that should
drive implementation. Historical references to "UPL Match Intelligence"
remain for archival context; the active frontend source-of-truth for launch is
the UPL Lens design guidance below and
[UPL_LENS_FRONTEND_START_HERE.md](UPL_LENS_FRONTEND_START_HERE.md).

This document is the single source of truth for:

- approved visual direction
- durable UI and UX rules
- layout, token, and component guidance
- page templates and product-surface expectations
- visual acceptance criteria for future frontend work

Use this with:

- [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md)
- [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md)
- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)
- [UPL_LENS_FRONTEND_START_HERE.md](UPL_LENS_FRONTEND_START_HERE.md)

## UPL Lens Launch Docs

For the current public frontend relaunch, use these companion docs in this
order:

1. [UPL_LENS_HIGH_FIDELITY_DESIGN_BRIEF.md](UPL_LENS_HIGH_FIDELITY_DESIGN_BRIEF.md)
2. [UPL_LENS_TEXT_WIREFRAMES.md](UPL_LENS_TEXT_WIREFRAMES.md)
3. [UPL_LENS_PAGE_REQUIREMENTS.md](UPL_LENS_PAGE_REQUIREMENTS.md)
4. [UPL_LENS_INFORMATION_ARCHITECTURE.md](UPL_LENS_INFORMATION_ARCHITECTURE.md)
5. this design system
6. [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md)

Use this file for durable implementation rules and accepted standards. If a
launch-specific UPL Lens artifact carries an explicit exception, follow that
artifact and then fold the durable part back into this file once implemented.

## Product Architecture Rule

The product path is:

```text
React UI -> FastAPI endpoint -> Postgres query/view -> JSON -> chart/table
```

React must not read:

- raw CSV files
- notebooks
- exported notebook charts
- local database files

If the UI needs new data, add or extend the FastAPI and query layer instead of
bypassing it.

## Source Record Vs Intelligence Layer

Durable product boundary:

```text
Official UPL site = source record.
UPL Lens = analytical meaning.
```

UPL Lens should not drift into becoming a cleaner copy of official UPL match
pages. A surface may show raw source details only when those details support a
clear analytical purpose.

Use this treatment ladder for official-source details:

- **Transform** details into insight when possible: timing patterns, match
  rhythm, card pressure, late-drama signals, trend fit, season-relative
  comparisons, official tendencies, or anomaly flags.
- **Summarize** details when they provide useful context: scoreline, key
  events, a short match context strip, or compact source facts.
- **Link out** when the user wants full archive detail that UPL Lens is not
  transforming yet: full raw timeline, full lineup, plain officials list, or
  full official match record.

Match detail pages should behave as **Match Intelligence Briefs**. They should
explain why a match matters and how it fits league/team patterns, not simply
rebuild the official match report with a different design.

When a frontend request or page requirement risks duplicating the official UPL
site, review it against this boundary before implementation.


## UPL Lens high-fidelity design decisions (durable)

The UPL Lens frontend redesign uses a focused set of high-fidelity decisions
that are binding for the public launch. These are the durable visual rules
that the frontend must implement unless a new approved request changes them.

- Editorial Light default theme (light visual baseline for content-forward
  presentation)
- Stacked "UPL / Lens" brand lockup (do not use legacy long-form logos)
- Desktop: left fixed sidebar navigation (desktop app shell)
- Mobile: bottom navigation bar for primary sections (mobile bottom nav)
- "About" as the only visible support link in the sidebar (keep support
  minimal and discoverable)
- Social links grouped in a single bottom row of the sidebar/footer
- No export button on public pages (no CSV/print export affordance by default)
- No official club logos embedded or used; use initials/badges instead
- Team initials badges use native-colour-inspired palettes (stable seeded
  palettes derived from club name initials)

These decisions are intentionally narrow and durable: they guide the UI
structure, placement of support links, theming baseline, and asset usage.

Use the rest of this file to describe component tokens, layout rules, and
accessible behaviors that implement the rules above.

## Product Visual Identity (context)

UPL Lens should feel like:

```text
a football intelligence workspace
+ a league analytics control room
+ a clean sports report card
```

The app should feel:

- practical
- premium
- data-rich
- football-native
- fast to scan
- mobile-first
- credible for analysts
- understandable for fans

It should not feel like:

- a generic AI SaaS dashboard
- a betting product
- Power BI or Tableau
- a raw database admin panel
- a notebook export
- a developer portfolio homepage
- a decorative marketing website
- a purple or cyan glassmorphic template

## Approved Product Surfaces

These surfaces are approved as part of the public product direction:

- League Overview
- Goal Timing Explorer
- Match Explorer
- Team Insights / Team Profile
- Discipline Dashboard
- Methodology / Data Notes

The current deployed app is still a pilot. It proves the architecture, but the
long-term direction is a richer analytical product.

## Current Implementation Baseline

The current frontend implementation baseline and the approved launch
direction are aligned as follows:

- Editorial Light is the default theme for UPL Lens (content-forward, readable
  baseline).
- Dark mode is supported as an optional future theme/variant; dark tokens are
  retained in this document as an explicitly labelled optional variant.
- Desktop left sidebar for primary navigation (fixed on desktop).
- A compact top control bar for season, search affordance, and contextual
  controls (avoid export affordances by default).
- Compact mobile navigation; mobile first layout rules apply.
- reusable surface primitives
- modular page components under `frontend/src/pages/`
- reusable components under `frontend/src/components/`
- FastAPI-backed hooks and client calls

The first mockup-aligned redesign pass is complete. Future frontend work should
come from [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md) or explicit user
instruction.

## Approved Visual Direction

The approved direction is a hybrid of:

1. grounded sports analytics dashboard structure
2. restrained premium product polish

That means:

- structured, readable, operational layouts
- subtle elevation and spacing improvements
- football-native green and gold accents
- strong number hierarchy
- mobile-first composition

It does not mean:

- heavy glassmorphism
- decorative blur
- fake AI gradients
- unsupported navigation concepts
- dense desktop layouts that collapse on mobile

## Layout Principles

Approved principles:

- Design product-facing screens mobile first, then enhance for desktop.
- Use dense but readable layouts.
- Keep controls close to the data they affect.
- Use the available desktop width like a real workspace.
- Avoid article-style narrow columns on analytical pages.
- Keep the first screen useful, not promotional.
- Avoid decorative sections that do not help analysis.

### Desktop App Shell

Desktop should use:

```text
Sidebar | Main Workspace
        | Top Controls
        | Page Content Grid
```

Rules:

- Sidebar remains fixed on desktop.
- Main workspace fills the remaining width.
- Analytical pages should support widths around `1200px-1440px`.
- The top bar should align visually with the content grid.
- KPI rows and main grids should use multiple columns when helpful.

Recommended structure:

```text
AppShell
  Sidebar
  Main
    TopBar
    Compact PageHeader
    KPI Row
    Main Grid
    Supporting Insights
```

League Overview should use a compact dashboard header, not a hero banner:
title, one short subtitle, no duplicated season/status/coverage content, and no
decorative panel treatment that delays the KPI row.

### Mobile Layout

Mobile is not a squeezed desktop.

Rules:

- Show the most important numbers first.
- Use one-column flow by default.
- Use two-column KPI grids only when readable.
- Prefer compact previews over wide tables.
- Keep caveats near affected data.
- Avoid horizontal scroll except for genuinely tabular comparison.

## Navigation Principles

Approved principles:

- The app should have clear sections for major workflows.
- Primary navigation should behave like page navigation once a section is a real
  product area.
- Lightweight hash-based navigation is acceptable while the product has only a
  few top-level pages.
- Navigation labels should use product language, not database language.
- Disabled or future sections should not look like finished features.
- Phone layouts should use compact primary navigation instead of horizontally
  scrolling link bars.
- Navigation must expose the current page clearly.

## Data Display Principles

Approved principles:

- Use readable football labels instead of raw database column names.
- Use football-native team and match markers where they improve scanning, but
  only from existing team names or real future assets.
- When crest assets are not available, use stable initials or restrained badge
  placeholders; never invent official club logos.
- Map visible frontend data needs before adding new API endpoints.
- Show season context clearly.
- Show loading, empty, and error states.
- Do not hide source-data limitations.
- Do not calculate durable league-wide metrics in React if they belong in
  Postgres or FastAPI.
- Keep backend route functions thin and query logic in `src/api/`.

## UX State Principles

Approved principles:

- Use skeleton loading states during the first meaningful wait before confirmed
  errors.
- Skeletons should match the incoming content shape and avoid layout jumps.
- Loading states should make free-tier backend cold starts understandable.
- API offline states should identify the API host when useful.
- Empty states should explain what is missing without blaming the user.
- Validation and data caveats should stay visible when they affect
  interpretation.

## Accessibility Principles

Approved principles:

- Use semantic HTML where practical.
- Keep interactive controls keyboard-accessible.
- Preserve readable contrast.
- Do not rely on color alone to communicate status.
- Use clear labels for filters and controls.

## Color System

The color system should feel public, clean, editorial, trustworthy, warm, and analytical.


### Light Mode Tokens (default)

| Token | Purpose | Value |
|------|---------|-------|
| `--color-bg` | Main editorial background | `#F5F3EE` |
| `--color-surface` | Primary card and shell surface | `#FFFDFC` |
| `--color-surface-soft` | Secondary surface | `#F3F0E9` |
| `--color-text` | Main text / Deep Navy | `#0F1720` |
| `--color-text-secondary` | Supporting text / Charcoal | `#1E2933` |
| `--color-text-muted` | Quiet labels | `#667064` |
| `--color-green` | Primary action, selection, and data emphasis | `#1F7A3A` |
| `--color-gold` | Peak insight and warm attention accent | `#D4A017` |
| `--color-gold-deep` | Accessible gold text | `#6F5208` |
| `--color-border` | Base border, softened through surface tokens | `#E6E6EB` |
| `--surface-border` | Default subtle card border | `rgba(15, 23, 32, 0.045)` |

### Dark Mode Tokens (optional / future variant)

These tokens are retained for reference. Dark mode is a future/optional
variant and should be implemented only if explicitly approved as a toggle or
alternate theme. Use the light tokens as the default implementation target.

| Token | Purpose | Value |
|------|---------|-------|
| `--color-bg-app` | Main app background | `#071118` |
| `--color-bg-shell` | Sidebar and top bar | `#0B1720` |
| `--color-bg-panel` | Primary cards and panels | `#101F2A` |
| `--color-bg-panel-soft` | Secondary surfaces | `#162533` |
| `--color-bg-elevated` | Raised cards | `#122635` |
| `--color-border-subtle` | Default border | `#243544` |
| `--color-border-strong` | Active border | `#315062` |
| `--color-text-primary` | Main text | `#F3F7F2` |
| `--color-text-secondary` | Supporting text | `#A9B6BF` |
| `--color-text-muted` | Quiet labels | `#7F8D99` |
| `--color-accent-green` | Primary accent | `#1F7A3A` |
| `--color-accent-gold` | Peak insight | `#D4A017` |
| `--color-risk` | Error and discipline | `#EF4444` |
| `--color-success` | Healthy status | `#22C55E` |

### Color Rules

- Football green is the main action and selected-state accent.
- Warm gold is reserved for peak insight moments and chart emphasis.
- Use `--color-gold-deep` or `--color-accent-gold-text` when gold carries text.
- Red is for errors, risk, discipline, or negative states.
- Purple and cyan gradients should not become the dominant treatment.
- Default surfaces should use neutral borders unless they are selected or
  carrying a meaningful signal.
- Green and gold interaction states should use `--state-green-*` and
  `--state-gold-*` tokens instead of one-off alpha values.

## Typography And Number Hierarchy

Approved decisions:

- Global font rule:
  - Headings (`h1`-`h6`) must use **Manrope Semibold** (`font-weight: 600`).
  - Body and UI text must use **Source Sans 3 Regular** (`font-weight: 400`), with Semibold for labels and controls.
  - This is a cross-app requirement and should be enforced in shared global
    styles, not per-page overrides.
- Headline numbers should be visually dominant.
- Metric cards should prioritize the number, then a short context line.
- `KpiCard` is the shared component for headline metric cards. It supports
  label, value, context/detail text, optional trend/meta text, optional icon,
  neutral/green/gold/risk accents, and default/featured/compact variants.
- Page titles should be strong and clear without becoming oversized.
- Section labels should remain small, uppercase, and muted.
- Every major number should carry context, trend, rank, or caveat.
- Use football-facing labels instead of database field names.

## Spacing, Radius, And Elevation

Approved decisions:

- Use a restrained but more polished radius scale: `6px` controls, `10px` KPI
  cards, `12px` panels, and `14px` large featured surfaces.
- Shared surface variants are `surface-flat`, `surface-card`,
  `surface-panel`, `surface-featured`, `surface-muted`, and `surface-active`.
- Use `--surface-editorial-translucent` and `--surface-editorial-quiet` for
  overview cards that sit over atmospheric imagery. Data-heavy pages should
  continue using mostly solid surfaces.
- Common control and card motion should use `--transition-control` and
  `--transition-surface`.
- Use subtle depth instead of heavy shadows.
- Panels should not all look identical; hierarchy should come from surface tone,
  size, and information density.
- Data-heavy surfaces should stay mostly solid for readability. Avoid heavy
  glow, strong blur, neon borders, and generic glassmorphism.

## Component System

Approved reusable directions:

- `PageHero`
- `SectionPanel`
- `MetricCard`
- `InsightCard`
- `RankingCard`
- `ChartPanel`
- `MatchCard`
- `DataStatusCard`

Component rules:

- Metric cards should combine a clear label, strong numeric value, and one
  short football-readable explanation.
- Rankings should show clear rank, team, and value hierarchy.
- Match rows should surface date, teams, score, and result state before deeper
  detail.
- Match detail surfaces should prioritize intelligence summaries over complete
  raw source replication. Full official details should be linked out unless
  they are transformed into UPL Lens analysis.
- Team summary cards should show analytical signals such as win rate, ranking,
  record, goal difference, and goals for or against where available.
- Filter groups should be moderate and page-specific.
- Empty states should explain what is missing calmly and briefly.

## Chart And Table Guidelines

Approved principles:

- Analytical charts must use Recharts through reusable frontend chart
  components. Do not build new chart-like visuals from ad hoc cards, div bars,
  or CSS-only blocks when a real chart is being displayed.
- Charts should answer a football question, not merely decorate the page.
- Tables should support comparison and scanning.
- Chart labels should be understandable without reading code.
- Caveats should sit near the chart or table they affect.
- Explorer pages should favor filters, compact cards, summaries, and drilldown
  paths over raw database-style tables.
- Top-level pages should use previews before full tables when the data is still
  understandable clearly.

## Page Templates


### League Overview

The first screen should present UPL Lens as a football data observatory, not a
generic dashboard or fixtures site.

It should lead with:

- product positioning
- season and data status
- analytical summary cards
- the current featured insight
- visible trust and caveat context
- atmospheric football imagery behind the overview composition, not enclosed as
  a separate banner image

### Featured Insight Pages

Use a reusable structure:

- football question
- headline finding
- useful chart
- short explanation
- data note
- drilldown where the data supports it

Goal Timing is the current flagship example.

### Explorer Pages

Use:

- moderate filters
- compact summaries
- compact ranked or grouped cards
- drilldown paths instead of giant raw tables by default

### Team Pages

Team pages should be analytical summaries, not basic profiles.

### Methodology And Data Notes

Technical trust details belong on a dedicated page instead of crowding the
overview. Explain source, data path, freshness, known limitations, and caveats
in plain language.

## Anti-Patterns

Avoid these directions in this order:

- too much like Tableau or Power BI
- too much like a betting site
- too much like a generic template dashboard
- too developer-ish
- too crowded
- too empty
- too playful
- too corporate

## Visual Acceptance Criteria

Every frontend redesign pass should be reviewed against these checks:

- It feels like a real sports intelligence product.
- It avoids generic AI dashboard aesthetics.
- It uses desktop width properly without becoming visually crowded.
- The most important numbers are easier to scan than before.
- Green and gold accents are used intentionally and sparingly.
- Cards and panels are visually distinct by purpose.
- Mobile preserves the analysis workflow instead of merely shrinking desktop.
- Caveats remain visible near the data they affect.
- The implementation uses shared tokens and reusable patterns instead of
  page-by-page styling drift.

## UPL Lens Public Launch Acceptance Checklist

Use this checklist to confirm a release build is ready for the UPL Lens public
launch. Every item marked as required must be satisfied or carry an explicit
acceptance note in the release PR.

- Theme and tokens:
  - Editorial Light is implemented as the default theme and matches the
    `Light Mode Tokens (default)` in this file.
  - Dark mode is not required for launch; if present it must be behind an
    explicit toggle and documented as an optional variant.
- Branding and lockup:
  - Stacked "UPL / Lens" brand lockup is present on the site header or shell
    as specified in the high-fidelity brief.
  - No legacy long-form or unofficial logos are used on public pages.
- Navigation and support:
  - Desktop: fixed left sidebar present and functioning.
  - Mobile: bottom navigation implemented for primary sections.
  - The sidebar shows only one visible support link: "About". Methodology,
    data notes, and contact information are accessible from the About page,
    not as a separate top-level navigation item.
  - Social links grouped in a single bottom row of the sidebar or footer.
- Asset and data rules:
  - No official club logos are embedded; use team-initial badges with stable
    seeded palettes.
  - No export button on public pages by default.
  - No UI element invents or displays fake data (crests, scores, etc.).
- Accessibility and states:
  - Loading, empty, and error states match the UX state principles in this
    document.
  - Mobile-first layouts validated at typical narrow widths.

Document any approved exceptions in the release PR and link the approving
note or ticket.

### League Overview Mockup Checklist

Use this checklist when reviewing League Overview work against the approved
mockup direction. The goal is close product feel, not pixel-perfect copying.

- Desktop first viewport shows the compact page header, KPI row, and the start
  of Goal Timing, Top 5 Teams, and Recent Matches without requiring a long
  scroll.
- The page reads as a football intelligence workspace: dense, practical,
  sports-native, and fan-facing, not a generic dashboard or marketing page.
- The hero/header is compact and supports the dashboard instead of becoming the
  main content.
- The overview photograph should live behind the header and summary cards as a
  softened page-level layer. Cards remain readable and should not become glassy.
- KPI cards feel like a scoreboard summary: short labels, dominant numbers,
  one-line context, and restrained visual treatment.
- Goal Timing on the overview is a compact visual preview, not the full explorer
  detail view.
- Top 5 Teams and Recent Matches are visible near Goal Timing on desktop and
  feel like quick football modules rather than database tables.
- The insight strip is compact enough to behave like a dashboard footer, with
  short routes into deeper analysis.
- Mobile review uses a common narrow width and confirms the order is header,
  KPIs, Goal Timing, teams/results, then insights, with no horizontal overflow.
- Loading, empty, and error states preserve the same layout contracts so the
  overview does not jump into a different composition.
- No panel introduces fake scores, fake crests, unsupported claims, or data not
  returned by the FastAPI JSON contract.
- Caveats remain visible where they affect interpretation, but do not dominate
  the first viewport.
- Green and gold accents remain purposeful: action/selection/positive emphasis
  for green, peak timing or attention moments for gold.

## Update Rules

Only add guidance here when one of these is true:

- a request in [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md) was approved
  and implemented
- the user explicitly approved a frontend behavior or design decision
- an existing implementation was accepted as the durable standard

Keep brainstorm notes and unapproved requests out of this file. Those belong in
[FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md).
