import type { GoalTimingInsightResponse } from "../../api/types";
import { formatPercent } from "../../utils/format";
import { ChartLegend, GoalTimingHeatmap, InsightChartCard } from "./ChartPrimitives";

export function GoalTimingChart({ goalTiming }: { goalTiming: GoalTimingInsightResponse }) {
  const maxGoals = Math.max(...goalTiming.intervals.map((interval) => interval.goals), 1);
  const chartData = goalTiming.intervals.map((interval) => ({
    color: interval.rank === 1 ? "#f5b82e" : "#16a34a",
    label: interval.interval,
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
      chart={<GoalTimingHeatmap data={chartData} height={300} valueLabel="Goals" />}
      eyebrow="Explore the timing"
      legend={
        <ChartLegend
          items={[
            { color: "#16a34a", label: "Regular scoring window" },
            { color: "#f5b82e", label: "Peak scoring window" },
          ]}
        />
      }
      text="Compare each 15-minute regular-time window and keep the peak period visible in both the chart and the text values."
      title="Regular-time goals by 15-minute period"
    />
  );
}
