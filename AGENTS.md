# AGENTS.md - UPL Lens (repo-level guidance)

## Project Direction

This repository contains the **UPL Lens** data platform, research lab, API, and
frontend. It began as a UPL goal-timing / UPL Match Intelligence project, but
the unified project and product name is now **UPL Lens**.

Keep historical operational and research context where it explains current
decisions; current frontend design and launch direction should follow the UPL
Lens frontend docs (see `docs/FRONTEND_DESIGN_SYSTEM.md`).

The long-term goal is to collect official UPL match data, store it in Postgres,
clean and model it for analysis, expose it through a FastAPI backend, and present
the best insights in a React web app. Notebooks remain the research lab where new
questions are explored before they become dashboard features.

Use [docs/START_HERE.md](docs/START_HERE.md) as the first orientation document,
[docs/PRODUCT_STRATEGY.md](docs/PRODUCT_STRATEGY.md) as the product identity
and positioning reference, and [docs/PROJECT_ROADMAP.md](docs/PROJECT_ROADMAP.md)
as the main planning reference. The old launch phases are historical context;
new work should be planned through the four continuous development areas.

## Current State

- `scripts/data_platform/scrape_upl_matches.py` is the scraper command
  entrypoint; the implementation lives under `src/scraping/upl/`.
- Current raw tables include `matches`, `events`, `lineups`, `staff`,
  `officials`, `stats`, and `failed_matches`.
- Staging rebuild code lives under `src/db/staging/`, with
  `src/db/staging_loader.py` kept as a compatibility facade.
- API query logic lives under `src/api/query_services/`, with
  `src/api/queries.py` kept as a compatibility facade.
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
structure only when the current area of work needs it.

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
- Run the current-season refresh: `python scripts/data_platform/update_current_season.py --season 2025-26 --skip-migrations`
- Run tests: `python -m pytest`
- Run the FastAPI dev server: `python -m uvicorn api.main:app --reload`
- Build the React frontend: from `frontend/`, run `npm run build`
- Open notebooks from `notebooks/features/feature_01_goal_timing/` for the pilot analysis.

Use `.venv\Scripts\python.exe` instead of `python` when working inside the local
Windows virtual environment.

For a fuller local setup, command, verification, and troubleshooting guide, use
[docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md).

The pytest suite is still early. Validate changes by running the relevant test,
script, notebook, API endpoint, or frontend page end to end.

## Continuous Development Areas

Use these areas for planning, review, and scoping:

1. **Data Reliability & Operations** - scraper behavior, Postgres, staging
   validation, automation, deployment health, logs, tests, and escalation.
2. **Research & Football Intelligence** - notebooks, football questions,
   feature packages, metric definitions, caveats, and promotion decisions.
3. **Product Experience** - FastAPI endpoints, query/service logic, React pages,
   UI/UX, filters, tables, charts, and browser-facing states.
4. **Developer Experience & Documentation** - onboarding, setup instructions,
   command guides, troubleshooting, repo conventions, and documentation
   navigation.

Keep changes area-appropriate and scoped. Do not jump from a documentation,
research, or data-reliability task into unrelated product UI work unless the
user explicitly changes the scope.

## Feature Promotion Workflow

Research & Football Intelligence notebook experiments should use the feature
package workflow documented in
[docs/FEATURE_PROMOTION_WORKFLOW.md](docs/FEATURE_PROMOTION_WORKFLOW.md).
That document also owns notebook data-source rules, feature lifecycle tracking,
research backlog notes, and the decision guide for when stable notebook metrics
should become `analytics.*` views.

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

When creating a feature package, add it to the feature table in
`docs/FEATURE_PROMOTION_WORKFLOW.md` and update its lifecycle status as it moves
from research to promotion.

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

The durable product definition lives in
[docs/PRODUCT_STRATEGY.md](docs/PRODUCT_STRATEGY.md). Treat the app as an
independent UPL football intelligence platform: curated insight first, deeper
analytical exploration second, and technical portfolio value quietly supporting
the product rather than leading the user experience.

Use the source-record boundary consistently:

```text
Official UPL site = source record.
UPL Lens = analytical meaning.
```

Do not rebuild official match pages, fixtures, lineups, officials lists, or raw
timelines unless the product adds a clear analytical layer. For raw source
details that are not yet transformed, prefer compact summaries and links back
to the official UPL source. Match-detail surfaces should be Match Intelligence
Briefs, not official match-report clones.

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

For staging work, use Postgres `raw.*` as the input for cleaning. Do not make
the staging pipeline read raw CSV files directly; CSV-to-Postgres protection
happens in the raw ingestion layer.

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

- Before coding, check [docs/START_HERE.md](docs/START_HERE.md),
  [docs/PRODUCT_STRATEGY.md](docs/PRODUCT_STRATEGY.md),
  [docs/PROJECT_ROADMAP.md](docs/PROJECT_ROADMAP.md), the relevant document
  from the seven-doc structure, and the current files related to the task. For
  frontend, API contract, page-requirement, wireframe, or UX-request work, use
  [docs/FRONTEND_DESIGN_SYSTEM.md](docs/FRONTEND_DESIGN_SYSTEM.md).
- When creating, editing, consolidating, deleting, or relying on repository
  documentation, consult and follow the installed `docs-steward` skill. Keep
  docs current with code, commands, API contracts, workflows, diagrams, and
  agent instructions.
- When the user provides a GitHub Issue number or asks for issue-based work,
  read the Issue, comments, labels, milestone, Project, checklist, and acceptance criteria before
  changing files. Report progress against the Issue and leave important Issue
  closure and release approval to the project owner unless explicitly told
  otherwise.
- For meaningful Issue or Project work, create or use an Issue-specific branch
  such as `codex/issue-8-red-card-research`. Do not push directly to `main`.
  Commit scoped work to the branch, push it, and open a draft Pull Request by
  default. Link the Issue, list verification, and do not merge unless explicitly
  instructed.
- When opening a PR from an Issue, copy the Issue's relevant area/type/priority
  labels, assign the same milestone, add the PR to the same GitHub Project, and
  set the PR status to `status: needs-review` only when the Issue checklist and
  acceptance criteria are complete. Use `Closes #<issue-number>` in the PR body
  so the Issue closes automatically after the owner-reviewed PR is merged.
- If useful work is discovered outside the Issue scope, do not silently expand
  the PR. Add a PR comment or create a follow-up Issue so the owner can decide
  whether it belongs in a later milestone.
- For small, clear, low-risk fixes such as typos, broken links, tiny copy
  changes, or obvious one-file doc/config corrections, a GitHub Issue is
  optional. Still use a branch and PR for code, docs, config, or deployment
  changes unless the owner explicitly says otherwise.
- If a direct user request is meaningful, risky, multi-step, unclear, tied to a
  milestone, likely to need follow-up, or useful for another agent to resume,
  create or request a GitHub Issue before implementation.
- Keep PRs in draft while the linked Issue checklist, acceptance criteria, PR
  template, or verification evidence is incomplete. Mark or request ready for
  review only after the in-scope checklist is complete.
- Include PR testing evidence: local command output, browser notes, Cloudflare
  preview URL, endpoint check, or a short reason that the item is not
  applicable.
- After merge, delete short-lived work branches unless the owner explicitly
  wants to preserve an experimental branch. Avoid long-lived fixed branches for
  routine feature or agent work.
- GitHub network operations such as `gh issue`, `gh pr`, `gh project`,
  `git push`, and creating remote branches may require running outside the
  sandbox with approval. Use escalation for those operations when needed, while
  keeping local file edits scoped to the workspace and avoiding unrelated files.
- When doing frontend work, consult and follow the installed
  `build-web-apps:frontend-app-builder`, `impeccable`, `tufte-viz`, and
  `upl-react-doctor` skills
  as applicable. Use `frontend-app-builder` for new frontend surfaces or
  redesigns, `impeccable` for UI shaping, audit, and polish passes, and
  `tufte-viz` for chart and data-visualization choices. Use
  `upl-react-doctor` when running React Doctor, improving its score, or
  reevaluating older React patterns in `frontend/`.
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
- Keep changes area-appropriate and scoped.
- If adding dependencies, update the relevant dependency file and document how
  to run the new component.
- If adding generated artifacts, make sure they belong in the repo before
  committing them.
- If a change affects architecture, major workflows, endpoints, database tables,
  deployment shape, or known gaps, check whether
  [docs/diagram_collection.md](docs/diagram_collection.md) needs an update.
- Copilot instructions also exist at `.github/copilot-instructions.md`.
- Shared production frontend URL: `https://upl-lens.pages.dev/`. The older
  Cloudflare Pages URL may remain live as a fallback during the rename
  transition, but do not present it as the primary product URL.
