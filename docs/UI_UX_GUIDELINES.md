# UI/UX Guidelines

This is the approved UI and UX reference for UPL Match Intelligence.

Use [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md) for proposed changes,
drafts, and implementation requests. Use this file only for decisions that have
been approved or already implemented.

## Purpose

The frontend should feel like a practical football intelligence workspace.

For the broader product identity, audience, positioning, and "what this app is
and is not" rules, use [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md). This UI
guide records approved interface decisions; the product strategy explains the
kind of public product those decisions should serve.

It should help users:

- scan a league season quickly
- compare teams and match patterns
- inspect match records and event signals
- understand validated football insights
- see caveats when source data is incomplete

It should not feel like:

- a marketing landing page
- a generic admin template
- a raw mirror of the official UPL website
- a notebook export pasted into a browser

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

If the UI needs new data, add or extend the API/query layer instead of bypassing
FastAPI.

## Current Approved Product Surfaces

These surfaces are currently approved as part of the public product direction:

- League Overview
- Goal Timing Explorer
- Match Explorer
- Team Insights / Team Profile
- Discipline Dashboard
- Methodology / Data Notes

The current deployed app is still a pilot. It proves the architecture, but the
approved long-term direction is a richer analytical product with multiple
usable sections.

## Current Visual Baseline

The current frontend uses:

- a sticky top navigation bar
- compact mobile menu behavior for primary navigation
- a light analytical workspace
- compact cards and panels
- tables for team and match summaries
- horizontal bars for goal timing
- green/yellow accents

These choices are acceptable as a starting baseline, but they are not a final
brand system. Future approved changes should be recorded in the sections below.

## Layout Principles

Approved principles:

- Design product-facing screens mobile first, then enhance for tablet and
  desktop.
- Use dense but readable layouts.
- Prioritize scanning, comparison, and repeated use.
- Keep controls close to the data they affect.
- Use tables for structured match/team data.
- Use charts only when they make a pattern easier to understand.
- Keep the first screen useful, not promotional.
- Avoid decorative sections that do not help analysis.

## Navigation Principles

Approved principles:

- The app should have clear sections for major workflows.
- Primary navigation should behave like page navigation, not like cramped
  same-page anchor jumping, once a section represents a real product area.
- Lightweight hash-based navigation is acceptable while the product has only a
  few top-level pages.
- Navigation labels should use product language, not database language.
- Disabled or future sections should not look like finished features.
- Users should be able to move from league summary to more detailed match or
  team views as the app matures.
- Phone layouts should use a compact menu button for primary navigation instead
  of horizontally scrolling navigation links.
- Navigation must expose the current page clearly.

## Data Display Principles

Approved principles:

- Use readable football labels instead of raw database column names.
- Map visible frontend data needs before adding new API endpoints.
- Show season context clearly.
- Show loading, empty, and error states.
- Do not hide source-data limitations.
- Do not calculate durable league-wide metrics in React if they belong in
  Postgres/FastAPI.
- Keep backend route functions thin and query logic in `src/api/`.

## UX State Principles

Approved principles:

- Use skeleton loading states during the first meaningful wait before showing
  confirmed error states.
- Skeletons should match the shape of the incoming content and avoid layout
  jumps on mobile.
- Loading states should make free-tier backend cold starts understandable.
- API offline states should identify the API host when useful.
- Browser-extension blocking should be mentioned only when relevant to the
  deployed app error.
- Empty states should explain what is missing without blaming the user.
- Validation or data caveats should be visible when they affect interpretation.

## Accessibility Principles

Approved principles:

- Use semantic HTML where practical.
- Keep interactive controls keyboard-accessible.
- Preserve readable contrast.
- Do not rely on color alone to communicate status.
- Use clear labels for filters and controls.

## Iconography

Approved decisions:

```text
none yet
```

Future decisions should specify:

- icon library, if any
- where icons are required
- where text labels should remain visible
- how status icons differ from navigation icons

## Color

Approved decisions:

```text
none beyond current baseline
```

Future decisions should specify:

- primary background colors
- sidebar/navigation colors
- accent colors
- success/warning/error colors
- chart palette rules
- accessibility/contrast notes

## Typography

Approved decisions:

```text
none beyond current baseline
```

Future decisions should specify:

- font family
- heading scale
- table and compact-panel text sizing
- numeric/stat display rules

## Components

Approved reusable component directions:

- Cards, panels, chart containers, metric blocks, buttons, filter controls, and
  empty states should use a small radius, currently 5-6px, to feel modern
  without becoming playful.
- Metric cards should combine a clear label, strong numeric value, and one
  short football-readable explanation.
- Filter groups should be moderate and page-specific; do not expose every
  possible database filter by default.
- Match rows should remain compact cards that surface date, teams, score, and
  result state before deeper detail.
- Team summary cards should show analytical signals such as win rate, ranking,
  record, goal difference, and goals for/against where available.
- Empty states should explain what is missing calmly and briefly.

## Chart And Table Guidelines

Approved principles:

- Charts should answer a football question, not merely decorate the page.
- Tables should support comparison and scanning.
- Chart labels should be understandable without reading code.
- Caveats should be near the chart/table they affect.
- Explorer pages should favor filters, compact cards, summaries, and drilldown
  paths over raw database-style tables.
- Top-level pages should use visual summaries before full tables when the data
  can still be understood clearly.

## Mobile Guidelines

Approved principles:

- Mobile layouts should preserve the core workflow.
- The phone viewport is the starting point for new product-facing frontend
  slices.
- The product header, season controls, status messages, summary cards, charts,
  and caveats should stack cleanly before desktop layout enhancements are added.
- Tables may scroll horizontally if the data is genuinely tabular.
- Critical controls should remain reachable without excessive scrolling.
- Text should wrap cleanly and not overlap controls or chart labels.
- Same-page anchors, where they still exist, should account for sticky header
  height with scroll-margin or equivalent behavior.

## League Intelligence Overview

Approved decisions:

- The first screen should present UPL Match Intelligence as a football data
  observatory, not as a generic dashboard or fixtures site.
- The front page should sit between dashboard summary, sports analytics control
  room, and league report card.
- The overview should lead with product positioning, season/data status,
  analytical summary cards, and the current featured insight.
- Goal Timing is the current flagship insight preview on the overview.
- Explore The Numbers previews may show planned product areas, but should not
  imply unfinished tools are already complete.
- Trust, source, freshness, and caveat information should be visible on the
  overview instead of hidden in developer-only notes.
- Overview copy should be fan-facing and avoid internal implementation language
  such as "endpoint", "product slice", and "supporting evidence".
- The overview may keep a small data-note link, but detailed source, freshness,
  update, and technical trust context belongs on the Data Notes page.

## Goal Timing

Approved decisions:

- Goal Timing is the first dedicated deep insight page.
- Featured insight pages should use a reusable structure: question, headline
  finding, useful chart, short explanation, data note, and drilldown where the
  data supports it.
- The page should lead with the football question and main finding before long
  explanation.
- The 15-minute period chart should be backed by readable text values.
- The peak scoring window should be labelled in text, not communicated through
  color alone.
- Added-time exclusions and event-timeline caveats should stay close to the
  chart.

## Methodology And Data Notes

Approved decisions:

- Technical trust details belong on a dedicated Data Notes page rather than
  crowding the main overview.
- Data Notes should explain source, data path, freshness, known limitations,
  and caveats in plain language.
- The Data Notes page should support credibility without becoming a developer
  portfolio landing page.

## Page Templates

Approved decisions:

- League overview pages should entice users into deeper product areas without
  becoming one long page.
- Featured insight pages should explain researched features without becoming
  long article pages inside React.
- Explorer pages should use moderate filters, result summaries, compact cards,
  and drilldown paths.
- Team pages should be analytical summaries, not basic profiles.
- Methodology/Data Notes pages should collect source, freshness, limitations,
  update context, and contact/about context in plain language.

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

These are guardrails, not a ban on visual experimentation.

## How To Update This File

Only add a guideline here when one of these is true:

- a request in [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md) was approved
  and implemented
- the user explicitly approves a design or UX decision
- an existing implemented behavior is accepted as the durable standard

When updating this file, keep it factual. Do not add brainstorm notes here.
