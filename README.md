# UPL Lens

An open-source Uganda Premier League data platform that turns official match
pages into structured data, API access, and a public football intelligence
dashboard.

The project demonstrates a full data-to-product path:

```text
Official UPL website
  -> Python scraper
  -> Postgres raw/staging/analytics schemas
  -> FastAPI
  -> React dashboard
```

The goal is not to mirror the official UPL website. The official site is the
source archive; this project is the analysis layer on top of it.

The product identity is documented in
[docs/PRODUCT_STRATEGY.md](docs/PRODUCT_STRATEGY.md): the public product is now
called **UPL Lens**, an independent football intelligence platform rather than
a fixtures clone or developer-portfolio landing page.

## Live Demo

- Frontend: [UPL Lens](https://upl-lens.pages.dev/)
- App API proxy: [UPL Lens API via Cloudflare](https://upl-lens.pages.dev/api/health)
- Backend API origin: [UPL Lens API on Render](https://upl-match-intelligence-api.onrender.com/)
- API liveness check:
  [`/health/live`](https://upl-match-intelligence-api.onrender.com/health/live)
- API/database health check:
  [`/health`](https://upl-match-intelligence-api.onrender.com/health)

The backend runs on a free Render service, so the first API request after an
idle period can be slow while the service wakes up.

The older Cloudflare Pages URL remains available as a fallback during the
rename transition, but `https://upl-lens.pages.dev/` is the URL to share.

## Intelligence-layer API

The backend now supports routine intelligence modules for the public frontend,
so UPL Lens can show football meaning instead of only archive records.

These endpoints support season trend charts, attack/defence comparison, team
profile signals, match interest scoring, key moments, player contribution
leaderboards, and visible data-quality caveats:

- `GET /trends/seasons`
- `GET /teams/{team_slug}/profile`
- `GET /matches/intelligence`
- `GET /players/leaderboards`
- `GET /teams`
- `GET /matches/{match_id}`
- `GET /players/{player_slug}`
- `GET /overview/intelligence`
- `GET /seasons/overview`

For the current frontend-facing contract, see
[docs/FRONTEND_DESIGN_SYSTEM.md](docs/FRONTEND_DESIGN_SYSTEM.md).

## What It Shows

UPL Lens is built to answer football questions that are difficult
to answer from individual match pages:

- Which teams score or concede most in different match periods?
- Which clubs are most disciplined or card-prone?
- How do cards, lineups, officials, and match events shape outcomes?
- Which teams, players, and matches stand out across seasons?

Highlighted analyses belong in the dashboard and
[research playbook](docs/FEATURE_PROMOTION_WORKFLOW.md) rather than in this README. The first
promoted analysis is the goal-timing explorer, which started as a notebook
finding and now runs through Postgres, FastAPI, and React.

## Current Product

The deployed app currently proves the production path end to end:

- React frontend hosted on Cloudflare Pages.
- FastAPI backend hosted on Render.
- Supabase Postgres database with `raw`, `staging`, `analytics`, and `app_meta`
  schemas.
- Dashboard reads FastAPI JSON, not CSV files or notebook exports.
- Current-season data refresh is automated through GitHub Actions.
- Notebook research can be promoted into API endpoints and dashboard surfaces.

## Technical Highlights

For portfolio and recruiting review, this repository demonstrates:

- **Data engineering**: official-source scraping, raw persistence, idempotent
  loading, and current-season refresh orchestration.
- **Database modeling**: Postgres schemas for raw source data, cleaned staging
  tables, analytics-ready objects, migrations, and least-privilege roles.
- **Validation and operations**: row-count verification, staging validation
  issues, run summaries, logs, artifacts, and escalation rules.
- **Backend development**: read-first FastAPI routes backed by a query/service
  layer under `src/api/`.
- **Frontend development**: React dashboard surfaces for league summaries,
  goal-timing insight, match/team/event data, loading states, and API status.
- **Research workflow**: notebooks, research briefs, product plans, and a
  single research playbook for moving useful analysis into production.
- **Deployment**: Cloudflare Pages, Render, Supabase, GitHub Actions, CORS, and
  environment-based configuration.

## Architecture

```mermaid
flowchart LR
    A["Official UPL website"] --> B["Python scraper"]
    B --> C["Postgres raw/staging/analytics"]
    C --> D["FastAPI"]
    D --> E["React dashboard"]
```

The browser-facing contract is:

```text
React UI -> FastAPI endpoint -> Postgres query/view -> JSON -> chart/table
```

The frontend must not read raw CSV files, notebooks, or exported notebook
images. Research happens in notebooks; production data is served through
Postgres and FastAPI.

Main repository areas:

```text
api/          FastAPI app and routers
database/     SQL migrations, seeds, and permission templates
docs/         roadmap, operations, feature workflow, deployment, and doc map
frontend/     React dashboard
notebooks/    research feature packages
scripts/      scraping, loading, staging, and automation scripts
src/          shared Python modules for scraping, db, API, research, validation
tests/        early pytest coverage for risky logic
```

## Run Locally

For full setup, use [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md).
After configuring `.env` and a local Postgres database, the short version is:

```powershell
# Python dependencies
pip install -r requirements.txt

# Apply database migrations and build trusted tables
python scripts/data_platform/apply_db_migrations.py
python scripts/data_platform/load_raw_to_postgres.py
python scripts/data_platform/build_staging_from_raw.py
python scripts/data_platform/verify_staging_outputs.py

# Run the API
python -m uvicorn api.main:app --reload

# Run the frontend
cd frontend
npm install
npm run dev
```

On this Windows development setup, `.venv\Scripts\python.exe` is the preferred
Python executable once the virtual environment exists.

Run tests with:

```powershell
python -m pytest
```

## Documentation

Use these docs instead of trying to learn the whole repository from the README:

| Need | Start here |
|------|------------|
| First orientation | [docs/START_HERE.md](docs/START_HERE.md) |
| Product identity and strategy | [docs/PRODUCT_STRATEGY.md](docs/PRODUCT_STRATEGY.md) |
| Local setup, common commands, and operations | [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) |
| Visual codebase overview | [docs/diagram_collection.md](docs/diagram_collection.md) |
| Which doc to open | [docs/START_HERE.md](docs/START_HERE.md) |
| Roadmap and current priorities | [docs/PROJECT_ROADMAP.md](docs/PROJECT_ROADMAP.md) |
| Notebook-to-product feature workflow | [docs/FEATURE_PROMOTION_WORKFLOW.md](docs/FEATURE_PROMOTION_WORKFLOW.md) |
| Research ideas, feature status, and promotion rules | [docs/FEATURE_PROMOTION_WORKFLOW.md](docs/FEATURE_PROMOTION_WORKFLOW.md) |
| Frontend, API contract, UX requests, and approved design rules | [docs/FRONTEND_DESIGN_SYSTEM.md](docs/FRONTEND_DESIGN_SYSTEM.md) |

## Data Note

Raw and processed data files are not committed to this repository. The scraper
and pipeline are included so the methodology can be inspected and rerun against
the official UPL website for analytical purposes.

## Author

**Humphrey Nyanzi**  
Sports Scientist & Data Analyst  
[GitHub](https://github.com/humphrey-nyanzi) ·
[Substack](https://humphreyn-substack.com) · [X](https://x.com/phreyn)
