import { useEffect, useState } from "react";

import { apiClient } from "../api/client";
import type { DashboardData, LoadState } from "../app/types";
import { ALL_SEASONS_KEY, isAllSeasonsSelection, toApiSeason } from "../utils/seasonScope";

const initialData: DashboardData = {
  health: null,
  seasons: [],
  overview: null,
  goalTiming: null,
  featuredGoalTiming: null,
  matches: [],
  teams: [],
  players: [],
};

export function useDashboardData() {
  const [data, setData] = useState<DashboardData>(initialData);
  const [selectedSeason, setSelectedSeason] = useState("");
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let ignore = false;

    async function loadInitialData() {
      setLoadState("loading");
      setErrorMessage("");

      try {
        const [health, seasons, featuredGoalTiming] = await Promise.all([
          apiClient.getHealth(),
          apiClient.getSeasons(),
          apiClient.getGoalTimingInsight(),
        ]);
        const defaultSeason = seasons.at(-1)?.season ?? "";

        if (!ignore) {
          setData((current) => ({ ...current, health, seasons, featuredGoalTiming }));
          setSelectedSeason(defaultSeason);
        }
      } catch (error) {
        if (!ignore) {
          setLoadState("error");
          setErrorMessage(error instanceof Error ? error.message : "The data service could not be reached.");
        }
      }
    }

    void loadInitialData();

    return () => {
      ignore = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedSeason) return;

    let ignore = false;

    async function loadSeasonData() {
      setLoadState("loading");
      setErrorMessage("");
      const apiSeason = toApiSeason(selectedSeason);

      try {
        const [overview, goalTiming, matches, teams, players] = await Promise.all([
          apiClient.getSeasonOverview(apiSeason),
          apiClient.getGoalTimingInsight(apiSeason),
          apiClient.getMatches(apiSeason, 500),
          apiClient.getTeams(apiSeason, 500),
          apiClient.getPlayers(apiSeason, 200),
        ]);

        if (!ignore) {
          setData((current) => ({ ...current, overview, goalTiming, matches, teams, players }));
          setLoadState("success");
        }
      } catch (error) {
        if (!ignore) {
          setLoadState("error");
          setErrorMessage(error instanceof Error ? error.message : "Season data could not be loaded.");
        }
      }
    }

    void loadSeasonData();

    return () => {
      ignore = true;
    };
  }, [selectedSeason]);

  function refreshSeason() {
    if (!selectedSeason) return;

    setLoadState("loading");
    const apiSeason = toApiSeason(selectedSeason);
    void Promise.all([
      apiClient.getHealth().then((health) => setData((current) => ({ ...current, health }))),
      apiClient
        .getGoalTimingInsight()
        .then((featuredGoalTiming) => setData((current) => ({ ...current, featuredGoalTiming }))),
      apiClient
        .getSeasonOverview(apiSeason)
        .then((seasonOverview) => setData((current) => ({ ...current, overview: seasonOverview }))),
      apiClient
        .getGoalTimingInsight(apiSeason)
        .then((seasonGoalTiming) => setData((current) => ({ ...current, goalTiming: seasonGoalTiming }))),
      apiClient.getMatches(apiSeason, 500).then((matches) => setData((current) => ({ ...current, matches }))),
      apiClient.getTeams(apiSeason, 500).then((teams) => setData((current) => ({ ...current, teams }))),
      apiClient.getPlayers(apiSeason, 200).then((players) => setData((current) => ({ ...current, players }))),
    ])
      .then(() => setLoadState("success"))
      .catch((error) => {
        setLoadState("error");
        setErrorMessage(error instanceof Error ? error.message : "Refresh failed.");
      });
  }

  const selectedSeasonInfo = isAllSeasonsSelection(selectedSeason)
    ? {
        season: ALL_SEASONS_KEY,
        match_count: data.seasons.reduce((total, season) => total + season.match_count, 0),
        first_match_date: data.seasons[0]?.first_match_date ?? null,
        last_match_date: data.seasons.at(-1)?.last_match_date ?? null,
        team_count: data.overview?.team_count ?? 0,
      }
    : data.seasons.find((season) => season.season === selectedSeason);
  const expectedScopeKey = isAllSeasonsSelection(selectedSeason) ? "all" : selectedSeason;
  const overview = data.overview?.scope_key === expectedScopeKey ? data.overview : null;
  const goalTiming = data.goalTiming?.scope_key === expectedScopeKey ? data.goalTiming : null;
  const apiOnline = data.health?.status === "ok" && data.health.database === "ok";

  return {
    apiOnline,
    data,
    errorMessage,
    featuredGoalTiming: data.featuredGoalTiming,
    goalTiming,
    loadState,
    overview,
    refreshSeason,
    selectedSeason,
    selectedSeasonInfo,
    setSelectedSeason,
  };
}
