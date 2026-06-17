# Repository-specific Copilot / AI Agent Instructions

## Big Picture

This repository is evolving from a UPL goal timing notebook project into an
open-source Uganda Premier League data platform with **UPL Lens** as the public
frontend product.

The target architecture is:

```text
scraper -> raw data/cache -> cleaning/modeling -> Postgres -> FastAPI -> React
```

Notebooks remain the research lab. They are where analysis ideas are explored
and validated before becoming SQL views, API endpoints, or React dashboard
features.

Read `AGENTS.md`, `docs/START_HERE.md`, `docs/PRODUCT_STRATEGY.md`, and
`docs/PROJECT_ROADMAP.md` before making large changes.
When creating, editing, consolidating, deleting, or depending on project
documentation, use the installed `docs-steward` skill to keep documentation
accurate, non-redundant, linked, and aligned with agent guidance.
When an Issue number is provided, treat the Issue as the active task brief:
read its body, comments, labels, milestone, Project, checklist, and acceptance criteria before
editing. Comment or report against the Issue, but do not close important Issues
or approve releases unless the project owner explicitly instructs it.
For meaningful Issue or Project work, use an Issue-specific branch and Pull
Request instead of pushing directly to `main`. Open draft PRs by default, link
the Issue, include verification, and leave merge/release approval to the owner.
When opening a PR from an Issue, copy relevant Issue labels, assign the same
milestone, add the PR to the same Project, set PR status to
`status: needs-review` only after the Issue checklist and acceptance criteria
are complete, and use `Closes #<issue-number>` so the Issue closes when the
owner-reviewed PR is merged. Put useful out-of-scope follow-up in a PR comment
or follow-up Issue.
Small, clear, low-risk fixes may skip Issue creation, but they still need a
branch and PR when they change code, docs, config, or deployment behavior. If a
direct request is meaningful, risky, unclear, multi-step, milestone-related, or
useful for another agent to resume, create or request a GitHub Issue before
implementation. Keep PRs draft until the linked Issue checklist, acceptance
criteria, PR template, and verification evidence are complete. Include local
command output, browser notes, preview URL, endpoint evidence, or an N/A reason
in the PR. After merge, short-lived branches should be deleted unless the owner
explicitly preserves an experiment. Avoid long-lived fixed branches for routine
feature or agent work.
GitHub network operations such as `gh issue`, `gh pr`, `gh project`, and
`git push` may need to run outside sandboxed environments with approval.
If the task affects the public frontend relaunch, also read
`docs/FRONTEND_DESIGN_SYSTEM.md` first and treat it as the frontend, API,
page-requirements, and launch-precedence guide for UPL Lens UI work.

## Current Project State

- `scripts/data_platform/scrape_upl_matches.py` is the scraper command
  entrypoint; the implementation lives under `src/scraping/upl/`.
- Current raw tables include:
  - `matches`
  - `events`
  - `lineups`
  - `staff`
  - `officials`
  - `stats`
  - `failed_matches`
- Raw per-season CSVs are written under `data/raw/<season>/`.
- Staging rebuild code lives under `src/db/staging/`, with
  `src/db/staging_loader.py` kept as a compatibility facade.
- API query logic lives under `src/api/query_services/`, with
  `src/api/queries.py` kept as a compatibility facade.
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

The durable product identity is documented in
`docs/PRODUCT_STRATEGY.md`. The app should feel like an independent UPL football
intelligence platform: curated statistical insight first, dashboard-style
drilldowns second, and the technical portfolio story quietly available through
docs and methodology rather than driving the main UI.

Use the source-record boundary consistently:

```text
Official UPL site = source record.
UPL Lens = analytical meaning.
```

Do not recreate official UPL pages in React unless the UI transforms the raw
record into insight. Plain timelines, lineups, officials, fixtures, or match
metadata should be compactly summarized or linked to the official source unless
UPL Lens adds context such as timing, trends, anomalies, comparisons, or other
football intelligence.

Prefer features that answer questions a user cannot easily answer from
individual match pages.

## Planned Tracks And Work Areas

The production system still has three technical tracks: Data Platform, Research
Lab, and Public Product. New planning should use the four continuous development
areas in `docs/START_HERE.md`:

- Data Reliability & Operations
- Research & Football Intelligence
- Product Experience
- Developer Experience & Documentation

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

Do not create empty architecture for its own sake. Add structure when the
current work area needs it.

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
- Run tests with `python -m pytest` or `.venv\Scripts\python.exe -m pytest` in
  the local Windows virtual environment.

The pytest suite is still early. Validate by running the relevant test, script,
notebook, API endpoint, or frontend view end to end.

## Command Documentation

When command behavior changes, update the relevant docs instead of letting setup
knowledge live only in chat or local machine history. Common command docs live
in `README.md`, `docs/START_HERE.md`, `docs/LOCAL_DEVELOPMENT.md`, this file,
and `AGENTS.md`.

Keep these commands current when their flags, requirements, or expected output
change:

- Local setup and common commands in `docs/LOCAL_DEVELOPMENT.md`.
- Visual architecture and workflow diagrams in `docs/diagram_collection.md`.
- Postgres setup and migration commands.
- Database ingestion and staging rebuild commands.
- FastAPI dev server command.
- React dev server and build commands.
- Scheduled update workflow behavior.
- Test and validation commands.

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

Staging must read from Postgres `raw.*`, not directly from CSV files. The raw
loader already filters historical season-contaminated rows before they enter the
trusted raw database layer.

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
- Read `docs/START_HERE.md`.
- Read `docs/PROJECT_ROADMAP.md`.
- Inspect the current files touched by the task.
- Check whether the task belongs to Data Reliability & Operations, Research &
  Football Intelligence, Product Experience, or Developer Experience &
  Documentation.
- Keep the change area-appropriate.
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
