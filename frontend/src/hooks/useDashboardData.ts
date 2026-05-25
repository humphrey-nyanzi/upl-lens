import { useEffect, useState } from "react";

import { apiClient } from "../api/client";
import type { DashboardData, LoadState } from "../app/types";

const initialData: DashboardData = {
  health: null,
  seasons: [],
  overview: null,
  goalTiming: null,
  matches: [],
  teams: [],
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
        const [health, seasons] = await Promise.all([apiClient.getHealth(), apiClient.getSeasons()]);
        const defaultSeason = seasons.at(-1)?.season ?? "";

        if (!ignore) {
          setData((current) => ({ ...current, health, seasons }));
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

      try {
        const [overview, goalTiming, matches, teams] = await Promise.all([
          apiClient.getSeasonOverview(selectedSeason),
          apiClient.getGoalTimingInsight(selectedSeason),
          apiClient.getMatches(selectedSeason, 200),
          apiClient.getTeams(selectedSeason, 200),
        ]);

        if (!ignore) {
          setData((current) => ({ ...current, overview, goalTiming, matches, teams }));
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
    void Promise.all([
      apiClient.getHealth().then((health) => setData((current) => ({ ...current, health }))),
      apiClient
        .getSeasonOverview(selectedSeason)
        .then((seasonOverview) => setData((current) => ({ ...current, overview: seasonOverview }))),
      apiClient
        .getGoalTimingInsight(selectedSeason)
        .then((seasonGoalTiming) => setData((current) => ({ ...current, goalTiming: seasonGoalTiming }))),
      apiClient.getMatches(selectedSeason, 200).then((matches) => setData((current) => ({ ...current, matches }))),
      apiClient.getTeams(selectedSeason, 200).then((teams) => setData((current) => ({ ...current, teams }))),
    ])
      .then(() => setLoadState("success"))
      .catch((error) => {
        setLoadState("error");
        setErrorMessage(error instanceof Error ? error.message : "Refresh failed.");
      });
  }

  const selectedSeasonInfo = data.seasons.find((season) => season.season === selectedSeason);
  const overview = data.overview?.season === selectedSeason ? data.overview : null;
  const goalTiming = data.goalTiming?.season === selectedSeason ? data.goalTiming : null;
  const apiOnline = data.health?.status === "ok" && data.health.database === "ok";

  return {
    apiOnline,
    data,
    errorMessage,
    goalTiming,
    loadState,
    overview,
    refreshSeason,
    selectedSeason,
    selectedSeasonInfo,
    setSelectedSeason,
  };
}
