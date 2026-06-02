import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { apiClient } from "../api/client";
import type { MatchSummary } from "../api/types";
import type { PageProps } from "../app/types";
import { EditorialTable, EditorialTableHeader } from "../components/common/EditorialTable";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { MatchRow } from "../components/matches/MatchRow";

const resultOptions = [
  { label: "All matches", value: "all" },
  { label: "Completed matches", value: "completed" },
  { label: "Draws", value: "draw" },
];

export function MatchExplorerPage({ data, loadState, onPageChange, selectedSeason }: PageProps) {
  const [searchParams] = useSearchParams();
  const initialTeamFilter = searchParams.get("team") ?? "all";
  const [teamFilter, setTeamFilter] = useState(initialTeamFilter);
  const [resultFilter, setResultFilter] = useState("all");
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

    apiClient
      .getTeamMatches(selectedSeason, teamFilter, 500)
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
        return matchesResult;
      })
      .sort((left, right) => (right.match_date ?? "").localeCompare(left.match_date ?? "") || right.match_id - left.match_id);
  }, [data.matches, resultFilter, serverFilteredMatches]);

  const visibleMatches = filteredMatches.slice(0, 12);
  const completedMatches = filteredMatches.filter((match) => match.result !== null).length;
  const administrativeMatches = filteredMatches.filter((match) => match.is_administrative_result).length;
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
        eyebrow="Explore matches"
        title="Match Explorer"
        text="Browse scorelines, teams, venues, and match context in a cleaner public-facing match report list."
      />

      <section className="panel match-explorer-results">
        <div className="section-heading compact">
          <div>
            <h2>Find a match pattern</h2>
            <p>Start with a team or result type. Deeper event filters can come later when the workflow needs them.</p>
          </div>
        </div>
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
        </div>
      </section>

      <section className="metric-grid compact-metrics" aria-label="Match explorer summary">
        <KpiCard
          label="Matches found"
          value={isTeamFilterLoading ? "..." : filteredMatches.length}
          context={matchCountContext}
          variant="compact"
        />
        <KpiCard accent="green" label="Completed" value={completedMatches} context="Rows with a recorded result." variant="compact" />
        <KpiCard
          accent="risk"
          label="Admin results"
          value={administrativeMatches}
          context="Forfeits, walkovers, or awarded results in this set."
          variant="compact"
        />
        <KpiCard
          accent="gold"
          label="Average goals"
          value={averageGoals.toFixed(1)}
          context="Goals per completed match in this filtered set."
          variant="compact"
        />
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Match report list</h2>
            <p>Showing the latest 12 matches from the current filter set with scoreline, status, and route into the full report.</p>
          </div>
          <button className="text-button" type="button" onClick={() => onPageChange("about")}>
            View data notes
          </button>
        </div>
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
