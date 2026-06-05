import type { GoalTimingInsightResponse } from "../../api/types";
import { formatPercent } from "../../utils/format";
import { getPeakRegularTimeInterval, getRegularTimeIntervals } from "../../utils/goalTiming";
import { ChartLegend, DistributionBarChart, InsightChartCard } from "./ChartPrimitives";

export function GoalTimingChart({ goalTiming }: { goalTiming: GoalTimingInsightResponse }) {
  const regularIntervals = getRegularTimeIntervals(goalTiming.intervals);
  const maxGoals = Math.max(...regularIntervals.map((interval) => interval.goals), 1);
  const peakInterval = getPeakRegularTimeInterval(goalTiming.intervals);
  const chartData = regularIntervals.map((interval) => ({
    color: peakInterval?.interval === interval.interval ? "var(--color-accent-gold)" : "var(--color-chart-green-muted)",
    isPeak: peakInterval?.interval === interval.interval,
    label: interval.interval,
    peakLabel: peakInterval?.interval === interval.interval ? "Peak" : undefined,
    rank: interval.rank,
    share: interval.share,
    value: interval.goals,
  }));

  return (
    <InsightChartCard
      caveat={
        <>
          <div className="chart-value-list" aria-label="Readable goal timing values">
            {regularIntervals.map((interval) => (
              <span key={interval.interval}>
                <strong>{interval.interval}</strong>
                {interval.goals.toLocaleString()} goals, {formatPercent(interval.share)}
              </span>
            ))}
          </div>
          <p className="caveat">
            Peak regular-time window: {peakInterval?.interval ?? "not available"}. Chart scale is based on the highest regular-time interval count of{" "}
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
            { color: "var(--color-chart-green-muted)", label: "Regular scoring window" },
            { color: "var(--color-accent-gold)", label: "Peak scoring window" },
          ]}
        />
      }
      text="Compare each 15-minute regular-time window and keep the peak period visible in both the chart and the text values."
      title="Goal timing distribution"
    />
  );
}
