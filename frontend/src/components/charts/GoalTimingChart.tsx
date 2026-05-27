import type { GoalTimingInsightResponse } from "../../api/types";
import { formatPercent } from "../../utils/format";
import { ChartLegend, DistributionBarChart, InsightChartCard } from "./ChartPrimitives";

export function GoalTimingChart({ goalTiming }: { goalTiming: GoalTimingInsightResponse }) {
  const maxGoals = Math.max(...goalTiming.intervals.map((interval) => interval.goals), 1);
  const peakInterval = goalTiming.intervals.find((interval) => interval.rank === 1);
  const chartData = goalTiming.intervals.map((interval) => ({
    color: interval.rank === 1 ? "var(--color-accent-gold)" : "var(--color-accent-green-muted)",
    label: interval.interval,
    rank: interval.rank,
    share: interval.share,
    value: interval.goals,
  }));

  return (
    <InsightChartCard
      caveat={
        <>
          <div className="chart-value-list" aria-label="Readable goal timing values">
            {goalTiming.intervals.map((interval) => (
              <span key={interval.interval}>
                <strong>{interval.interval}</strong>
                {interval.goals.toLocaleString()} goals, {formatPercent(interval.share)}
              </span>
            ))}
          </div>
          <p className="caveat">
            Peak window: {goalTiming.peak_interval ?? "not available"}. Chart scale is based on the highest interval count of{" "}
            {maxGoals.toLocaleString()} goals.
          </p>
        </>
      }
      chart={
        <div className="goal-distribution-chart">
          {peakInterval ? (
            <div className="chart-peak-note" aria-label="Peak scoring window">
              <span>Peak</span>
              <strong>{peakInterval.interval}</strong>
              <small>
                {peakInterval.goals.toLocaleString()} goals, {formatPercent(peakInterval.share)}
              </small>
            </div>
          ) : null}
          <DistributionBarChart data={chartData} height={224} valueLabel="Goals" />
        </div>
      }
      eyebrow="Explore the timing"
      legend={
        <ChartLegend
          items={[
            { color: "var(--color-accent-green-muted)", label: "Regular scoring window" },
            { color: "var(--color-accent-gold)", label: "Peak scoring window" },
          ]}
        />
      }
      text="Compare each 15-minute regular-time window and keep the peak period visible in both the chart and the text values."
      title="Goal timing distribution"
    />
  );
}
