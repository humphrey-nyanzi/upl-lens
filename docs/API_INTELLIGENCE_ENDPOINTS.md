# UPL Lens API Intelligence Endpoints

This note documents backend shapes added for routine UPL Lens page intelligence.
These endpoints are not promoted notebook insights. They are reusable product
modules that help React render analytical pages without duplicating durable
backend logic.

For the canonical frontend-facing contract, read
[API_CONTRACT.md](API_CONTRACT.md). This file stays as the focused routine
intelligence note for the backend shapes that support those pages.

The product boundary remains:

```text
Official UPL site = source record.
UPL Lens = analytical meaning layer.
```

## Endpoints

| Endpoint | Frontend page | Purpose |
|----------|---------------|---------|
| `GET /trends/seasons` | Trends | Season-by-season chart data for goals, cards, results, high-scoring shares, timeline coverage, and data quality. |
| `GET /teams` | Teams | Existing team index, now with derived rates, goal difference, team slugs, and profile labels. |
| `GET /teams/{team_slug}/profile?season=` | Team Profile | One-team record, home/away split, recent form, event summary, goal timing buckets, discipline summary, and caveats. |
| `GET /matches/intelligence?season=&team=&match_day=&signal=&sort=&limit=&offset=` | Matches | Match rows with backend-computed signal labels, interest score, event counts, late-goal counts, and data quality notes. |
| `GET /matches/{match_id}` | Match Detail | Existing match detail, now with an intelligence summary, key moments, phase summary, and score progression. |
| `GET /players/leaderboards?season=&limit=` | Players | Grouped player leaderboards for goals, assists, appearances, starts, contributions, cards, and bench impact. |
| `GET /players/{player_slug}?season=` | Player Detail | Existing player profile, now with contribution rates, labels, season trend, and data quality note. |
| `GET /overview/intelligence?season=` | Overview | Composed front-page pulse, notices, signal matches, team signals, and data quality summary. |

## Data Rules

- Public aggregates use cleaned `staging.*` tables and
  `analytics.team_season_summary`.
- Source anomalies are excluded from normal public calculations and counted as
  caveats where a response includes quality fields.
- Timeline uncertainty is exposed through `timeline_status`, signal labels,
  data quality notes, or coverage shares.
- Match, team, and player labels are derived in `src/api/intelligence.py` so the
  frontend does not have to recreate durable football logic.

## Verification

Run focused backend checks after changing these contracts:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_intelligence_helpers.py
.venv\Scripts\python.exe -c "from api.main import app; print([route.path for route in app.routes if hasattr(route, 'path')])"
```

Run broader API or full pytest checks when response schemas, query services, or
database-facing SQL change.
