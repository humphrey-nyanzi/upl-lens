import type { GoalTimingInsightResponse } from "../../api/types";
import type { LoadState, PageKey } from "../../app/types";
import { formatPercent } from "../../utils/format";
import { ChartLegend, GoalTimingHeatmap, InsightChartCard } from "../charts/ChartPrimitives";

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

  return (
    <InsightChartCard
      action={
        <button className="text-button dark" type="button" onClick={() => onPageChange("goal-timing")}>
          Open Goal Timing
        </button>
      }
      caveat={
        goalTiming ? (
          <>
            <div className="chart-value-list compact" aria-label="Readable goal timing values">
              {goalTiming.intervals.map((interval) => (
                <span key={interval.interval}>
                  <strong>{interval.interval}</strong>
                  {interval.goals.toLocaleString()} goals, {formatPercent(interval.share)}
                </span>
              ))}
            </div>
            <p className="caveat">Data note: added-time goals are excluded from this period comparison.</p>
          </>
        ) : null
      }
      chart={
        goalTiming ? (
          <div className="overview-goal-layout">
            <div className="insight-stat">
              <span>Peak scoring window</span>
              <strong>{goalTiming.peak_interval ?? "Unavailable"}</strong>
              <p>{goalTiming.total_regular_time_goals.toLocaleString()} regular-time goals counted.</p>
            </div>
            <GoalTimingHeatmap data={chartData} height={210} valueLabel="Goals" />
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
      text="The current flagship insight compares regular-time scoring windows and points readers toward the periods that shape a season."
      title="When do UPL goals arrive?"
    />
  );
}
