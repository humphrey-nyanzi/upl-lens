import { useMemo } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, BarChartBig, CalendarRange, Clock3, Flag, LineChart, SplitSquareVertical, Trophy } from "lucide-react";

import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { formatDate, formatPercent, formatSeason } from "../utils/format";
import { getSelectedSeasonLabel } from "../utils/seasonScope";

function getSeasonSpanInDays(firstMatchDate: string | null, lastMatchDate: string | null) {
  if (!firstMatchDate || !lastMatchDate) return null;

  const first = new Date(firstMatchDate);
  const last = new Date(lastMatchDate);
  const millisecondsPerDay = 1000 * 60 * 60 * 24;
  return Math.max(1, Math.round((last.getTime() - first.getTime()) / millisecondsPerDay) + 1);
}

export function TrendsPage({ data, featuredGoalTiming, loadState, selectedSeason, selectedSeasonInfo }: PageProps) {
  const sortedSeasons = useMemo(() => {
    return [...data.seasons].sort((left, right) => right.season.localeCompare(left.season));
  }, [data.seasons]);

  const latestSeason = sortedSeasons[0];
  const earliestSeason = sortedSeasons.at(-1);
  const totalMatches = sortedSeasons.reduce((total, season) => total + season.match_count, 0);
  const averageMatches = sortedSeasons.length > 0 ? Math.round(totalMatches / sortedSeasons.length) : 0;
  const maxMatchCount = sortedSeasons.reduce((maximum, season) => Math.max(maximum, season.match_count), 0);
  const maxSeasonSpan = sortedSeasons.reduce((maximum, season) => {
    return Math.max(maximum, getSeasonSpanInDays(season.first_match_date, season.last_match_date) ?? 0);
  }, 0);
  const selectedPeakShare = featuredGoalTiming?.intervals.find((interval) => interval.rank === 1)?.share ?? null;
  const selectedSeasonLabel = getSelectedSeasonLabel(selectedSeason, selectedSeasonInfo);

  const seasonRows = sortedSeasons.map((season) => {
    const spanDays = getSeasonSpanInDays(season.first_match_date, season.last_match_date);
    const matchesPerTeam = season.team_count > 0 ? season.match_count / season.team_count : null;
    const matchShare = maxMatchCount > 0 ? season.match_count / maxMatchCount : 0;
    const seasonSpanShare = maxSeasonSpan > 0 && spanDays ? spanDays / maxSeasonSpan : 0;

    return {
      ...season,
      matchShare,
      matchesPerTeam,
      seasonSpanShare,
      spanDays,
    };
  });

  return (
    <>
      <PageIntro
        eyebrow="Historical context"
        title="Trends"
        text="Season-level comparisons, coverage notes, and compact visual summaries that help place the current season inside a broader UPL story."
      />

      <section className="metric-grid compact-metrics" aria-label="Trends summary">
        <KpiCard
          accent="green"
          icon={<CalendarRange size={18} />}
          label="Seasons tracked"
          value={sortedSeasons.length}
          context={
            earliestSeason && latestSeason
              ? `${formatSeason(earliestSeason.season)} to ${formatSeason(latestSeason.season)}`
              : "Season range unavailable"
          }
          variant="compact"
        />
        <KpiCard
          accent="gold"
          icon={<BarChartBig size={18} />}
          label="Matches recorded"
          value={totalMatches}
          context="Total matches across available seasons."
          variant="compact"
        />
        <KpiCard
          icon={<Flag size={18} />}
          label="Average per season"
          value={averageMatches}
          context="Approximate match count per recorded season."
          variant="compact"
        />
      </section>

      <section className="trends-discovery-grid" aria-label="Trends discovery">
        <article className="trends-card trends-card-featured trends-discovery-feature">
          <div className="trends-card-featured-content">
            <span className="eyebrow">League context</span>
            <div className="trends-card-icon" aria-hidden="true">
              <LineChart size={18} />
            </div>
            <strong>Read this season against the rest of the archive.</strong>
            <p>
              UPL Lens can already compare season coverage, match volume, and calendar span across the recorded league
              seasons. This gives every insight a stronger frame before we layer in richer trend modules.
            </p>
            <div className="insight-feature-stat-grid trends-feature-stats" aria-label="Trend highlights">
              <div className="insight-feature-stat">
                <span>Latest season</span>
                <strong>{latestSeason ? formatSeason(latestSeason.season) : "N/A"}</strong>
              </div>
              <div className="insight-feature-stat">
                <span>Coverage span</span>
                <strong>{earliestSeason && latestSeason ? `${sortedSeasons.length} seasons` : "N/A"}</strong>
              </div>
              <div className="insight-feature-stat">
                <span>Total matches</span>
                <strong>{totalMatches.toLocaleString()}</strong>
              </div>
            </div>
          </div>
          <div className="trends-card-featured-graph" aria-hidden="true">
            <BarChartBig size={168} />
          </div>
        </article>

        <article className="panel trends-discovery-note">
          <div className="trends-discovery-note-icon" aria-hidden="true">
            <SplitSquareVertical size={18} />
          </div>
          <div className="trends-discovery-note-copy">
            <strong>What you can compare today</strong>
            <p>
              Season windows, match volume, team field size, and the shape of currently promoted scoring trends can be
              read together without leaving this page.
            </p>
          </div>
        </article>

        <article className="panel trends-discovery-note">
          <div className="trends-discovery-note-icon" aria-hidden="true">
            <Trophy size={18} />
          </div>
          <div className="trends-discovery-note-copy">
            <strong>Current promoted angle</strong>
            <p>
              {featuredGoalTiming
                ? `Goal Timing is currently framed across ${featuredGoalTiming.season_count} season${featuredGoalTiming.season_count === 1 ? "" : "s"}, while your active dashboard selection is ${selectedSeasonLabel.toLowerCase()}. The leading window share in the featured insight is ${selectedPeakShare !== null ? formatPercent(selectedPeakShare) : "N/A"}.`
                : "Goal Timing will appear here once the current promoted insight is available."}
            </p>
            {featuredGoalTiming ? (
              <Link className="text-button subtle" to="/insights/goal-timing">
                Open featured insight
              </Link>
            ) : null}
          </div>
        </article>
      </section>

      <section className="panel">
        <div className="section-heading compact">
          <div>
            <h2>Season comparison</h2>
            <p>Coverage, match volume, and season span from the metadata currently loaded into the public app.</p>
          </div>
        </div>

        {sortedSeasons.length > 0 ? (
          <div className="trend-table-shell">
            <div className="trend-table-header" aria-hidden="true">
              <span>Season</span>
              <span>Matches</span>
              <span>Teams</span>
              <span>Span</span>
              <span>Window</span>
            </div>
            <div className="trend-table-list">
              {seasonRows.map((season) => (
                <article className="trend-table-row" key={season.season}>
                  <div className="trend-table-primary">
                    <strong>{formatSeason(season.season)}</strong>
                    <small>
                      {formatDate(season.first_match_date)} to {formatDate(season.last_match_date)}
                    </small>
                  </div>
                  <div className="trend-table-metric">
                    <strong>{season.match_count.toLocaleString()}</strong>
                    <small>matches</small>
                  </div>
                  <div className="trend-table-metric">
                    <strong>{season.team_count.toLocaleString()}</strong>
                    <small>teams</small>
                  </div>
                  <div className="trend-table-metric">
                    <strong>{season.spanDays ? `${season.spanDays} days` : "N/A"}</strong>
                    <small>
                      {season.matchesPerTeam !== null
                        ? `${season.matchesPerTeam.toFixed(1)} matches per team`
                        : "Per-team rate unavailable"}
                    </small>
                  </div>
                  <div className="trend-table-bar-stack" aria-label={`Season coverage bars for ${season.season}`}>
                    <div className="trend-table-bar-row">
                      <span>Volume</span>
                      <div className="trend-table-bar-track">
                        <div
                          className="trend-table-bar-fill is-green"
                          style={{ width: `${season.matchShare > 0 ? Math.max(12, season.matchShare * 100) : 0}%` }}
                        />
                      </div>
                    </div>
                    <div className="trend-table-bar-row">
                      <span>Span</span>
                      <div className="trend-table-bar-track">
                        <div
                          className="trend-table-bar-fill is-gold"
                          style={{ width: `${season.seasonSpanShare > 0 ? Math.max(12, season.seasonSpanShare * 100) : 0}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        ) : (
          <EmptyState
            message={loadState === "loading" ? "Loading season trend summaries." : "No season trend data available yet."}
          />
        )}
      </section>

      <section className="trends-grid" aria-label="Trend reading notes">
        <article className="trends-card">
          <div className="trends-card-icon" aria-hidden="true">
            <Clock3 size={18} />
          </div>
          <div className="trends-card-content">
            <strong>Season windows</strong>
            <p>
              Use the first and last recorded match dates to understand whether a season snapshot covers a compact run
              or a longer competition window.
            </p>
          </div>
        </article>
        <article className="trends-card">
          <div className="trends-card-icon" aria-hidden="true">
            <Flag size={18} />
          </div>
          <div className="trends-card-content">
            <strong>Match volume</strong>
            <p>
              Match totals show how complete each season looks in the current archive and give a quick sense of sample
              depth before you compare findings.
            </p>
          </div>
        </article>
        <article className="trends-card">
          <div className="trends-card-icon" aria-hidden="true">
            <CalendarRange size={18} />
          </div>
          <div className="trends-card-content">
            <strong>Team field size</strong>
            <p>
              Team counts help explain why some seasons may need careful reading before you compare totals or rate-like
              signals directly.
            </p>
          </div>
        </article>
        <article className="trends-card">
          <div className="trends-card-icon" aria-hidden="true">
            <ArrowRight size={18} />
          </div>
          <div className="trends-card-content">
            <strong>Next step</strong>
            <p>
              Move from this archive view into the promoted insight, then back to matches or teams to check how the
              league-level pattern shows up in specific reports.
            </p>
          </div>
          <Link className="trends-card-action" to={featuredGoalTiming ? "/insights/goal-timing" : "/matches"}>
            {featuredGoalTiming ? "Open goal timing" : "Browse matches"}
          </Link>
        </article>
      </section>
    </>
  );
}
