# Phase 7 Deployment Runbook

Status: **deployment runbook / historical launch-phase reference**.

Current planning home: use [START_HERE.md](START_HERE.md) for the four
continuous development areas, [OPERATIONS.md](OPERATIONS.md) for operational
health and escalation, and [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md) for the
original deployment decision record.

This runbook turns the Phase 7 architecture decision into careful manual steps.
It is intentionally written for a human operator. Do not paste secrets,
passwords, connection strings, or API keys into chat or committed files.

## Current Recommendation

```text
React frontend: Cloudflare Pages first choice, Vercel acceptable alternative
FastAPI backend: Render free web service
Database: existing Supabase Postgres project
Automation: existing GitHub Actions workflow
```

The deployed data path remains:

```text
React UI -> FastAPI endpoint -> Supabase Postgres query/view -> JSON -> chart/table
```

## Deployment Order

Deploy in this order:

1. Confirm Supabase roles and connection details.
2. Deploy FastAPI to Render.
3. Confirm the hosted API can reach Supabase.
4. Deploy the React frontend.
5. Add the final frontend URL to the API `ALLOWED_ORIGINS`.
6. Verify the public app end to end.
7. Attach a custom domain later, after the free-subdomain deployment works.

Do not deploy the frontend first. The frontend needs the hosted API URL for
`VITE_API_BASE_URL`.

## Supabase Checklist

The existing Supabase project already supports Phase 5 automation. For Phase 7,
it also needs a read-only API role:

```text
upl_api_reader
```

That role should be created from:

```text
database/permissions/003_create_upl_api_reader.sql
```

Use this role for the deployed FastAPI service. Do not use the owner/admin role
for the public API.

### Supabase Values Needed Later

When creating the Render service, you will need these values from Supabase:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_SSLMODE
```

Use the `upl_api_reader` password for `POSTGRES_PASSWORD`.

For Supabase pooler connections, the user value may need the project reference
suffix:

```text
upl_api_reader.<project-ref>
```

The role inside Postgres is still just:

```text
upl_api_reader
```

If a direct connection is used instead of the pooler, the user may be simply:

```text
upl_api_reader
```

Use SSL in production:

```text
POSTGRES_SSLMODE=require
```

## Render Backend Setup

The repo now includes:

```text
render.yaml
requirements-api.txt
```

The Render service should use:

```text
Build command: pip install -r requirements-api.txt
Start command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
Health check path: /health/live
```

The hosted API should expose:

```text
GET /health/live
GET /health
GET /seasons
GET /insights/goal-timing?season=2025_26
```

Current Phase 7 Render API URL:

```text
https://upl-match-intelligence-api.onrender.com
```

Use `/health/live` for Render's service health check. Use `/health` when you
want to confirm the API can connect to Supabase.

### Render Environment Variables

Set these in Render:

```text
POSTGRES_HOST=<from Supabase>
POSTGRES_PORT=<from Supabase>
POSTGRES_DB=<from Supabase>
POSTGRES_USER=<upl_api_reader or upl_api_reader.<project-ref>>
POSTGRES_PASSWORD=<saved privately>
POSTGRES_SSLMODE=require
ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

At first, `ALLOWED_ORIGINS` only needs the local origins. After the frontend is
deployed, add the hosted frontend URL too.

Example after frontend deployment:

```text
ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173,https://your-frontend.pages.dev
```

Current Phase 7 hosted CORS value:

```text
ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173,https://upl-match-intelligence.pages.dev
```

## Cloudflare Pages Frontend Setup

The frontend lives in:

```text
frontend/
```

Cloudflare Pages should use:

```text
Root directory: frontend
Build command: npm run build
Build output directory: dist
```

Set this frontend environment variable:

```text
VITE_API_BASE_URL=https://<your-render-api>.onrender.com
```

The exact Render URL is only known after the API service exists.

Current Phase 7 Cloudflare Pages frontend URL:

```text
https://upl-match-intelligence.pages.dev
```

Current Phase 7 status:

```text
Essential deployment complete.
Chrome, Edge, and Brave verified after disabling the browser extension that was
blocking hosted API requests in the default profiles.
```

## Vercel Frontend Alternative

If using Vercel instead of Cloudflare Pages:

```text
Root directory: frontend
Build command: npm run build
Output directory: dist
```

Set:

```text
VITE_API_BASE_URL=https://<your-render-api>.onrender.com
```

## Verification Checklist

After the backend is deployed, check:

```text
https://<your-render-api>.onrender.com/health/live
https://<your-render-api>.onrender.com/health
https://<your-render-api>.onrender.com/seasons
https://<your-render-api>.onrender.com/insights/goal-timing?season=2025_26
```

Expected meaning:

- `/health/live` proves the FastAPI process is running.
- `/health` proves FastAPI can connect to Supabase.
- `/seasons` proves the API can read cleaned staging match data.
- `/insights/goal-timing` proves the promoted goal-timing feature works from the
  hosted database.

After the frontend is deployed:

1. Open the hosted frontend URL.
2. Confirm the League Overview loads real seasons.
3. Confirm Goal Timing Explorer loads data.
4. Confirm the browser console has no CORS errors.
5. If there is a CORS error, add the exact frontend origin to Render's
   `ALLOWED_ORIGINS` and redeploy/restart the API service.

## Known Free-Tier Tradeoffs

- Render free backend services can sleep when idle. The first API request may be
  slow.
- Supabase free projects have storage and inactivity limits.
- The frontend should still load quickly because static hosting is separate from
  the sleeping API.
- Do not treat this as final production infrastructure. Treat it as a polished,
  honest portfolio deployment.

## Browser Troubleshooting

If the public frontend loads but shows the API as offline, first open the API
directly:

```text
https://upl-match-intelligence-api.onrender.com/health/live
```

If that URL works but the frontend request fails with:

```text
net::ERR_BLOCKED_BY_CLIENT
```

the request is being blocked by the browser, an extension, browser privacy
settings, DNS filtering, antivirus web protection, or another client-side
filter. That is different from a CORS failure.

During the first Phase 7 verification pass, Ghostery was confirmed as the
extension blocking the Render API request in default Edge and Brave profiles.
Guest/private profiles worked because the blocking extension was not active
there.

Useful checks:

- Try an InPrivate/incognito window with extensions disabled.
- Disable ad blockers, privacy extensions, and site-injection extensions. Test
  Ghostery first if it is installed.
- Clear site data for `upl-match-intelligence.pages.dev` and
  `upl-match-intelligence-api.onrender.com`.
- Add exceptions for both:
  - `https://upl-match-intelligence.pages.dev`
  - `https://upl-match-intelligence-api.onrender.com`
- If a browser blocks the request but another browser works, keep the deployment
  marked healthy and treat it as a local browser configuration issue.
