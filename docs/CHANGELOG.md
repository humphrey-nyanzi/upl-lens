# Changelog

This changelog records high-signal repo changes for the UPL Lens repo and its
UPL Match Intelligence history.

It is intentionally concise. Use it to understand what changed recently before
you start editing code or docs.

## 2026-06-06

### Intelligence-layer docs sync

- Added a frontend-facing API contract at `docs/API_CONTRACT.md` and linked it
  from the main docs entrypoints.
- Documented the new backend intelligence-layer page roles, endpoint mapping,
  and page-by-page upgrade order.
- Added the frontend UX request group for API client sync, reusable intelligence
  components, and page upgrades.

### Docs naming and launch-precedence sync

- Clarified the repository devex and workflow docs so they speak to UPL Lens as
  the public product while keeping UPL Match Intelligence as repo history.
- Reinforced the UPL Lens frontend launch precedence in the Copilot
  instructions for public UI work.
- Added an AGENTS rule that requires frontend work to consult the
  `frontend-app-builder`, `impeccable`, and `tufte-viz` skills.

## 2026-06-05

### Roadmap naming sync

- Updated the roadmap and diagram collection public-product language so Product
  Experience planning points at UPL Lens while preserving UPL Match Intelligence
  as the broader repo, data-platform, research, API, and historical context.

## 2026-05-31

### UPL Lens frontend doc package

- Added the UPL Lens frontend launch docs:
  `UPL_LENS_FRONTEND_START_HERE.md`,
  `UPL_LENS_HIGH_FIDELITY_DESIGN_BRIEF.md`,
  `UPL_LENS_TEXT_WIREFRAMES.md`,
  `UPL_LENS_PAGE_REQUIREMENTS.md`, and
  `UPL_LENS_INFORMATION_ARCHITECTURE.md`.
- Added `visual_inspo.png` as the approved visual-reference asset for the
  frontend redesign.
- Updated the central project docs so the new UPL Lens files are discoverable,
  linked, and treated as a temporary exception to the earlier 10-doc cap.

## 2026-05-26

### Documentation consolidation

- Reduced `docs/` to a 10-file structure: 9 core docs plus this changelog.
- Merged navigation guidance into [START_HERE.md](START_HERE.md).
- Merged research backlog, feature lifecycle, notebook data-access rules, and
  analytics-promotion rules into
  [FEATURE_PROMOTION_WORKFLOW.md](FEATURE_PROMOTION_WORKFLOW.md).
- Merged durable UI and UX rules into
  [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md).
- Merged automation and deployment runbooks into
  [OPERATIONS.md](OPERATIONS.md).
- Removed retired docs that were creating overlapping sources of truth.

### Documentation standards

- Reset [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md) to a planning-only
  state with no active approved implementation requests.
- Re-linked the surviving docs so each work area has one obvious source of
  truth.

## 2026-05-25

### Documentation sync after refactor work

- Updated onboarding and planning docs to reflect the modular scraper,
  `src/db/staging/`, and `src/api/query_services/`.
- Replaced stale top-navigation references with the current `AppShell`
  structure.
- Updated frontend docs to point at the modular page, component, hook, and
  utility structure.

## 2026-05-24

### Frontend redesign foundation

- Added the `AppShell`-based frontend workspace with desktop sidebar, top
  control bar, and mobile-aware navigation.
- Introduced the first-pass frontend design system and reusable surface
  primitives.
- Implemented the first mockup-aligned redesign pass for the League Overview
  and supporting product pages.
- Added visual acceptance criteria and a stronger mobile-first frontend
  standard.

## 2026-05-23

### Data-trust and feature-promotion groundwork

- Added source-anomaly safeguards so raw evidence can be preserved while public
  app aggregates stay protected.
- Continued formalizing the research-to-product workflow for notebook-backed
  features.

## How To Use This File

- Read this before a large edit if you need recent context quickly.
- Add a dated entry when a meaningful repo change ships.
- Keep entries short and outcome-focused.
- Put the current behavior details in the owning doc, not here.
