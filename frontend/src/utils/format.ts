import type { MatchSummary } from "../api/types";

export function formatSeason(season: string) {
  return season.replace("_", "/");
}

export function formatDate(value: string | null) {
  if (!value) return "Date TBC";
  const dateValue = value.includes("T") ? value : `${value}T00:00:00`;
  return new Intl.DateTimeFormat("en", { day: "2-digit", month: "short", year: "numeric" }).format(
    new Date(dateValue),
  );
}

export function formatResult(result: string | null) {
  if (result === "home_win" || result === "away_win" || result === "draw") return "Full-time";
  return "Result pending";
}

export function formatScoreline(homeScore: number | null, awayScore: number | null) {
  return `${homeScore ?? "-"} - ${awayScore ?? "-"}`;
}

export function formatPercent(value: number) {
  return `${Math.round(value * 1000) / 10}%`;
}

export function matchStatus(match: MatchSummary) {
  if (match.is_administrative_result) {
    if (match.administrative_result_type === "forfeit") return "Forfeit";
    return "Administrative result";
  }
  return formatResult(match.result);
}
