import React from "react";
import type { PageProps } from "../app/types";
import { useParams } from "react-router-dom";

function slugify(value: string) {
  return value.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

export default function TeamDetailPage({ data }: Pick<PageProps, "data">) {
  const { teamSlug } = useParams();
  const team = data.teams.find((row) => slugify(row.team_name) === teamSlug);

  if (!team) {
    return (
      <section className="panel">
        <h2>Team not found</h2>
        <p>The selected team is not available in the current season dataset.</p>
      </section>
    );
  }

  const goalDifference = team.goals_for - team.goals_against;
  const points = team.wins * 3 + team.draws;
  const winRate = team.matches_played > 0 ? Math.round((team.wins / team.matches_played) * 100) : 0;

  return (
    <section className="panel">
      <h2>{team.team_name}</h2>
      <p>{points} pts · {team.wins}W {team.draws}D {team.losses}L · {winRate}% wins</p>
      <p>
        Goals: {team.goals_for} scored, {team.goals_against} conceded, {goalDifference >= 0 ? "+" : ""}
        {goalDifference} difference.
      </p>
    </section>
  );
}
