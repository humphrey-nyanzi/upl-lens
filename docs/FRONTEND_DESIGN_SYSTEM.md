# Frontend Design System

This document translates the approved mockup direction into an implementation
reference for UPL Match Intelligence.

It is not a pixel-copy instruction. It defines the product visual system,
component intent, data-display rules, and rollout checklist for future frontend
work.

Use this with:

- [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md)
- [UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md)
- [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md)

## Product Visual Identity

UPL Match Intelligence should feel like a modern football intelligence operating
system.

The closest product model is:

```text
league dashboard + sports analytics control room + football report card
```

The app should feel:

- data-rich
- powerful
- modern
- practical
- mobile-first
- fan-facing
- credible for analysts

It should not feel:

- like a generic AI SaaS dashboard
- like a betting product
- like Power BI or Tableau
- like a raw database admin panel
- like a notebook export
- like a developer portfolio landing page
- like a decorative marketing site

## Mockup Interpretation

The approved mockup shows a dashboard system with:

- a dark-first desktop app shell
- a left sidebar for primary navigation
- a top control/search/filter bar
- season and competition controls near the page title
- KPI cards for fast season scanning
- a central goal timing heatmap
- top-five rankings
- recent results
- contextual insight cards
- mobile views that preserve the same analytical hierarchy
- light-mode equivalents using the same structure
- side panels that explain principles, palette, and feature highlights

Copy conceptually:

- the operational sports analytics feel
- compact density without raw-table clutter
- green and gold football-native accents
- goal timing as a flagship heatmap-style insight
- top-five previews before full tables
- visible data status
- desktop sidebar plus mobile navigation adaptation
- numbers with interpretation, not numbers alone

Do not copy literally:

- the exact fake team names, values, or logos
- every navigation item before the app has those product areas
- decorative side panels inside the real product
- the exact phone mockup framing
- any AI-concept artifacts that do not map to real data
- dense layouts that would break mobile readability

## Alignment With Existing Direction

Strong alignment:

- The product is already defined as a football intelligence platform.
- The docs already reject raw official-site duplication.
- The app already uses FastAPI JSON instead of CSVs.
- Goal Timing is already the flagship promoted insight.
- Existing docs already prefer top-five previews, fan-facing language, caveats,
  and mobile-first layouts.

Partial alignment:

- Current React pages are modular, but the shell is still a top-nav light
  workspace rather than a mature sports intelligence app shell.
- Current cards and panels are clean, but not yet a full reusable design system.
- Current charts are readable, but Goal Timing is still bar-based rather than a
  richer heatmap treatment.
- Team and match views exist, but they are still early analytical summaries.

Divergence:

- The mockup uses a desktop sidebar; the current app uses sticky top navigation.
- The mockup is dark-first; the current app is light-first with dark feature
  panels.
- The mockup includes search, export, players, statistics, standings, compare,
  and news areas that are not all current product surfaces.
- The mockup presents richer visual hierarchy than the current CSS token set.

Main risk:

The mockup is visually attractive enough that future agents may overbuild the
surface before the API, research, and data caveats support it. The correct path
is to build tokens and reusable components first, then apply them page by page.

## Color Tokens

Use semantic tokens before hardcoding page colors.

Suggested dark-first palette:

| Token | Purpose | Suggested value |
|-------|---------|-----------------|
| `--color-bg-app` | app background | `#071118` |
| `--color-bg-shell` | sidebar/topbar surface | `#0b1720` |
| `--color-bg-panel` | primary card/panel | `#101f2a` |
| `--color-bg-panel-soft` | secondary panel | `#162533` |
| `--color-border-subtle` | default border | `#243544` |
| `--color-text-primary` | primary text | `#f3f7f2` |
| `--color-text-secondary` | secondary text | `#a9b6bf` |
| `--color-text-muted` | quiet labels | `#7f8d99` |
| `--color-accent-green` | primary action/selected | `#16a34a` |
| `--color-accent-lime` | active data highlight | `#a3e635` |
| `--color-accent-gold` | peak/caution/key insight | `#f5b82e` |
| `--color-risk` | errors/negative/discipline risk | `#ef4444` |
| `--color-success` | healthy status | `#22c55e` |

Suggested light equivalent:

| Token | Purpose | Suggested value |
|-------|---------|-----------------|
| `--color-bg-app-light` | app background | `#f5f7f1` |
| `--color-bg-panel-light` | card/panel | `#ffffff` |
| `--color-bg-panel-soft-light` | secondary surface | `#eef3ea` |
| `--color-border-light` | default border | `#d9dfd2` |
| `--color-text-primary-light` | primary text | `#17211b` |
| `--color-text-secondary-light` | secondary text | `#59665b` |

Rules:

- Green is the main football/action accent.
- Lime is for active data highlights and selected chart cells.
- Gold is for peak zones, key insights, cautions, or attention moments.
- Red is only for error, risk, discipline, or negative state.
- Purple should not become a dominant brand color.
- Avoid generic purple/cyan gradients.

## Typography And Numbers

Use compact, readable typography.

Principles:

- Headline metrics should be visually dominant.
- Labels should use football language, not database column names.
- Every major number needs context: comparison, interpretation, rank, trend, or
  caveat.
- Short uppercase labels are acceptable for compact dashboard metadata.
- Avoid long article paragraphs inside dense product panels.
- Use tables only when comparison needs the table.

Number pattern:

```text
Label
Primary number
Context line
Optional trend/rank/caveat
```

Examples:

- `Goals scored`, `256`, `2.0 per match`
- `Peak scoring window`, `61-75`, `Highest regular-time goal share`
- `Top attack`, `28`, `Vipers SC goals scored`

## Spacing And Layout

Desktop layout direction:

- left sidebar
- top control/search/filter bar
- main analytical workspace
- reusable card and panel grid
- high-priority metrics above deeper evidence
- controls close to the data they affect

Mobile layout direction:

- top app bar
- menu or bottom navigation for primary product areas
- season/status controls near the first meaningful content
- one-column panels
- top-five previews instead of wide tables where possible
- horizontal scroll only when the data is genuinely tabular

Recommended spacing tokens:

| Token | Purpose | Suggested value |
|-------|---------|-----------------|
| `--space-1` | tight inline gap | `4px` |
| `--space-2` | small gap | `8px` |
| `--space-3` | card internal gap | `12px` |
| `--space-4` | panel padding mobile | `16px` |
| `--space-5` | panel padding desktop | `20px` |
| `--space-6` | section gap | `24px` |

Radius:

- Controls: `5px`
- Cards and panels: `6px`
- Large shell surfaces: `8px` maximum unless a component needs otherwise

## Surface Hierarchy

Use surfaces intentionally:

1. App shell
   - Sidebar, mobile top bar, top controls.
   - Dark, stable, navigation-focused.

2. Workspace background
   - Deep app background in dark mode.
   - Light neutral background in light mode.

3. Primary panels
   - KPI groups, chart panels, rankings, recent results.
   - Solid enough for readability.

4. Secondary panels
   - data notes, supporting explanations, caveats.
   - Quieter contrast.

5. Attention panels
   - flagship insight, peak zone, major finding.
   - Use green/gold sparingly.

Avoid putting cards inside decorative cards. Use nested structure only when it
helps scanning and remains visually quiet.

## Component Variants

### App Shell

Purpose: hold the product structure.

Treatment:

- desktop sidebar with brand, navigation, data status, and profile/contact area
- top bar with season, competition, search/filter, and export/report actions
- mobile top bar with compact menu or bottom navigation

Responsive behavior:

- desktop: sidebar remains visible
- tablet: sidebar may collapse to icons or compact rail
- mobile: top bar plus bottom navigation or menu

Do not use for:

- marketing hero layouts
- long methodology content

### Sidebar Navigation

Purpose: move between product areas.

Treatment:

- dark surface
- clear active state using green
- icons plus text on desktop where practical
- disabled/future sections should be visibly unfinished, not fake-active

Hover/focus:

- visible border or background change
- keyboard focus ring must be clear

### Top Bar And Controls

Purpose: hold season, competition, search, filters, status, and report actions.

Treatment:

- compact, solid, slightly elevated
- subtle glass-like treatment allowed only here
- controls should remain close to affected data

Do not use:

- global filters that silently change unrelated pages without clear context

### KPI Cards

Purpose: provide fast season scanning.

Treatment:

- strong number
- short label
- one context line
- optional trend/rank/caveat
- icon optional but not required

Responsive behavior:

- mobile: two-column only if values remain readable; otherwise one column
- desktop: compact grid

### Insight Cards

Purpose: explain what a number means.

Treatment:

- football question
- main finding
- chart or compact evidence
- caveat near the evidence
- action to explore deeper

Do not use:

- vague promotional copy
- unvalidated findings

### Ranking And Top-Five Cards

Purpose: replace boring tables when the user only needs the leaders.

Treatment:

- rank number
- team/player/official name
- value
- optional trend or context
- action to open full table only when useful

Mobile:

- preferred over wide tables
- keep row labels short

### Recent Results Cards

Purpose: show match context without becoming a fixtures clone.

Treatment:

- teams
- scoreline/result state
- date or matchday
- optional venue/status

Do not use:

- as the main product identity

### Chart Panels

Purpose: answer a football question.

Treatment:

- clear title written as a question or useful claim
- chart with readable labels
- legend close to chart
- caveat close to chart
- table/text fallback when needed

### Heatmap Panels

Purpose: show distribution over time, especially Goal Timing.

Treatment:

- green-to-gold intensity scale
- labeled period rows/columns
- peak zones clearly labelled in text
- accessible fallback list of values

Do not use:

- decorative heatmaps without an interpretable football question

### Mobile Bottom Navigation

Purpose: keep core product areas reachable on phones.

Treatment:

- 4 to 5 primary items maximum
- icons plus short labels
- clear selected state

Do not use:

- every desktop navigation item
- future sections that are not usable

### Empty, Loading, Error, And Data Status States

Purpose: preserve trust during cold starts, missing data, or source issues.

Treatment:

- skeletons before confirmed errors
- calm empty-state copy
- API/data status visible but not alarming
- source limitations visible where they affect interpretation

## Chart And Table Guidance

Charts should answer football questions, not decorate the page.

Use:

- heatmaps for timing/distribution patterns
- top-five lists for leaders and rankings
- bars for simple comparisons
- compact tables for structured comparison
- text summaries for caveats and interpretation

Avoid:

- charts without labels
- charts whose meaning depends on color alone
- raw database tables as a default view
- notebook screenshots
- over-animated dashboards

## Mobile Adaptation Rules

Mobile is not a squeezed desktop.

Rules:

- preserve the core analytics workflow
- show the most important number first
- use top-five previews before full tables
- keep filters local to the affected section
- let charts simplify if labels become unreadable
- keep caveats near the data they affect
- keep tap targets at least 44px high where practical
- avoid horizontal scrolling except for genuine comparison tables

## Motion And Interaction

Motion should be minimal and functional.

Allowed:

- quick hover/focus transitions
- skeleton shimmer, disabled for reduced motion
- menu open/close transitions
- chart hover states if they remain accessible

Avoid:

- excessive animation
- parallax
- decorative pulsing
- motion that makes analytical content harder to read

## Accessibility Requirements

Minimum requirements:

- semantic HTML for navigation, sections, buttons, lists, and tables
- keyboard-accessible controls
- visible focus states
- readable contrast in dark and light modes
- do not rely on color alone for status or peak values
- labels for filters and chart legends
- reduced-motion support
- text must wrap without overlap on mobile

## Anti-Patterns

Avoid:

- generic AI SaaS dashboard look
- purple gradient glassmorphism
- betting-site aesthetics
- Power BI or Tableau clone
- developer portfolio landing page
- raw database admin panel
- notebook-export interface
- overcrowded cards
- overly empty decorative sections
- excessive animation
- visual effects that reduce trust or readability

## Surface Adoption Map

League Overview:

- adopt the app shell, KPI system, goal timing preview, top teams, recent
  results, and data status first

Goal Timing Explorer:

- become the flagship heatmap-style insight page with question, finding,
  heatmap, values, caveats, and drilldown

Match Explorer:

- use filters, compact match cards, result summaries, and future match detail
  links

Team Insights / Team Profile:

- use top-five rankings, team cards, compact trend summaries, and later team
  detail pages

Discipline Dashboard:

- wait for a promoted research feature before final UI; the visual system may
  define the placeholder and future card/chart style

Methodology / Data Notes:

- use calmer secondary surfaces, clear source/freshness indicators, and visible
  limitations without turning into a technical landing page

## Implementation Checklist

Before redesigning a page:

- confirm the request is approved in `FRONTEND_UX_REQUESTS.md`
- map visible data needs to existing FastAPI endpoints
- propose backend/API changes separately if data is missing
- define the mobile version first
- use design tokens instead of page-specific hardcoded colors where practical
- use reusable cards/panels before one-off page CSS
- keep caveats near affected data
- run `npm run build`
- run a rendered browser check on mobile and desktop when code changes

Recommended rollout:

1. Design tokens and shell/component foundations.
2. App shell redesign.
3. League Overview.
4. Goal Timing Explorer.
5. Team Insights.
6. Match Explorer.
7. Discipline Dashboard after research promotion.
