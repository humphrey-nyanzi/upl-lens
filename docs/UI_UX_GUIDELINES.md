# UI/UX Guidelines

This is the approved UI and UX reference for UPL Match Intelligence.

Use [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md) for proposed changes,
drafts, and implementation requests. Use this file only for decisions that have
been approved or already implemented.

## Purpose

The frontend should feel like a practical football intelligence workspace.

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
- Team Profile
- Discipline Dashboard

The current deployed app is still a pilot. It proves the architecture, but the
approved long-term direction is a richer analytical product with multiple
usable sections.

## Current Visual Baseline

The current frontend uses:

- a dark left sidebar
- a light analytical workspace
- compact cards and panels
- tables for team and match summaries
- horizontal bars for goal timing
- green/yellow accents

These choices are acceptable as a starting baseline, but they are not a final
brand system. Future approved changes should be recorded in the sections below.

## Layout Principles

Approved principles:

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
- Navigation labels should use product language, not database language.
- Disabled or future sections should not look like finished features.
- Users should be able to move from league summary to more detailed match or
  team views as the app matures.

## Data Display Principles

Approved principles:

- Use readable football labels instead of raw database column names.
- Show season context clearly.
- Show loading, empty, and error states.
- Do not hide source-data limitations.
- Do not calculate durable league-wide metrics in React if they belong in
  Postgres/FastAPI.
- Keep backend route functions thin and query logic in `src/api/`.

## UX State Principles

Approved principles:

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

```text
none yet
```

Future decisions should specify reusable patterns for:

- metric cards
- filters
- status banners
- tables
- match rows
- chart panels
- empty states

## Chart And Table Guidelines

Approved principles:

- Charts should answer a football question, not merely decorate the page.
- Tables should support comparison and scanning.
- Chart labels should be understandable without reading code.
- Caveats should be near the chart/table they affect.

## Mobile Guidelines

Approved principles:

- Mobile layouts should preserve the core workflow.
- Tables may scroll horizontally if the data is genuinely tabular.
- Critical controls should remain reachable without excessive scrolling.
- Text should wrap cleanly and not overlap controls or chart labels.

## How To Update This File

Only add a guideline here when one of these is true:

- a request in [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md) was approved
  and implemented
- the user explicitly approves a design or UX decision
- an existing implemented behavior is accepted as the durable standard

When updating this file, keep it factual. Do not add brainstorm notes here.

