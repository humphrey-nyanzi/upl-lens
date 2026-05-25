import type { PageProps } from "./app/types";
import { TopNavigation } from "./components/navigation/TopNavigation";
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
    <main className="app-shell">
      <TopNavigation apiOnline={apiOnline} currentPage={currentPage} onPageChange={setPage} />
      <section className="workspace" aria-live={loadState === "loading" ? "polite" : "off"}>
        {currentPage === "overview" ? <OverviewPage {...pageProps} /> : null}
        {currentPage === "goal-timing" ? <GoalTimingPage {...pageProps} /> : null}
        {currentPage === "matches" ? <MatchExplorerPage {...pageProps} /> : null}
        {currentPage === "teams" ? <TeamInsightsPage {...pageProps} /> : null}
        {currentPage === "methodology" ? <MethodologyPage {...pageProps} /> : null}
      </section>
    </main>
  );
}

export default App;
