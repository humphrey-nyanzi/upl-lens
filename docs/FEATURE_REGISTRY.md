# Feature Registry

This registry is the project map for notebook-backed product features.

Use it to answer four practical questions:

- What feature ideas exist?
- Which ones are still research-only?
- Which ones have been promoted into the app?
- Where should a human or AI agent go to modify each feature?

The registry should stay small and factual. Detailed football thinking belongs
in each feature's `research_brief.md`; detailed implementation requests belong
in each feature's `product_plan.md`.

Rough ideas that are not feature packages yet belong in
[RESEARCH_IDEAS.md](RESEARCH_IDEAS.md).

## Lifecycle Statuses

Use these statuses for feature folders and registry rows.

| Status | Meaning | What Usually Happens Next |
|--------|---------|---------------------------|
| `idea` | The question exists, but analysis has not started. | Create or copy a feature package. |
| `researching` | The notebook is actively exploring the question. | Keep experimenting in `analysis.ipynb`. |
| `validated` | The notebook has a useful finding, metric, or chart. | Write the finding and caveats in `research_brief.md`. |
| `promotion_ready` | The feature has a clear product plan and is ready for implementation. | Ask an AI agent or engineer to promote it. |
| `promoted` | The feature is available through FastAPI and React. | Track follow-up edits in `product_plan.md`. |
| `needs_revision` | The feature exists, but the logic, data, UI, or caveats need review. | Add change requests before more promotion work. |
| `deprecated` | The feature should no longer be used as a current product feature. | Keep history, but avoid new UI/API work unless revived. |

## Registry Maintenance Rules

- Add a row when a feature package is created.
- Update the status when the feature moves from research to promotion.
- Link to the feature folder, not to every individual file.
- Keep endpoint and analytics-object names current after promotion.
- If a feature is still notebook-only, write `none yet` for API and UI fields.
- If a promoted feature is implemented with a direct query instead of an
  `analytics.*` view, say that explicitly.

## Features

| Feature | Status | Feature Package | Research Source | Production Source | API Endpoint | Frontend Surface | Notes |
|---------|--------|-----------------|-----------------|-------------------|--------------|------------------|-------|
| Feature 1 - Goal Timing | `promoted` | `notebooks/features/feature_01_goal_timing/` | `staging.events` via notebook and API query | Direct query on `staging.events`; no `analytics.*` view yet | `GET /insights/goal-timing?season=...` | Goal Timing Explorer panel | First Phase 6 vertical slice. Counts regular-time goal events by 15-minute interval and excludes added-time goals. |
| Feature XX - Template | `idea` | `notebooks/features/_feature_template/` | `staging.*` by default | choose during promotion | none yet | none yet | Copy this folder to start a new experimental feature. |

## How To Use This Registry

When starting a feature:

1. Start from a `selected` idea in `docs/RESEARCH_IDEAS.md`.
2. Copy `notebooks/features/_feature_template/`.
3. Add a registry row with status `researching`.
4. Work in the notebook.

When the notebook has a useful result:

1. Update the status to `validated`.
2. Fill in `research_brief.md`.
3. Fill in the Promotion Plan section of `product_plan.md`.

When the feature is ready for production:

1. Update the status to `promotion_ready`.
2. Ask an AI agent to promote the feature.
3. After implementation, update the row to `promoted`.

When changing a promoted feature:

1. Add the change request to that feature's `product_plan.md`.
2. Keep the registry row stable unless the source, endpoint, UI surface, or
   status changes.
