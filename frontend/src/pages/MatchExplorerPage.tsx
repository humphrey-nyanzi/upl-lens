import { useMemo, useState } from "react";

import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { MatchRow } from "../components/matches/MatchRow";

const resultOptions = [
  { label: "All results", value: "all" },
  { label: "Home wins", value: "home_win" },
  { label: "Away wins", value: "away_win" },
  { label: "Draws", value: "draw" },
];

export function MatchExplorerPage({ data, loadState, onPageChange }: PageProps) {
  const [teamFilter, setTeamFilter] = useState("all");
  const [resultFilter, setResultFilter] = useState("all");

  const teamOptions = useMemo(() => {
    const names = new Set<string>();
    data.matches.forEach((match) => {
      if (match.home_team) names.add(match.home_team);
      if (match.away_team) names.add(match.away_team);
    });
    return [...names].sort((left, right) => left.localeCompare(right));
  }, [data.matches]);

  const filteredMatches = useMemo(() => {
    return [...data.matches]
      .filter((match) => {
        const matchesTeam = teamFilter === "all" || match.home_team === teamFilter || match.away_team === teamFilter;
        const matchesResult = resultFilter === "all" || match.result === resultFilter;
        return matchesTeam && matchesResult;
      })
      .sort((left, right) => (right.match_date ?? "").localeCompare(left.match_date ?? "") || right.match_id - left.match_id);
  }, [data.matches, resultFilter, teamFilter]);

  const visibleMatches = filteredMatches.slice(0, 12);
  const completedMatches = filteredMatches.filter((match) => match.result !== null).length;
  const averageGoals =
    completedMatches > 0
      ? filteredMatches.reduce((total, match) => total + (match.total_goals ?? 0), 0) / completedMatches
      : 0;

  return (
    <>
      <PageIntro
        eyebrow="Explore matches"
        title="Match Explorer"
        text="Browse scorelines, teams, venues, and result patterns without turning the page into a raw database table."
      />

      <section className="panel">
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
        <KpiCard label="Matches found" value={filteredMatches.length} detail="Matches matching the current filters." />
        <KpiCard accent="green" label="Completed" value={completedMatches} detail="Rows with a recorded result." />
        <KpiCard accent="gold" label="Average goals" value={averageGoals.toFixed(1)} detail="Goals per completed match in this filtered set." />
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Match cards</h2>
            <p>Showing the latest 12 matches from the current filter set.</p>
          </div>
          <button className="text-button" type="button" onClick={() => onPageChange("methodology")}>
            View data notes
          </button>
        </div>
        <div className="match-list">
          {visibleMatches.length > 0 ? (
            visibleMatches.map((match) => <MatchRow key={match.match_id} match={match} />)
          ) : (
            <EmptyState message={loadState === "loading" ? "Loading matches." : "No matches fit the current filters."} />
          )}
        </div>
      </section>
    </>
  );
}
