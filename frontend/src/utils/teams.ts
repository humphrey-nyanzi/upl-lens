import type { EventResponse, MatchSummary, TeamResponse } from "../api/types";
import { slugify } from "./slugs";

export type TeamSortKey = "points" | "name" | "wins" | "goals_for" | "goals_against" | "goal_difference";

export type TeamEventSummary = {
  goals: number;
  yellowCards: number;
  redCards: number;
  substitutions: number;
};

export function getTeamSlug(teamName: string) {
  return slugify(teamName);
}

export function getTeamPoints(team: TeamResponse) {
  return team.wins * 3 + team.draws;
}

export function getTeamGoalDifference(team: TeamResponse) {
  return team.goals_for - team.goals_against;
}

export function getTeamWinRate(team: TeamResponse) {
  return team.matches_played > 0 ? team.wins / team.matches_played : 0;
}

export function formatGoalDifference(value: number) {
  return value > 0 ? `+${value}` : String(value);
}

export function sortTeams(teams: TeamResponse[], sortKey: TeamSortKey) {
  return [...teams].sort((left, right) => {
    if (sortKey === "name") return left.team_name.localeCompare(right.team_name);
    if (sortKey === "points") return getTeamPoints(right) - getTeamPoints(left) || right.wins - left.wins || right.goals_for - left.goals_for;
    if (sortKey === "goal_difference") return getTeamGoalDifference(right) - getTeamGoalDifference(left) || right.goals_for - left.goals_for;
    return right[sortKey] - left[sortKey] || left.team_name.localeCompare(right.team_name);
  });
}

export function getOpponent(match: MatchSummary, teamName: string) {
  const isHome = match.home_team === teamName;
  return {
    isHome,
    opponent: isHome ? match.away_team : match.home_team,
    teamScore: isHome ? match.home_score : match.away_score,
    opponentScore: isHome ? match.away_score : match.home_score,
  };
}

export function getTeamMatchResult(match: MatchSummary, teamName: string) {
  if (!match.result) return "Pending";
  const isHome = match.home_team === teamName;
  if (match.result === "draw") return "Draw";
  if ((match.result === "home_win" && isHome) || (match.result === "away_win" && !isHome)) return "Win";
  return "Loss";
}

export function summarizeTeamEvents(events: EventResponse[]): TeamEventSummary {
  return events.reduce<TeamEventSummary>(
    (summary, event) => ({
      goals: summary.goals + (event.event_type === "goal" ? 1 : 0),
      yellowCards: summary.yellowCards + (event.event_type === "yellow_card" ? 1 : 0),
      redCards: summary.redCards + (event.event_type === "red_card" ? 1 : 0),
      substitutions: summary.substitutions + (event.event_type === "substitution" ? 1 : 0),
    }),
    { goals: 0, yellowCards: 0, redCards: 0, substitutions: 0 },
  );
}
