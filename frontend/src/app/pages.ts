import type { PageDefinition, PageKey } from "./types";

export const pages: PageDefinition[] = [
  { key: "overview", label: "League Overview", shortLabel: "Overview" },
  { key: "goal-timing", label: "Goal Timing", shortLabel: "Goals" },
  { key: "matches", label: "Match Explorer", shortLabel: "Matches" },
  { key: "teams", label: "Team Insights", shortLabel: "Teams" },
  { key: "methodology", label: "Data Notes", shortLabel: "Notes" },
];

export function parsePageHash(): PageKey {
  const value = window.location.hash.replace(/^#\/?/, "");
  return pages.some((page) => page.key === value) ? (value as PageKey) : "overview";
}
