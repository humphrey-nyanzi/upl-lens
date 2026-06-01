import type { TeamResponse } from "../../api/types";
import { Link } from "react-router-dom";
import { TeamMarker } from "../common/TeamMarker";
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
    <article className="team-card team-index-card">
      <div className="team-card-header">
        <div className="team-card-title">
          {rank ? <span className="team-rank">{rank}</span> : null}
          <TeamMarker label={team.team_name} />
          <div>
            <strong>{team.team_name}</strong>
            <span>
              {points} pts{hasPointsCaveat ? "*" : ""} · {winRate}% wins
            </span>
          </div>
        </div>
        <Link className="text-button compact-result-link" to={`/teams/${getTeamSlug(team.team_name)}`}>
          Open profile
        </Link>
      </div>
      <div className="team-card-metrics" aria-label={`${team.team_name} team summary`}>
        <div>
          <span>Record</span>
          <strong>{team.wins}W {team.draws}D {team.losses}L</strong>
        </div>
        <div>
          <span>Goals</span>
          <strong>{team.goals_for}:{team.goals_against}</strong>
        </div>
        <div>
          <span>GD</span>
          <strong>{formatGoalDifference(goalDifference)}</strong>
        </div>
        <div>
          <span>Fixtures</span>
          <strong>
            {team.matches_played}
            {team.expected_matches !== null && team.matches_played !== team.expected_matches ? `/${team.expected_matches}` : ""}
          </strong>
        </div>
      </div>
      {fixtureNote || pointsNote ? (
        <p className="team-card-note">
          {[fixtureNote, pointsNote ? `* ${pointsNote}` : ""].filter(Boolean).join(" ")}
        </p>
      ) : null}
    </article>
  );
}
