
# UPL Match Intelligence — Mermaid Diagram Collection

Status: **visual system overview / maintained architecture reference**.

Use this file when you need a high-level visual map of the codebase, data
pipeline, database shape, API flow, or scraper lifecycle. Keep it accurate when
code changes affect the architecture, major workflows, endpoints, database
tables, or known gaps.

Current planning home: use [START_HERE.md](START_HERE.md) for the four
continuous development areas and [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md)
for the full documentation index.

---

## Diagram 1 — Detailed Two-Flow Data Pipeline
> Solid lines = primary automated flow. Dashed lines = research/promotion flow.
> ⚠️ marks known gaps or areas worth improving.

```mermaid
flowchart TD

    %% ═══════════════════════════════
    %% EXTERNAL SOURCE
    %% ═══════════════════════════════
    WEB(["🌐 upl.co.ug\nOfficial UPL website"])

    %% ═══════════════════════════════
    %% AUTOMATION TRIGGER
    %% ═══════════════════════════════
    GA["⚙️ GitHub Actions\nweekly trigger\n--season 2025-26"]
    GA -->|"runs"| ORCH

    ORCH["🎛️ update_current_season.py\norchestrator script\nscrape · migrate/load · verify · staging"]

    %% ═══════════════════════════════
    %% STEP 1: SCRAPING
    %% ═══════════════════════════════
    ORCH -->|"step 1"| SCRAPER

    subgraph SCRAPING["PRIMARY ① — Scraping"]
        direction TB
        SCRAPER["⚙️ scrape_upl_matches.py\nScraperClient · RateLimiter\nThreadPoolExecutor x4"]

        CACHE[("📦 data/cache/\nHTML per URL\nMD5-keyed files\nPrevents re-download")]

        SCRAPER <-->|"read/write\ncached HTML"| CACHE

        SCRAPER -->|"success"| CSV
        SCRAPER -->|"failure after retries"| FAILED

        CSV[("📁 data/raw/2025_26/\nmatches · events · lineups\nstaff · officials · stats\n~6 CSV files")]

        FAILED[("📁 upl_failed_matches\n_2025_26.csv\nmatch_url · attempt_count\nlast_error · timestamp")]
    end

    WEB -->|"GET /event/<id>/\nGET /calendar/"| SCRAPER

    NOTE1["⚠️ GAP: Scraper has no\nchange-detection yet.\nRe-scrapes all known URLs\nevery run unless cached.\nFuture: compare match_id\nagainst Postgres first."]
    SCRAPING -.->|"known gap"| NOTE1

    %% ═══════════════════════════════
    %% STEP 2: RAW LOAD
    %% ═══════════════════════════════
    ORCH -->|"step 2"| RAWLOAD

    subgraph RAW_INGESTION["PRIMARY ② — Raw Ingestion"]
        direction TB
        RAWLOAD["📥 load_raw_to_postgres.py\n→ src/db/raw_loader.py\nfor each season:\n  1. delete existing season rows\n  2. read CSV rows\n  3. filter in-season rows only\n  4. fingerprint child table keys\n  5. upsert into raw.*"]

        RAWVERIFY["✅ verify_raw_postgres_counts.py\ncompares CSV row counts\nvs Postgres row counts\nflags mismatches"]

        RAWLOAD --> RAWVERIFY
    end

    CSV -->|"reads"| RAWLOAD
    FAILED -->|"reads"| RAWLOAD

    subgraph PGRAW["🐘 Postgres — raw schema"]
        direction LR
        R1["raw.matches\n1 row per match\nconflict on match_id"]
        R2["raw.events\nconflict on event_row_key\n(SHA-256 fingerprint)"]
        R3["raw.lineups\nraw.staff\nraw.officials\nraw.stats"]
        R4["raw.failed_matches\nconflict on\nfailed_match_row_key"]
    end

    RAWLOAD -->|"upserts"| PGRAW

    NOTE2["⚠️ GAP: raw.* tables have\nno foreign keys between\nmatches and child tables.\nIntegrity is only checked\nin staging validation layer."]
    PGRAW -.->|"known gap"| NOTE2

    %% ═══════════════════════════════
    %% STEP 3: STAGING
    %% ═══════════════════════════════
    ORCH -->|"step 3"| STAGLOAD

    subgraph STAGING_BUILD["PRIMARY ③ — Staging Build"]
        direction TB
        STAGLOAD["🧹 build_staging_from_raw.py\n→ src/db/staging_loader.py\nReads raw.* via SQLAlchemy\nApplies transformations:\n  • normalize_team_name()\n  • _parse_minute() → 8 cols\n  • _extract_man_of_match()\n  • result / winner_team\n  • total_goals · goal_difference\n  • is_goal · is_yellow_card etc\nLogs issues to validation_runs"]

        STAGVERIFY["✅ verify_staging_outputs.py\nspot-checks staging tables:\n  • row counts\n  • null rates on key columns\n  • season coverage"]

        STAGLOAD --> STAGVERIFY
    end

    PGRAW -->|"SELECT * FROM raw.*"| STAGLOAD

    subgraph PGSTAGE["🐘 Postgres — staging schema"]
        direction LR
        S1["staging.matches\n+result · +winner_team\n+total_goals · +goal_difference\n+match_date (Date)"]
        S2["staging.events\n+minute_base/added/total\n+minute_period (0-15…90+)\n+is_goal · is_yellow_card\n+is_red_card · is_substitution\n+team_name (resolved from side)"]
        S3["staging.lineups\nstaging.staff\nstaging.officials\nstaging.stats"]
        S4["staging.validation_runs\nseverity · check_name\nmatch_id · issue_message"]
    end

    STAGLOAD -->|"writes cleaned rows"| PGSTAGE

    subgraph PGANALYTICS["🐘 Postgres — analytics schema"]
        direction LR
        A1["analytics.team_season_summary\nstored team-season rows\nmatches · goals · wins/draws/losses\nrefreshed after staging rebuild"]
    end

    STAGLOAD -->|"refreshes summaries"| PGANALYTICS

    NOTE3["⚠️ GAP: Most reusable metrics\nstill need analytics objects.\nDiscipline, official, home/away,\nand match-drama summaries are\nnot promoted yet."]
    PGANALYTICS -.->|"remaining analytics backlog"| NOTE3

    %% ═══════════════════════════════
    %% SECONDARY: RESEARCH FLOW
    %% ═══════════════════════════════
    subgraph RESEARCH["SECONDARY — Research & Promotion"]
        direction TB
        NB["📓 analysis.ipynb\nExploratory queries\nCharts · stats · hypotheses"]
        RB["📝 research_brief.md\nFootball question defined\nMetric definitions\nCaveats documented"]
        PP["📋 product_plan.md\nPromotion decision\nSQL design\nAPI shape\nReact UI plan"]
        REG["📒 docs/FEATURE_REGISTRY.md\nLifecycle status:\nexperiment → promoted"]

        NB --> RB --> PP --> REG
    end

    PGSTAGE -.->|"read_sql() queries\nstaging.* for exploration"| NB
    PP -.->|"defines query\nfor endpoint"| INSIGHTS

    INSIGHTS["📊 Promoted insight\n/insights/goal-timing\nSQL query over staging.events\nintervals · goals · share · peak\n\n⚠️ GAP: No analytics.* view.\nQuery re-runs on every\nAPI call. Should become\na named view or mat. view."]

    NOTE4["⚠️ GAP: Only 1 insight\npromoted so far (goal timing).\nCard trends, official discipline,\nhome/away advantage etc are\nstill research ideas only."]
    RESEARCH -.->|"backlog"| NOTE4

    %% ═══════════════════════════════
    %% API LAYER
    %% ═══════════════════════════════
    subgraph API["⚡ FastAPI — api/"]
        direction LR
        DIRECT["Read queries\nGET /seasons\nGET /matches\nGET /teams (analytics)\nGET /events\nGET /officials"]
        INS_EP["Insight endpoints\nGET /insights/goal-timing"]
        HEALTH["GET /health\ndb ping\nlatest_staging_completed_at"]
    end

    PGSTAGE -->|"SQL queries\nvia SQLAlchemy"| DIRECT
    PGANALYTICS -->|"precomputed team summaries"| DIRECT
    INSIGHTS -->|"SQL query"| INS_EP
    PGSTAGE -->|"latest run check"| HEALTH

    NOTE5["⚠️ GAP: No pagination\ncursor yet. Limit param\nexists but no next-page\ntoken for large seasons."]
    API -.->|"known gap"| NOTE5

    %% ═══════════════════════════════
    %% FRONTEND
    %% ═══════════════════════════════
    subgraph FRONTEND["⚛️ React — frontend/src/"]
        direction TB
        CLIENT["api/client.ts\napiClient fetch() wrappers\nAPI_BASE_URL from .env"]
        APPSTATE["App.tsx state\nuseEffect #1 → health + seasons\nuseEffect #2 → overview +\n  goalTiming + matches + teams\nloadState: idle/loading/success/error"]
        PANELS["Rendered panels\nLeague Overview\nGoal Timing bar chart\nRecent Matches list\nTeam standings table\nEvent breakdown"]
        FUTURE["🔲 Future pages (disabled)\nMatch Explorer\nDiscipline Dashboard\nTeam Profile"]

        CLIENT --> APPSTATE --> PANELS
        PANELS -.->|"planned"| FUTURE
    end

    DIRECT -->|"JSON :8000"| CLIENT
    INS_EP -->|"JSON :8000"| CLIENT
    HEALTH -->|"JSON :8000"| CLIENT

    NOTE6["⚠️ GAP: All data loaded\nin one App.tsx file.\nNo React Router yet.\nFuture pages need routing\nand code splitting."]
    FRONTEND -.->|"known gap"| NOTE6

    %% ═══════════════════════════════
    %% DEPLOY
    %% ═══════════════════════════════
    RENDER["🚀 Render.com\nFastAPI service\nrender.yaml"]
    SUPABASE["🐘 Supabase Postgres\nraw · staging · analytics · app_meta"]
    API -.->|"deployed to"| RENDER
    RENDER -.->|"reads from"| SUPABASE
    PGRAW -.->|"hosted on"| SUPABASE
    PGSTAGE -.->|"hosted on"| SUPABASE
    PGANALYTICS -.->|"hosted on"| SUPABASE

    %% ═══════════════════════════════
    %% STYLES
    %% ═══════════════════════════════
    classDef primary   fill:#0c4a6e,stroke:#38bdf8,color:#e0f2fe,stroke-width:2px
    classDef rawdb     fill:#064e3b,stroke:#34d399,color:#d1fae5,stroke-width:2px
    classDef stagedb   fill:#14532d,stroke:#4ade80,color:#dcfce7,stroke-width:2px
    classDef research  fill:#431407,stroke:#fb923c,color:#ffedd5,stroke-width:2px
    classDef api       fill:#1e1b4b,stroke:#a78bfa,color:#ede9fe,stroke-width:2px
    classDef frontend  fill:#4a044e,stroke:#e879f9,color:#fae8ff,stroke-width:2px
    classDef warning   fill:#422006,stroke:#f59e0b,color:#fef3c7,stroke-width:1px,stroke-dasharray:4
    classDef infra     fill:#1c1917,stroke:#94a3b8,color:#cbd5e1,stroke-width:1px
    classDef source    fill:#172554,stroke:#93c5fd,color:#dbeafe,stroke-width:3px

    class WEB source
    class SCRAPER,CACHE,CSV,FAILED,RAWLOAD,RAWVERIFY,STAGLOAD,STAGVERIFY,ORCH primary
    class R1,R2,R3,R4 rawdb
    class S1,S2,S3,S4 stagedb
    class NB,RB,PP,REG,INSIGHTS research
    class DIRECT,INS_EP,HEALTH,API api
    class CLIENT,APPSTATE,PANELS,FUTURE frontend
    class NOTE1,NOTE2,NOTE3,NOTE4,NOTE5,NOTE6 warning
    class GA,RENDER,SUPABASE infra
```

---

## Diagram 2 — Database Entity Relationship (ERD)
> Shows how staging tables relate to each other. All child tables share match_id with staging.matches.

```mermaid
erDiagram

    MATCHES {
        int     match_id        PK
        string  match_url
        string  season
        date    match_date
        string  home_team
        string  away_team
        int     home_score
        int     away_score
        int     total_goals
        string  result
        string  winner_team
        string  man_of_the_match
        string  ground_name
    }

    EVENTS {
        string  event_row_key   PK
        int     match_id        FK
        string  season
        int     event_index
        string  event_type
        int     minute_base
        int     minute_added
        int     minute_total
        string  minute_period
        bool    is_added_time
        string  team_side
        string  team_name
        string  player_name
        string  goal_type
        bool    is_goal
        bool    is_yellow_card
        bool    is_red_card
        bool    is_substitution
    }

    LINEUPS {
        string  lineup_row_key  PK
        int     match_id        FK
        string  season
        string  team_name
        string  team_side
        string  squad_role
        int     shirt_number
        string  player_name
        string  player_position
        bool    is_player_of_match
    }

    STAFF {
        string  staff_row_key   PK
        int     match_id        FK
        string  season
        string  team_name
        string  team_side
        string  role
        string  person_name
    }

    OFFICIALS {
        string  official_row_key PK
        int     match_id         FK
        string  season
        string  role
        string  official_name
    }

    STATS {
        string  stat_row_key    PK
        int     match_id        FK
        string  season
        string  statistic_name
        string  home_value
        string  away_value
    }

    VALIDATION_RUNS {
        string  run_id
        string  severity
        string  check_name
        string  table_name
        int     match_id        FK
        string  issue_message
        string  issue_value
    }

    MATCHES ||--o{ EVENTS          : "has timeline events"
    MATCHES ||--o{ LINEUPS         : "has squad"
    MATCHES ||--o{ STAFF           : "has coaching staff"
    MATCHES ||--o{ OFFICIALS       : "has officials"
    MATCHES ||--o{ STATS           : "has match stats"
    MATCHES ||--o{ VALIDATION_RUNS : "logged issues"
```

---

## Diagram 3 — API Request Sequence
> What actually happens between the browser and the database when you open the dashboard.

```mermaid
sequenceDiagram
    actor User
    participant React as React App<br/>(browser)
    participant Client as api/client.ts<br/>fetch()
    participant FastAPI as FastAPI<br/>api/main.py
    participant Router as Router<br/>e.g. seasons.py
    participant PG as Postgres<br/>staging schema

    User->>React: Opens dashboard in browser

    Note over React,PG: Phase 1 — Initial load (parallel)
    React->>Client: loadInitialData()
    Client->>FastAPI: GET /health
    Client->>FastAPI: GET /seasons
    FastAPI->>PG: SELECT version(), current_database()
    FastAPI->>PG: SELECT latest staging run FROM validation_runs
    PG-->>FastAPI: db name + version + timestamp
    FastAPI-->>Client: HealthResponse JSON
    FastAPI->>Router: seasons router
    Router->>PG: SELECT season, COUNT(match_id),<br/>COUNT(DISTINCT team), SUM(total_goals)<br/>FROM staging.matches GROUP BY season
    PG-->>Router: season rows
    Router-->>Client: SeasonResponse[] JSON
    Client-->>React: setData({ health, seasons })
    React->>User: shows season dropdown

    Note over React,PG: Phase 2 — Season selected (5 parallel calls)
    User->>React: selects season "2025_26"
    React->>Client: loadSeasonData("2025_26")

    par all 5 fetch in parallel
        Client->>FastAPI: GET /seasons/2025_26/overview
        and
        Client->>FastAPI: GET /insights/goal-timing?season=2025_26
        and
        Client->>FastAPI: GET /matches?season=2025_26&limit=200
        and
        Client->>FastAPI: GET /teams?season=2025_26
        and
        Client->>FastAPI: GET /events?season=2025_26&limit=200
    end

    FastAPI->>PG: 5 separate SQL queries\nagainst staging.matches,\nstaging.events, staging.lineups
    PG-->>FastAPI: result sets
    FastAPI-->>Client: 5 JSON responses

    Client-->>React: setData({ overview, goalTiming,\nmatches, teams, events })
    React->>User: renders full dashboard
```

---

## Diagram 4 — Scraper Class & State
> The internal structure of the scraper and what can happen to each match URL.

```mermaid
stateDiagram-v2
    direction LR

    [*] --> Discovered : Calendar page fetched,\nmatch URLs extracted

    Discovered --> CacheHit : HTML file exists\nin data/cache/

    Discovered --> Requesting : No cache,\nrate limiter waits

    Requesting --> Fetched : HTTP 200 OK
    Requesting --> Retrying : HTTP 429/5xx\nor network error

    Retrying --> Fetched : Retry succeeded\n(up to 3 attempts)
    Retrying --> Failed : All retries exhausted

    CacheHit --> Parsing : Reads .html from disk
    Fetched --> Cached : Writes .html to disk
    Cached --> Parsing : Passes bytes to\nBeautifulSoup

    Parsing --> Extracted : All 6 table sections\nparsed successfully

    Parsing --> PartiallyExtracted : Some sections missing\n(e.g. no timeline,\nno lineups)

    Extracted --> CheckpointSaved : Every 25 matches\nCSVs flushed to disk
    PartiallyExtracted --> CheckpointSaved : Partial row still saved\nhas_timeline=False etc

    CheckpointSaved --> [*] : Match complete

    Failed --> FailedCSV : Written to\nupl_failed_matches\n_2025_26.csv

    FailedCSV --> [*]

    note right of Retrying
        Retry config:
        SCRAPE_RETRY_ATTEMPTS = 3
        RETRY_BACKOFF_SECONDS = 1.5
        forcelist: 429, 500, 502, 503, 504
    end note

    note right of Requesting
        Rate limiter:
        RATE_LIMIT_SECONDS = 0.75
        MAX_CONCURRENT = 4 threads
    end note
```
