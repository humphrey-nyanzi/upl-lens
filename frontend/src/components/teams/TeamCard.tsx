import type { TeamResponse } from "../../api/types";
import { Link } from "react-router-dom";
import { StatCell, StatusPill, TeamName } from "../common/EditorialRows";
import {
  formatGoalDifference,
  getTeamFixtureNote,
  getTeamGoalDifference,
  getTeamPoints,
  getTeamPointsNote,
  getTeamSlug,
  getTeamWinRate,
} from "../../utils/teams";

export function TeamCard({ rank, team }: { rank?: number; team: TeamResponse }) {
  const goalDifference = getTeamGoalDifference(team);
  const points = getTeamPoints(team);
  const winRate = Math.round(getTeamWinRate(team) * 100);
  const fixtureNote = getTeamFixtureNote(team);
  const pointsNote = getTeamPointsNote(team);
  const hasPointsCaveat = pointsNote.length > 0;

  return (
    <article className="team-card team-index-card editorial-table-row">
      <div className="team-card-header">
        <div className="team-card-title">
          {rank ? <span className="team-rank">{rank}</span> : null}
          <div>
            <TeamName className="team-card-name" label={team.team_name} />
            <span>{points} pts{hasPointsCaveat ? "*" : ""} · {winRate}% wins</span>
          </div>
        </div>
        <div className="team-card-actions">
          {team.points_adjustment !== 0 ? <StatusPill tone="warning" value="Adjustment" /> : null}
          <Link className="text-button compact-result-link" to={`/teams/${getTeamSlug(team.team_name)}`}>
            Open profile
          </Link>
        </div>
      </div>
      <div className="team-card-metrics" aria-label={`${team.team_name} team summary`}>
        <StatCell label="Record" value={`${team.wins}W ${team.draws}D ${team.losses}L`} />
        <StatCell label="Goals" value={`${team.goals_for} - ${team.goals_against}`} />
        <StatCell label="GD" value={formatGoalDifference(goalDifference)} />
        <StatCell
          label="Fixtures"
          value={`${team.matches_played}${team.expected_matches !== null && team.matches_played !== team.expected_matches ? `/${team.expected_matches}` : ""}`}
        />
      </div>
      {fixtureNote || pointsNote ? (
        <p className="team-card-note">
          {[fixtureNote, pointsNote ? `* ${pointsNote}` : ""].filter(Boolean).join(" ")}
        </p>
      ) : null}
    </article>
  );
}
