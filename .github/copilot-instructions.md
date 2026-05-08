# Repository-specific Copilot / AI Agent Instructions

## Big Picture

This repository is evolving from a UPL goal timing notebook project into **UPL
Match Intelligence**: an open-source Uganda Premier League data platform.

The target architecture is:

```text
scraper -> raw data/cache -> cleaning/modeling -> Postgres -> FastAPI -> React
```

Notebooks remain the research lab. They are where analysis ideas are explored
and validated before becoming SQL views, API endpoints, or React dashboard
features.

Read `AGENTS.md` and `docs/PROJECT_ROADMAP.md` before making large changes.

## Current Project State

- `scripts/data_platform/scrape_upl_matches.py` scrapes official UPL match
  pages.
- Current raw tables include:
  - `matches`
  - `events`
  - `lineups`
  - `staff`
  - `officials`
  - `stats`
  - `failed_matches`
- Raw per-season CSVs are written under `data/raw/<season>/`.
- Older processed goal-only outputs remain under `data/processed/`.
- Notebook analysis remains useful, especially Feature 1: the original goal
  timing pilot under `notebooks/features/feature_01_goal_timing/`.
- Raw and processed data are gitignored.

## Product Direction

Do not treat the app as a simple clone of the official UPL website. The official
site is the source/archive. This project should add an intelligence layer:

- Goal timing patterns.
- Discipline trends.
- Cards and match outcomes.
- Team profiles.
- Player appearances and impact.
- Officials summaries.
- Match timeline exploration.
- Season-over-season league changes.

Prefer features that answer questions a user cannot easily answer from
individual match pages.

## Planned Tracks

### Data Platform

Owns scraping, cleaning, loading, validation, and scheduled updates.

Expected future pieces:

- Postgres schema/migrations.
- CSV-to-Postgres ingestion.
- Idempotent current-season update script.
- Data quality checks.
- GitHub Actions workflow.

### Research Lab

Owns exploration.

Use notebooks to:

- Prototype relationships.
- Create rough visualizations.
- Validate findings.
- Document caveats.

Do not make notebooks responsible for production serving.

### Public Product

Owns API and frontend.

Expected future pieces:

- FastAPI backend.
- React frontend.
- Interactive match, team, player, discipline, and goal timing pages.

The React app should call FastAPI. It should not read CSV files directly.

## Preferred Repository Evolution

Grow toward this shape gradually:

```text
scripts/
  data_platform/
    scrape_upl_matches.py
    load_to_postgres.py
    update_current_season.py
  features/
    feature_01_goal_timing/
      build_goal_timing_dataset.py

src/
  scraping/
  cleaning/
  db/
  validation/
  analytics/
  config.py
  dataset.py

database/
  schema.sql
  migrations/
  seeds/

api/
  main.py
  routers/

frontend/
  React app

notebooks/
  features/
    feature_01_goal_timing/

docs/
  PROJECT_ROADMAP.md
```

Do not create empty architecture for its own sake. Add structure when a phase
needs it.

## Current Commands

- Install Python deps: `pip install -r requirements.txt`
- Run scraper: `python scripts/data_platform/scrape_upl_matches.py --season 2025-26`
- Build Feature 1 goal timing dataset: `python scripts/features/feature_01_goal_timing/build_goal_timing_dataset.py`
- Apply database migrations: `python scripts/data_platform/apply_db_migrations.py`
- Load raw CSVs into Postgres: `python scripts/data_platform/load_raw_to_postgres.py`
- Verify raw CSVs against Postgres: `python scripts/data_platform/verify_raw_postgres_counts.py`
- Build staging from raw Postgres tables: `python scripts/data_platform/build_staging_from_raw.py`
- Verify staging outputs: `python scripts/data_platform/verify_staging_outputs.py`
- Work with Feature 1 notebooks from `notebooks/features/feature_01_goal_timing/`.

No formal test suite exists yet. Validate by running the relevant script,
notebook, API endpoint, or frontend view end to end.

## Future Commands To Document When Added

When these pieces are introduced, update this file and `AGENTS.md`:

- Postgres setup command.
- Database migration command.
- Database ingestion command.
- FastAPI dev server command.
- React dev server command.
- Scheduled update workflow behavior.

## Coding Guidance

- Keep constants, paths, URLs, and team-name corrections centralized in
  `src/config.py` or a clear config module.
- Use lowercase, underscore-separated column names.
- Write beginner-readable code with clear names, small functions, and simple
  control flow.
- Add comments where they explain non-obvious decisions, database modeling,
  idempotent ingestion, validation rules, or API/frontend data flow.
- Avoid comments that only repeat the code. Prefer comments that explain why a
  choice was made.
- Prefer typed Python functions.
- Use NumPy-style docstrings for public Python functions.
- Copy DataFrames before mutation: `df = df.copy()`.
- Prefer reusable modules under `src/` over notebook-only logic.
- Preserve source IDs such as `match_id`, team URLs, player URLs, and match URLs
  when modeling relationships.
- Keep scraping, cleaning, database loading, API, and frontend concerns
  separate.

## Database Guidance

Postgres is the intended production database.

Use layered modeling:

- `raw` for source-shaped scraped records.
- `staging` for cleaned and normalized records.
- `analytics` for facts, dimensions, summaries, and views.

Phase 2 staging must read from Postgres `raw.*`, not directly from CSV files.
The raw loader already filters historical season-contaminated rows before they
enter the trusted raw database layer.

Likely modeled tables:

- `dim_seasons`
- `dim_teams`
- `dim_players`
- `dim_officials`
- `dim_venues`
- `fact_matches`
- `fact_events`
- `fact_lineups`
- `fact_match_stats`

Ingestion should be idempotent. Re-running a season import must not duplicate
matches, events, lineups, officials, or stats.

## API Guidance

FastAPI should start read-only.

Good first endpoints:

- `GET /health`
- `GET /seasons`
- `GET /matches`
- `GET /matches/{match_id}`
- `GET /teams`
- `GET /teams/{team_id}/summary`
- `GET /events`

Keep route handlers thin. Put query/service logic in separate modules when it
grows.

## Frontend Guidance

Build a real React analytical app, not another Streamlit-style notebook
dashboard.

Good first pages:

- League overview.
- Goal timing explorer.
- Discipline dashboard.
- Team profile.
- Match explorer.

Use readable labels and football language. Avoid exposing raw database column
names to users.

## Automation Guidance

GitHub Actions is the preferred automation path.

The future scheduled workflow should:

1. Run the current-season scraper.
2. Detect new or changed matches.
3. Load updates into Postgres idempotently.
4. Run validation checks.
5. Log failed matches and errors clearly.

## Agent Checklist

Before making non-trivial changes:

- Read `AGENTS.md`.
- Read `docs/PROJECT_ROADMAP.md`.
- Inspect the current files touched by the task.
- Check whether the task belongs to data platform, research lab, or public
  product.
- Keep the change phase-appropriate.
- Explain each step in beginner-friendly language: what changed, why it matters,
  and how to run or verify it.
- When adding unfamiliar technologies such as Postgres, SQLAlchemy, Alembic,
  FastAPI, React, Docker, or GitHub Actions, include a short explanation of the
  concept and how it fits into this project.
- Do not provide unexplained code-only changes.

Do not:

- Move production serving into notebooks.
- Make the future frontend read CSVs directly.
- Introduce a different primary database without user approval.
- Hardcode team names, source URLs, or paths in random modules.
- Add broad architecture scaffolding with no runnable value.
