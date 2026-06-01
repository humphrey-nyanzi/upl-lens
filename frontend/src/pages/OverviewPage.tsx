import { useMemo } from "react";
import { Goal, Trophy, Home, BarChartBig, Grip } from "lucide-react";

import type { PageProps } from "../app/types";
import { ErrorPanel } from "../components/common/ErrorPanel";
import { KpiCard } from "../components/common/KpiCard";
import { OverviewSkeleton } from "../components/common/Skeletons";
import { FeaturedInsight } from "../components/overview/FeaturedInsight";
import { HeroSection } from "../components/overview/HeroSection";
import {
  ExplorePreview,
  RecentMatchPanel,
  TeamSignalPanel,
} from "../components/overview/OverviewPanels";

export function OverviewPage({
  data,
  errorMessage,
  goalTiming,
  loadState,
  onPageChange,
  overview,
  selectedSeasonInfo,
}: PageProps) {
  const initialLoading = loadState === "loading" && overview === null;
  const completedMatches = data.matches.filter((match) => match.result !== null);
  const homeWins = completedMatches.filter((match) => match.result === "home_win").length;
  const homeWinRate = completedMatches.length > 0 ? Math.round((homeWins / completedMatches.length) * 100) : 0;
  const averageGoals =
    completedMatches.length > 0
      ? completedMatches.reduce((total, match) => total + (match.total_goals ?? 0), 0) / completedMatches.length
      : 0;

  const summaryCards = [
    {
      label: "Matches Played",
      value: overview?.match_count ?? selectedSeasonInfo?.match_count ?? data.matches.length,
      detail: "Cleaned match records for this season.",
      icon: <Goal size={18} />,
      accent: "green" as const,
    },
    {
      label: "Goals Scored",
      value: overview?.timeline_goal_count ?? overview?.goal_count ?? 0,
      detail: "Goals from match event timelines.",
      meta: completedMatches.length > 0 ? `${averageGoals.toFixed(2)} per match` : undefined,
      icon: <Trophy size={18} />,
      accent: "green" as const,
    },
    {
      label: "Home Win %",
      value: `${homeWinRate}%`,
      detail: "Home team victory rate this season.",
      icon: <Home size={18} />,
      accent: "green" as const,
    },
    {
      label: "Avg. Goals/Match",
      value: averageGoals.toFixed(2),
      detail: "Average goals per match this season.",
      icon: <BarChartBig size={18} />,
      accent: "green" as const,
    },
  ];

  const topTeams = useMemo(() => {
    return [...data.teams]
      .sort((left, right) => {
        const leftPoints = left.wins * 3 + left.draws;
        const rightPoints = right.wins * 3 + right.draws;

        return rightPoints - leftPoints || right.goals_for - left.goals_for;
      })
      .slice(0, 5);
  }, [data.teams]);

  const recentMatches = useMemo(() => {
    return [...data.matches]
      .sort((left, right) => {
        const leftDate = left.match_date ?? "";
        const rightDate = right.match_date ?? "";
        return rightDate.localeCompare(leftDate) || right.match_id - left.match_id;
      })
      .slice(0, 4);
  }, [data.matches]);

  if (initialLoading) {
    return <OverviewSkeleton />;
  }

  return (
    <div className="overview-page">
      <HeroSection />

      {loadState === "error" ? <ErrorPanel errorMessage={errorMessage} /> : null}

      <section className="metric-grid overview-kpi-grid" aria-label="Selected season intelligence summary">
        {summaryCards.map((card) => (
          <KpiCard
            key={card.label}
            {...card}
            variant="compact"
          />
        ))}
      </section>

      <section className="overview-main-grid" aria-label="League intelligence dashboard">
        <FeaturedInsight goalTiming={goalTiming} loadState={loadState} onPageChange={onPageChange} />
        <div className="overview-side-stack">
          <TeamSignalPanel teams={topTeams} loadState={loadState} onPageChange={onPageChange} />
          <RecentMatchPanel matches={recentMatches} loadState={loadState} onPageChange={onPageChange} />
        </div>
      </section>

      <ExplorePreview onPageChange={onPageChange} />
    </div>
  );
}
