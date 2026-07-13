import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  CalendarDays,
  ChartColumnBig,
  Clock3,
  Goal,
  ShieldCheck,
  Users,
} from "lucide-react";

import { apiClient } from "../api/client";
import type {
  MatchIntelligenceSummary,
  OverviewIntelligenceResponse,
} from "../api/types";
import type { PageProps } from "../app/types";
import { ErrorPanel } from "../components/common/ErrorPanel";
import { KpiCard } from "../components/common/KpiCard";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { FeaturedInsight } from "../components/overview/FeaturedInsight";
import { HeroSection } from "../components/overview/HeroSection";
import {
  OverviewCoveragePanel,
  OverviewNoticePanel,
  RecentSignalMatchesPanel,
  TeamSignalsPanel,
  type OverviewModuleState,
} from "../components/overview/OverviewIntelligencePanels";
import { formatPercent } from "../utils/format";
import { getSelectedSeasonLabel, toApiSeason } from "../utils/seasonScope";

type RequestState = Exclude<OverviewModuleState, "partial">;

type OverviewModules = {
  intelligence: OverviewIntelligenceResponse | null;
  matches: MatchIntelligenceSummary[];
};

type OverviewModulesViewState = {
  intelligenceState: RequestState;
  matchesState: OverviewModuleState;
  modules: OverviewModules;
  requestKey: string | null;
};

const emptyModules: OverviewModules = {
  intelligence: null,
  matches: [],
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

function ExploreCard({
  description,
  href,
  title,
}: {
  description: string;
  href: string;
  title: string;
}) {
  return (
    <Link className="overview-explore-card" to={href}>
      <strong>{title}</strong>
      <p>{description}</p>
      <span>Open section</span>
    </Link>
  );
}

export function OverviewPage({
  errorMessage,
  featuredGoalTiming,
  loadState,
  onPageChange,
  overview,
  selectedSeason,
  selectedSeasonInfo,
}: PageProps) {
  const [modulesView, setModulesView] = useState<OverviewModulesViewState>({
    intelligenceState: "loading",
    matchesState: "loading",
    modules: emptyModules,
    requestKey: null,
  });
  const apiSeason = toApiSeason(selectedSeason);
  const modulesRequestKey = selectedSeason;
  const seasonLabel = getSelectedSeasonLabel(selectedSeason, selectedSeasonInfo);

  useEffect(() => {
    if (!modulesRequestKey) return;

    let ignore = false;

    Promise.allSettled([
      apiClient.getOverviewIntelligence(apiSeason),
      apiClient.getMatchIntelligence(apiSeason, { sort: "interest", limit: 6 }),
    ]).then(([overviewResult, matchesResult]) => {
      if (ignore) return;

      const intelligence =
        overviewResult.status === "fulfilled" ? overviewResult.value : null;
      const overviewMatches = intelligence?.recent_signal_matches ?? [];
      const matches =
        matchesResult.status === "fulfilled"
          ? matchesResult.value
          : overviewMatches;

      setModulesView({
        intelligenceState:
          overviewResult.status === "fulfilled" ? "success" : "error",
        matchesState:
          matchesResult.status === "fulfilled"
            ? "success"
            : overviewMatches.length > 0
              ? "partial"
              : "error",
        modules: {
          intelligence,
          matches,
        },
        requestKey: modulesRequestKey,
      });
    });

    return () => {
      ignore = true;
    };
  }, [apiSeason, modulesRequestKey]);

  const intelligenceState: RequestState =
    modulesView.requestKey === modulesRequestKey
      ? modulesView.intelligenceState
      : "loading";
  const matchesState: OverviewModuleState =
    modulesView.requestKey === modulesRequestKey
      ? modulesView.matchesState
      : "loading";
  const modules =
    modulesView.requestKey === modulesRequestKey
      ? modulesView.modules
      : emptyModules;
  const pulse = modules.intelligence?.season_pulse;
  const unavailableValue =
    intelligenceState === "loading" ? "Loading" : "Unavailable";

  const initialLoading =
    loadState === "loading" &&
    overview === null &&
    intelligenceState === "loading";
  if (initialLoading) return <OverviewSkeleton />;

  return (
    <div className="overview-page overview-control-room">
      <HeroSection />

      {loadState === "error" ? (
        <ErrorPanel errorMessage={errorMessage} />
      ) : null}

      <section className="overview-kpi-grid" aria-label="Season pulse">
        <KpiCard
          accent="green"
          context="Match records returned by Overview intelligence."
          icon={<CalendarDays size={18} />}
          label="Matches covered"
          value={pulse?.matches_covered ?? unavailableValue}
        />
        <KpiCard
          accent="green"
          context="Clubs represented in the selected season records."
          icon={<Users size={18} />}
          label="Teams tracked"
          value={pulse?.teams_tracked ?? unavailableValue}
        />
        <KpiCard
          accent="green"
          context="Scoreline scoring rate returned by Overview intelligence."
          icon={<Goal size={18} />}
          label="Goals per match"
          value={pulse?.goals_per_match?.toFixed(2) ?? unavailableValue}
        />
        <KpiCard
          accent="gold"
          context="Available discipline events per covered match."
          icon={<ChartColumnBig size={18} />}
          label="Cards per match"
          value={pulse?.cards_per_match?.toFixed(2) ?? unavailableValue}
        />
        <KpiCard
          accent="green"
          context="Share of matches supporting timeline-led interpretation."
          icon={<Clock3 size={18} />}
          label="Timeline coverage"
          value={
            pulse?.timeline_coverage_share == null
              ? unavailableValue
              : formatPercent(pulse.timeline_coverage_share)
          }
        />
        <KpiCard
          accent="gold"
          context="Share of covered matches with at least three goals."
          icon={<ShieldCheck size={18} />}
          label="High-scoring matches"
          value={
            pulse?.high_scoring_match_share == null
              ? unavailableValue
              : formatPercent(pulse.high_scoring_match_share)
          }
        />
      </section>

      <OverviewNoticePanel
        notices={modules.intelligence?.things_to_notice ?? []}
        state={intelligenceState}
      />

      <section className="overview-story-grid">
        <RecentSignalMatchesPanel
          className="overview-story-module overview-story-module-recent"
          matches={modules.matches}
          state={matchesState}
        />
        <FeaturedInsight
          className="overview-story-module overview-story-module-featured"
          goalTiming={featuredGoalTiming}
          loadState={loadState}
          onPageChange={onPageChange}
        />
        <TeamSignalsPanel
          className="overview-story-module overview-story-module-signals"
          signals={modules.intelligence?.team_signals ?? []}
          state={intelligenceState}
        />
      </section>

      <OverviewCoveragePanel
        quality={modules.intelligence?.data_quality ?? null}
        seasonLabel={seasonLabel}
        state={intelligenceState}
      />

      <section className="panel overview-product-map">
        <ReportSectionHeader
          title="Explore more"
          text="Each section turns official match records into a different kind of football intelligence."
        />
        <div className="overview-explore-grid">
          <ExploreCard
            href="/insights"
            title="Insights Library"
            description="Open promoted insights and key takeaways."
          />
          <ExploreCard
            href="/matches"
            title="Match Evidence"
            description="Review recent scorelines and match-by-match context."
          />
          <ExploreCard
            href="/teams"
            title="Team Summaries"
            description="Compare team form, results, and scoring output."
          />
          <ExploreCard
            href="/trends"
            title="Dive Deeper"
            description="Move from overview into dedicated analysis pages."
          />
        </div>
      </section>
    </div>
  );
}
