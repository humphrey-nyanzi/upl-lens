import { useEffect, useMemo, useState } from "react";

import { API_BASE_URL, apiClient } from "./api/client";
import type {
  GoalTimingInsightResponse,
  HealthResponse,
  MatchSummary,
  SeasonOverviewResponse,
  SeasonResponse,
  TeamResponse,
} from "./api/types";

type LoadState = "idle" | "loading" | "success" | "error";
type PageKey = "overview" | "goal-timing" | "matches" | "teams" | "methodology";

type DashboardData = {
  health: HealthResponse | null;
  seasons: SeasonResponse[];
  overview: SeasonOverviewResponse | null;
  goalTiming: GoalTimingInsightResponse | null;
  matches: MatchSummary[];
  teams: TeamResponse[];
};

type PageDefinition = {
  key: PageKey;
  label: string;
  shortLabel: string;
};

type PageProps = {
  apiOnline: boolean;
  data: DashboardData;
  errorMessage: string;
  loadState: LoadState;
  onPageChange: (page: PageKey) => void;
  onRefresh: () => void;
  onSeasonChange: (season: string) => void;
  overview: SeasonOverviewResponse | null;
  selectedSeason: string;
  selectedSeasonInfo: SeasonResponse | undefined;
  goalTiming: GoalTimingInsightResponse | null;
};

const pages: PageDefinition[] = [
  { key: "overview", label: "League Overview", shortLabel: "Overview" },
  { key: "goal-timing", label: "Goal Timing", shortLabel: "Goals" },
  { key: "matches", label: "Match Explorer", shortLabel: "Matches" },
  { key: "teams", label: "Team Insights", shortLabel: "Teams" },
  { key: "methodology", label: "Data Notes", shortLabel: "Notes" },
];

function parsePageHash(): PageKey {
  const value = window.location.hash.replace(/^#\/?/, "");
  return pages.some((page) => page.key === value) ? (value as PageKey) : "overview";
}

function formatSeason(season: string) {
  return season.replace("_", "/");
}

function formatDate(value: string | null) {
  if (!value) return "Date TBC";
  const dateValue = value.includes("T") ? value : `${value}T00:00:00`;
  return new Intl.DateTimeFormat("en", { day: "2-digit", month: "short", year: "numeric" }).format(
    new Date(dateValue),
  );
}

function formatResult(result: string | null) {
  if (result === "home_win") return "Home win";
  if (result === "away_win") return "Away win";
  if (result === "draw") return "Draw";
  return "Result pending";
}

function formatPercent(value: number) {
  return `${Math.round(value * 1000) / 10}%`;
}

function matchStatus(match: MatchSummary) {
  if (match.is_forfeit) return "Forfeit";
  return formatResult(match.result);
}

function App() {
  const [currentPage, setCurrentPage] = useState<PageKey>(parsePageHash);
  const [data, setData] = useState<DashboardData>({
    health: null,
    seasons: [],
    overview: null,
    goalTiming: null,
    matches: [],
    teams: [],
  });
  const [selectedSeason, setSelectedSeason] = useState("");
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    function syncPageFromHash() {
      setCurrentPage(parsePageHash());
    }

    window.addEventListener("hashchange", syncPageFromHash);
    return () => window.removeEventListener("hashchange", syncPageFromHash);
  }, []);

  useEffect(() => {
    let ignore = false;

    async function loadInitialData() {
      setLoadState("loading");
      setErrorMessage("");

      try {
        const [health, seasons] = await Promise.all([apiClient.getHealth(), apiClient.getSeasons()]);
        const defaultSeason = seasons.at(-1)?.season ?? "";

        if (!ignore) {
          setData((current) => ({ ...current, health, seasons }));
          setSelectedSeason(defaultSeason);
        }
      } catch (error) {
        if (!ignore) {
          setLoadState("error");
          setErrorMessage(error instanceof Error ? error.message : "The data service could not be reached.");
        }
      }
    }

    loadInitialData();

    return () => {
      ignore = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedSeason) return;

    let ignore = false;

    async function loadSeasonData() {
      setLoadState("loading");
      setErrorMessage("");

      try {
        const [overview, goalTiming, matches, teams] = await Promise.all([
          apiClient.getSeasonOverview(selectedSeason),
          apiClient.getGoalTimingInsight(selectedSeason),
          apiClient.getMatches(selectedSeason, 200),
          apiClient.getTeams(selectedSeason, 200),
        ]);

        if (!ignore) {
          setData((current) => ({ ...current, overview, goalTiming, matches, teams }));
          setLoadState("success");
        }
      } catch (error) {
        if (!ignore) {
          setLoadState("error");
          setErrorMessage(error instanceof Error ? error.message : "Season data could not be loaded.");
        }
      }
    }

    loadSeasonData();

    return () => {
      ignore = true;
    };
  }, [selectedSeason]);

  const selectedSeasonInfo = data.seasons.find((season) => season.season === selectedSeason);
  const overview = data.overview?.season === selectedSeason ? data.overview : null;
  const goalTiming = data.goalTiming?.season === selectedSeason ? data.goalTiming : null;
  const apiOnline = data.health?.status === "ok" && data.health.database === "ok";

  function setPage(page: PageKey) {
    window.location.hash = `/${page}`;
    setCurrentPage(page);
  }

  function refreshSeason() {
    if (!selectedSeason) return;

    setLoadState("loading");
    void Promise.all([
      apiClient.getHealth().then((health) => setData((current) => ({ ...current, health }))),
      apiClient
        .getSeasonOverview(selectedSeason)
        .then((seasonOverview) => setData((current) => ({ ...current, overview: seasonOverview }))),
      apiClient
        .getGoalTimingInsight(selectedSeason)
        .then((seasonGoalTiming) => setData((current) => ({ ...current, goalTiming: seasonGoalTiming }))),
      apiClient.getMatches(selectedSeason, 200).then((matches) => setData((current) => ({ ...current, matches }))),
      apiClient.getTeams(selectedSeason, 200).then((teams) => setData((current) => ({ ...current, teams }))),
    ])
      .then(() => setLoadState("success"))
      .catch((error) => {
        setLoadState("error");
        setErrorMessage(error instanceof Error ? error.message : "Refresh failed.");
      });
  }

  const pageProps: PageProps = {
    apiOnline,
    data,
    errorMessage,
    goalTiming,
    loadState,
    onPageChange: setPage,
    onRefresh: refreshSeason,
    onSeasonChange: setSelectedSeason,
    overview,
    selectedSeason,
    selectedSeasonInfo,
  };

  return (
    <main className="app-shell">
      <TopNavigation apiOnline={apiOnline} currentPage={currentPage} onPageChange={setPage} />
      <section className="workspace" aria-live={loadState === "loading" ? "polite" : "off"}>
        {currentPage === "overview" ? <OverviewPage {...pageProps} /> : null}
        {currentPage === "goal-timing" ? <GoalTimingPage {...pageProps} /> : null}
        {currentPage === "matches" ? <MatchExplorerPage {...pageProps} /> : null}
        {currentPage === "teams" ? <TeamInsightsPage {...pageProps} /> : null}
        {currentPage === "methodology" ? <MethodologyPage {...pageProps} /> : null}
      </section>
    </main>
  );
}

function TopNavigation({
  apiOnline,
  currentPage,
  onPageChange,
}: {
  apiOnline: boolean;
  currentPage: PageKey;
  onPageChange: (page: PageKey) => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);

  function choosePage(page: PageKey) {
    onPageChange(page);
    setMenuOpen(false);
  }

  return (
    <header className="top-nav">
      <button className="brand-lockup" type="button" onClick={() => choosePage("overview")} aria-label="UPL Match Intelligence home">
        <span className="brand-mark">UPL</span>
        <span>
          <span className="brand-title">Match Intelligence</span>
          <span className="brand-subtitle">Football data observatory</span>
        </span>
      </button>

      <button
        className="menu-button"
        type="button"
        aria-controls="primary-navigation"
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen((open) => !open)}
      >
        <span className="menu-icon" aria-hidden="true" />
        Menu
      </button>

      <nav className={menuOpen ? "nav-list open" : "nav-list"} id="primary-navigation" aria-label="Product sections">
        {pages.map((page) => (
          <button
            className={page.key === currentPage ? "nav-item active" : "nav-item"}
            key={page.key}
            type="button"
            aria-current={page.key === currentPage ? "page" : undefined}
            onClick={() => choosePage(page.key)}
          >
            {page.label}
          </button>
        ))}
      </nav>

      <div className="api-pill" aria-label={apiOnline ? "Data is ready" : "Data is still loading"}>
        <span className={apiOnline ? "status-dot online" : "status-dot offline"} />
        <span>{apiOnline ? "Data ready" : "Loading data"}</span>
      </div>
    </header>
  );
}

function OverviewPage({
  apiOnline,
  data,
  errorMessage,
  goalTiming,
  loadState,
  onPageChange,
  onRefresh,
  onSeasonChange,
  overview,
  selectedSeason,
  selectedSeasonInfo,
}: PageProps) {
  const initialLoading = loadState === "loading" && overview === null;

  const summaryCards = [
    {
      label: "Matches covered",
      value: overview?.match_count ?? selectedSeasonInfo?.match_count ?? data.matches.length,
      detail: "Cleaned match records available for the selected season.",
    },
    {
      label: "Timeline goals",
      value: overview?.timeline_goal_count ?? overview?.goal_count ?? 0,
      detail: "Goals recorded from match event timelines.",
    },
    {
      label: "Teams tracked",
      value: overview?.team_count ?? selectedSeasonInfo?.team_count ?? data.teams.length,
      detail: "Distinct clubs appearing in official match pages.",
    },
    {
      label: "Cards logged",
      value: overview ? overview.yellow_card_count + overview.red_card_count : 0,
      detail: "Cards available for future discipline analysis.",
    },
  ];

  const eventBreakdown = useMemo(() => {
    return (
      overview?.event_breakdown.map((item) => ({
        eventType: item.event_type,
        label: item.label,
        count: item.count,
      })) ?? []
    );
  }, [overview]);

  const topTeams = useMemo(() => {
    return [...data.teams]
      .sort((left, right) => right.wins - left.wins || right.goals_for - left.goals_for)
      .slice(0, 5);
  }, [data.teams]);

  const recentMatches = useMemo(() => {
    return [...data.matches]
      .sort((left, right) => {
        const leftDate = left.match_date ?? "";
        const rightDate = right.match_date ?? "";
        return rightDate.localeCompare(leftDate) || right.match_id - left.match_id;
      })
      .slice(0, 4);
  }, [data.matches]);

  if (initialLoading) {
    return <OverviewSkeleton />;
  }

  return (
    <>
      <HeroSection
        apiOnline={apiOnline}
        seasons={data.seasons}
        selectedSeason={selectedSeason}
        selectedSeasonInfo={selectedSeasonInfo}
        overview={overview}
        loadState={loadState}
        onSeasonChange={onSeasonChange}
        onRefresh={onRefresh}
        onPageChange={onPageChange}
      />

      {loadState === "error" ? <ErrorPanel errorMessage={errorMessage} /> : null}

      <section className="metric-grid" aria-label="Selected season intelligence summary">
        {summaryCards.map((card) => (
          <MetricCard key={card.label} {...card} />
        ))}
      </section>

      <FeaturedInsight goalTiming={goalTiming} loadState={loadState} onPageChange={onPageChange} />

      <section className="overview-grid" aria-label="League patterns preview">
        <TeamSignalPanel teams={topTeams} loadState={loadState} />
        <EventSignalPanel eventBreakdown={eventBreakdown} />
      </section>

      <ExplorePreview onPageChange={onPageChange} />

      <section className="overview-grid" aria-label="Recent matches and data notes">
        <RecentMatchPanel matches={recentMatches} loadState={loadState} />
        <OverviewDataNote onPageChange={onPageChange} selectedSeasonInfo={selectedSeasonInfo} overview={overview} />
      </section>
    </>
  );
}

function HeroSection({
  apiOnline,
  seasons,
  selectedSeason,
  selectedSeasonInfo,
  overview,
  loadState,
  onSeasonChange,
  onRefresh,
  onPageChange,
}: {
  apiOnline: boolean;
  seasons: SeasonResponse[];
  selectedSeason: string;
  selectedSeasonInfo: SeasonResponse | undefined;
  overview: SeasonOverviewResponse | null;
  loadState: LoadState;
  onSeasonChange: (season: string) => void;
  onRefresh: () => void;
  onPageChange: (page: PageKey) => void;
}) {
  const dateRange = selectedSeasonInfo
    ? `${formatDate(overview?.first_match_date ?? selectedSeasonInfo.first_match_date)} to ${formatDate(
        overview?.latest_match_date ?? selectedSeasonInfo.last_match_date,
      )}`
    : "Date range unavailable";

  return (
    <section className="hero-panel" aria-labelledby="page-title">
      <div className="hero-copy">
        <p className="eyebrow">Uganda Premier League data, made analytical</p>
        <h1 id="page-title">UPL Match Intelligence</h1>
        <p className="hero-text">
          Understand the league through statistical signals from official match data, beyond ordinary fixtures,
          results, and tables.
        </p>
      </div>

      <SeasonControls
        seasons={seasons}
        selectedSeason={selectedSeason}
        loadState={loadState}
        onRefresh={onRefresh}
        onSeasonChange={onSeasonChange}
        variant="hero"
      />

      <div className="status-strip" aria-label="Data freshness and availability">
        <StatusItem label="Selected season" value={selectedSeason ? formatSeason(selectedSeason) : "No season loaded"} />
        <StatusItem label="Coverage window" value={dateRange} />
        <div>
          <span>Data status</span>
          <strong>{apiOnline ? "Ready for analysis" : "Loading latest data"}</strong>
          <button className="text-link inverse" type="button" onClick={() => onPageChange("methodology")}>
            How this data is collected
          </button>
        </div>
      </div>
    </section>
  );
}

function SeasonControls({
  seasons,
  selectedSeason,
  loadState,
  onRefresh,
  onSeasonChange,
  variant = "default",
}: {
  seasons: SeasonResponse[];
  selectedSeason: string;
  loadState: LoadState;
  onRefresh: () => void;
  onSeasonChange: (season: string) => void;
  variant?: "default" | "hero";
}) {
  return (
    <div className={variant === "hero" ? "season-controls hero-controls" : "season-controls"} aria-label="Season controls">
      <label>
        Season
        <select value={selectedSeason} onChange={(event) => onSeasonChange(event.target.value)} disabled={seasons.length === 0}>
          {seasons.map((season) => (
            <option value={season.season} key={season.season}>
              {formatSeason(season.season)}
            </option>
          ))}
        </select>
      </label>
      <button type="button" onClick={onRefresh} disabled={!selectedSeason || loadState === "loading"}>
        {loadState === "loading" ? "Refreshing" : "Refresh"}
      </button>
    </div>
  );
}

function GoalTimingPage({
  data,
  goalTiming,
  loadState,
  onRefresh,
  onSeasonChange,
  selectedSeason,
}: PageProps) {
  const peakInterval = goalTiming?.intervals.find((interval) => interval.rank === 1);
  const secondHalfGoals =
    goalTiming?.intervals
      .filter((interval) => interval.start_minute >= 46)
      .reduce((total, interval) => total + interval.goals, 0) ?? 0;
  const secondHalfShare = goalTiming && goalTiming.total_regular_time_goals > 0 ? secondHalfGoals / goalTiming.total_regular_time_goals : 0;

  return (
    <>
      <PageIntro
        eyebrow="Featured insight"
        title="Goal Timing"
        text="A fan-facing look at when UPL goals arrive, built from the first validated notebook insight promoted into the app."
      >
        <SeasonControls
          seasons={data.seasons}
          selectedSeason={selectedSeason}
          loadState={loadState}
          onRefresh={onRefresh}
          onSeasonChange={onSeasonChange}
        />
      </PageIntro>

      {loadState === "loading" && !goalTiming ? <GoalTimingSkeleton /> : null}

      {goalTiming ? (
        <>
          <section className="feature-story">
            <div>
              <p className="eyebrow">Main finding</p>
              <h2>Goals cluster most in the {goalTiming.peak_interval ?? "available"} window.</h2>
              <p>
                The available regular-time event data shows {goalTiming.total_regular_time_goals.toLocaleString()} goals for
                this season. The strongest period accounts for{" "}
                {peakInterval ? `${peakInterval.goals.toLocaleString()} goals (${formatPercent(peakInterval.share)})` : "the clearest share"}.
              </p>
            </div>
            <div className="insight-stat">
              <span>Second-half share</span>
              <strong>{formatPercent(secondHalfShare)}</strong>
              <p>{secondHalfGoals.toLocaleString()} regular-time goals came after halftime.</p>
            </div>
          </section>

          <section className="featured-insight">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Explore the timing</p>
                <h2>Regular-time goals by 15-minute period</h2>
                <p>Each bar shows a readable period comparison. The peak period is highlighted and also labelled in text.</p>
              </div>
            </div>
            <GoalTimingChart goalTiming={goalTiming} />
          </section>

          <section className="overview-grid">
            <section className="panel">
              <div className="section-heading compact">
                <div>
                  <h2>How to read this</h2>
                  <p>
                    This is a period trend, not a tactical claim. It helps show when goals appear in the available match
                    timelines, then gives us a base for deeper team and match questions later.
                  </p>
                </div>
              </div>
            </section>
            <section className="panel">
              <div className="section-heading compact">
                <div>
                  <h2>Worth noting</h2>
                  <p>
                    Added-time goals are excluded from this comparison, and the chart only uses goals available in the
                    cleaned event timeline.
                  </p>
                </div>
              </div>
            </section>
          </section>
        </>
      ) : null}
    </>
  );
}

function MatchExplorerPage({ data, loadState, onPageChange }: PageProps) {
  const recentMatches = [...data.matches]
    .sort((left, right) => (right.match_date ?? "").localeCompare(left.match_date ?? "") || right.match_id - left.match_id)
    .slice(0, 8);

  return (
    <>
      <PageIntro
        eyebrow="Explore matches"
        title="Match Explorer"
        text="A dedicated home for browsing scorelines, venues, match days, and event evidence. Search and filters will grow here without crowding the overview."
      />
      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Recent matches</h2>
            <p>This first page shell uses the existing match data while fuller filters are prepared.</p>
          </div>
          <button className="text-button" type="button" onClick={() => onPageChange("methodology")}>
            View data notes
          </button>
        </div>
        <div className="match-list">
          {recentMatches.length > 0 ? (
            recentMatches.map((match) => <MatchRow key={match.match_id} match={match} />)
          ) : (
            <EmptyState message={loadState === "loading" ? "Loading recent matches." : "No matches returned for this season yet."} />
          )}
        </div>
      </section>
    </>
  );
}

function TeamInsightsPage({ data, loadState }: PageProps) {
  const teams = [...data.teams].sort((left, right) => right.wins - left.wins || right.goals_for - left.goals_for);

  return (
    <>
      <PageIntro
        eyebrow="Team trends"
        title="Team Insights"
        text="A clean destination for team summaries and future comparison work, without turning the overview into a league-table clone."
      />
      <section className="panel">
        <div className="section-heading compact">
          <div>
            <h2>Current team summaries</h2>
            <p>Wins, draws, losses, goals for, and goals against from cleaned match data.</p>
          </div>
        </div>
        <div className="team-grid">
          {teams.length > 0 ? (
            teams.map((team) => <TeamCard key={team.team_name} team={team} />)
          ) : (
            <EmptyState message={loadState === "loading" ? "Loading team summaries." : "No team summaries returned yet."} />
          )}
        </div>
      </section>
    </>
  );
}

function MethodologyPage({ apiOnline, data, overview, selectedSeasonInfo }: PageProps) {
  return (
    <>
      <PageIntro
        eyebrow="Data notes"
        title="Methodology and freshness"
        text="The app is built from official UPL match pages. This page keeps source, freshness, and limitations visible without crowding the football overview."
      />
      <section className="overview-grid">
        <section className="panel">
          <div className="section-heading compact">
            <div>
              <h2>How the data is collected</h2>
              <p>
                Official UPL match pages are collected, cleaned into Postgres, checked for structural issues, then served
                through FastAPI to the React app.
              </p>
            </div>
          </div>
          <div className="trust-list">
            <StatusItem label="Source" value="Official UPL match pages" />
            <StatusItem label="App data path" value="Postgres to FastAPI to React" />
            <StatusItem label="Current status" value={apiOnline ? "Data service ready" : "Data service loading"} />
          </div>
        </section>

        <section className="panel">
          <div className="section-heading compact">
            <div>
              <h2>Freshness and coverage</h2>
              <p>These details help readers judge how recent and complete the current season view is.</p>
            </div>
          </div>
          <div className="trust-list">
            <StatusItem
              label="Last checked"
              value={data.health?.latest_staging_completed_at ? formatDate(data.health.latest_staging_completed_at) : "Unknown"}
            />
            <StatusItem
              label="Season window"
              value={
                selectedSeasonInfo
                  ? `${formatDate(overview?.first_match_date ?? selectedSeasonInfo.first_match_date)} to ${formatDate(
                      overview?.latest_match_date ?? selectedSeasonInfo.last_match_date,
                    )}`
                  : "Unavailable"
              }
            />
            <StatusItem
              label="Scoreline goals"
              value={overview?.scoreline_goal_count != null ? overview.scoreline_goal_count.toLocaleString() : "Unavailable"}
            />
          </div>
        </section>
      </section>

      <section className="panel">
        <div className="section-heading compact">
          <div>
            <h2>Known limitations</h2>
            <p>
              Scraped source data can be incomplete or change structure. Public numbers should be read with caveats when
              event timelines are missing, seasons are unusual, or validation finds a source anomaly.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}

function PageIntro({
  children,
  eyebrow,
  text,
  title,
}: {
  children?: React.ReactNode;
  eyebrow: string;
  text: string;
  title: string;
}) {
  return (
    <section className="page-intro">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p>{text}</p>
      </div>
      {children}
    </section>
  );
}

function FeaturedInsight({
  goalTiming,
  loadState,
  onPageChange,
}: {
  goalTiming: GoalTimingInsightResponse | null;
  loadState: LoadState;
  onPageChange: (page: PageKey) => void;
}) {
  return (
    <section className="featured-insight" aria-labelledby="featured-insight-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Featured insight</p>
          <h2 id="featured-insight-title">When do UPL goals arrive?</h2>
          <p>
            The current flagship insight compares regular-time scoring windows and points readers toward the periods that
            shape a season.
          </p>
        </div>
        <button className="text-button dark" type="button" onClick={() => onPageChange("goal-timing")}>
          Open Goal Timing
        </button>
      </div>

      {goalTiming ? (
        <div className="insight-layout">
          <div className="insight-stat">
            <span>Peak scoring window</span>
            <strong>{goalTiming.peak_interval ?? "Unavailable"}</strong>
            <p>{goalTiming.total_regular_time_goals.toLocaleString()} regular-time goals counted.</p>
          </div>
          <GoalTimingChart goalTiming={goalTiming} />
          <p className="caveat">Data note: added-time goals are excluded from this period comparison.</p>
        </div>
      ) : (
        <EmptyState message={loadState === "loading" ? "Loading the goal timing insight." : "No goal timing insight returned yet."} />
      )}
    </section>
  );
}

function GoalTimingChart({ goalTiming }: { goalTiming: GoalTimingInsightResponse }) {
  const maxGoals = Math.max(...goalTiming.intervals.map((interval) => interval.goals), 1);

  return (
    <div className="goal-timing-chart" aria-label="Regular-time goals by 15-minute interval">
      {goalTiming.intervals.map((interval) => {
        const width = `${Math.max((interval.goals / maxGoals) * 100, interval.goals > 0 ? 8 : 0)}%`;

        return (
          <div className="goal-timing-row" key={interval.interval}>
            <span>{interval.interval}</span>
            <div className="goal-timing-bar-track">
              <div className={interval.rank === 1 ? "goal-timing-bar peak" : "goal-timing-bar"} style={{ width }} />
            </div>
            <strong>
              {interval.goals.toLocaleString()} ({formatPercent(interval.share)})
            </strong>
          </div>
        );
      })}
    </div>
  );
}

function TeamSignalPanel({ teams, loadState }: { teams: TeamResponse[]; loadState: LoadState }) {
  return (
    <section className="panel">
      <div className="section-heading compact">
        <div>
          <h2>Team trends</h2>
          <p>Quick summaries from cleaned match records.</p>
        </div>
      </div>
      <div className="team-list">
        {teams.length > 0 ? (
          teams.map((team) => <TeamCard key={team.team_name} team={team} />)
        ) : (
          <EmptyState message={loadState === "loading" ? "Loading team summaries." : "No team summaries returned yet."} />
        )}
      </div>
    </section>
  );
}

function TeamCard({ team }: { team: TeamResponse }) {
  return (
    <article className="team-card">
      <strong>{team.team_name}</strong>
      <span>
        {team.wins}W {team.draws}D {team.losses}L
      </span>
      <p>
        {team.goals_for} scored, {team.goals_against} conceded across {team.matches_played} matches.
      </p>
    </article>
  );
}

function EventSignalPanel({ eventBreakdown }: { eventBreakdown: Array<{ eventType: string; label: string; count: number }> }) {
  return (
    <section className="panel">
      <div className="section-heading compact">
        <div>
          <h2>Event coverage</h2>
          <p>Timeline signals available for the selected season.</p>
        </div>
      </div>
      <div className="breakdown-list">
        {eventBreakdown.length > 0 ? (
          eventBreakdown.slice(0, 6).map((item) => (
            <div className="breakdown-row" key={item.eventType}>
              <span>{item.label}</span>
              <strong>{item.count.toLocaleString()}</strong>
            </div>
          ))
        ) : (
          <EmptyState message="No event totals returned for this season yet." />
        )}
      </div>
    </section>
  );
}

function ExplorePreview({ onPageChange }: { onPageChange: (page: PageKey) => void }) {
  const exploreCards = [
    {
      page: "goal-timing" as PageKey,
      status: "Available",
      title: "Goal Timing",
      description: "Read the main scoring-window insight and inspect the period chart.",
    },
    {
      page: "matches" as PageKey,
      status: "Coming soon",
      title: "Match Explorer",
      description: "Browse matches and event evidence as the explorer grows.",
    },
    {
      page: "teams" as PageKey,
      status: "Available",
      title: "Team Trends",
      description: "Scan team records and scoring summaries from cleaned match data.",
    },
    {
      page: "methodology" as PageKey,
      status: "Data notes",
      title: "How It Works",
      description: "See source, freshness, and limitations behind the numbers.",
    },
  ];

  return (
    <section className="explore-panel" aria-labelledby="explore-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Explore more</p>
          <h2 id="explore-title">Choose your next question</h2>
          <p>Start with the insight, then move into matches, teams, and data notes when you need more context.</p>
        </div>
      </div>
      <div className="explore-grid">
        {exploreCards.map((card) => (
          <button className="explore-card" key={card.title} type="button" onClick={() => onPageChange(card.page)}>
            <span>{card.status}</span>
            <strong>{card.title}</strong>
            <p>{card.description}</p>
          </button>
        ))}
      </div>
    </section>
  );
}

function RecentMatchPanel({ matches, loadState }: { matches: MatchSummary[]; loadState: LoadState }) {
  return (
    <section className="panel">
      <div className="section-heading compact">
        <div>
          <h2>Recent matches</h2>
          <p>Latest scorelines for context around the season view.</p>
        </div>
      </div>
      <div className="match-list">
        {matches.length > 0 ? (
          matches.map((match) => <MatchRow key={match.match_id} match={match} />)
        ) : (
          <EmptyState message={loadState === "loading" ? "Loading recent matches." : "No matches returned for this season yet."} />
        )}
      </div>
    </section>
  );
}

function MatchRow({ match }: { match: MatchSummary }) {
  return (
    <article className="match-row">
      <div>
        <span>{formatDate(match.match_date)}</span>
        <strong>
          {match.home_team ?? "Home team TBC"} vs {match.away_team ?? "Away team TBC"}
        </strong>
      </div>
      <div className="score-block">
        <strong>
          {match.home_score ?? "-"}:{match.away_score ?? "-"}
        </strong>
        <span>{matchStatus(match)}</span>
      </div>
    </article>
  );
}

function OverviewDataNote({
  onPageChange,
  selectedSeasonInfo,
  overview,
}: {
  onPageChange: (page: PageKey) => void;
  selectedSeasonInfo: SeasonResponse | undefined;
  overview: SeasonOverviewResponse | null;
}) {
  return (
    <section className="panel">
      <div className="section-heading compact">
        <div>
          <h2>Data note</h2>
          <p>
            This view uses official UPL match data. The selected season currently covers{" "}
            {selectedSeasonInfo
              ? `${formatDate(overview?.first_match_date ?? selectedSeasonInfo.first_match_date)} to ${formatDate(
                  overview?.latest_match_date ?? selectedSeasonInfo.last_match_date,
                )}`
              : "the available match window"}
            .
          </p>
        </div>
      </div>
      <button className="text-button" type="button" onClick={() => onPageChange("methodology")}>
        Read data notes
      </button>
    </section>
  );
}

function ErrorPanel({ errorMessage }: { errorMessage: string }) {
  return (
    <section className="error-panel" role="alert">
      <h2>The data service is not returning data yet</h2>
      <p>{errorMessage}</p>
      <p>
        The hosted service may still be waking up. Check that the API is reachable at {API_BASE_URL}. If this only
        happens in one browser profile, a privacy or ad-blocking extension may be blocking the request.
      </p>
    </section>
  );
}

function StatusItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function MetricCard({ label, value, detail }: { label: string; value: number; detail: string }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value.toLocaleString()}</strong>
      <p>{detail}</p>
    </article>
  );
}

function EmptyState({ message }: { message: string }) {
  return <p className="empty-state">{message}</p>;
}

function OverviewSkeleton() {
  return (
    <>
      <section className="hero-panel skeleton-panel" aria-busy="true" aria-label="Loading league overview">
        <div className="skeleton-line short" />
        <div className="skeleton-line title" />
        <div className="skeleton-line" />
        <div className="skeleton-line medium" />
      </section>
      <section className="metric-grid" aria-label="Loading summary cards">
        {[0, 1, 2, 3].map((item) => (
          <article className="metric-card skeleton-card" key={item}>
            <div className="skeleton-line short" />
            <div className="skeleton-line number" />
            <div className="skeleton-line" />
          </article>
        ))}
      </section>
      <section className="featured-insight skeleton-card">
        <div className="skeleton-line short" />
        <div className="skeleton-line title" />
        <div className="skeleton-line" />
        <p className="empty-state">Loading the latest league data. The service may be waking up.</p>
      </section>
    </>
  );
}

function GoalTimingSkeleton() {
  return (
    <section className="featured-insight skeleton-card" aria-busy="true" aria-label="Loading goal timing">
      <div className="skeleton-line short" />
      <div className="skeleton-line title" />
      <div className="skeleton-line" />
      <div className="skeleton-line medium" />
    </section>
  );
}

export default App;
