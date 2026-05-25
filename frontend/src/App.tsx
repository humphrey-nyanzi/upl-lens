import type { PageProps } from "./app/types";
import { AppShell } from "./components/navigation/AppShell";
import { useDashboardData } from "./hooks/useDashboardData";
import { useHashNavigation } from "./hooks/useHashNavigation";
import { GoalTimingPage } from "./pages/GoalTimingPage";
import { MatchExplorerPage } from "./pages/MatchExplorerPage";
import { MethodologyPage } from "./pages/MethodologyPage";
import { OverviewPage } from "./pages/OverviewPage";
import { TeamInsightsPage } from "./pages/TeamInsightsPage";

function App() {
  const { currentPage, setPage } = useHashNavigation();
  const {
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
  } = useDashboardData();

  const pageProps: PageProps = {
    apiOnline,
    data,
    errorMessage,
    goalTiming,
    loadState,
    onPageChange: setPage,
    onRefresh: refreshSeason,
    onSeasonChange: setSelectedSeason,
    overview,
    selectedSeason,
    selectedSeasonInfo,
  };

  return (
    <AppShell
      apiOnline={apiOnline}
      currentPage={currentPage}
      loadState={loadState}
      onPageChange={setPage}
      onRefresh={refreshSeason}
      onSeasonChange={setSelectedSeason}
      seasons={data.seasons}
      selectedSeason={selectedSeason}
    >
      {currentPage === "overview" ? <OverviewPage {...pageProps} /> : null}
      {currentPage === "goal-timing" ? <GoalTimingPage {...pageProps} /> : null}
      {currentPage === "matches" ? <MatchExplorerPage {...pageProps} /> : null}
      {currentPage === "teams" ? <TeamInsightsPage {...pageProps} /> : null}
      {currentPage === "methodology" ? <MethodologyPage {...pageProps} /> : null}
    </AppShell>
  );
}

export default App;
