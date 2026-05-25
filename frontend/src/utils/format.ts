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
  if (result === "home_win") return "Home win";
  if (result === "away_win") return "Away win";
  if (result === "draw") return "Draw";
  return "Result pending";
}

export function formatPercent(value: number) {
  return `${Math.round(value * 1000) / 10}%`;
}

export function matchStatus(match: MatchSummary) {
  if (match.is_forfeit) return "Forfeit";
  return formatResult(match.result);
}
