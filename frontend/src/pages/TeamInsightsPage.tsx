import { useMemo, useState } from "react";

import type { TeamResponse } from "../api/types";
import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { TeamCard } from "../components/teams/TeamCard";
import { formatGoalDifference, getTeamGoalDifference, getTeamPoints, sortTeams, type TeamSortKey } from "../utils/teams";

const sortOptions: { label: string; value: TeamSortKey }[] = [
  { label: "Points", value: "points" },
  { label: "Team name", value: "name" },
  { label: "Wins", value: "wins" },
  { label: "Goals for", value: "goals_for" },
  { label: "Goals against", value: "goals_against" },
  { label: "Goal difference", value: "goal_difference" },
];

function TeamIndexSkeleton() {
  return (
    <div className="team-grid" aria-busy="true" aria-label="Loading team summaries">
      {[0, 1, 2, 3].map((item) => (
        <div className="skeleton-card team-skeleton-card" key={item}>
          <span className="skeleton-line medium"></span>
          <span className="skeleton-line"></span>
          <span className="skeleton-line short"></span>
        </div>
      ))}
    </div>
  );
}

export function TeamInsightsPage({ data, loadState, onRefresh, selectedSeason }: PageProps) {
  const [teamQuery, setTeamQuery] = useState("");
  const [sortKey, setSortKey] = useState<TeamSortKey>("points");

  const filteredTeams = useMemo(() => {
    const normalizedQuery = teamQuery.trim().toLowerCase();
    const matchingTeams = normalizedQuery
      ? data.teams.filter((team) => team.team_name.toLowerCase().includes(normalizedQuery))
      : data.teams;

    return sortTeams(matchingTeams, sortKey);
  }, [data.teams, sortKey, teamQuery]);

  const bestAttack = data.teams.reduce<TeamResponse | null>((best, team) => {
    if (best === null || team.goals_for > best.goals_for) return team;
    return best;
  }, null);
  const bestDefense = data.teams.reduce<TeamResponse | null>((best, team) => {
    if (best === null || team.goals_against < best.goals_against) return team;
    return best;
  }, null);
  const bestGoalDifference = data.teams.reduce<TeamResponse | null>((best, team) => {
    if (best === null || getTeamGoalDifference(team) > getTeamGoalDifference(best)) return team;
    return best;
  }, null);

  const couldNotLoad = loadState === "error" && data.teams.length === 0;

  return (
    <>
      <PageIntro
        eyebrow="Team index"
        title="Teams"
        text="Compare UPL teams by record, scoring, conceding, and season-level performance signals."
      />

      {couldNotLoad ? (
        <section className="error-panel" role="alert">
          <span className="eyebrow">Teams</span>
          <h2>Could not load team summaries</h2>
          <p>The team index did not load for the selected season. The data service may be waking up.</p>
          <button className="text-button" type="button" onClick={onRefresh}>
            Retry
          </button>
        </section>
      ) : null}

      <section className="panel">
        <div className="section-heading compact">
          <div>
            <h2>Find a team</h2>
            <p>{selectedSeason ? `Showing team summaries for ${selectedSeason.replace("_", "/")}.` : "Showing the selected season."}</p>
          </div>
        </div>
        <div className="filter-grid team-filter-grid" aria-label="Team filters">
          <label>
            Search teams
            <input
              className="filter-input"
              onChange={(event) => setTeamQuery(event.target.value)}
              placeholder="Search by team name"
              type="search"
              value={teamQuery}
            />
          </label>
          <label>
            Sort by
            <select value={sortKey} onChange={(event) => setSortKey(event.target.value as TeamSortKey)}>
              {sortOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>

      <section className="metric-grid compact-metrics" aria-label="Team index highlights">
        <KpiCard label="Teams tracked" value={data.teams.length} context="Distinct clubs in the selected season data." variant="compact" />
        <KpiCard
          accent="green"
          label="Top attack"
          value={bestAttack?.goals_for ?? 0}
          context={bestAttack ? `${bestAttack.team_name} goals scored.` : "No team data available yet."}
          variant="compact"
        />
        <KpiCard
          accent="gold"
          label="Tightest defence"
          value={bestDefense?.goals_against ?? 0}
          context={bestDefense ? `${bestDefense.team_name} goals conceded.` : "No team data available yet."}
          variant="compact"
        />
        <KpiCard
          label="Best goal difference"
          value={bestGoalDifference ? formatGoalDifference(getTeamGoalDifference(bestGoalDifference)) : 0}
          context={bestGoalDifference ? `${bestGoalDifference.team_name}, ${getTeamPoints(bestGoalDifference)} points.` : "No team data available yet."}
          variant="compact"
        />
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Team ranking</h2>
            <p>Each card links to a team profile and uses only available season summary data.</p>
          </div>
        </div>
        {loadState === "loading" && data.teams.length === 0 ? (
          <TeamIndexSkeleton />
        ) : filteredTeams.length > 0 ? (
          <div className="team-grid">
            {filteredTeams.map((team, index) => <TeamCard key={team.team_name} rank={index + 1} team={team} />)}
          </div>
        ) : (
          <EmptyState message={data.teams.length === 0 ? "No team summaries are available for this season yet." : "No teams match the current search."} />
        )}
      </section>
    </>
  );
}
