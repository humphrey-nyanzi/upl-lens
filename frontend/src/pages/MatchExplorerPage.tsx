import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { apiClient } from "../api/client";
import type { MatchSummary } from "../api/types";
import type { PageProps } from "../app/types";
import { EditorialTable, EditorialTableHeader } from "../components/common/EditorialTable";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { MatchRow } from "../components/matches/MatchRow";
import { hasMatchBriefSignal } from "../utils/matchBriefs";
import { toApiSeason } from "../utils/seasonScope";

const resultOptions = [
  { label: "All matches", value: "all" },
  { label: "Completed matches", value: "completed" },
  { label: "Draws", value: "draw" },
];

const signalOptions = [
  { label: "All briefs", value: "all" },
  { label: "Timeline backed", value: "timeline_backed" },
  { label: "Goal-heavy", value: "goal_heavy" },
  { label: "Discipline notes", value: "discipline" },
  { label: "Result notes", value: "result_note" },
];

export function MatchExplorerPage({ data, loadState, onPageChange, selectedSeason }: PageProps) {
  const [searchParams] = useSearchParams();
  const initialTeamFilter = searchParams.get("team") ?? "all";
  const [teamFilter, setTeamFilter] = useState(initialTeamFilter);
  const [resultFilter, setResultFilter] = useState("all");
  const [signalFilter, setSignalFilter] = useState("all");
  const [serverFilteredMatches, setServerFilteredMatches] = useState<MatchSummary[] | null>(null);
  const [serverFilterState, setServerFilterState] = useState<"idle" | "loading" | "success" | "error">("idle");

  const teamOptions = useMemo(() => {
    const names = new Set<string>();
    data.matches.forEach((match) => {
      if (match.home_team) names.add(match.home_team);
      if (match.away_team) names.add(match.away_team);
    });
    return [...names].sort((left, right) => left.localeCompare(right));
  }, [data.matches]);

  useEffect(() => {
    if (!selectedSeason || teamFilter === "all") {
      setServerFilteredMatches(null);
      setServerFilterState("idle");
      return;
    }

    let ignore = false;
    setServerFilterState("loading");
    const apiSeason = toApiSeason(selectedSeason);

    apiClient
      .getTeamMatches(apiSeason, teamFilter, 500)
      .then((matches) => {
        if (!ignore) {
          setServerFilteredMatches(matches);
          setServerFilterState("success");
        }
      })
      .catch(() => {
        if (!ignore) {
          setServerFilteredMatches(null);
          setServerFilterState("error");
        }
      });

    return () => {
      ignore = true;
    };
  }, [selectedSeason, teamFilter]);

  const filteredMatches = useMemo(() => {
    const sourceMatches = serverFilteredMatches ?? data.matches;
    return [...sourceMatches]
      .filter((match) => {
        const matchesResult =
          resultFilter === "all" ||
          (resultFilter === "completed" ? match.result !== null : match.result === resultFilter);
        const matchesSignal =
          signalFilter === "all" || hasMatchBriefSignal(match, signalFilter as Parameters<typeof hasMatchBriefSignal>[1]);
        return matchesResult && matchesSignal;
      })
      .sort((left, right) => (right.match_date ?? "").localeCompare(left.match_date ?? "") || right.match_id - left.match_id);
  }, [data.matches, resultFilter, serverFilteredMatches, signalFilter]);

  const visibleMatches = filteredMatches.slice(0, 12);
  const completedMatches = filteredMatches.filter((match) => match.result !== null).length;
  const timelineBackedMatches = filteredMatches.filter((match) => hasMatchBriefSignal(match, "timeline_backed")).length;
  const goalHeavyMatches = filteredMatches.filter((match) => hasMatchBriefSignal(match, "goal_heavy")).length;
  const notedMatches = filteredMatches.filter((match) => hasMatchBriefSignal(match, "result_note")).length;
  const averageGoals =
    completedMatches > 0
      ? filteredMatches.reduce((total, match) => total + (match.total_goals ?? 0), 0) / completedMatches
      : 0;
  const isTeamFilterLoading = teamFilter !== "all" && serverFilterState === "loading";
  const matchCountContext =
    teamFilter === "all"
      ? "Season fixtures matching the current filters."
      : serverFilterState === "error"
        ? "Using loaded season data because the team-specific request failed."
        : "Team fixtures loaded directly from the API before filtering.";

  return (
    <>
      <PageIntro
        eyebrow="Match intelligence"
        title="Match Briefs"
        text="Scan evidence-led match briefs built from recorded UPL results, then open the fixtures that deserve a closer read."
      />

      <section className="panel match-explorer-results">
        <ReportSectionHeader
          title="Filter the evidence"
          text="Start with a team, result type, or evidence signal, then narrow the set down to the fixtures worth reading as briefs."
        />
        <div className="filter-grid" aria-label="Match filters">
          <label>
            Team
            <select value={teamFilter} onChange={(event) => setTeamFilter(event.target.value)}>
              <option value="all">All teams</option>
              {teamOptions.map((team) => (
                <option value={team} key={team}>
                  {team}
                </option>
              ))}
            </select>
          </label>
          <label>
            Result
            <select value={resultFilter} onChange={(event) => setResultFilter(event.target.value)}>
              {resultOptions.map((option) => (
                <option value={option.value} key={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Brief signal
            <select value={signalFilter} onChange={(event) => setSignalFilter(event.target.value)}>
              {signalOptions.map((option) => (
                <option value={option.value} key={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>

      <section className="metric-grid compact-metrics" aria-label="Match explorer summary">
        <KpiCard
          label="Briefs found"
          value={isTeamFilterLoading ? "..." : filteredMatches.length}
          context={matchCountContext}
          variant="compact"
        />
        <KpiCard
          accent="green"
          label="Timeline backed"
          value={timelineBackedMatches}
          context="Briefs with event evidence beyond the final scoreline."
          variant="compact"
        />
        <KpiCard
          accent="gold"
          label="Goal-heavy"
          value={goalHeavyMatches}
          context="Matches in this set with at least five total goals."
          variant="compact"
        />
        <KpiCard
          accent="risk"
          label="Result notes"
          value={notedMatches}
          context="Administrative outcomes or source issues that need extra reading care."
          variant="compact"
        />
        <KpiCard
          label="Average goals"
          value={averageGoals.toFixed(1)}
          context="Goals per completed brief in this filtered set."
          variant="compact"
        />
      </section>

      <section className="panel">
        <ReportSectionHeader
          title="Latest briefs"
          text="Showing the latest 12 matches from the current filter set with scoreline, brief signal, and a route into the fuller match evidence page."
        >
          <button className="text-button" type="button" onClick={() => onPageChange("about")}>
            View data notes
          </button>
        </ReportSectionHeader>
        <EditorialTable className="match-table-shell">
          <EditorialTableHeader
            className="match-table-header"
            columns={[
              { label: "Date & fixture" },
              { align: "center", label: "Status" },
              { align: "right", label: "Action" },
            ]}
          />
          <div className="match-list match-explorer-list">
            {visibleMatches.length > 0 ? (
              visibleMatches.map((match) => <MatchRow key={match.match_id} match={match} />)
            ) : (
              <EmptyState message={loadState === "loading" ? "Loading matches." : "No matches fit the current filters."} />
            )}
          </div>
        </EditorialTable>
      </section>
    </>
  );
}
