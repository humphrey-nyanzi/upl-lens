# Phase 7 Deployment Plan

Status: **historical deployment decision record**.

Current planning home: use [START_HERE.md](START_HERE.md) for the four
continuous development areas, [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) for
current priorities, and [PHASE7_DEPLOYMENT_RUNBOOK.md](PHASE7_DEPLOYMENT_RUNBOOK.md)
for the practical deployment steps.

This document is the Phase 7 deployment decision record for UPL Match
Intelligence. It does not deploy anything by itself. Its job is to choose a
practical, low-cost architecture before implementation starts.

## Phase 7 Goal

Phase 7 should make the project understandable, professional, and usable outside
the local machine.

The target production request flow stays the same:

```text
React UI -> FastAPI endpoint -> Postgres query/view -> JSON -> chart/table
```

The frontend must not read CSV files, notebooks, or exported notebook images.
Notebooks remain the research lab. Postgres remains the production database.

## Current Architecture

The project currently has four deployable or operational parts.

| Part | Current local shape | Deployment need |
|------|---------------------|-----------------|
| React frontend | Vite app in `frontend/` | Static hosting with `VITE_API_BASE_URL` pointing at the hosted API |
| FastAPI backend | `api/main.py` with routers under `api/routers/` | Python web service that runs `uvicorn api.main:app` |
| Postgres database | `raw.*`, `staging.*`, and `analytics.*` schemas through migrations | Hosted Postgres with enough storage, SSL, and external access for API plus automation |
| Current-season automation | `.github/workflows/current-season-update.yml` | Keep GitHub Actions, connect it to hosted Postgres through secrets |

The backend reads from cleaned Postgres tables through domain query modules under
`src/api/query_services/`, with `src/api/queries.py` kept as a compatibility
facade for older imports. Route handlers are intentionally thin. Database
settings are loaded from:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_SSLMODE
```

The frontend reads its API host from:

```text
VITE_API_BASE_URL
```

One important readiness gap: `api/main.py` currently allows only local Vite
origins in CORS. Before a hosted frontend can call the hosted API from a browser,
the API needs a production CORS configuration.

## Deployment Requirements

A good Phase 7 architecture needs to support:

- A fast static React dashboard.
- A public FastAPI backend.
- A hosted Postgres database with SSL.
- GitHub Actions updating hosted Postgres on a schedule.
- Environment variables and secrets in the right places.
- A free subdomain first, with a clean custom-domain path later.
- Beginner-readable setup notes for reviewers and future contributors.

## Current Free-Tier Reality

Hosting free tiers change often, so this plan was checked against official docs
and pricing pages on May 21, 2026.

### Frontend Hosting Options

| Option | Free-tier notes | Fit for this project |
|--------|-----------------|----------------------|
| Cloudflare Pages | Free plan supports 500 builds per month and custom domains, with static sites served globally. | Strong fit. Very fast static hosting and pairs naturally with Cloudflare DNS/domain later. |
| Vercel | Hobby is free for personal projects, includes automatic CI/CD, CDN, custom domains, and generous static/frontend limits. | Strong fit. Very easy Vite deploy and strong portfolio familiarity. |
| Netlify | Free plan includes custom domains, SSL, deploy previews, global CDN, and a monthly credit limit. | Strong fit. Good developer experience, but the newer credit model is a little harder to explain to beginners. |
| Render static site | Static sites can be free, but Render is more compelling for the backend than the frontend here. | Fine, but not the best first choice. |
| GitHub Pages | Free static hosting for public repos. | Possible, but weaker for modern app environment management and preview workflows. |

Frontend conclusion: use Cloudflare Pages or Vercel. Both keep the React app
fast even if the backend sleeps, because static files are served from an edge
network or CDN.

### Backend Hosting Options

| Option | Free-tier notes | Fit for this project |
|--------|-----------------|----------------------|
| Render free web service | Supports Python/FastAPI web services. Free services spin down after 15 minutes without inbound traffic and may take about a minute to spin back up. | Best first backend choice if zero-budget matters. Cold starts are real, but setup is straightforward. |
| Koyeb free web service | One free web service with 512 MB RAM, 0.1 vCPU, 2 GB SSD, and scale-to-zero after 1 hour of no traffic. | Worth considering. Less common in portfolios than Render, but the free shape is reasonable for a small API. |
| Railway | Free trial gives a one-time $5 credit for up to 30 days, then the Free plan gives $1 credit/month. Hobby is $5/month. | Pleasant platform, but not a durable zero-budget backend. |
| Fly.io | Current docs say there is no free account/free tier for new customers; all organizations require a credit card. | Strong platform, but not the right zero-budget first move. |
| Serverless functions | Vercel/Netlify functions can run Python-style endpoints in some setups, but this repo is a conventional FastAPI app with Postgres connections and scheduled data jobs. | Avoid for first deployment. It would add adaptation work without solving the core project goal. |

Backend conclusion: Render is the least painful first backend deployment.
Koyeb is the backup if Render's cold-start behavior or limits feel worse after
testing.

### Postgres Hosting Options

| Option | Free-tier notes | Fit for this project |
|--------|-----------------|----------------------|
| Supabase | Free plan includes a dedicated Postgres database, 500 MB database size, 5 GB egress plus 5 GB cached egress, and up to 2 active free projects; free projects pause after 1 week of inactivity. | Best first database choice for this repo because Phase 5 docs already discuss Supabase pooler and loader-role patterns. |
| Neon | Free plan includes 0.5 GB storage per project, 100 compute-hours per month per project, scale-to-zero after inactivity, pooled connections, and branching. | Also excellent. Better developer database ergonomics in some ways, but the existing project docs already lean Supabase. |
| Render Postgres | Free Postgres has 1 GB storage but expires after 30 days and has no backups. | Not suitable for a professional portfolio database. Good only for temporary experiments. |
| Railway Postgres | Easy if already using Railway, but durable use usually pushes toward paid usage. | Not ideal for near-zero-budget production. |
| Koyeb Postgres | Free database exists, but official docs list only 5 hours of active time per month and 1 GB storage. | Too constrained for this project's hosted database. |

Database conclusion: use Supabase first. Neon is the strongest alternative if
Supabase pausing or pooler behavior becomes painful.

## Recommended Architecture

Recommended first Phase 7 architecture:

```text
Cloudflare Pages or Vercel
  hosts React static frontend
  VITE_API_BASE_URL=https://<api-service>.onrender.com

Render Free Web Service
  hosts FastAPI backend
  runs uvicorn api.main:app --host 0.0.0.0 --port $PORT
  reads POSTGRES_* environment variables

Supabase Free Postgres
  stores raw.*, staging.*, analytics.*, and app_meta.*
  uses admin credentials only for setup/migrations
  uses least-privilege loader credentials for routine refreshes

GitHub Actions
  keeps current-season update workflow
  uses POSTGRES_* repository secrets for the Supabase loader role
```

My recommended frontend choice is **Cloudflare Pages** if the priority is the
cleanest long-term domain and DNS story. Choose **Vercel** instead if the
priority is the most familiar portfolio deployment brand and the simplest Vite
import flow.

My recommended backend choice is **Render Free Web Service** for the first
public API. The tradeoff is cold start. A reviewer may see the first API request
take around a minute if the service has slept. The React app should handle this
with a calm loading/error state and possibly a visible API status indicator.

My recommended database choice is **Supabase Free Postgres**. The tradeoff is
the 500 MB size limit and free-project pausing after inactivity. The current UPL
dataset should be small enough for the first deployment, but the database size
must be watched as more seasons, lineups, stats, and analytics objects grow.

## Cheapest Professional Architecture

The cheapest professional first version is:

```text
Cloudflare Pages free frontend
Render free FastAPI backend
Supabase free Postgres
GitHub Actions in a public repository
Free platform subdomains first
```

Expected monthly cost: `0 USD`, excluding a future custom domain.

This is professional enough for a portfolio demo if the documentation clearly
states that the backend is on a free service and can cold-start.

## Least Painful Architecture

The least painful architecture is:

```text
Vercel frontend
Render backend
Supabase Postgres
GitHub Actions
```

Vercel and Render both have straightforward Git-driven deploy flows, and
Supabase gives a clear dashboard for inspecting Postgres tables and connection
strings.

The only reason this is not the default recommendation is domain strategy:
Cloudflare Pages plus Cloudflare DNS is slightly cleaner if the project is
already planning for a serious custom domain.

## Most Reliable Free-Tier Architecture

No truly reliable production architecture is free. Free backends and free
databases usually sleep, pause, throttle, or have limited support.

Within that reality, the most reliable free-tier shape is:

```text
Cloudflare Pages or Vercel static frontend
Koyeb or Render sleeping backend
Neon or Supabase sleeping/pausable Postgres
GitHub Actions scheduled refresh
```

The frontend will remain fast. The backend and database are the parts most
likely to cold-start or pause.

## Domain Strategy

Do not buy a domain before the first deployment works on free subdomains.

Recommended order:

1. Deploy on free provider subdomains:
   - frontend: `*.pages.dev` or `*.vercel.app`
   - backend: `*.onrender.com`
   - database: Supabase hosted Postgres
2. Verify the whole public flow end to end.
3. Pick a short, credible domain only after the app is worth sharing.
4. Use Cloudflare DNS even if the domain is bought elsewhere.
5. Prefer Cloudflare Registrar when the desired TLD is supported, because
   Cloudflare sells and renews domains at registry/ICANN cost with no markup.

Possible naming directions to evaluate later:

- `uplmatchintelligence.com`
- `uplintelligence.com`
- `ugandaleagueinsights.com`
- `upldata.org`

Domain cost is unavoidable. A `.com` or `.org` usually has an annual fee, and
prices vary by TLD and registrar. Avoid expensive novelty TLDs until the project
has a clear audience.

## Environment Variables And Secrets

Use separate secret stores for separate jobs.

Frontend host:

```text
VITE_API_BASE_URL=https://<hosted-api-domain>
```

Backend host:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_SSLMODE
ALLOWED_ORIGINS
```

`ALLOWED_ORIGINS` is a comma-separated list. Keep the local Vite origins for
development and add the hosted frontend URL before deploying the public app.

GitHub Actions repository secrets:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_SSLMODE
```

Use different database users where possible:

- Admin or owner credential: manual migrations and setup only.
- `upl_actions_loader`: scheduled current-season refresh.
- Optional read-only role: notebooks and public read contexts.
- `upl_api_reader`: deployed FastAPI backend reads from `staging.*` and
  `analytics.*` without write permissions.

Do not put real database passwords in `.env.example`, docs, screenshots, or chat.

## Database Setup Strategy

The hosted database should be created manually at first, then managed through
the existing migration scripts.

Recommended first database path:

1. Create a Supabase project.
2. Apply `database/migrations/*.sql` from a trusted admin connection.
3. Create the least-privilege loader role using
   `database/permissions/001_create_upl_actions_loader.sql`.
4. Create the read-only API role using
   `database/permissions/003_create_upl_api_reader.sql`.
5. Load existing raw season CSVs into hosted Postgres from a local trusted
   machine.
6. Rebuild `staging.*`.
7. Verify with `scripts/data_platform/verify_raw_postgres_counts.py` and
   `scripts/data_platform/verify_staging_outputs.py`.
8. Point FastAPI and GitHub Actions to the hosted database.

This keeps schema changes versioned and avoids manual database edits becoming
the hidden source of truth.

## Automation Strategy

Keep GitHub Actions.

The current workflow already matches the deployment architecture:

```text
GitHub Actions
  -> live UPL scrape
  -> raw CSV files in the runner
  -> hosted Postgres raw.*
  -> hosted Postgres staging.*
  -> validation logs and artifacts
```

For routine scheduled runs:

```text
season_scope=current
run_type=routine-refresh
apply_migrations=false
use_cache=false
force_full_scrape=false
```

That means the weekly job updates data rows but does not change schema.

For migrations:

- Run migrations manually during setup, or trigger a manual workflow run only
  while using admin-capable secrets.
- Switch back to the loader role after migration work.

GitHub Actions is a good portfolio signal because reviewers can see the data
platform being maintained, not just a static demo.

## Risks And Tradeoffs

| Risk | Why it matters | Mitigation |
|------|----------------|------------|
| Backend cold start | Render free web services sleep after idle time. First API load may be slow. | Make frontend loading/error states clear. Document free-tier behavior. Upgrade backend later if traffic matters. |
| Database pause or storage limit | Supabase free projects can pause after inactivity and have a 500 MB database limit. | Monitor size. Keep hosted data lean. Move to Neon or paid Supabase if needed. |
| CORS must include the hosted frontend | Browsers will block the hosted React app if its origin is missing from `ALLOWED_ORIGINS`. | Add the final frontend URL to the backend environment before public deployment. |
| Browser extensions can block the API | Privacy/ad-blocking extensions can block requests to the hosted Render API and report `net::ERR_BLOCKED_BY_CLIENT`. | Verify in guest/private profiles, then disable or allow-list blocking extensions such as Ghostery. |
| Secrets sprawl | API, Actions, and admin setup need different credentials. | Use least-privilege roles and document exactly where each secret lives. |
| Render free filesystem is ephemeral | Local files disappear across redeploys or sleep. | Do not store data in the backend filesystem. Keep Postgres as durable storage and Actions artifacts for logs/raw files. |
| Source-site scraping can fail | UPL source pages may time out or change HTML. | Keep failed-match artifacts and validation logs from GitHub Actions. |
| Free-tier terms can change | Hosting providers change limits and pricing. | Re-check official docs before implementing or committing to a domain. |

## Recommendation Summary

Start with this:

```text
Frontend: Cloudflare Pages
Backend: Render Free Web Service
Database: Supabase Free Postgres
Automation: GitHub Actions
Domain: free subdomains first, Cloudflare-managed custom domain later
```

This is the best balance of zero-budget, professional presentation, low setup
pain, and long-term credibility.

Phase 7 used this recommended architecture. The deployed URLs are:

```text
Frontend: https://upl-match-intelligence.pages.dev/
Backend: https://upl-match-intelligence-api.onrender.com/
Liveness: https://upl-match-intelligence-api.onrender.com/health/live
Readiness: https://upl-match-intelligence-api.onrender.com/health
```

If implementation testing shows Supabase pausing or pooler behavior is painful,
switch the database recommendation to Neon before public launch. If Render cold
starts feel too rough, test Koyeb as the backend alternative before paying for a
backend.

## First Implementation Slice After Approval

After this plan is approved, the first narrow implementation slice should be:

1. Add production CORS configuration to FastAPI with an `ALLOWED_ORIGINS`
   environment variable. **Completed as the first Phase 7 implementation step.**
2. Add a minimal Render deploy note or config for the FastAPI service.
   **Completed: `render.yaml` and `requirements-api.txt` now define the API
   service build/start path.**
3. Add a frontend deployment note for Cloudflare Pages or Vercel, including
   `VITE_API_BASE_URL`. **Completed in `docs/PHASE7_DEPLOYMENT_RUNBOOK.md`.**
4. Update `.env.example` and `frontend/.env.example` only with non-secret
   placeholders. **Completed.**
5. Run local verification:
   - `.venv\Scripts\python.exe -m compileall api src scripts`
   - `cd frontend`
   - `npm run build`
   **Completed during Phase 7 implementation.**

The essential Phase 7 deployment is complete. Optional follow-up work now belongs
to product polish, custom domains, monitoring, or future paid infrastructure
decisions rather than the initial deployment milestone.

## Official Sources Checked

- [Cloudflare Pages limits](https://developers.cloudflare.com/pages/platform/limits/)
- [Cloudflare Pages custom domains](https://developers.cloudflare.com/pages/configuration/custom-domains/)
- [Cloudflare Registrar overview](https://developers.cloudflare.com/registrar/)
- [Vercel pricing](https://vercel.com/pricing)
- [Vercel Hobby plan](https://vercel.com/docs/accounts/plans/hobby)
- [Netlify pricing](https://www.netlify.com/pricing/)
- [Render free services](https://render.com/free)
- [Render web services](https://render.com/docs/web-services/)
- [Render Postgres free limits](https://render.com/free)
- [Supabase pricing](https://supabase.com/pricing)
- [Neon pricing](https://neon.com/pricing)
- [Railway free trial](https://docs.railway.com/pricing/free-trial)
- [Railway pricing plans](https://docs.railway.com/reference/pricing/plans)
- [Fly.io pricing](https://fly.io/docs/about/pricing/)
- [Fly.io cost management](https://fly.io/docs/about/cost-management/)
- [Koyeb instances](https://www.koyeb.com/docs/reference/instances)
- [Koyeb database services](https://www.koyeb.com/docs/databases)
- [GitHub Actions billing and usage](https://docs.github.com/en/actions/administering-github-actions/usage-limits-billing-and-administration)
- [GitHub Actions secrets reference](https://docs.github.com/en/actions/reference/security/secrets)
- [GitHub Actions secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
