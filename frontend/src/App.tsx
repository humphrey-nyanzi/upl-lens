import React, { Suspense, lazy } from "react";
import type { PageProps } from "./app/types";
import { AppShell } from "./components/navigation/AppShell";
import { useDashboardData } from "./hooks/useDashboardData";
import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import type { PageKey } from "./app/types";

const GoalTimingPage = lazy(() => import("./pages/GoalTimingPage").then((m) => ({ default: m.GoalTimingPage })));
const MatchExplorerPage = lazy(() => import("./pages/MatchExplorerPage").then((m) => ({ default: m.MatchExplorerPage })));
const MethodologyPage = lazy(() => import("./pages/MethodologyPage").then((m) => ({ default: m.MethodologyPage })));
const OverviewPage = lazy(() => import("./pages/OverviewPage").then((m) => ({ default: m.OverviewPage })));
const TeamInsightsPage = lazy(() => import("./pages/TeamInsightsPage").then((m) => ({ default: m.TeamInsightsPage })));
const MatchDetailPage = lazy(() => import("./pages/MatchDetailPage").then((m) => ({ default: m.default })));
const PlayersPage = lazy(() => import("./pages/PlayersPage").then((m) => ({ default: m.PlayersPage })));
const PlayerDetailPage = lazy(() => import("./pages/PlayerDetailPage").then((m) => ({ default: m.default })));
const TeamDetailPage = lazy(() => import("./pages/TeamDetailPage").then((m) => ({ default: m.default })));
const InsightsListPage = lazy(() => import("./pages/InsightsListPage").then((m) => ({ default: m.InsightsListPage })));
const InsightsDetailWrapper = lazy(() => import("./pages/InsightsDetailWrapper").then((m) => ({ default: m.InsightsDetailWrapper })));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage").then((m) => ({ default: m.NotFoundPage })));
const TrendsPage = lazy(() => import("./pages/TrendsPage").then((m) => ({ default: m.TrendsPage })));

function RouteLoadingFallback() {
  return (
    <section className="route-loading-state" aria-busy="true" aria-label="Loading page">
      <div className="skeleton-line short" />
      <div className="skeleton-line title" />
      <div className="skeleton-line medium" />
    </section>
  );
}

function App() {
  const {
    apiOnline,
    data,
    errorMessage,
    featuredGoalTiming,
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
    featuredGoalTiming,
    goalTiming,
    loadState,
    onPageChange: (() => {}) as (page: PageKey) => void,
    onRefresh: refreshSeason,
    onSeasonChange: setSelectedSeason,
    overview,
    selectedSeason,
    selectedSeasonInfo,
  };

  const navigate = useNavigate();
  function setPage(page: PageKey) {
    const path = page === "overview" ? "/" : `/${page}`;
    navigate(path);
  }

  // supply a working onPageChange for legacy components
  pageProps.onPageChange = setPage;
  return (
    <AppShell
      apiOnline={apiOnline}
      health={data.health}
      loadState={loadState}
      onRefresh={refreshSeason}
      onSeasonChange={setSelectedSeason}
      seasons={data.seasons}
      selectedSeason={selectedSeason}
      matches={data.matches}
      teams={data.teams}
      players={data.players}
    >
      <Suspense fallback={<RouteLoadingFallback />}>
        <Routes>
          <Route path="/" element={<OverviewPage {...pageProps} />} />
          <Route path="/matches" element={<MatchExplorerPage {...pageProps} />} />
          <Route path="/matches/:matchId" element={<MatchDetailPage {...pageProps} />} />
          <Route path="/teams" element={<TeamInsightsPage {...pageProps} />} />
          <Route path="/teams/:teamSlug" element={<TeamDetailPage {...pageProps} />} />
          <Route path="/players" element={<PlayersPage {...pageProps} />} />
          <Route path="/players/:playerSlug" element={<PlayerDetailPage {...pageProps} />} />
          <Route path="/insights" element={<InsightsListPage {...pageProps} />} />
          <Route path="/insights/:insightSlug" element={<InsightsDetailWrapper {...pageProps} />} />
          <Route path="/trends" element={<TrendsPage {...pageProps} />} />
          <Route path="/about" element={<MethodologyPage {...pageProps} />} />
          <Route path="/goal-timing" element={<Navigate to="/insights/goal-timing" replace />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </AppShell>
  );
}

export default App;
