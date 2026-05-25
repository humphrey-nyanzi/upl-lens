import { useMemo } from "react";

import type { PageProps } from "../app/types";
import { ErrorPanel } from "../components/common/ErrorPanel";
import { KpiCard } from "../components/common/KpiCard";
import { OverviewSkeleton } from "../components/common/Skeletons";
import { FeaturedInsight } from "../components/overview/FeaturedInsight";
import { HeroSection } from "../components/overview/HeroSection";
import {
  EventSignalPanel,
  ExplorePreview,
  OverviewDataNote,
  RecentMatchPanel,
  TeamSignalPanel,
} from "../components/overview/OverviewPanels";

export function OverviewPage({
  apiOnline,
  data,
  errorMessage,
  goalTiming,
  loadState,
  onPageChange,
  overview,
  selectedSeason,
  selectedSeasonInfo,
}: PageProps) {
  const initialLoading = loadState === "loading" && overview === null;

  const summaryCards = [
    {
      label: "Matches covered",
      value: overview?.match_count ?? selectedSeasonInfo?.match_count ?? data.matches.length,
      detail: "Cleaned match records available for the selected season.",
    },
    {
      label: "Timeline goals",
      value: overview?.timeline_goal_count ?? overview?.goal_count ?? 0,
      detail: "Goals recorded from match event timelines.",
    },
    {
      label: "Teams tracked",
      value: overview?.team_count ?? selectedSeasonInfo?.team_count ?? data.teams.length,
      detail: "Distinct clubs appearing in official match pages.",
    },
    {
      label: "Cards logged",
      value: overview ? overview.yellow_card_count + overview.red_card_count : 0,
      detail: "Cards available for future discipline analysis.",
    },
  ];

  const eventBreakdown = useMemo(() => {
    return (
      overview?.event_breakdown.map((item) => ({
        eventType: item.event_type,
        label: item.label,
        count: item.count,
      })) ?? []
    );
  }, [overview]);

  const topTeams = useMemo(() => {
    return [...data.teams]
      .sort((left, right) => right.wins - left.wins || right.goals_for - left.goals_for)
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
    <>
      <HeroSection
        apiOnline={apiOnline}
        selectedSeason={selectedSeason}
        selectedSeasonInfo={selectedSeasonInfo}
        overview={overview}
        loadState={loadState}
        onPageChange={onPageChange}
      />

      {loadState === "error" ? <ErrorPanel errorMessage={errorMessage} /> : null}

      <section className="metric-grid" aria-label="Selected season intelligence summary">
        {summaryCards.map((card, index) => (
          <KpiCard key={card.label} {...card} accent={index === 1 ? "gold" : index === 2 ? "green" : "neutral"} />
        ))}
      </section>

      <FeaturedInsight goalTiming={goalTiming} loadState={loadState} onPageChange={onPageChange} />

      <section className="overview-grid" aria-label="League patterns preview">
        <TeamSignalPanel teams={topTeams} loadState={loadState} />
        <EventSignalPanel eventBreakdown={eventBreakdown} />
      </section>

      <ExplorePreview onPageChange={onPageChange} />

      <section className="overview-grid" aria-label="Recent matches and data notes">
        <RecentMatchPanel matches={recentMatches} loadState={loadState} />
        <OverviewDataNote onPageChange={onPageChange} selectedSeasonInfo={selectedSeasonInfo} overview={overview} />
      </section>
    </>
  );
}
