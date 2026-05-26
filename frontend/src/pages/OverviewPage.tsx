import { useMemo } from "react";

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

  const summaryCards = [
    {
      label: "Matches covered",
      value: overview?.match_count ?? selectedSeasonInfo?.match_count ?? data.matches.length,
      detail: "Cleaned match records for this season.",
    },
    {
      label: "Timeline goals",
      value: overview?.timeline_goal_count ?? overview?.goal_count ?? 0,
      detail: "Goals from match event timelines.",
    },
    {
      label: "Teams tracked",
      value: overview?.team_count ?? selectedSeasonInfo?.team_count ?? data.teams.length,
      detail: "Clubs in official match pages.",
    },
    {
      label: "Cards logged",
      value: overview ? overview.yellow_card_count + overview.red_card_count : 0,
      detail: "Cards ready for discipline analysis.",
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
        {summaryCards.map((card, index) => (
          <KpiCard
            key={card.label}
            {...card}
            accent={index === 1 ? "gold" : index === 2 ? "green" : "neutral"}
            variant="compact"
          />
        ))}
      </section>

      <section className="overview-main-grid" aria-label="League intelligence dashboard">
        <FeaturedInsight goalTiming={goalTiming} loadState={loadState} onPageChange={onPageChange} />
        <TeamSignalPanel teams={topTeams} loadState={loadState} />
        <RecentMatchPanel matches={recentMatches} loadState={loadState} />
      </section>

      <ExplorePreview onPageChange={onPageChange} />
    </div>
  );
}
