import type { GoalTimingInsightResponse } from "../../api/types";
import type { LoadState, PageKey } from "../../app/types";
import { formatPercent, formatSeasonScope } from "../../utils/format";
import { getPeakRegularTimeInterval, getRegularTimeIntervals } from "../../utils/goalTiming";
import { useNavigate } from "react-router-dom";
import { ChartLegend, DistributionBarChart, InsightChartCard } from "../charts/ChartPrimitives";

type FeaturedInsightProps = {
  className?: string;
  goalTiming: GoalTimingInsightResponse | null;
  loadState: LoadState;
  onPageChange: (page: PageKey) => void;
};

export function FeaturedInsight({ className, goalTiming, loadState, onPageChange }: FeaturedInsightProps) {
  const navigate = useNavigate();
  const peakInterval = goalTiming ? getPeakRegularTimeInterval(goalTiming.intervals) : null;
  const chartData = getRegularTimeIntervals(goalTiming?.intervals ?? []).map((interval) => ({
    color: interval.interval === peakInterval?.interval ? "var(--color-accent-gold)" : "var(--color-chart-green-muted)",
    isPeak: interval.interval === peakInterval?.interval,
    label: interval.interval,
    peakLabel: interval.interval === peakInterval?.interval ? "Peak" : undefined,
    rank: interval.rank,
    share: interval.share,
    value: interval.goals,
  }));
  const seasonLabel = goalTiming ? formatSeasonScope(goalTiming.scope_key, goalTiming.season_count) : "Current insight window";

  return (
    <InsightChartCard
      action={
        <button className="text-button dark" type="button" onClick={() => navigate("/insights/goal-timing")}>
          Explore Goal Timing
        </button>
      }
      caveat={
        goalTiming ? (
          <p className="caveat compact">
            {seasonLabel}. The Goal Timing page explains added-time handling and regular-time window values.
          </p>
        ) : null
      }
      chart={
        goalTiming ? (
          <div className="overview-goal-preview compact">
            <div className="overview-goal-summary" aria-label="Peak goal timing summary">
              <strong>{peakInterval ? formatPercent(peakInterval.share) : "Unavailable"}</strong>
              <p>
                of all goals scored in{" "}
                <span>{peakInterval?.interval ?? "the peak interval"}</span>
              </p>
              <small>{seasonLabel}</small>
            </div>
            <DistributionBarChart data={chartData} height={122} valueLabel="Goals" />
          </div>
        ) : null
      }
      className={`featured-insight overview-goal-card ${className ?? ""}`.trim()}
      emptyMessage="Goal timing insight is unavailable for this season yet."
      eyebrow="Featured Insight"
      isEmpty={!goalTiming && loadState !== "loading"}
      isLoading={!goalTiming && loadState === "loading"}
      legend={
        goalTiming ? (
          <ChartLegend
            items={[
              { color: "var(--color-chart-green-muted)", label: "Regular window" },
              { color: "var(--color-accent-gold)", label: "Peak window" },
            ]}
          />
        ) : null
      }
      text="A quick read on where the season's goals cluster most, with the strongest regular-time window highlighted for fast comparison."
      title="Goal Timing: The Decisive Minutes"
      largeMetric={null}
    />
  );
}
