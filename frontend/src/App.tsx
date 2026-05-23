import { useEffect, useMemo, useState } from "react";

import { API_BASE_URL, apiClient } from "./api/client";
import type {
  EventResponse,
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
  events: EventResponse[];
};

const futurePages = ["Match Explorer", "Discipline Dashboard", "Team Profile"];

const eventLabels: Record<string, string> = {
  goal: "Goals",
  own_goal: "Own goals",
  penalty_goal: "Penalty goals",
  yellow_card: "Yellow cards",
  red_card: "Red cards",
  substitution: "Substitutions",
};

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

function eventLabel(eventType: string | null) {
  if (!eventType) return "Other events";
  return eventLabels[eventType] ?? eventType.replaceAll("_", " ");
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
    events: [],
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
        const [overview, goalTiming, matches, teams, events] = await Promise.all([
          apiClient.getSeasonOverview(selectedSeason),
          apiClient.getGoalTimingInsight(selectedSeason),
          apiClient.getMatches(selectedSeason, 200),
          apiClient.getTeams(selectedSeason, 200),
          apiClient.getEvents(selectedSeason, 200),
        ]);

        if (!ignore) {
          setData((current) => ({ ...current, overview, goalTiming, matches, teams, events }));
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

  const summary = {
    matches: overview?.match_count ?? selectedSeasonInfo?.match_count ?? data.matches.length,
    teams: overview?.team_count ?? selectedSeasonInfo?.team_count ?? data.teams.length,
    goals: overview?.goal_count ?? 0,
    cards: overview ? overview.yellow_card_count + overview.red_card_count : 0,
  };

  const eventBreakdown = useMemo(() => {
    if (overview) {
      return overview.event_breakdown.map((item) => ({
        eventType: item.event_type,
        label: item.label,
        count: item.count,
      }));
    }

    const counts = data.events.reduce<Record<string, number>>((accumulator, event) => {
      const key = event.event_type ?? "other";
      accumulator[key] = (accumulator[key] ?? 0) + 1;
      return accumulator;
    }, {});

    return Object.entries(counts)
      .map(([eventType, count]) => ({ eventType, label: eventLabel(eventType), count }))
      .sort((left, right) => right.count - left.count);
  }, [data.events, overview]);

  const topTeams = useMemo(() => {
    return [...data.teams]
      .sort((left, right) => right.wins - left.wins || right.goals_for - left.goals_for)
      .slice(0, 12);
  }, [data.teams]);

  const recentMatches = useMemo(() => {
    return [...data.matches]
      .sort((left, right) => {
        const leftDate = left.match_date ?? "";
        const rightDate = right.match_date ?? "";
        return rightDate.localeCompare(leftDate) || right.match_id - left.match_id;
      })
      .slice(0, 10);
  }, [data.matches]);

  function refreshSeason() {
    if (selectedSeason) {
      setLoadState("loading");
      void Promise.all([
        apiClient.getHealth().then((health) => setData((current) => ({ ...current, health }))),
        apiClient.getSeasonOverview(selectedSeason).then((overview) =>
          setData((current) => ({ ...current, overview })),
        ),
        apiClient.getGoalTimingInsight(selectedSeason).then((goalTiming) =>
          setData((current) => ({ ...current, goalTiming })),
        ),
        apiClient.getMatches(selectedSeason, 200).then((matches) =>
          setData((current) => ({ ...current, matches })),
        ),
        apiClient.getTeams(selectedSeason, 200).then((teams) => setData((current) => ({ ...current, teams }))),
        apiClient.getEvents(selectedSeason, 200).then((events) => setData((current) => ({ ...current, events }))),
      ])
        .then(() => setLoadState("success"))
        .catch((error) => {
          setLoadState("error");
          setErrorMessage(error instanceof Error ? error.message : "Refresh failed.");
        });
    }
  }

  const apiOnline = data.health?.status === "ok" && data.health.database === "ok";

  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Product sections">
        <div className="brand-lockup">
          <div className="brand-mark">UPL</div>
          <div>
            <p className="brand-title">Match Intelligence</p>
            <p className="brand-subtitle">League workspace</p>
          </div>
        </div>

        <nav className="nav-list" aria-label="Future dashboard pages">
          <a className="nav-item active" href="#overview">
            League Overview
          </a>
          <a className="nav-item" href="#goal-timing">
            Goal Timing
          </a>
          {futurePages.map((page) => (
            <a className="nav-item disabled" href="#future-pages" key={page} aria-disabled="true">
              {page}
            </a>
          ))}
        </nav>

        <div className="source-note">
          <span className={apiOnline ? "status-dot online" : "status-dot offline"} />
          <div>
            <strong>{apiOnline ? "API connected" : "API offline"}</strong>
            <p>React is reading FastAPI JSON backed by cleaned Postgres data.</p>
          </div>
        </div>
      </aside>

      <section className="workspace" id="overview">
        <header className="workspace-header">
          <div>
            <h1>League Overview</h1>
            <p>
              A first product slice for browsing seasons, match records, team summaries, and event signals.
            </p>
          </div>

          <div className="toolbar" aria-label="Dashboard controls">
            <label>
              Season
              <select
                value={selectedSeason}
                onChange={(event) => setSelectedSeason(event.target.value)}
                disabled={data.seasons.length === 0}
              >
                {data.seasons.map((season) => (
                  <option value={season.season} key={season.season}>
                    {formatSeason(season.season)}
                  </option>
                ))}
              </select>
            </label>
            <button type="button" onClick={refreshSeason} disabled={!selectedSeason || loadState === "loading"}>
              Refresh
            </button>
          </div>
        </header>

        {loadState === "error" ? (
          <section className="error-panel" role="alert">
            <h2>FastAPI is not returning data yet</h2>
            <p>{errorMessage}</p>
            <p>
              Check that the API is reachable at {API_BASE_URL}. If this only happens in one browser
              profile, disable privacy or ad-blocking extensions for this site and refresh.
            </p>
          </section>
        ) : null}

        <section className="metric-grid" aria-label="Selected season summary">
          <MetricCard label="Matches" value={summary.matches} detail="From season availability" />
          <MetricCard label="Teams" value={summary.teams} detail="Distinct clubs in matches" />
          <MetricCard label="Goals" value={summary.goals} detail="Actual timeline goals" />
          <MetricCard label="Cards" value={summary.cards} detail="Yellow and red cards counted by Postgres" />
        </section>

        <section className="insight-strip">
          <div>
            <span>Health</span>
            <strong>{apiOnline ? "Database ready" : "Waiting for API"}</strong>
          </div>
          <div>
            <span>Selected season</span>
            <strong>{selectedSeason ? formatSeason(selectedSeason) : "No season loaded"}</strong>
          </div>
          <div>
            <span>Date range</span>
            <strong>
              {selectedSeasonInfo
                ? `${formatDate(overview?.first_match_date ?? selectedSeasonInfo.first_match_date)} - ${formatDate(
                    overview?.latest_match_date ?? selectedSeasonInfo.last_match_date,
                  )}`
                : "Unavailable"}
            </strong>
          </div>
          <div>
            <span>Staging run</span>
            <strong>{data.health?.latest_staging_completed_at ? formatDate(data.health.latest_staging_completed_at) : "Unknown"}</strong>
          </div>
        </section>

        <GoalTimingPanel goalTiming={goalTiming} loadState={loadState} />

        <div className="content-grid">
          <section className="panel wide">
            <div className="section-heading">
              <div>
                <h2>Recent Matches</h2>
                <p>Scorelines and venues from the selected season.</p>
              </div>
              <span>{loadState === "loading" ? "Loading..." : `${recentMatches.length} shown`}</span>
            </div>
            <div className="match-list">
              {recentMatches.length > 0 ? (
                recentMatches.map((match) => <MatchRow key={match.match_id} match={match} />)
              ) : (
                <EmptyState message="No matches returned for this season yet." />
              )}
            </div>
          </section>

          <section className="panel">
            <div className="section-heading">
              <div>
                <h2>Event Breakdown</h2>
                <p>Season-wide event totals from the overview endpoint.</p>
              </div>
            </div>
            <div className="breakdown-list">
              {eventBreakdown.length > 0 ? (
                eventBreakdown.slice(0, 8).map((item) => (
                  <div className="breakdown-row" key={item.eventType}>
                    <span>{item.label}</span>
                    <strong>{item.count}</strong>
                  </div>
                ))
              ) : (
                <EmptyState message="No timeline events returned for this season yet." />
              )}
            </div>
          </section>
        </div>

        <section className="panel">
          <div className="section-heading">
            <div>
              <h2>Teams</h2>
              <p>Sorted by wins, then goals scored, using the existing team summary endpoint.</p>
            </div>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Team</th>
                  <th>Matches</th>
                  <th>Wins</th>
                  <th>Draws</th>
                  <th>Losses</th>
                  <th>Goals For</th>
                  <th>Goals Against</th>
                </tr>
              </thead>
              <tbody>
                {topTeams.map((team) => (
                  <tr key={team.team_name}>
                    <td>{team.team_name}</td>
                    <td>{team.matches_played}</td>
                    <td>{team.wins}</td>
                    <td>{team.draws}</td>
                    <td>{team.losses}</td>
                    <td>{team.goals_for}</td>
                    <td>{team.goals_against}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {topTeams.length === 0 ? <EmptyState message="No team rows returned for this season yet." /> : null}
          </div>
        </section>

        <section className="future-panel" id="future-pages">
          <h2>Next Product Areas</h2>
          <div className="future-grid">
            {futurePages.map((page) => (
              <div key={page}>
                <strong>{page}</strong>
                <p>Reserved for future dashboard expansion after the deployed overview is stable.</p>
              </div>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

function GoalTimingPanel({
  goalTiming,
  loadState,
}: {
  goalTiming: GoalTimingInsightResponse | null;
  loadState: LoadState;
}) {
  const maxGoals = Math.max(...(goalTiming?.intervals.map((interval) => interval.goals) ?? [0]), 1);

  return (
    <section className="panel goal-timing-panel" id="goal-timing">
      <div className="section-heading">
        <div>
          <h2>Goal Timing Explorer</h2>
          <p>Regular-time goal distribution promoted from the Feature 1 notebook.</p>
        </div>
        <span>{loadState === "loading" ? "Loading..." : goalTiming?.peak_interval ?? "No peak yet"}</span>
      </div>

      {goalTiming ? (
        <>
          <div className="goal-timing-summary">
            <div>
              <span>Regular-time goals</span>
              <strong>{goalTiming.total_regular_time_goals.toLocaleString()}</strong>
            </div>
            <div>
              <span>Peak interval</span>
              <strong>{goalTiming.peak_interval ?? "Unavailable"}</strong>
            </div>
          </div>

          <div className="goal-timing-chart" aria-label="Regular-time goals by 15-minute interval">
            {goalTiming.intervals.map((interval) => {
              const width = `${Math.max((interval.goals / maxGoals) * 100, interval.goals > 0 ? 8 : 0)}%`;

              return (
                <div className="goal-timing-row" key={interval.interval}>
                  <span>{interval.interval}</span>
                  <div className="goal-timing-bar-track">
                    <div
                      className={interval.rank === 1 ? "goal-timing-bar peak" : "goal-timing-bar"}
                      style={{ width }}
                    />
                  </div>
                  <strong>
                    {interval.goals.toLocaleString()} ({formatPercent(interval.share)})
                  </strong>
                </div>
              );
            })}
          </div>
        </>
      ) : (
        <EmptyState message="No goal timing insight returned for this season yet." />
      )}
    </section>
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
      <div>
        <span>Venue</span>
        <strong>{match.ground_name ?? "Venue TBC"}</strong>
      </div>
    </article>
  );
}

function EmptyState({ message }: { message: string }) {
  return <p className="empty-state">{message}</p>;
}

export default App;
