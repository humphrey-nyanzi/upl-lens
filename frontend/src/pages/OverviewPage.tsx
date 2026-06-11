import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { apiClient } from "../api/client";
import type {
  MatchIntelligenceSummary,
  OverviewIntelligenceResponse,
  OverviewNotice,
  PlayerLeaderboardsResponse,
  SeasonTrendsResponse,
  TeamResponse,
} from "../api/types";
import type { PageProps } from "../app/types";
import { ErrorPanel } from "../components/common/ErrorPanel";
import { EmptyState } from "../components/common/EmptyState";
import { PageIntro } from "../components/common/PageIntro";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { ShowMoreList } from "../components/common/ShowMoreList";
import { TeamMarker } from "../components/common/TeamMarker";
import { DataQualityNote, type DataQualityTone } from "../components/intelligence/DataQualityNote";
import { MetricDelta } from "../components/intelligence/MetricDelta";
import { MiniBarChart, type MiniBarDatum } from "../components/intelligence/MiniBarChart";
import { SignalChipGroup, type SignalChipItem } from "../components/intelligence/SignalChip";
import { formatDate, formatPercent, formatScoreline } from "../utils/format";
import { getPeakRegularTimeInterval, getRegularTimeIntervals } from "../utils/goalTiming";
import { getSelectedSeasonLabel, toApiSeason } from "../utils/seasonScope";
import { formatGoalDifference, getTeamPoints } from "../utils/teams";

type IntelligenceState = "loading" | "success" | "partial" | "error";

type OverviewModules = {
  intelligence: OverviewIntelligenceResponse | null;
  leaderboards: PlayerLeaderboardsResponse | null;
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
  leaderboards: null,
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

function formatRate(value: number | null | undefined, digits = 2) {
  return value === null || value === undefined ? "Unavailable" : value.toFixed(digits);
}

function formatShare(value: number | null | undefined) {
  return value === null || value === undefined ? "Unavailable" : formatPercent(value);
}

function dataQualityTone(status: string | undefined | null): DataQualityTone {
  if (status === "good") return "good";
  if (status === "limited") return "limited";
  if (status === "caution") return "caution";
  return "neutral";
}

function toSignalItems(items: Array<{ key?: string; label: string; tone?: SignalChipItem["tone"] }>): SignalChipItem[] {
  return items.map((item, index) => ({
    key: item.key ?? `${item.label}-${index}`,
    label: item.label,
    tone: item.tone,
  }));
}

function topByNumber<T>(rows: T[], getter: (row: T) => number | null | undefined) {
  let topRow: T | undefined;
  let topValue = Number.NEGATIVE_INFINITY;

  for (const row of rows) {
    const value = getter(row) ?? Number.NEGATIVE_INFINITY;
    if (value > topValue) {
      topRow = row;
      topValue = value;
    }
  }

  return topRow;
}

function lowByNumber<T>(rows: T[], getter: (row: T) => number | null | undefined) {
  let lowRow: T | undefined;
  let lowValue = Number.POSITIVE_INFINITY;

  for (const row of rows) {
    const value = getter(row) ?? Number.POSITIVE_INFINITY;
    if (value < lowValue) {
      lowRow = row;
      lowValue = value;
    }
  }

  return lowRow;
}

function getFallbackNotices(teams: TeamResponse[], signalMatches: MatchIntelligenceSummary[]): OverviewNotice[] {
  const notices: OverviewNotice[] = [];
  const topAttack = topByNumber(teams, (team) => team.goals_for);
  const tightDefence = lowByNumber(teams.filter((team) => team.played_matches > 0), (team) => team.goals_against);
  const bestGoalDifference = topByNumber(teams, (team) => team.goal_difference);
  const caveatTeams = teams.filter((team) => team.administrative_matches > 0 || team.missing_matches > 0).length;
  const lateOrScoringSignals = signalMatches.filter(
    (match) => match.signal_labels.some((signal) => signal.key === "goal_heavy" || signal.key === "late_drama") || match.late_goal_count > 0,
  ).length;

  if (topAttack) {
    notices.push({
      key: "top-attack",
      link_path: `/teams/${topAttack.team_slug ?? topAttack.team_name.toLowerCase().replace(/\s+/g, "-")}`,
      text: `${topAttack.team_name} leads this scope for goals scored with ${topAttack.goals_for.toLocaleString()}.`,
      title: "Top attack",
      tone: "positive",
    });
  }
  if (tightDefence) {
    notices.push({
      key: "tight-defence",
      link_path: `/teams/${tightDefence.team_slug ?? tightDefence.team_name.toLowerCase().replace(/\s+/g, "-")}`,
      text: `${tightDefence.team_name} has conceded ${tightDefence.goals_against.toLocaleString()} goal${tightDefence.goals_against === 1 ? "" : "s"} in available records.`,
      title: "Tight defence",
      tone: "positive",
    });
  }
  if (bestGoalDifference) {
    notices.push({
      key: "goal-difference",
      link_path: `/teams/${bestGoalDifference.team_slug ?? bestGoalDifference.team_name.toLowerCase().replace(/\s+/g, "-")}`,
      text: `${bestGoalDifference.team_name} has the strongest goal difference at ${formatGoalDifference(bestGoalDifference.goal_difference)}.`,
      title: "Scoring balance",
      tone: "neutral",
    });
  }
  if (lateOrScoringSignals > 0) {
    notices.push({
      key: "match-signals",
      link_path: "/matches",
      text: `${lateOrScoringSignals.toLocaleString()} returned match signal${lateOrScoringSignals === 1 ? "" : "s"} involve high scoring or late-goal evidence.`,
      title: "Match signal",
      tone: "warning",
    });
  }
  if (caveatTeams > 0) {
    notices.push({
      key: "coverage-caveat",
      link_path: "/about",
      text: `${caveatTeams.toLocaleString()} team record${caveatTeams === 1 ? "" : "s"} include administrative or missing-match caveats.`,
      title: "Coverage note",
      tone: "warning",
    });
  }

  return notices.slice(0, 5);
}

function SignalMatchCard({ match }: { match: MatchIntelligenceSummary }) {
  const homeTeam = match.home_team ?? "Home team TBC";
  const awayTeam = match.away_team ?? "Away team TBC";

  return (
    <Link className="overview-signal-match" to={`/matches/${match.match_id}`}>
      <span>{formatDate(match.match_date)}</span>
      <strong>
        {homeTeam} {formatScoreline(match.home_score, match.away_score)} {awayTeam}
      </strong>
      <SignalChipGroup items={toSignalItems(match.signal_labels)} emptyLabel={match.primary_signal ?? "Evidence-led"} maxVisible={3} size="small" />
      <small>{match.primary_signal ?? "Match brief"} · {match.event_count.toLocaleString()} events</small>
    </Link>
  );
}

function TeamSignalCard({ label, metric, team }: { label: string; metric: string; team: TeamResponse }) {
  const href = `/teams/${team.team_slug ?? team.team_name.toLowerCase().replace(/\s+/g, "-")}`;

  return (
    <Link className="overview-team-card" to={href}>
      <div className="overview-team-card-title">
        <TeamMarker label={team.team_name} size="small" />
        <div>
          <span>{label}</span>
          <strong>{team.team_name}</strong>
        </div>
      </div>
      <MetricDelta label="Signal value" value={metric} context={`${team.wins}W ${team.draws}D ${team.losses}L`} />
      <SignalChipGroup items={toSignalItems(team.profile_labels ?? [])} maxVisible={3} size="small" />
    </Link>
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
  overview,
  selectedSeason,
  selectedSeasonInfo,
}: PageProps) {
  const [modulesView, setModulesView] = useState<OverviewModulesViewState>({
    modules: emptyModules,
    requestKey: "",
    status: "success",
  });
  const seasonLabel = getSelectedSeasonLabel(selectedSeason, selectedSeasonInfo);
  const apiSeason = toApiSeason(selectedSeason);
  const modulesRequestKey = selectedSeason;

  useEffect(() => {
    let ignore = false;

    Promise.allSettled([
      apiClient.getOverviewIntelligence(apiSeason),
      apiClient.getMatchIntelligence(apiSeason, { sort: "interest", limit: 6 }),
      apiClient.getSeasonTrends(),
      apiClient.getPlayerLeaderboards(apiSeason, 5),
    ]).then(([overviewResult, matchesResult, trendsResult, leaderboardsResult]) => {
      if (ignore) return;

      const nextModules: OverviewModules = {
        intelligence: overviewResult.status === "fulfilled" ? overviewResult.value : null,
        leaderboards: leaderboardsResult.status === "fulfilled" ? leaderboardsResult.value : null,
        matches: matchesResult.status === "fulfilled" ? matchesResult.value : [],
        trends: trendsResult.status === "fulfilled" ? trendsResult.value : null,
      };
      const successCount = [overviewResult, matchesResult, trendsResult, leaderboardsResult].filter((result) => result.status === "fulfilled").length;

      setModulesView({
        modules: nextModules,
        requestKey: modulesRequestKey,
        status: successCount === 4 ? "success" : successCount > 0 ? "partial" : "error",
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
  const teamCount = pulse?.teams_tracked ?? overview?.team_count ?? selectedSeasonInfo?.team_count ?? data.teams.length;
  const goalsPerMatch =
    pulse?.goals_per_match ??
    trendForSeason?.goals_per_match ??
    (matchCount > 0 && overview ? overview.scoreline_goal_count / matchCount : null);
  const cardsPerMatch =
    pulse?.cards_per_match ??
    trendForSeason?.cards_per_match ??
    (matchCount > 0 && overview ? (overview.yellow_card_count + overview.red_card_count) / matchCount : null);
  const timelineCoverage = pulse?.timeline_coverage_share ?? trendForSeason?.timeline_coverage_share ?? null;
  const highScoringShare = pulse?.high_scoring_match_share ?? trendForSeason?.high_scoring_match_share ?? null;

  const notices = modules.intelligence?.things_to_notice.length
    ? modules.intelligence.things_to_notice
    : getFallbackNotices(data.teams, modules.matches);

  const topAttack = topByNumber(data.teams, (team) => team.goals_for);
  const tightDefence = lowByNumber(data.teams.filter((team) => team.played_matches > 0), (team) => team.conceded_per_match ?? team.goals_against);
  const bestGoalDifference = topByNumber(data.teams, (team) => team.goal_difference);
  const bestPointsProfile = topByNumber(data.teams, (team) => team.points_per_match ?? getTeamPoints(team));
  const caveatTeam = data.teams.find((team) => team.profile_labels?.some((label) => label.key === "data_caveat")) ?? data.teams.find((team) => team.administrative_matches > 0 || team.missing_matches > 0);

  const peakGoalWindow = featuredGoalTiming ? getPeakRegularTimeInterval(featuredGoalTiming.intervals) : null;
  const goalTimingData: MiniBarDatum[] = getRegularTimeIntervals(featuredGoalTiming?.intervals ?? []).map((interval) => ({
    key: interval.interval,
    label: interval.interval,
    tone: interval.interval === peakGoalWindow?.interval ? "gold" : "green",
    value: interval.goals,
  }));
  const trendChartData: MiniBarDatum[] =
    modules.trends?.seasons.slice(-5).map((season) => ({
      key: season.season,
      label: season.season.replace("_", "/"),
      tone: season.data_quality_status === "limited" ? "muted" : "green",
      value: season.goals_per_match ?? 0,
    })) ?? [];

  const initialLoading = loadState === "loading" && overview === null && moduleState === "loading";
  if (initialLoading) return <OverviewSkeleton />;

  return (
    <div className="overview-control-room">
      <PageIntro
        eyebrow="Editorial control room"
        title="UPL Lens"
        text="Uganda Premier League match intelligence and statistical insights. Understand the league through trusted match data, statistical signals, and team-level exploration that goes beyond ordinary fixtures and results."
      >
        <div className="season-context-pill">{seasonLabel}</div>
      </PageIntro>

      {loadState === "error" ? <ErrorPanel errorMessage={errorMessage} /> : null}

      <section className="overview-pulse-grid" aria-label="Season pulse">
        <MetricDelta label="Matches covered" value={matchCount} context="Selected season records." />
        <MetricDelta label="Teams tracked" value={teamCount} context="Clubs in available records." />
        <MetricDelta label="Goals per match" value={formatRate(goalsPerMatch)} context="Scoreline comparison rate." tone="positive" />
        <MetricDelta label="Cards per match" value={formatRate(cardsPerMatch)} context="Available discipline records." tone="warning" />
        <MetricDelta label="Timeline coverage" value={formatShare(timelineCoverage)} context="Complete or partial event coverage." />
        <MetricDelta label="High-scoring share" value={formatShare(highScoringShare)} context="Season-level match signal." tone="positive" />
        <MetricDelta label="Latest match" value={formatDate(overview?.latest_match_date ?? selectedSeasonInfo?.last_match_date ?? null)} context="Most recent available result." />
      </section>

      <section className="overview-control-grid">
        <section className="panel overview-notice-panel">
          <ReportSectionHeader
            title="Things to notice"
            text="A short editorial readout from overview signals, with simple fallbacks from loaded season data when needed."
          />
          <div className="overview-notice-list">
            {notices.length > 0 ? (
              notices.map((notice) => {
                const content = (
                  <>
                    <SignalChipGroup items={toSignalItems([{ key: notice.key, label: notice.title, tone: notice.tone }])} size="small" />
                    <p>{notice.text}</p>
                  </>
                );
                return notice.link_path ? (
                  <Link className="overview-notice-card" key={notice.key} to={notice.link_path}>
                    {content}
                  </Link>
                ) : (
                  <article className="overview-notice-card" key={notice.key}>
                    {content}
                  </article>
                );
              })
            ) : (
              <EmptyState message="No overview signals are available for the selected season yet." />
            )}
          </div>
        </section>

        <aside className="panel overview-quality-panel">
          <ReportSectionHeader title="Can I trust this view?" text="UPL Lens separates the source record from the analytical layer, then keeps caveats visible." />
          <DataQualityNote
            tone={dataQualityTone(modules.intelligence?.data_quality.status)}
            note={modules.intelligence?.data_quality.note ?? "Timeline-based sections should be read with event coverage in mind."}
            metrics={[
              { label: "Timeline coverage", value: formatShare(modules.intelligence?.data_quality.timeline_coverage_share ?? timelineCoverage) },
              { label: "Administrative results", value: modules.intelligence?.data_quality.administrative_result_count ?? trendForSeason?.administrative_result_count ?? 0 },
              { label: "Source caveats", value: modules.intelligence?.data_quality.source_anomaly_count ?? trendForSeason?.source_anomaly_count ?? 0 },
            ]}
          />
        </aside>
      </section>

      <section className="panel overview-featured-insight-panel">
        <ReportSectionHeader
          eyebrow="Featured insight"
          title="Goal Timing: The Decisive Minutes"
          text="Football question: when do UPL goals arrive in regular time, and which interval stands out in available event data?"
        >
          <Link className="text-button" to="/insights/goal-timing">
            Open Goal Timing
          </Link>
        </ReportSectionHeader>
        <div className="overview-featured-insight-grid">
          <MetricDelta
            label="Main finding"
            value={peakGoalWindow ? `${peakGoalWindow.interval}` : "Unavailable"}
            context={peakGoalWindow ? `${formatPercent(peakGoalWindow.share)} of regular-time goals in the featured scope.` : "Goal timing data is not available yet."}
            tone="positive"
          />
          <MiniBarChart
            data={goalTimingData}
            emptyLabel="Goal timing insight is unavailable for this season yet."
            height="compact"
            valueFormatter={(value) => value.toLocaleString()}
          />
        </div>
        <p className="overview-panel-note">The available event data shows interval patterns, not a claim that one period decides every match.</p>
      </section>

      <section className="overview-control-grid">
        <section className="panel">
          <ReportSectionHeader
            title="Recent signal matches"
            text="Matches worth opening because scoring, late-goal, discipline, timeline, or caveat signals stand out."
          />
          {modules.matches.length > 0 ? (
            <ShowMoreList
              className="overview-signal-match-list"
              getKey={(match) => match.match_id}
              initialCount={3}
              itemNoun="match"
              items={modules.matches}
              renderItem={(match) => <SignalMatchCard match={match} />}
            />
          ) : (
            <EmptyState message={moduleState === "loading" ? "Loading match signals." : "No signal matches are available for this season yet."} />
          )}
        </section>

        <section className="panel">
          <ReportSectionHeader title="Team signals" text="A compact route into attack, defence, points profile, and caveat-led team dossiers." />
          <div className="overview-team-signal-grid">
            {topAttack ? <TeamSignalCard label="Top attack" metric={`${topAttack.goals_for} goals`} team={topAttack} /> : null}
            {tightDefence ? <TeamSignalCard label="Tight defence" metric={`${formatRate(tightDefence.conceded_per_match, 1)} conceded/match`} team={tightDefence} /> : null}
            {bestGoalDifference ? <TeamSignalCard label="Goal difference" metric={formatGoalDifference(bestGoalDifference.goal_difference)} team={bestGoalDifference} /> : null}
            {bestPointsProfile ? <TeamSignalCard label="Points profile" metric={`${formatRate(bestPointsProfile.points_per_match, 2)} pts/match`} team={bestPointsProfile} /> : null}
            {caveatTeam ? <TeamSignalCard label="Caveat watch" metric={`${caveatTeam.administrative_matches + caveatTeam.missing_matches} caveat(s)`} team={caveatTeam} /> : null}
          </div>
        </section>
      </section>

      <section className="overview-control-grid">
        <section className="panel overview-trends-teaser">
          <ReportSectionHeader title="Season trends" text="Compare scoring, cards, result balance, and data coverage across available UPL seasons." />
          <MiniBarChart
            data={trendChartData}
            emptyLabel="Season trend data is unavailable right now."
            height="compact"
            title="Goals per match"
            valueFormatter={(value) => value.toFixed(2)}
          />
          <Link className="text-button" to="/trends">
            Open Season Trends
          </Link>
        </section>

        <section className="panel overview-player-teaser">
          <ReportSectionHeader title="Player contribution" text="Leading contributors in available player data, with lineup and event coverage caveats." />
          {modules.leaderboards ? (
            <div className="overview-player-list">
              {modules.leaderboards.goal_contributions[0] ? (
                <Link to={`/players/${modules.leaderboards.goal_contributions[0].player_slug}`}>
                  <span>Goal contributions</span>
                  <strong>{modules.leaderboards.goal_contributions[0].player_name}</strong>
                  <small>{modules.leaderboards.goal_contributions[0].goal_contributions} goals plus assists</small>
                </Link>
              ) : null}
              {modules.leaderboards.assists[0] ? (
                <Link to={`/players/${modules.leaderboards.assists[0].player_slug}`}>
                  <span>Assists</span>
                  <strong>{modules.leaderboards.assists[0].player_name}</strong>
                  <small>{modules.leaderboards.assists[0].assists} recorded assists</small>
                </Link>
              ) : null}
              {modules.leaderboards.starts[0] ? (
                <Link to={`/players/${modules.leaderboards.starts[0].player_slug}`}>
                  <span>Starts</span>
                  <strong>{modules.leaderboards.starts[0].player_name}</strong>
                  <small>{modules.leaderboards.starts[0].starts} starts</small>
                </Link>
              ) : null}
            </div>
          ) : (
            <EmptyState message={moduleState === "loading" ? "Loading player contribution signals." : "Player leaderboards are unavailable right now."} />
          )}
          <DataQualityNote compact note={modules.leaderboards?.data_quality_note} tone="caution" />
          <Link className="text-button" to="/players">
            Open Player Contributions
          </Link>
        </section>
      </section>

      <section className="panel overview-product-map">
        <ReportSectionHeader title="Explore the product" text="Each section turns official match records into a different kind of football intelligence." />
        <div className="overview-explore-grid">
          <ExploreCard href="/matches" title="Match Briefs" description="Find matches by scoring, late goals, discipline, result context, and evidence quality." />
          <ExploreCard href="/teams" title="Team Profiles" description="Compare records, attack and defence shape, home-away splits, form, and caveats." />
          <ExploreCard href="/players" title="Player Contributions" description="Read goals, assists, appearances, starts, discipline, and contribution patterns from available player data." />
          <ExploreCard href="/trends" title="Season Trends" description="Compare scoring, cards, result balance, and data coverage across available UPL seasons." />
          <ExploreCard href="/insights" title="Promoted Insights" description="Open validated research features that have been promoted into the product." />
          <ExploreCard href="/about" title="About the Data" description="See source boundaries, pipeline, caveats, freshness, and maintainer context." />
        </div>
      </section>

      <DataQualityNote
        title="Source boundary"
        tone="neutral"
        note="Built from official UPL match pages and transformed into public football intelligence. Data caveats and methodology are documented in About."
        metrics={[
          { label: "Official site", value: "Source record" },
          { label: "UPL Lens", value: "Analytical layer" },
        ]}
      />

      {moduleState === "partial" ? (
        <DataQualityNote compact note="One or more optional intelligence modules are unavailable right now, so this page is using the data that loaded successfully." tone="caution" />
      ) : null}
    </div>
  );
}
