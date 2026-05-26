import type { GoalTimingInsightResponse } from "../../api/types";
import type { LoadState, PageKey } from "../../app/types";
import { formatPercent } from "../../utils/format";
import { ChartLegend, GoalTimingHeatmapPreview, InsightChartCard } from "../charts/ChartPrimitives";

type FeaturedInsightProps = {
  goalTiming: GoalTimingInsightResponse | null;
  loadState: LoadState;
  onPageChange: (page: PageKey) => void;
};

export function FeaturedInsight({ goalTiming, loadState, onPageChange }: FeaturedInsightProps) {
  const chartData =
    goalTiming?.intervals.map((interval) => ({
      color: interval.rank === 1 ? "var(--color-accent-gold)" : "var(--color-accent-green)",
      label: interval.interval,
      rank: interval.rank,
      share: interval.share,
      value: interval.goals,
    })) ?? [];
  const peakInterval = goalTiming?.intervals.find((interval) => interval.rank === 1);

  return (
    <InsightChartCard
      action={
        <button className="text-button dark" type="button" onClick={() => onPageChange("goal-timing")}>
          Open Goal Timing
        </button>
      }
      caveat={
        goalTiming ? (
          <p className="caveat compact">
            Preview only: added-time goals and full interval values live on the Goal Timing page.
          </p>
        ) : null
      }
      chart={
        goalTiming ? (
          <div className="overview-goal-preview">
            <div className="overview-goal-peek" aria-label="Peak goal timing summary">
              <span>Peak window</span>
              <strong>{goalTiming.peak_interval ?? "Unavailable"}</strong>
              {peakInterval ? <small>{peakInterval.goals.toLocaleString()} goals, {formatPercent(peakInterval.share)}</small> : null}
            </div>
            <GoalTimingHeatmapPreview data={chartData} valueLabel="Goals" />
          </div>
        ) : null
      }
      className="featured-insight overview-goal-card"
      emptyMessage="No goal timing insight returned yet."
      eyebrow="Featured insight"
      isEmpty={!goalTiming && loadState !== "loading"}
      isLoading={!goalTiming && loadState === "loading"}
      legend={
        goalTiming ? (
          <ChartLegend
            items={[
              { color: "var(--color-accent-green)", label: "Regular window" },
              { color: "var(--color-accent-gold)", label: "Peak window" },
            ]}
          />
        ) : null
      }
      text="Heatmap preview of the strongest regular-time scoring windows."
      title="Goal timing heatmap"
    />
  );
}
