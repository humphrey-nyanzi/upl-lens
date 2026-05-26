import type { TeamResponse } from "../api/types";
import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { PageIntro } from "../components/common/PageIntro";
import { TeamCard } from "../components/teams/TeamCard";

export function TeamInsightsPage({ data, loadState }: PageProps) {
  const teams = [...data.teams].sort((left, right) => right.wins - left.wins || right.goals_for - left.goals_for);
  const bestAttack = teams.reduce<TeamResponse | null>((best, team) => {
    if (best === null || team.goals_for > best.goals_for) return team;
    return best;
  }, null);
  const bestDefense = teams.reduce<TeamResponse | null>((best, team) => {
    if (best === null || team.goals_against < best.goals_against) return team;
    return best;
  }, null);

  return (
    <>
      <PageIntro
        eyebrow="Team trends"
        title="Team Insights"
        text="Compare team records, scoring balance, and early ranking signals without turning the page into a basic club profile."
      />
      <section className="metric-grid compact-metrics" aria-label="Team insight highlights">
        <article className="metric-card">
          <span>Teams tracked</span>
          <strong>{teams.length.toLocaleString()}</strong>
          <p>Distinct clubs in the selected season data.</p>
        </article>
        <article className="metric-card">
          <span>Top attack</span>
          <strong>{bestAttack?.goals_for ?? 0}</strong>
          <p>{bestAttack ? `${bestAttack.team_name} goals scored.` : "No team data available yet."}</p>
        </article>
        <article className="metric-card">
          <span>Tightest defence</span>
          <strong>{bestDefense?.goals_against ?? 0}</strong>
          <p>{bestDefense ? `${bestDefense.team_name} goals conceded.` : "No team data available yet."}</p>
        </article>
      </section>
      <section className="panel">
        <div className="section-heading compact">
          <div>
            <h2>Ranked team summaries</h2>
            <p>Sorted by wins, then goals scored. Each card adds win rate and goal difference for quicker comparison.</p>
          </div>
        </div>
        <div className="team-grid">
          {teams.length > 0 ? (
            teams.map((team, index) => <TeamCard key={team.team_name} rank={index + 1} team={team} />)
          ) : (
            <EmptyState message={loadState === "loading" ? "Loading team summaries." : "No team summaries returned yet."} />
          )}
        </div>
      </section>
    </>
  );
}
