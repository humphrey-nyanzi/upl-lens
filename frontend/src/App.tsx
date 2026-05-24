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

type DashboardData = {
  health: HealthResponse | null;
  seasons: SeasonResponse[];
  overview: SeasonOverviewResponse | null;
  goalTiming: GoalTimingInsightResponse | null;
  matches: MatchSummary[];
  teams: TeamResponse[];
};

type ExploreArea = {
  title: string;
  status: string;
  description: string;
};

const exploreAreas: ExploreArea[] = [
  {
    title: "Goal Timing Explorer",
    status: "Live insight",
    description: "See when regular-time goals arrive and which match periods shape the season.",
  },
  {
    title: "Match/Event Explorer",
    status: "Next product slice",
    description: "Browse fixtures, scorelines, venues, and event evidence once the explorer is built out.",
  },
  {
    title: "Team Analytical Summaries",
    status: "Preview data live",
    description: "Compare early team records from cleaned match data without pretending this is a table clone.",
  },
  {
    title: "Discipline Dashboard",
    status: "Research-led",
    description: "Card trends will wait for validated football questions and clear caveats.",
  },
];

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

function matchStatus(match: MatchSummary) {
  if (match.is_forfeit) return "Forfeit";
  return formatResult(match.result);
}

function formatPercent(value: number) {
  return `${Math.round(value * 1000) / 10}%`;
}

function App() {
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
          setErrorMessage(error instanceof Error ? error.message : "The API could not be reached.");
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

  const summaryCards = [
    {
      label: "Matches covered",
      value: overview?.match_count ?? selectedSeasonInfo?.match_count ?? data.matches.length,
      detail: "Cleaned match records available for the selected season.",
    },
    {
      label: "Timeline goals",
      value: overview?.timeline_goal_count ?? overview?.goal_count ?? 0,
      detail: "Goals recorded from event timelines, not just copied from scorelines.",
    },
    {
      label: "Teams tracked",
      value: overview?.team_count ?? selectedSeasonInfo?.team_count ?? data.teams.length,
      detail: "Distinct clubs appearing in official match pages.",
    },
    {
      label: "Cards logged",
      value: overview ? overview.yellow_card_count + overview.red_card_count : 0,
      detail: "Yellow and red cards available for future discipline analysis.",
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

  return (
    <main className="app-shell">
      <TopNavigation apiOnline={apiOnline} />

      <section className="workspace" id="overview">
        <HeroSection
          apiOnline={apiOnline}
          seasons={data.seasons}
          selectedSeason={selectedSeason}
          selectedSeasonInfo={selectedSeasonInfo}
          overview={overview}
          loadState={loadState}
          onSeasonChange={setSelectedSeason}
          onRefresh={refreshSeason}
        />

        {loadState === "error" ? <ErrorPanel errorMessage={errorMessage} /> : null}

        <section className="metric-grid" aria-label="Selected season intelligence summary">
          {summaryCards.map((card) => (
            <MetricCard key={card.label} {...card} />
          ))}
        </section>

        <FeaturedInsight goalTiming={goalTiming} loadState={loadState} />

        <section className="overview-grid" aria-label="League evidence preview">
          <TeamSignalPanel teams={topTeams} loadState={loadState} />
          <EventSignalPanel eventBreakdown={eventBreakdown} />
        </section>

        <ExplorePreview />

        <section className="overview-grid" aria-label="Recent match evidence and methodology">
          <RecentMatchPanel matches={recentMatches} loadState={loadState} />
          <TrustPanel health={data.health} selectedSeasonInfo={selectedSeasonInfo} overview={overview} />
        </section>
      </section>
    </main>
  );
}

function TopNavigation({ apiOnline }: { apiOnline: boolean }) {
  return (
    <header className="top-nav">
      <a className="brand-lockup" href="#overview" aria-label="UPL Match Intelligence home">
        <span className="brand-mark">UPL</span>
        <span>
          <span className="brand-title">Match Intelligence</span>
          <span className="brand-subtitle">Football data observatory</span>
        </span>
      </a>

      <nav className="nav-list" aria-label="Product sections">
        <a className="nav-item active" href="#overview">
          Overview
        </a>
        <a className="nav-item" href="#featured-insight">
          Goal timing
        </a>
        <a className="nav-item" href="#explore">
          Explore
        </a>
        <a className="nav-item" href="#methodology">
          Methodology
        </a>
      </nav>

      <div className="api-pill" aria-label={apiOnline ? "API and database connected" : "API connection pending"}>
        <span className={apiOnline ? "status-dot online" : "status-dot offline"} />
        <span>{apiOnline ? "Data live" : "Checking data"}</span>
      </div>
    </header>
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
}: {
  apiOnline: boolean;
  seasons: SeasonResponse[];
  selectedSeason: string;
  selectedSeasonInfo: SeasonResponse | undefined;
  overview: SeasonOverviewResponse | null;
  loadState: LoadState;
  onSeasonChange: (season: string) => void;
  onRefresh: () => void;
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
          Understand the league through curated statistical signals from official match data, beyond ordinary
          fixtures, results, and tables.
        </p>
      </div>

      <div className="hero-controls" aria-label="Season and data controls">
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

      <div className="status-strip" aria-label="Data freshness and availability">
        <StatusItem label="Selected season" value={selectedSeason ? formatSeason(selectedSeason) : "No season loaded"} />
        <StatusItem label="Coverage window" value={dateRange} />
        <StatusItem label="Data status" value={apiOnline ? "API and database ready" : "Waiting for data"} />
      </div>
    </section>
  );
}

function ErrorPanel({ errorMessage }: { errorMessage: string }) {
  return (
    <section className="error-panel" role="alert">
      <h2>FastAPI is not returning data yet</h2>
      <p>{errorMessage}</p>
      <p>
        Check that the API is reachable at {API_BASE_URL}. If this only happens in one browser profile, disable
        privacy or ad-blocking extensions for this site and refresh.
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

function FeaturedInsight({
  goalTiming,
  loadState,
}: {
  goalTiming: GoalTimingInsightResponse | null;
  loadState: LoadState;
}) {
  const maxGoals = Math.max(...(goalTiming?.intervals.map((interval) => interval.goals) ?? [0]), 1);

  return (
    <section className="featured-insight" id="featured-insight" aria-labelledby="featured-insight-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Featured insight</p>
          <h2 id="featured-insight-title">When do UPL goals arrive?</h2>
          <p>
            Goal Timing is the first notebook-backed analysis promoted into the public product. It focuses on
            regular-time goals so stoppage-time noise does not distort the period comparison.
          </p>
        </div>
        <a href="#explore">Dig deeper</a>
      </div>

      {goalTiming ? (
        <div className="insight-layout">
          <div className="insight-stat">
            <span>Peak scoring window</span>
            <strong>{goalTiming.peak_interval ?? "Unavailable"}</strong>
            <p>{goalTiming.total_regular_time_goals.toLocaleString()} regular-time goals counted for this insight.</p>
          </div>

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

          <p className="caveat">
            Caveat: this preview excludes added-time goals and only counts goals available in the cleaned event timeline.
          </p>
        </div>
      ) : (
        <EmptyState message={loadState === "loading" ? "Loading the goal timing insight." : "No goal timing insight returned yet."} />
      )}
    </section>
  );
}

function TeamSignalPanel({ teams, loadState }: { teams: TeamResponse[]; loadState: LoadState }) {
  return (
    <section className="panel">
      <div className="section-heading compact">
        <div>
          <h2>Team signals</h2>
          <p>Early analytical summaries from the existing team endpoint.</p>
        </div>
      </div>
      <div className="team-list">
        {teams.length > 0 ? (
          teams.map((team) => (
            <article className="team-card" key={team.team_name}>
              <strong>{team.team_name}</strong>
              <span>
                {team.wins}W {team.draws}D {team.losses}L
              </span>
              <p>
                {team.goals_for} scored, {team.goals_against} conceded across {team.matches_played} matches.
              </p>
            </article>
          ))
        ) : (
          <EmptyState message={loadState === "loading" ? "Loading team summaries." : "No team summaries returned yet."} />
        )}
      </div>
    </section>
  );
}

function EventSignalPanel({ eventBreakdown }: { eventBreakdown: Array<{ eventType: string; label: string; count: number }> }) {
  return (
    <section className="panel">
      <div className="section-heading compact">
        <div>
          <h2>Event coverage</h2>
          <p>What the current data can already explain.</p>
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

function ExplorePreview() {
  return (
    <section className="explore-panel" id="explore" aria-labelledby="explore-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Explore the numbers</p>
          <h2 id="explore-title">Where the product goes next</h2>
          <p>These surfaces show the intended drilldowns without pretending unfinished tools are already live.</p>
        </div>
      </div>
      <div className="explore-grid">
        {exploreAreas.map((area) => (
          <article className="explore-card" key={area.title}>
            <span>{area.status}</span>
            <strong>{area.title}</strong>
            <p>{area.description}</p>
          </article>
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
          <h2>Recent evidence</h2>
          <p>Latest match rows are supporting context, not the main product promise.</p>
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

function TrustPanel({
  health,
  selectedSeasonInfo,
  overview,
}: {
  health: HealthResponse | null;
  selectedSeasonInfo: SeasonResponse | undefined;
  overview: SeasonOverviewResponse | null;
}) {
  return (
    <section className="trust-panel" id="methodology" aria-labelledby="methodology-title">
      <div className="section-heading compact">
        <div>
          <h2 id="methodology-title">Trust and methodology</h2>
          <p>Credibility comes from showing source, freshness, and caveats close to the numbers.</p>
        </div>
      </div>
      <div className="trust-list">
        <StatusItem label="Source" value="Official UPL match pages" />
        <StatusItem
          label="Latest staging run"
          value={health?.latest_staging_completed_at ? formatDate(health.latest_staging_completed_at) : "Unknown"}
        />
        <StatusItem
          label="Scoreline goals"
          value={overview?.scoreline_goal_count != null ? overview.scoreline_goal_count.toLocaleString() : "Unavailable"}
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
      </div>
    </section>
  );
}

function EmptyState({ message }: { message: string }) {
  return <p className="empty-state">{message}</p>;
}

export default App;
