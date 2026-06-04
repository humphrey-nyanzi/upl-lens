import type { SeasonResponse } from "../api/types";

export const ALL_SEASONS_KEY = "__all__";

export function isAllSeasonsSelection(season: string) {
  return season === ALL_SEASONS_KEY;
}

export function toApiSeason(season: string) {
  if (!season || isAllSeasonsSelection(season)) return undefined;
  return season;
}

export function getSelectedSeasonLabel(selectedSeason: string, selectedSeasonInfo?: Pick<SeasonResponse, "season">) {
  if (isAllSeasonsSelection(selectedSeason)) return "All seasons";
  return (selectedSeasonInfo?.season ?? selectedSeason).replace("_", "/");
}
