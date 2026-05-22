# UPL Match Intelligence

An open-source Uganda Premier League data platform for collecting, modeling,
analyzing, and presenting official UPL match data.

This project began as a focused goal timing analysis. It is now evolving into a
full-stack football intelligence system: Python scraping and cleaning, Postgres
storage, FastAPI access, React presentation, notebook-based research, and
scheduled updates.

## Live Demo

The first public Phase 7 deployment is available here:

- Frontend: [UPL Match Intelligence](https://upl-match-intelligence.pages.dev/)
- API: [UPL Match Intelligence API](https://upl-match-intelligence-api.onrender.com/)
- API liveness check:
  [`/health/live`](https://upl-match-intelligence-api.onrender.com/health/live)
- API/database health check:
  [`/health`](https://upl-match-intelligence-api.onrender.com/health)

The deployed app uses the same production path as the local architecture:

```text
React UI -> FastAPI endpoint -> Supabase Postgres query/view -> JSON -> chart/table
```

The backend currently runs on a free Render web service, so the first request
after an idle period can be slow while the service wakes up.

If the app loads in one browser profile but reports the API as offline in
another, check browser extensions before changing deployment settings. Privacy
or ad-blocking extensions can block the hosted Render API request and surface as
`net::ERR_BLOCKED_BY_CLIENT`; Ghostery was the confirmed blocker during the
first Phase 7 verification pass.

## What This Project Is Becoming

The official UPL website is the source archive. UPL Match Intelligence is the
analysis layer on top of it.

The long-term goal is to answer questions that are difficult to answer from
individual match pages:

- Which teams are most dangerous after halftime?
- Which clubs concede late most often?
- Which teams are most disciplined or most card-prone?
- How do cards affect match outcomes?
- Which players are regular starters or impact substitutes?
- Which officials produce high-card matches?
- How do team profiles change across seasons?
- Which matches had the most dramatic timelines?

## Feature 1: Goal Timing Pilot

The first completed analysis in this project is the original UPL goal timing
study. It remains the pilot feature for the wider platform.

The pilot covered six completed seasons from 2019/20 through 2024/25 and found
that the most dangerous regular-time period in UPL matches was not the final 15
minutes, but the first 15 minutes after halftime.

Across 3,222 regular-time goals, the 46-60 minute interval accounted for 17.9%
of goals. At finer resolution, the 51-60 minute window was the highest-volume
10-minute block, and the 56-60 minute window was the highest-volume five-minute
block.

![Goal Timing Distribution](outputs/features/feature_01_goal_timing/goal_timing_upl.png)

### Pilot Finding: Goal Distribution By Interval

| Interval | Goals | Share | Note |
|----------|-------|-------|------|
| 0-15' | 413 | 14.5% | Settling phase |
| 16-30' | 488 | 17.1% | Organised, settled play |
| 31-45' | 441 | 15.4% | Late first half |
| **46-60'** | **517** | **17.9%** | **Peak: second-half restart** |
| 61-75' | 480 | 16.6% | Mid second half |
| 76-90' | 504 | 17.4% | Final phase |

Regular-time goals only. Added-time goals are separated from interval analysis.

![Seasonal Trends](outputs/features/feature_01_goal_timing/gqr_gtsi_trends.png)

### Pilot Research Questions

The pilot analysis answered:

1. When in a match are goals most likely to be scored in Ugandan top-flight
   football?
2. Has the proportion of open-play goals changed across seasons?
3. Are decisive late goals becoming more or less common relative to the rest of
   the match?

The next phase is to keep this analysis as Feature 1 and promote its most useful
findings into the future API and React dashboard.

## Platform Architecture

Target flow:

```text
official UPL website
  -> Python scraper
  -> raw files/cache
  -> cleaning and validation
  -> Postgres
  -> FastAPI
  -> React web app
```

The project is organized into three tracks.

### 1. Data Platform

Responsible for scraping, cleaning, loading, validating, and updating data.

Current scraper output includes:

- `matches`
- `events`
- `lineups`
- `staff`
- `officials`
- `stats`
- `failed_matches`

### 2. Research Lab

Responsible for exploratory analysis in notebooks.

Notebook work is where new questions are tested before becoming production
features. The goal timing study is Feature 1. Future features may include
discipline analysis, home advantage, comeback analysis, player impact, official
profiles, and team style summaries.

### 3. Public Product

Responsible for the user-facing API and dashboard.

The future React app should consume FastAPI endpoints backed by Postgres. It
should not read CSV files directly.

## Repository Structure

```text
upl-goal-timing/
├── README.md
├── AGENTS.md
├── requirements.txt
├── api/
│   └── routers/
├── database/
│   ├── migrations/
│   ├── permissions/
│   └── seeds/
├── docs/
│   ├── ANALYTICS_VIEW_CONVENTIONS.md
│   ├── FEATURE_DATA_ACCESS.md
│   ├── FEATURE_REGISTRY.md
│   ├── FEATURE_PROMOTION_WORKFLOW.md
│   ├── PHASE5_AUTOMATION.md
│   └── PROJECT_ROADMAP.md
├── frontend/
├── notebooks/
│   └── features/
│       ├── _feature_template/
│       │   ├── analysis.ipynb
│       │   ├── research_brief.md
│       │   └── product_plan.md
│       └── feature_01_goal_timing/
│           ├── analysis.ipynb
│           ├── analysis_v2.ipynb
│           ├── research_brief.md
│           └── product_plan.md
├── outputs/
│   └── features/
│       └── feature_01_goal_timing/
│           ├── goal_timing_upl.png
│           ├── gqr_gtsi_trends.png
│           └── gqr_gtsi_trends_notebook.png
├── scripts/
│   ├── data_platform/
│   │   └── scrape_upl_matches.py
│   └── features/
│       └── feature_01_goal_timing/
│           └── build_goal_timing_dataset.py
└── src/
    ├── analytics/
    ├── db/
    ├── features/
    │   └── feature_01_goal_timing/
    ├── research/
    ├── scraping/
    ├── validation/
    ├── cleaning.py
    ├── config.py
    └── dataset.py
```

Some folders are intentionally empty for now. They reserve the approved
architecture for future implementation.

## Current Commands

Install dependencies:

```bash
pip install -r requirements.txt
```

Scrape a season:

```bash
python scripts/data_platform/scrape_upl_matches.py --season 2025-26
```

Build the Feature 1 goal timing dataset:

```bash
python scripts/features/feature_01_goal_timing/build_goal_timing_dataset.py
```

Create the local Postgres database:

```sql
CREATE DATABASE upl_match_intelligence;
```

Apply the Phase 1 database migrations:

```bash
python scripts/data_platform/apply_db_migrations.py
```

Load raw season CSVs into Postgres:

```bash
python scripts/data_platform/load_raw_to_postgres.py
```

Load only one season into Postgres:

```bash
python scripts/data_platform/load_raw_to_postgres.py --season 2025-26
```

Build cleaned staging tables from Postgres raw tables:

```bash
python scripts/data_platform/build_staging_from_raw.py
```

Build cleaned staging tables for one season:

```bash
python scripts/data_platform/build_staging_from_raw.py --season 2025-26
```

Verify staging row counts and validation issues:

```bash
python scripts/data_platform/verify_staging_outputs.py
```

Run the read-first FastAPI backend:

```bash
python -m uvicorn api.main:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Open the Feature 1 research notebooks:

```text
notebooks/features/feature_01_goal_timing/
```

Start a new experimental feature from the template:

```powershell
Copy-Item -Recurse notebooks\features\_feature_template notebooks\features\feature_02_card_trends
```

Track notebook-to-product features:

```text
docs/FEATURE_REGISTRY.md
```

Use these Phase 6 guides when researching or promoting a feature:

```text
docs/FEATURE_PROMOTION_WORKFLOW.md
docs/FEATURE_DATA_ACCESS.md
docs/ANALYTICS_VIEW_CONVENTIONS.md
```

## Phase 1 Database Setup

Phase 1 introduces the first real Postgres foundation for the project.

- `database/migrations/001_create_raw_schema.sql` creates the `raw`,
  `staging`, and `analytics` schemas.
- `database/migrations/002_create_staging_foundation.sql` creates the first
  cleaned staging tables and the validation issue log.
- `database/migrations/003_create_staging_validation_runs.sql` records each
  staging build run, even when no validation issues are found.
- The `raw` schema contains source-shaped tables that mirror the current
  scraper CSV outputs.
- `scripts/data_platform/apply_db_migrations.py` applies versioned SQL files in
  order and records them in `app_meta.schema_migrations`.
- `scripts/data_platform/load_raw_to_postgres.py` imports the season CSV files
  from `data/raw/<season>/` into Postgres.
- `scripts/data_platform/verify_raw_postgres_counts.py` compares season CSV
  counts to Postgres counts by season and table.

The raw ingestion is idempotent:

- `raw.matches` upserts by `match_id`.
- The child tables use stable row fingerprint keys so rerunning the loader
  updates the same logical record instead of inserting duplicates.
- `raw.failed_matches` upserts by season and match URL.

### Local Setup Steps

1. Copy `.env.example` to `.env`.
2. Fill in your Postgres credentials in `.env`.
3. Create the database:

```bash
psql -U postgres -c "CREATE DATABASE upl_match_intelligence;"
```

4. Apply migrations:

```bash
python scripts/data_platform/apply_db_migrations.py
```

5. Load the raw CSV files:

```bash
python scripts/data_platform/load_raw_to_postgres.py
```

6. Verify the CSV counts against Postgres:

```bash
python scripts/data_platform/verify_raw_postgres_counts.py
```

### Verification Queries

List the raw tables:

```bash
psql -U postgres -d upl_match_intelligence -c "\\dt raw.*"
```

Check row counts:

```bash
psql -U postgres -d upl_match_intelligence -c "SELECT 'matches' AS table_name, COUNT(*) FROM raw.matches UNION ALL SELECT 'events', COUNT(*) FROM raw.events UNION ALL SELECT 'lineups', COUNT(*) FROM raw.lineups UNION ALL SELECT 'staff', COUNT(*) FROM raw.staff UNION ALL SELECT 'officials', COUNT(*) FROM raw.officials UNION ALL SELECT 'stats', COUNT(*) FROM raw.stats UNION ALL SELECT 'failed_matches', COUNT(*) FROM raw.failed_matches;"
```

Inspect one season:

```bash
psql -U postgres -d upl_match_intelligence -c "SELECT season, COUNT(*) AS matches FROM raw.matches GROUP BY season ORDER BY season;"
```

Run the repeatable Phase 1 verification script:

```bash
python scripts/data_platform/verify_raw_postgres_counts.py
```

Verify just one season:

```bash
python scripts/data_platform/verify_raw_postgres_counts.py --season 2025-26
```

## Phase 2 Cleaning, Validation, And Staging

Phase 2 starts the cleaned database layer.

Plain-English database layers:

- `raw` is the source archive in Postgres. It keeps scraper-shaped records close
  to the original UPL pages and raw CSV columns.
- `staging` is the cleaned working layer. It standardizes dates, team names,
  event types, event minutes, result fields, and source quality checks.
- `analytics` will come later. It will hold facts, dimensions, summaries, and
  views that are easier for FastAPI and React to query.

The Phase 2 pipeline reads from Postgres `raw.*` tables, not directly from CSVs.
This matters because the Phase 1 loader already protects `raw.*` from known
historical season contamination.

Apply the staging migration:

```bash
python scripts/data_platform/apply_db_migrations.py
```

Rebuild all staging tables from Postgres raw tables:

```bash
python scripts/data_platform/build_staging_from_raw.py
```

Rebuild one season only:

```bash
python scripts/data_platform/build_staging_from_raw.py --season 2025-26
```

Verify staging outputs:

```bash
python scripts/data_platform/verify_staging_outputs.py
```

Verify one season and one specific validation run:

```bash
python scripts/data_platform/verify_staging_outputs.py --season 2025-26 --run-id <run-id>
```

The build command records each run in `staging.validation_runs` and records
individual validation issues in `staging.validation_issues`.
Review a run with SQL:

```sql
SELECT severity, check_name, table_name, COUNT(*)
FROM staging.validation_issues
WHERE run_id = '<run-id>'
GROUP BY severity, check_name, table_name
ORDER BY severity, check_name, table_name;
```

Initial Phase 2 cleaning handles:

- day-first date parsing
- padded/blank text normalization
- empty event minute strings
- inline minute annotations such as `56 (P)`
- missing team and player values where relevant
- strict Man of the Match extraction, keeping only a person name plus a team
  that actually played in the match
- duplicate natural-key risks
- season consistency checks
- match-reference checks from child tables back to `staging.matches`

## Phase 3 FastAPI Read Backend

Phase 3 starts the public product layer without building React yet.

Plain-English API flow:

```text
browser or future React app
  -> FastAPI route
  -> src/api/queries.py
  -> Postgres staging.* table
  -> beginner-readable JSON
```

The API reads from Postgres `staging.*` tables. It does not read raw CSV files.

Start the local API server:

```bash
python -m uvicorn api.main:app --reload
```

The server runs at:

```text
http://127.0.0.1:8000
```

Interactive OpenAPI docs are available at:

```text
http://127.0.0.1:8000/docs
```

Initial endpoints:

```text
GET /health
GET /seasons
GET /seasons/{season}/overview
GET /insights/goal-timing
GET /matches
GET /matches/{match_id}
GET /teams
GET /events
GET /officials
```

Example endpoint checks:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/seasons
curl "http://127.0.0.1:8000/seasons/2025_26/overview"
curl "http://127.0.0.1:8000/insights/goal-timing?season=2025_26"
curl "http://127.0.0.1:8000/matches?season=2025_26&limit=5"
curl "http://127.0.0.1:8000/matches/15463"
curl "http://127.0.0.1:8000/teams?season=2025_26"
curl "http://127.0.0.1:8000/events?season=2025_26&event_type=goal&limit=10"
curl "http://127.0.0.1:8000/officials?season=2025_26&limit=10"
```

Useful filters:

- `season`, for example `2025_26`
- `team`, for partial team-name matching
- `match_day`, for match, event, and official lists
- `event_type`, for event lists such as `goal`, `yellow_card`, or `red_card`
- `limit` and `offset`, for list pagination

## Phase 4 React Frontend Pilot

Phase 4 starts the browser product layer with a narrow League Overview screen.
The important flow is:

```text
React League Overview
  -> FastAPI endpoints
  -> src/api/queries.py
  -> Postgres staging.* tables
  -> JSON
  -> dashboard cards, lists, and tables
```

The frontend does not read CSV files. It uses the existing API endpoints for
health, seasons, season overview, goal timing, matches, teams, and events.

Start the local API server from the repository root:

```powershell
.venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

In a second terminal, start the React frontend:

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://127.0.0.1:5173
```

The frontend API URL is configured with Vite:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Copy `frontend/.env.example` to `frontend/.env` only if you need to point the
frontend at a different FastAPI host or port.

What the pilot shows:

- API/database health from `/health`
- available seasons from `/seasons`
- season-level totals from `/seasons/{season}/overview`
- the Feature 1 goal timing insight from `/insights/goal-timing?season=...`
- a season selector
- summary cards for matches, teams, goals, and cards
- a Goal Timing Explorer panel for regular-time goals by 15-minute interval
- recent matches from `/matches?season=...`
- team records from `/teams?season=...`
- event breakdown from `/events?season=...`
- placeholders for the next product areas

## Phase 5 Current-Season Automation

Phase 5 begins the automation layer. Instead of manually remembering every
pipeline command, use one orchestrator that runs the current-season update steps
in order.

Run the full local update from the repository root:

```powershell
.venv\Scripts\python.exe scripts\data_platform\update_current_season.py --season 2025-26
```

That command runs:

```text
scraper
  -> database migrations
  -> raw CSV to Postgres load
  -> raw count verification
  -> staging rebuild
  -> staging validation summary
```

By default, the Phase 5 update refreshes from the live UPL source. That means it
bypasses cached HTML and old checkpoint state so the current-season match list
does not become stale. For faster development runs where you intentionally want
to reuse cached pages and resume from checkpoints, add `--use-cache`:

```powershell
.venv\Scripts\python.exe scripts\data_platform\update_current_season.py --season 2025-26 --use-cache
```

If you already scraped the season and only want to refresh Postgres/staging:

```powershell
.venv\Scripts\python.exe scripts\data_platform\update_current_season.py --season 2025-26 --skip-scrape
```

At the end of each run, the orchestrator prints a data-completeness summary from
the season's failed-match manifest. By default, remaining failed matches are a
warning because temporary source-site timeouts can happen. Use strict mode when
you want automation to fail if any match still needs a retry:

```powershell
.venv\Scripts\python.exe scripts\data_platform\update_current_season.py --season 2025-26 --fail-on-remaining-failed-matches
```

### Routine Updates Versus Admin Migrations

There are two different database jobs in Phase 5:

- **Admin/migration setup** changes the database structure by creating schemas,
  tables, indexes, and migration records. Run this manually with a trusted
  Supabase/Postgres admin credential when the schema changes.
- **Routine current-season refresh** updates rows in the existing `raw` and
  `staging` tables. This is what the weekly GitHub Actions job should do.

For routine automation, skip migrations and use a least-privilege loader role:

```powershell
.venv\Scripts\python.exe scripts\data_platform\update_current_season.py --season 2025-26 --skip-migrations
```

The template at `database/permissions/001_create_upl_actions_loader.sql` creates
an example `upl_actions_loader` role for routine updates. Run it only in a
secure admin SQL session, replace the password placeholder there, and then store
that loader role's connection values in GitHub repository secrets. Do not paste
real Supabase passwords, connection strings, or API keys into chat or committed
files.

GitHub Actions has a starter workflow at
`.github/workflows/current-season-update.yml`. It can be triggered manually and
also runs weekly. The scheduled workflow runs `full` mode with migrations
skipped, so it is designed for the limited loader role described above. To apply
migrations from GitHub Actions, trigger the workflow manually and set
`apply_migrations` to `true` only while using admin-capable database secrets.

The working automation setup, manual run settings, artifact behavior, and common
Supabase connection errors are documented in
[`docs/PHASE5_AUTOMATION.md`](docs/PHASE5_AUTOMATION.md).

The workflow installs `requirements-automation.txt` instead of the full
`requirements.txt`, and `actions/setup-python` caches pip downloads. This keeps
scheduled refreshes lighter while leaving notebook, API, testing, and formatting
dependencies in the full development requirements file.

Full mode needs these GitHub repository secrets:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_SSLMODE
```

For Supabase pooler connections, the GitHub `POSTGRES_USER` secret may need the
project reference suffix, for example `upl_actions_loader.<project-ref>`, while
the database role created inside Postgres remains `upl_actions_loader`.

## Phase 6 Notebook Insight Promotion

Phase 6 starts the repeatable path from notebook research into the product.
New experiments should use the feature package workflow documented in
[`docs/FEATURE_PROMOTION_WORKFLOW.md`](docs/FEATURE_PROMOTION_WORKFLOW.md) and
the notebook data-access standard documented in
[`docs/FEATURE_DATA_ACCESS.md`](docs/FEATURE_DATA_ACCESS.md).

Feature package shape:

```text
notebooks/features/feature_xx_short_name/
  README.md
  analysis.ipynb
  research_brief.md
  product_plan.md
  outputs/
```

In plain English:

- `analysis.ipynb` is the lab where the football logic is tested.
- `research_brief.md` explains the question, finding, metrics, and caveats.
- `product_plan.md` tells an AI agent what to build or change in Postgres/FastAPI/React.
- `outputs/` stores reference charts only; the product must not depend on them.

Research notebooks should use cleaned Postgres `staging.*` tables by default.
Use `raw.*` only for source-data debugging, CSVs only for legacy comparison, and
`analytics.*` when a promoted metric becomes stable and reusable. For safer
notebook queries, use:

```python
from src.research import read_sql
```

The optional read-only research role template lives at:

```text
database/permissions/002_create_upl_research_reader.sql
```

The first promoted slice is Feature 1 goal timing:

```text
Feature 1 notebook finding
  -> staging.events regular-time goal query
  -> GET /insights/goal-timing?season=...
  -> React Goal Timing Explorer panel
```

This endpoint intentionally excludes added-time goals from the interval chart,
matching the original pilot caveat. It counts regular-time goal events in these
15-minute windows: `0-15`, `16-30`, `31-45`, `46-60`, `61-75`, and `76-90`.

Verify the first Phase 6 slice locally:

```powershell
.venv\Scripts\python.exe -m compileall api src scripts
.venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

Then check:

```powershell
curl "http://127.0.0.1:8000/insights/goal-timing?season=2025_26"
cd frontend
npm run build
npm run dev
```

## Roadmap

The detailed implementation plan lives in
[docs/PROJECT_ROADMAP.md](docs/PROJECT_ROADMAP.md).

Near-term phases:

1. Stabilize the structured scraper outputs.
2. Add Postgres schema and ingestion.
3. Add validation and analytics models.
4. Build a read-first FastAPI backend.
5. Build a React frontend with the goal timing pilot as Feature 1.
6. Add GitHub Actions for scheduled current-season updates.
7. Promote new notebook analyses into dashboard features.

## Data Note

Raw and processed data are not committed to this repository. The data is
collected from the official UPL website for analytical purposes. The scraper and
analysis pipeline are included so the methodology can be inspected and reused.

## References

Armatas, V., & Pollard, R. (2014). Home advantage in Greek football. *Journal of
Sports Sciences*, 32(12), 1210-1218.

Lago-Ballesteros, J., & Lago-Penas, C. (2010). Performance in team sports:
Identifying the keys to success in soccer. *Journal of Human Kinetics*, 25,
85-91.

Njororai, W. W. S. (2013). Analysis of goals scored in the 2010 World Cup soccer
tournament held in South Africa. *Journal of Physical Education and Sport*,
13(1), 6-13.

Yiannakos, A., & Armatas, V. (2006). Evaluation of the goal scoring patterns in
European Championship in Portugal 2004. *International Journal of Performance
Analysis in Sport*, 6(1), 178-188.

---

**Humphrey Nyanzi**  
Sports Scientist & Data Analyst  
[GitHub](https://github.com/humphrey-nyanzi) ·
[Substack](https://humphreyn-substack.com) · [X](https://x.com/phreyn)
