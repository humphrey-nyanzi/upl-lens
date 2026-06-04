# UPL Lens — Frontend Start Here

This file is the frontend redesign entry point for the public product now
called **UPL Lens**. It collects the new frontend documents, visual assets,
and the source-of-truth precedence order for design and implementation.

If you are working on the public UI or implementing frontend changes, read
this file first and follow the precedence order below.

## New UPL Lens frontend docs (added to `docs/`)

- [UPL_LENS_HIGH_FIDELITY_DESIGN_BRIEF.md](UPL_LENS_HIGH_FIDELITY_DESIGN_BRIEF.md) — Primary visual and editorial brief.
- [UPL_LENS_TEXT_WIREFRAMES.md](UPL_LENS_TEXT_WIREFRAMES.md) — Canonical text wireframes for pages.
- [UPL_LENS_PAGE_REQUIREMENTS.md](UPL_LENS_PAGE_REQUIREMENTS.md) — Page-by-page functional requirements.
- [UPL_LENS_INFORMATION_ARCHITECTURE.md](UPL_LENS_INFORMATION_ARCHITECTURE.md) — Navigation and content model.
- [visual_inspo.png](visual_inspo.png) — Approved visual inspiration for the redesign.

## Source-of-truth precedence (use this exact order when conflicts appear)

1. High Fidelity Design Brief
2. Text Wireframes
3. Page Requirements
4. Information Architecture
5. Frontend Design System
6. Frontend UX Requests
7. Older roadmap/history docs (PROJECT_ROADMAP.md, CHANGELOG.md, etc.)

When the High Fidelity Design Brief and Text Wireframes disagree, prefer the
High Fidelity Design Brief and seek clarification from the product/design
owner. The Frontend Design System contains durable implementation tokens and
components; it yields to the prioritized design artifacts above when those
artifacts carry an explicit exception or layout requirement.

## Quick working rules

- The public product name is **UPL Lens**. Use this name in public-facing
  documentation, site titles, and social links.
- The frontend should not read CSVs, notebooks, or exported notebook charts.
- Treat the official UPL site as the source record and UPL Lens as the
  intelligence layer. Do not clone official match pages, raw timelines,
  lineups, or officials lists unless the UI transforms them into analytical
  meaning.
- All durable visual decisions for the launch are listed in
  [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md) under "UPL Lens high-fidelity design
  decisions".
- If a frontend request needs backend data, add it to [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md)
  with `Data/API needs` filled and await approval.
 
Explicit launch defaults and source-of-truth rules:

- High Fidelity Design Brief is the top source of truth for visual and layout
  decisions. When in doubt prefer the High Fidelity Design Brief.
- Editorial Light is the default theme for UPL Lens (the light token set in
  [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md) is the launch baseline).
- Dark mode is an optional future variant. If implemented, it must be behind
  an explicit toggle and documented as an approved variant.
- The sidebar's only visible support link must be "About". Methodology,
  data notes, and contact information live inside the About page (link from
  About) rather than as separate top-level sidebar items.

## Files to read next (recommended order)

1. [UPL_LENS_HIGH_FIDELITY_DESIGN_BRIEF.md](UPL_LENS_HIGH_FIDELITY_DESIGN_BRIEF.md)
2. [UPL_LENS_TEXT_WIREFRAMES.md](UPL_LENS_TEXT_WIREFRAMES.md)
3. [UPL_LENS_PAGE_REQUIREMENTS.md](UPL_LENS_PAGE_REQUIREMENTS.md)
4. [UPL_LENS_INFORMATION_ARCHITECTURE.md](UPL_LENS_INFORMATION_ARCHITECTURE.md)
5. [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md) for durable tokens and components

## Where to record changes

- Minor UI requests: [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md) (mark status `idea` /
  `draft` / `needs_review` / `approved` accordingly).
- Durable design token or component changes: [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md).
- Product-level strategy or naming changes: [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md).

## Notes on historical docs

Do not delete historical documentation. Older documents remain valuable for
data, research, and operations context. When implementing the UPL Lens
frontend, prefer the new UPL Lens artifacts and move any implemented rules
into the design system.

---

If anything in these files is unclear, ask the product/design owner for a
clarifying acceptance note before implementing large frontend changes.
