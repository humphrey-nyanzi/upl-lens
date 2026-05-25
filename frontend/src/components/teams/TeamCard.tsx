import type { TeamResponse } from "../../api/types";

export function TeamCard({ rank, team }: { rank?: number; team: TeamResponse }) {
  const goalDifference = team.goals_for - team.goals_against;
  const winRate = team.matches_played > 0 ? Math.round((team.wins / team.matches_played) * 100) : 0;

  return (
    <article className="team-card">
      <div className="team-card-header">
        <strong>{rank ? `${rank}. ${team.team_name}` : team.team_name}</strong>
        <span>{winRate}% wins</span>
      </div>
      <div className="team-stat-row">
        <span>Record</span>
        <strong>
          {team.wins}W {team.draws}D {team.losses}L
        </strong>
      </div>
      <div className="team-stat-row">
        <span>Goal difference</span>
        <strong>{goalDifference > 0 ? `+${goalDifference}` : goalDifference}</strong>
      </div>
      <p>
        {team.goals_for} scored, {team.goals_against} conceded across {team.matches_played} matches.
      </p>
    </article>
  );
}
