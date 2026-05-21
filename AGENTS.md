# AGENTS.md - UPL Match Intelligence

## Project Direction

This repository is evolving from a one-off Uganda Premier League goal timing
analysis into an open-source UPL data platform.

The long-term goal is to collect official UPL match data, store it in Postgres,
clean and model it for analysis, expose it through a FastAPI backend, and present
the best insights in a React web app. Notebooks remain the research lab where new
questions are explored before they become dashboard features.

Use [docs/PROJECT_ROADMAP.md](docs/PROJECT_ROADMAP.md) as the main planning
reference for architecture, phases, and implementation priorities.

## Current State

- `scripts/data_platform/scrape_upl_matches.py` scrapes structured match data
  from the official UPL website.
- Current raw tables include `matches`, `events`, `lineups`, `staff`,
  `officials`, `stats`, and `failed_matches`.
- Raw per-season CSV outputs live under `data/raw/<season>/`.
- Older processed goal-only datasets still live under `data/processed/`.
- `notebooks/features/feature_01_goal_timing/` contains the original goal
  timing analysis, now treated as Feature 1 / the pilot project.
- Raw and processed CSVs are gitignored.

## Target Architecture

Keep the system split into three connected tracks:

1. **Data Platform**
   - Scrape official UPL data.
   - Detect new or changed matches.
   - Normalize team, player, venue, official, event, and match data.
   - Load modeled data into Postgres.
   - Validate data quality and log failures.

2. **Research Lab**
   - Use notebooks for exploratory analysis.
   - Test statistical relationships and visual ideas.
   - Promote only useful, validated analyses into SQL views/API endpoints.

3. **Public Product**
   - Serve data through FastAPI.
   - Build a React frontend for interactive exploration.
   - Focus on insights the official website does not provide.

Preferred request flow for the future app:

```text
React UI -> FastAPI endpoint -> Postgres query/view -> JSON -> chart/table
```

The frontend should not read CSV files directly.

## Planned Repository Shape

The exact structure may evolve, but future work should move toward:

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
    matches.py
    teams.py
    players.py
    events.py
    officials.py
    stats.py

frontend/
  React app

notebooks/
  features/
    feature_01_goal_timing/

docs/
  PROJECT_ROADMAP.md
```

Do not create all of this at once unless the task calls for it. Grow the
structure phase by phase.

## Build / Run

Current workflow:

- Install Python deps: `pip install -r requirements.txt`
- Run scraper: `python scripts/data_platform/scrape_upl_matches.py --season 2025-26`
- Build Feature 1 goal timing dataset: `python scripts/features/feature_01_goal_timing/build_goal_timing_dataset.py`
- Apply database migrations: `python scripts/data_platform/apply_db_migrations.py`
- Load raw CSVs into Postgres: `python scripts/data_platform/load_raw_to_postgres.py`
- Verify raw Postgres counts: `python scripts/data_platform/verify_raw_postgres_counts.py`
- Build cleaned staging tables: `python scripts/data_platform/build_staging_from_raw.py`
- Verify staging outputs: `python scripts/data_platform/verify_staging_outputs.py`
- Open notebooks from `notebooks/features/feature_01_goal_timing/` for the pilot analysis.

Future workflow should add:

- Postgres startup/configuration instructions.
- Database migration command.
- Data loading command.
- Raw-to-staging cleaning command.
- Staging validation command.
- FastAPI dev server command.
- React dev server command.
- GitHub Actions scheduled update workflow.

No formal test suite exists yet. Validate changes by running the relevant
script, notebook, API endpoint, or frontend page end to end.

## Implementation Priorities

Follow the roadmap phases:

1. Stabilize scraped outputs and schemas.
2. Add Postgres schema and ingestion.
3. Add FastAPI read endpoints.
4. Add React app with the goal timing pilot as Feature 1.
5. Add GitHub Actions automation for current-season updates.
6. Promote notebook discoveries into production views and dashboard features.

Avoid jumping ahead into UI work before the database model can support it.

## Feature Promotion Workflow

Phase 6 notebook experiments should use the feature package workflow documented
in [docs/FEATURE_PROMOTION_WORKFLOW.md](docs/FEATURE_PROMOTION_WORKFLOW.md).
Use [docs/FEATURE_DATA_ACCESS.md](docs/FEATURE_DATA_ACCESS.md) for notebook data
source rules and read-only research access. Use
[docs/FEATURE_REGISTRY.md](docs/FEATURE_REGISTRY.md) to track feature lifecycle
status, and [docs/ANALYTICS_VIEW_CONVENTIONS.md](docs/ANALYTICS_VIEW_CONVENTIONS.md)
to decide when stable notebook metrics should become `analytics.*` views.

When starting a new experimental feature, copy:

```text
notebooks/features/_feature_template/
```

into a numbered feature folder such as:

```text
notebooks/features/feature_02_card_trends/
```

Each feature package should contain:

- `analysis.ipynb` for exploratory research.
- `research_brief.md` for the football question, metric definitions, finding, and
  caveats.
- `product_plan.md` for the promotion plan, later change requests, desired
  React UI, validation plan, and implementation history.
- `outputs/` for reference notebook exports only.

When creating a feature package, add it to `docs/FEATURE_REGISTRY.md` and update
its lifecycle status as it moves from research to promotion.

For notebook data access, default to cleaned Postgres `staging.*` tables through
`src.research.read_sql`. Use `raw.*` only for source-data debugging, CSVs only
for legacy comparison, and `analytics.*` for stable promoted views or summaries.

Use a direct API query for small first slices. Use an `analytics.*` view when a
metric becomes stable, reusable, or complex enough to deserve a named database
contract. Use stored analytics tables or materialized views only when a normal
view is too slow or snapshot history is required.

When promoting or modifying a feature, treat `research_brief.md` and
`product_plan.md` as the source of truth, then use the notebook as
supporting evidence. Keep the promoted product path as:

```text
Postgres staging/analytics -> FastAPI endpoint -> JSON -> React dashboard
```

Do not make React read CSV files, notebooks, or exported notebook images.

## Product Principles

This project should not merely recreate the official UPL website. The official
site is the source/archive. This project should be the intelligence layer.

Prioritize questions like:

- Which teams concede most after halftime?
- Which teams are most disciplined or most card-prone?
- How do cards affect match outcomes?
- Which players are regular starters or late-impact contributors?
- Which officials give the most cards per match?
- Which teams are strong at home or vulnerable away?
- Which matches had the most dramatic timelines?
- How has the league changed across seasons?

Every dashboard feature should make the data easier to understand than a list of
match pages would.

## Code Style

- Python 3 with type annotations where practical.
- Use NumPy-style docstrings for public Python functions.
- Write beginner-readable code. Prefer clear names, small functions, and simple
  control flow over clever shortcuts.
- Add helpful comments for non-obvious decisions, database modeling choices,
  idempotent loading logic, validation rules, and cross-module workflows.
- Avoid noisy comments that restate the code. Explain why something exists, not
  merely what a single line does.
- Imports: standard library, third-party, then local modules.
- Copy DataFrames before mutation: `df = df.copy()`.
- Prefer functions that return new DataFrames rather than mutating inputs.
- Keep constants, paths, team-name corrections, and external URLs in
  `src/config.py` or another centralized config module.
- Column names should be lowercase and underscore-separated.
- Prefer stable IDs such as `match_id`, player URLs, team URLs, and official
  names when modeling relationships.
- Avoid hardcoding team names, paths, or season-specific assumptions outside
  configuration/modeling layers.

## Data Modeling Guidance

When adding Postgres support, separate:

- Raw scraped records.
- Staging/cleaned records.
- Analytics-ready facts, dimensions, and views.

For Phase 2, use Postgres `raw.*` as the input for cleaning. Do not make the new
staging pipeline read raw CSV files directly; CSV-to-Postgres protection happens
in Phase 1 ingestion.

Useful future concepts:

- `dim_teams`
- `dim_players`
- `dim_officials`
- `dim_venues`
- `dim_seasons`
- `fact_matches`
- `fact_events`
- `fact_lineups`
- `fact_match_stats`
- `team_match_summary`
- `player_season_summary`
- `discipline_summary`

Use migrations for schema changes once the database layer exists. Do not rely on
manual database edits.

## API Guidance

FastAPI should be read-first initially.

Start with simple endpoints:

- `GET /health`
- `GET /seasons`
- `GET /matches`
- `GET /matches/{match_id}`
- `GET /teams`
- `GET /teams/{team_id}/summary`
- `GET /players`
- `GET /events`
- `GET /officials`

Keep business logic out of route functions when it grows. Use service/query
modules so endpoints remain thin.

## Frontend Guidance

Build the React app as an analytical product, not a marketing site.

Initial pages should likely be:

- League overview.
- Goal timing explorer.
- Discipline dashboard.
- Team profile.
- Match explorer.

The UI should focus on comparison, filtering, and readable football stories.
Avoid generic framework defaults where a more deliberate design is practical.

## Automation Guidance

The current-season update flow should eventually:

1. Fetch the current fixture/results calendar.
2. Identify new or changed matches by `match_id`/URL.
3. Scrape only what is missing or stale.
4. Load updates into Postgres idempotently.
5. Record failed matches with reason and timestamp.
6. Run lightweight validation checks.
7. Expose the updated data to the API/dashboard.

GitHub Actions is the preferred automation path for portfolio visibility.

## AI Agent Rules

- Before coding, check [docs/PROJECT_ROADMAP.md](docs/PROJECT_ROADMAP.md) and
  the current files related to the task.
- Explain work systematically and beginner-consciously. For each implementation
  step, briefly state what is being changed, why it matters, and how to run or
  verify it.
- When introducing new tools such as Postgres, SQLAlchemy, Alembic, FastAPI,
  React, Docker, or GitHub Actions, include short plain-English explanations of
  the concept and how it fits into this project.
- Do not dump unexplained code. Pair meaningful code changes with enough
  explanation for a beginner to follow the design.
- Use comments and docstrings as teaching aids where they clarify important
  project logic, but keep them concise and maintainable.
- Preserve the three-track architecture: data platform, research lab, public
  product.
- Do not collapse production logic into notebooks.
- Do not make the React frontend depend directly on CSV files.
- Do not introduce a different database unless the user explicitly changes the
  decision. The target production database is Postgres.
- Keep changes phase-appropriate and scoped.
- If adding dependencies, update the relevant dependency file and document how
  to run the new component.
- If adding generated artifacts, make sure they belong in the repo before
  committing them.
- Copilot instructions also exist at `.github/copilot-instructions.md`.
