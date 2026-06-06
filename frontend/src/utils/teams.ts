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
  const fallbackPoints = team.wins * 3 + team.draws + (team.points_adjustment ?? 0);
  if ((team.official_points ?? 0) === 0 && fallbackPoints > 0) return fallbackPoints;
  return team.official_points ?? fallbackPoints;
}

export function getTeamGoalDifference(team: TeamResponse) {
  return team.goals_for - team.goals_against;
}

export function getTeamWinRate(team: TeamResponse) {
  const playedMatches = team.played_matches > 0 ? team.played_matches : team.matches_played;
  return playedMatches > 0 ? team.wins / playedMatches : 0;
}

export function getTeamFixtureNote(team: TeamResponse) {
  const parts: string[] = [];
  if (team.expected_matches !== null && team.matches_played < team.expected_matches) {
    parts.push(`${team.matches_played}/${team.expected_matches} fixtures recorded`);
  }
  if (team.administrative_matches > 0) {
    parts.push(
      `${team.played_matches} played on pitch, ${team.administrative_matches} administrative result${team.administrative_matches === 1 ? "" : "s"}`,
    );
  }
  if (team.missing_matches > 0) {
    parts.push(`${team.missing_matches} fixture${team.missing_matches === 1 ? "" : "s"} missing`);
  }
  return parts.join(" · ");
}

export function getTeamPointsNote(team: TeamResponse) {
  const parts: string[] = [];
  if (team.administrative_points > 0) {
    parts.push(`${team.administrative_points} point${team.administrative_points === 1 ? "" : "s"} from administrative result${team.administrative_matches === 1 ? "" : "s"}`);
  }
  if (team.points_adjustment !== 0) {
    const prefix = team.points_adjustment > 0 ? "+" : "";
    parts.push(`${prefix}${team.points_adjustment} official points adjustment`);
  }
  if (team.points_note) {
    parts.push(team.points_note);
  }
  return parts.join(" · ");
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
