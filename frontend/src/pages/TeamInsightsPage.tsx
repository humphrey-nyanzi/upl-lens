import type { TeamResponse } from "../api/types";
import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { RankingList } from "../components/common/RankingList";
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
  const topAttackItems = [...data.teams]
    .sort((left, right) => right.goals_for - left.goals_for)
    .slice(0, 5)
    .map((team) => ({
      context: `${team.matches_played} matches`,
      label: team.team_name,
      value: team.goals_for,
    }));

  return (
    <>
      <PageIntro
        eyebrow="Team trends"
        title="Team Insights"
        text="Compare team records, scoring balance, and early ranking signals without turning the page into a basic club profile."
      />
      <section className="metric-grid compact-metrics" aria-label="Team insight highlights">
        <KpiCard label="Teams tracked" value={teams.length} detail="Distinct clubs in the selected season data." />
        <KpiCard accent="green" label="Top attack" value={bestAttack?.goals_for ?? 0} detail={bestAttack ? `${bestAttack.team_name} goals scored.` : "No team data available yet."} />
        <KpiCard accent="gold" label="Tightest defence" value={bestDefense?.goals_against ?? 0} detail={bestDefense ? `${bestDefense.team_name} goals conceded.` : "No team data available yet."} />
      </section>
      {topAttackItems.length > 0 ? <RankingList title="Top 5 attacks" items={topAttackItems} actionLabel="Compare teams" /> : null}
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
