# [Product] Intelligence-layer API client sync

Labels: `area: product-experience`, `type: api-contract`, `priority: high`, `status: ready`
Milestone: `v0.2 Intelligence API Client Sync`

## Objective

Sync `frontend/src/api/types.ts` and `frontend/src/api/client.ts` with the
current intelligence-layer backend responses.

## Context

The backend exposes richer responses for trends, overview intelligence, match
triage, team profiles, player leaderboards, and player/match detail payloads.
The frontend should consume these through typed FastAPI JSON calls.

## Acceptance Criteria

- [ ] Types cover `/trends/seasons`, `/overview/intelligence`, `/matches/intelligence`, `/teams/{team_slug}/profile`, and `/players/leaderboards`.
- [ ] Existing client methods keep working or have safe compatibility fallbacks.
- [ ] No React page reads CSVs, notebooks, or exported notebook images.
- [ ] Frontend build passes.
- [ ] Durable API contract notes are updated if response assumptions change.

## Related Documents

- `docs/FRONTEND_DESIGN_SYSTEM.md`
- `docs/PROJECT_ROADMAP.md`
