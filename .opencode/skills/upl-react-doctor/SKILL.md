---
name: upl-react-doctor
description: Run and act on React Doctor diagnostics for the UPL Lens frontend in this repository's frontend/ directory. Use only when a current GitHub Issue explicitly scopes retained frontend work, or when asked to run react-doctor, improve a React Doctor score, fix React Doctor findings, reevaluate older frontend React patterns, or make frontend changes that should preserve a 100/100 React Doctor score.
---

# UPL React Doctor

The React frontend is a retained, frozen asset. Use this skill only when a
current GitHub Issue explicitly scopes frontend work. Keep the work scoped to
`frontend/` unless the user explicitly asks for broader repo changes.

## Workflow

1. Read repo guidance first when starting a non-trivial pass: `AGENTS.md`, `docs/START_HERE.md`, `docs/PRODUCT_STRATEGY.md`, `docs/PROJECT_ROADMAP.md`, and frontend docs that still exist in the current worktree.
2. Check `git status --short` before editing. Treat non-frontend docs/data changes as user-owned unless they are directly required for the request.
3. Run React Doctor from `frontend/`:

```powershell
npx react-doctor@latest --verbose --diff
```

If the package is not cached and network is blocked, rerun with approval. Do not guess findings from memory.

4. Treat diagnostics as hypotheses. Read each cited file before editing. Prefer confirmed, behavior-preserving fixes.
5. Fix in small batches, then run:

```powershell
npm run build
npx react-doctor@latest --verbose --diff
```

6. Continue until React Doctor reports `No issues found!` and `100 / 100`. A partial score is not done if the user asked for 100.

## Fix Patterns That Worked Here

- Replace effect-driven prop/state sync with request-keyed state or derived render state. Avoid showing stale data for one render just to set `loading` in an effect.
- Combine related page filter state with `useReducer` when React Doctor flags many related `useState` calls.
- Move event effects back into the event handler when an effect only reacts to an event-triggered boolean.
- For retry flows, call the async loader directly from the retry handler instead of using a `retryIndex` state that exists only to retrigger an effect.
- Replace barrel imports such as `../components/intelligence` with direct component imports when React Doctor flags extra eager code.
- Lazy-load heavy chart code. For Recharts views, keep the light wrapper in the calling component and move the chart canvas into a lazily imported component.
- Hoist static empty arrays and `Intl.*Format` instances to module scope.
- Use stable keys built from data fields instead of array indexes.
- Prefer native list elements (`ul`/`li`) over `role="list"`/`role="listitem"` when the markup is actually a list.
- Replace `[...array].sort(...)` with `array.toSorted(...)` when the TypeScript lib supports ES2023.
- Replace sort-then-first min/max patterns with a single-pass helper.
- Convert `.filter(...).map(...)` chains to `reduce` only when the transformation is local and obvious.
- Split large components into named subcomponents by page section; keep route/data loading in the page component and move stable JSX sections out.

## UPL Lens Guardrails

- Do not make product UI copy or page behavior drift while fixing diagnostics.
- Do not make React read CSVs, notebooks, or generated artifacts.
- Keep FastAPI JSON as the frontend data contract.
- Preserve analytical UPL Lens language: match briefs, team/player contribution, trends, data quality, and source-record boundaries.
- Do not touch unrelated docs deletions or broad repo cleanup while doing a React Doctor pass.

## Completion Evidence

Only call the work complete when both commands pass from `frontend/`:

```powershell
npm run build
npx react-doctor@latest --verbose --diff
```

The React Doctor output must say `No issues found!` and show `100 / 100`.
