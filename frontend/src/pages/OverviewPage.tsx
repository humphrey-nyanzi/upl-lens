import { useMemo } from "react";
import { BarChartBig, CircleCheck, Goal, Trophy } from "lucide-react";

import type { PageProps } from "../app/types";
import { ErrorPanel } from "../components/common/ErrorPanel";
import { KpiCard } from "../components/common/KpiCard";
import { FeaturedInsight } from "../components/overview/FeaturedInsight";
import { HeroSection } from "../components/overview/HeroSection";
import {
  ExplorePreview,
  RecentMatchPanel,
  TeamSignalPanel,
} from "../components/overview/OverviewPanels";
import { getTeamPoints } from "../utils/teams";

function OverviewSkeleton() {
  return (
    <>
      <section className="hero-panel skeleton-panel" aria-busy="true" aria-label="Loading league overview">
        <div className="skeleton-line short" />
        <div className="skeleton-line title" />
        <div className="skeleton-line" />
        <div className="skeleton-line medium" />
      </section>
      <section className="metric-grid" aria-label="Loading summary cards">
        {[0, 1, 2, 3].map((item) => (
          <article className="metric-card skeleton-card" key={item}>
            <div className="skeleton-line short" />
            <div className="skeleton-line number" />
            <div className="skeleton-line" />
          </article>
        ))}
      </section>
      <section className="featured-insight skeleton-card">
        <div className="skeleton-line short" />
        <div className="skeleton-line title" />
        <div className="skeleton-line" />
        <p className="empty-state">Loading the latest league data. The service may be waking up.</p>
      </section>
    </>
  );
}

export function OverviewPage({
  data,
  errorMessage,
  featuredGoalTiming,
  loadState,
  onPageChange,
  overview,
  selectedSeasonInfo,
}: PageProps) {
  const initialLoading = loadState === "loading" && overview === null;
  const completedMatches = data.matches.filter((match) => match.result !== null);
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
      label: "Completed",
      value: completedMatches.length,
      detail: "Matches with a recorded scoreline.",
      icon: <CircleCheck size={18} />,
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
        const leftPoints = getTeamPoints(left);
        const rightPoints = getTeamPoints(right);

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
        <FeaturedInsight goalTiming={featuredGoalTiming} loadState={loadState} onPageChange={onPageChange} />
        <div className="overview-side-stack">
          <TeamSignalPanel teams={topTeams} matches={data.matches} loadState={loadState} onPageChange={onPageChange} />
          <RecentMatchPanel matches={recentMatches} loadState={loadState} onPageChange={onPageChange} />
        </div>
      </section>

      <ExplorePreview onPageChange={onPageChange} />
    </div>
  );
}
