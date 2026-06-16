import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { apiClient } from "../api/client";
import type {
  MatchIntelligenceSummary,
  OverviewIntelligenceResponse,
  SeasonTrendsResponse,
} from "../api/types";
import type { PageProps } from "../app/types";
import { ErrorPanel } from "../components/common/ErrorPanel";
import { KpiCard } from "../components/common/KpiCard";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { FeaturedInsight } from "../components/overview/FeaturedInsight";
import { HeroSection } from "../components/overview/HeroSection";
import { RecentMatchPanel, TeamSignalPanel } from "../components/overview/OverviewPanels";
import { toApiSeason } from "../utils/seasonScope";
import { Goal, CalendarDays, CircleCheckBig, ChartColumnBig } from "lucide-react";

type IntelligenceState = "loading" | "success" | "partial" | "error";

type OverviewModules = {
  intelligence: OverviewIntelligenceResponse | null;
  matches: MatchIntelligenceSummary[];
  trends: SeasonTrendsResponse | null;
};

type OverviewModulesViewState = {
  modules: OverviewModules;
  requestKey: string;
  status: Exclude<IntelligenceState, "loading">;
};

const emptyModules: OverviewModules = {
  intelligence: null,
  matches: [],
  trends: null,
};

function OverviewSkeleton() {
  return (
    <div className="overview-control-room" aria-busy="true">
      <section className="hero-panel skeleton-panel" aria-label="Loading overview">
        <div className="skeleton-line short" />
        <div className="skeleton-line title" />
        <div className="skeleton-line" />
        <div className="skeleton-line medium" />
      </section>
      <section className="overview-pulse-grid">
        {[0, 1, 2, 3, 4, 5].map((item) => (
          <article className="skeleton-card metric-delta" key={item}>
            <div className="skeleton-line short" />
            <div className="skeleton-line number" />
            <div className="skeleton-line" />
          </article>
        ))}
      </section>
      <section className="skeleton-card overview-section-skeleton">
        <div className="skeleton-line title" />
        <div className="skeleton-line" />
        <div className="skeleton-line medium" />
      </section>
    </div>
  );
}

function ExploreCard({ description, href, title }: { description: string; href: string; title: string }) {
  return (
    <Link className="overview-explore-card" to={href}>
      <strong>{title}</strong>
      <p>{description}</p>
      <span>Open section</span>
    </Link>
  );
}

export function OverviewPage({
  data,
  errorMessage,
  featuredGoalTiming,
  loadState,
  onPageChange,
  overview,
  selectedSeason,
  selectedSeasonInfo,
}: PageProps) {
  const [modulesView, setModulesView] = useState<OverviewModulesViewState>({
    modules: emptyModules,
    requestKey: "",
    status: "success",
  });
  const apiSeason = toApiSeason(selectedSeason);
  const modulesRequestKey = selectedSeason;

  useEffect(() => {
    let ignore = false;

    Promise.allSettled([
      apiClient.getOverviewIntelligence(apiSeason),
      apiClient.getMatchIntelligence(apiSeason, { sort: "interest", limit: 6 }),
      apiClient.getSeasonTrends(),
    ]).then(([overviewResult, matchesResult, trendsResult]) => {
      if (ignore) return;

      const nextModules: OverviewModules = {
        intelligence: overviewResult.status === "fulfilled" ? overviewResult.value : null,
        matches: matchesResult.status === "fulfilled" ? matchesResult.value : [],
        trends: trendsResult.status === "fulfilled" ? trendsResult.value : null,
      };
      const successCount = [overviewResult, matchesResult, trendsResult].filter((result) => result.status === "fulfilled").length;

      setModulesView({
        modules: nextModules,
        requestKey: modulesRequestKey,
        status: successCount === 3 ? "success" : successCount > 0 ? "partial" : "error",
      });
    });

    return () => {
      ignore = true;
    };
  }, [apiSeason, modulesRequestKey]);

  const moduleState: IntelligenceState = modulesView.requestKey === modulesRequestKey ? modulesView.status : "loading";
  const modules = modulesView.requestKey === modulesRequestKey ? modulesView.modules : emptyModules;

  const trendForSeason = useMemo(
    () => modules.trends?.seasons.find((season) => season.season === selectedSeason || season.season === apiSeason) ?? null,
    [apiSeason, modules.trends, selectedSeason],
  );

  const pulse = modules.intelligence?.season_pulse;
  const matchCount = pulse?.matches_covered ?? overview?.match_count ?? selectedSeasonInfo?.match_count ?? data.matches.length;
  const goalsPerMatch =
    pulse?.goals_per_match ??
    trendForSeason?.goals_per_match ??
    (matchCount > 0 && overview ? overview.scoreline_goal_count / matchCount : null);
  const timelineCoverage = pulse?.timeline_coverage_share ?? trendForSeason?.timeline_coverage_share ?? null;
  const goalsScored = overview?.scoreline_goal_count ?? modules.matches.reduce((total, match) => total + (match.goal_count ?? 0), 0);
  const completedMatches = data.matches.filter((match) => match.home_score !== null && match.away_score !== null).length;
  const recentCompletedMatches = data.matches
    .filter((match) => match.home_score !== null && match.away_score !== null)
    .toSorted((left, right) => (right.match_date ?? "").localeCompare(left.match_date ?? "") || right.match_id - left.match_id)
    .slice(0, 5);

  const initialLoading = loadState === "loading" && overview === null && moduleState === "loading";
  if (initialLoading) return <OverviewSkeleton />;

  return (
    <div className="overview-page overview-control-room">
      <HeroSection />

      {loadState === "error" ? <ErrorPanel errorMessage={errorMessage} /> : null}

      <section className="overview-kpi-grid" aria-label="Season summary">
        <KpiCard accent="green" context="Cleaned match records for this season." icon={<CalendarDays size={18} />} label="Matches played" value={matchCount} />
        <KpiCard
          accent="green"
          context="Goals from available scorelines and event-backed records."
          icon={<Goal size={18} />}
          label="Goals scored"
          trend={goalsPerMatch !== null && goalsPerMatch !== undefined ? `${goalsPerMatch.toFixed(2)} per match` : undefined}
          value={goalsScored}
        />
        <KpiCard accent="green" context="Matches with a recorded scoreline." icon={<CircleCheckBig size={18} />} label="Completed" value={completedMatches} />
        <KpiCard
          accent="green"
          context="Average goals per completed match this season."
          icon={<ChartColumnBig size={18} />}
          label="Avg. goals/match"
          value={goalsPerMatch !== null && goalsPerMatch !== undefined ? goalsPerMatch.toFixed(2) : "Unavailable"}
        />
      </section>

      <section className="overview-story-grid">
        <div className="overview-story-card overview-story-card-recent">
          <RecentMatchPanel loadState={loadState} matches={recentCompletedMatches} onPageChange={onPageChange} />
        </div>
        <div className="overview-story-card overview-story-card-featured">
          <FeaturedInsight goalTiming={featuredGoalTiming} loadState={loadState} onPageChange={onPageChange} />
        </div>
        <div className="overview-story-card overview-story-card-signals">
          <TeamSignalPanel loadState={loadState} matches={data.matches} onPageChange={onPageChange} teams={data.teams} />
        </div>
      </section>

      <section className="panel overview-product-map">
        <ReportSectionHeader title="Explore more" text="Each section turns official match records into a different kind of football intelligence." />
        <div className="overview-explore-grid">
          <ExploreCard href="/insights" title="Insights Library" description="Open promoted insights and key takeaways." />
          <ExploreCard href="/matches" title="Match Evidence" description="Review recent scorelines and match-by-match context." />
          <ExploreCard href="/teams" title="Team Summaries" description="Compare team form, results, and scoring output." />
          <ExploreCard href="/trends" title="Dive Deeper" description="Move from overview into dedicated analysis pages." />
        </div>
      </section>
    </div>
  );
}
