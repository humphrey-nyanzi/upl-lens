import { useEffect, useMemo, useReducer, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { apiClient } from "../api/client";
import type { MatchIntelligenceSummary, MatchSignal } from "../api/types";
import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { ShowMoreList } from "../components/common/ShowMoreList";
import { TeamMarker } from "../components/common/TeamMarker";
import { DataQualityNote } from "../components/intelligence/DataQualityNote";
import { MetricDelta } from "../components/intelligence/MetricDelta";
import { SignalChipGroup, type SignalChipItem } from "../components/intelligence/SignalChip";
import { StackedShareBar, type ShareSegment } from "../components/intelligence/ComparisonBars";
import { formatDate, formatScoreline, formatSeason } from "../utils/format";
import { toApiSeason } from "../utils/seasonScope";

type IntelligenceLoadState = "loading" | "success" | "error";

type MatchIntelligenceViewState = {
  requestKey: string;
  rows: MatchIntelligenceSummary[];
  status: Exclude<IntelligenceLoadState, "loading">;
};

type MatchExplorerFilters = {
  matchDayFilter: string;
  signalFilter: string;
  sortKey: string;
  teamFilter: string;
};

type MatchExplorerFilterAction =
  | { type: "matchDay"; value: string }
  | { type: "signal"; value: string }
  | { type: "sort"; value: string }
  | { type: "team"; value: string };

const signalOptions = [
  { label: "All signals", value: "all" },
  { label: "Goal-heavy", value: "goal_heavy" },
  { label: "High scoring", value: "high_scoring" },
  { label: "Late drama", value: "late_drama" },
  { label: "Final-15 goal", value: "final_15_goal" },
  { label: "Red card", value: "red_card" },
  { label: "Discipline signal", value: "discipline_signal" },
  { label: "Timeline complete", value: "timeline_complete" },
  { label: "Partial timeline", value: "timeline_partial" },
  { label: "Timeline unavailable", value: "timeline_unavailable" },
  { label: "Administrative result", value: "administrative_result" },
  { label: "Source caveat", value: "source_caveat" },
];

const sortOptions = [
  { label: "Most interesting", value: "interest" },
  { label: "Latest", value: "latest" },
  { label: "Most goals", value: "goals" },
  { label: "Most events", value: "events" },
  { label: "Most cards", value: "cards" },
  { label: "Late drama", value: "late_drama" },
];

const emptyMatchRows: MatchIntelligenceSummary[] = [];

function matchExplorerFilterReducer(
  filters: MatchExplorerFilters,
  action: MatchExplorerFilterAction,
): MatchExplorerFilters {
  if (action.type === "matchDay") return { ...filters, matchDayFilter: action.value };
  if (action.type === "signal") return { ...filters, signalFilter: action.value };
  if (action.type === "sort") return { ...filters, sortKey: action.value };
  return { ...filters, teamFilter: action.value };
}

function formatNullableNumber(value: number | null) {
  return value === null ? "-" : value.toLocaleString();
}

function asSignalItems(signals: MatchSignal[]): SignalChipItem[] {
  return signals.map((signal) => ({
    key: signal.key,
    label: signal.label,
    tone: signal.tone,
  }));
}

function getTeamOptions(rows: MatchIntelligenceSummary[], fallbackMatches: PageProps["data"]["matches"]) {
  const names = new Set<string>();
  rows.forEach((match) => {
    if (match.home_team) names.add(match.home_team);
    if (match.away_team) names.add(match.away_team);
  });
  fallbackMatches.forEach((match) => {
    if (match.home_team) names.add(match.home_team);
    if (match.away_team) names.add(match.away_team);
  });
  return Array.from(names).toSorted((left, right) => left.localeCompare(right));
}

function getTimelineLabel(status: string | null) {
  if (status === "complete") return "Timeline complete";
  if (status === "partial") return "Partial timeline";
  if (status === "unavailable") return "Timeline unavailable";
  if (status === "administrative_result") return "Administrative result";
  return "Timeline status TBC";
}

function getMatchEvidenceLabel(match: MatchIntelligenceSummary) {
  if (match.is_administrative_result) return "Administrative result";
  if (match.is_source_anomaly) return "Source anomaly";
  return getTimelineLabel(match.timeline_status);
}
function MatchSignalCard({ match }: { match: MatchIntelligenceSummary }) {
  const homeTeam = match.home_team ?? "Home team TBC";
  const awayTeam = match.away_team ?? "Away team TBC";

  return (
    <article className="match-intelligence-card">
      <div className="match-card-main">
        <div className="match-card-kicker">
          <span>{formatDate(match.match_date)}</span>
          {match.match_day !== null ? <span>Matchday {match.match_day}</span> : null}
          {match.ground_name ? <span>{match.ground_name}</span> : null}
        </div>
        <div className="match-card-scoreboard">
          <div className="match-card-team">
            <TeamMarker label={homeTeam} size="small" />
            <span>{homeTeam}</span>
          </div>
          <strong>{formatScoreline(match.home_score, match.away_score)}</strong>
          <div className="match-card-team away">
            <span>{awayTeam}</span>
            <TeamMarker label={awayTeam} size="small" />
          </div>
        </div>
        <div className="match-card-signals">
          <strong>{match.primary_signal ?? "Evidence-led match"}</strong>
          <SignalChipGroup items={asSignalItems(match.signal_labels)} emptyLabel="No major signal" maxVisible={4} size="small" />
        </div>
      </div>

      <div className="match-card-metrics" aria-label="Match intelligence metrics">
        <MetricDelta label="Interest" value={match.interest_score} context="Computed signal score" />
        <MetricDelta label="Goals" value={match.goal_count} context={`${formatNullableNumber(match.total_goals)} from scoreline`} />
        <MetricDelta label="Cards" value={match.yellow_card_count + match.red_card_count} context={`${match.red_card_count} red`} />
        <MetricDelta label="Late goals" value={match.late_goal_count} context={`${match.final_15_goal_count} final-15`} />
      </div>

      <div className="match-card-evidence">
        <span>
          Events <strong>{match.event_count}</strong>
        </span>
        <span>{getMatchEvidenceLabel(match)}</span>
      </div>
      {match.data_quality_note ? <p className="match-card-caveat">{match.data_quality_note}</p> : null}

      <Link className="text-button match-card-link" to={`/matches/${match.match_id}`}>
        Open match brief
      </Link>
    </article>
  );
}

export function MatchExplorerPage({ data, loadState, selectedSeason }: PageProps) {
  const [searchParams] = useSearchParams();
  const initialTeamFilter = searchParams.get("team") ?? "all";
  const [{ matchDayFilter, signalFilter, sortKey, teamFilter }, updateFilters] = useReducer(matchExplorerFilterReducer, {
    matchDayFilter: "all",
    signalFilter: "all",
    sortKey: "interest",
    teamFilter: initialTeamFilter,
  });
  const requestKey = `${selectedSeason}|${teamFilter}|${matchDayFilter}|${signalFilter}|${sortKey}`;
  const [viewState, setViewState] = useState<MatchIntelligenceViewState>({
    requestKey: "",
    rows: [],
    status: "success",
  });

  useEffect(() => {
    let ignore = false;
    const apiSeason = toApiSeason(selectedSeason);
    const matchDay = matchDayFilter === "all" ? undefined : Number(matchDayFilter);

    apiClient
      .getMatchIntelligence(apiSeason, {
        team: teamFilter === "all" ? undefined : teamFilter,
        match_day: Number.isFinite(matchDay) ? matchDay : undefined,
        signal: signalFilter === "all" ? undefined : signalFilter,
        sort: sortKey,
        limit: 120,
      })
      .then((matches) => {
        if (!ignore) {
          setViewState({ requestKey, rows: matches, status: "success" });
        }
      })
      .catch(() => {
        if (!ignore) {
          setViewState({ requestKey, rows: [], status: "error" });
        }
      });

    return () => {
      ignore = true;
    };
  }, [matchDayFilter, requestKey, selectedSeason, signalFilter, sortKey, teamFilter]);

  const intelligenceState: IntelligenceLoadState = viewState.requestKey === requestKey ? viewState.status : "loading";
  const rows = viewState.requestKey === requestKey ? viewState.rows : emptyMatchRows;

  const teamOptions = useMemo(() => getTeamOptions(rows, data.matches), [data.matches, rows]);
  const matchDayOptions = useMemo(() => {
    const days = new Set<number>();
    data.matches.forEach((match) => {
      if (match.match_day !== null) days.add(match.match_day);
    });
    rows.forEach((match) => {
      if (match.match_day !== null) days.add(match.match_day);
    });
    return Array.from(days).toSorted((left, right) => left - right);
  }, [data.matches, rows]);

  const summary = useMemo(
    () => ({
      administrativeOrSource: rows.filter((match) => match.is_administrative_result || match.is_source_anomaly).length,
      highScoring: rows.filter((match) => match.goal_count >= 3 || (match.total_goals ?? 0) >= 3).length,
      lateDrama: rows.filter((match) => match.late_goal_count > 0 || match.final_15_goal_count > 0).length,
      redCards: rows.filter((match) => match.red_card_count > 0).length,
      timelineBacked: rows.filter((match) => match.timeline_status === "complete").length,
    }),
    [rows],
  );

  const evidenceSegments: ShareSegment[] = [
    { label: "Complete", value: rows.filter((match) => match.timeline_status === "complete").length, tone: "green" },
    { label: "Partial", value: rows.filter((match) => match.timeline_status === "partial").length, tone: "gold" },
    { label: "Unavailable", value: rows.filter((match) => match.timeline_status === "unavailable").length, tone: "muted" },
    {
      label: "Caveated",
      value: rows.filter((match) => match.is_source_anomaly || match.is_administrative_result).length,
      tone: "risk",
    },
  ];

  const isLoading = intelligenceState === "loading";

  return (
    <div className="match-triage-page">
      <PageIntro
        variant="dense"
        eyebrow="Match intelligence"
        title="Matches"
        text="Find UPL matches by football signal: scoring, late goals, discipline, result context, and evidence quality."
      >
        <div className="season-context-pill">{formatSeason(selectedSeason)}</div>
      </PageIntro>

      <section className="metric-grid compact-metrics" aria-label="Match intelligence summary">
        <KpiCard label="Matches found" value={isLoading ? "..." : rows.length} context="Matches in the current signal view." variant="compact" />
        <KpiCard accent="gold" label="High scoring" value={isLoading ? "..." : summary.highScoring} context="Three or more captured goals." variant="compact" />
        <KpiCard accent="green" label="Late drama" value={isLoading ? "..." : summary.lateDrama} context="Late or final-15 goal signal." variant="compact" />
        <KpiCard accent="risk" label="Red-card matches" value={isLoading ? "..." : summary.redCards} context="Matches with a captured dismissal." variant="compact" />
        <KpiCard label="Timeline backed" value={isLoading ? "..." : summary.timelineBacked} context="Complete timeline evidence." variant="compact" />
        <KpiCard accent="risk" label="Source caveats" value={isLoading ? "..." : summary.administrativeOrSource} context="Administrative or source-anomaly notes." variant="compact" />
      </section>

      <section className="panel match-triage-filters">
        <ReportSectionHeader
          title="Triage filters"
          text="Use supported signals and sorting to surface matches worth opening, then narrow by team or matchday when needed."
        />
        <div className="filter-grid" aria-label="Match intelligence filters">
          <label>
            Team
            <select value={teamFilter} onChange={(event) => updateFilters({ type: "team", value: event.target.value })}>
              <option value="all">All teams</option>
              {teamOptions.map((team) => (
                <option value={team} key={team}>
                  {team}
                </option>
              ))}
            </select>
          </label>
          <label>
            Matchday
            <select value={matchDayFilter} onChange={(event) => updateFilters({ type: "matchDay", value: event.target.value })}>
              <option value="all">All matchdays</option>
              {matchDayOptions.map((day) => (
                <option value={day} key={day}>
                  Matchday {day}
                </option>
              ))}
            </select>
          </label>
          <label>
            Signal
            <select value={signalFilter} onChange={(event) => updateFilters({ type: "signal", value: event.target.value })}>
              {signalOptions.map((option) => (
                <option value={option.value} key={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Sort
            <select value={sortKey} onChange={(event) => updateFilters({ type: "sort", value: event.target.value })}>
              {sortOptions.map((option) => (
                <option value={option.value} key={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>

      <section className="match-triage-layout">
        <section className="match-triage-list-section">
          <ReportSectionHeader
            title="Signal-led matches"
            text="Cards lead with the football reason to open the match, then show the supporting counts and evidence caveats."
          />
          {isLoading ? (
            <div className="match-intelligence-list">
              {Array.from({ length: 4 }).map((_, index) => (
                <div className="skeleton-card match-intelligence-card-skeleton" key={`match-card-skeleton-${index}`}>
                  <span className="skeleton-line short"></span>
                  <span className="skeleton-line title"></span>
                  <span className="skeleton-line"></span>
                  <span className="skeleton-line medium"></span>
                </div>
              ))}
            </div>
          ) : rows.length > 0 ? (
            <ShowMoreList
              className="match-intelligence-list"
              getKey={(match) => match.match_id}
              initialCount={8}
              itemNoun="match"
              items={rows}
              renderItem={(match) => <MatchSignalCard match={match} />}
            />
          ) : (
            <EmptyState
              title={intelligenceState === "error" ? "Match intelligence unavailable" : "No matches found"}
              message={
                intelligenceState === "error"
                  ? "Match intelligence did not respond. Try refreshing or changing the season."
                  : "No matches found for the selected signal and filters. Try changing the team, matchday, or signal filter."
              }
            />
          )}
        </section>

        <aside className="match-evidence-summary">
          <ReportSectionHeader
            eyebrow="Evidence quality"
            title="Coverage context"
            text="Timeline coverage and source caveats shape how much weight to place on event-led signals."
          />
          <StackedShareBar label="Returned matches" segments={evidenceSegments} />
          <DataQualityNote
            tone={summary.administrativeOrSource > 0 ? "caution" : "neutral"}
            note="UPL Lens uses these evidence notes to separate analytical signals from the official source record."
            metrics={[
              { label: "Complete", value: summary.timelineBacked },
              { label: "Partial/unavailable", value: evidenceSegments[1].value + evidenceSegments[2].value },
              { label: "Caveats", value: summary.administrativeOrSource },
            ]}
          />
        </aside>
      </section>

      {loadState === "error" && intelligenceState === "success" ? (
        <DataQualityNote
          tone="caution"
          note="The dashboard bootstrap data had an issue, but match intelligence loaded directly from the API."
          compact
        />
      ) : null}
    </div>
  );
}
