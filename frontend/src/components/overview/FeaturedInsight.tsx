import type { GoalTimingInsightResponse } from "../../api/types";
import type { LoadState, PageKey } from "../../app/types";
import { formatPercent } from "../../utils/format";
import { useNavigate } from "react-router-dom";
import { ChartLegend, DistributionBarChart, InsightChartCard } from "../charts/ChartPrimitives";

type FeaturedInsightProps = {
  goalTiming: GoalTimingInsightResponse | null;
  loadState: LoadState;
  onPageChange: (page: PageKey) => void;
};

export function FeaturedInsight({ goalTiming, loadState, onPageChange }: FeaturedInsightProps) {
  const navigate = useNavigate();
  const chartData =
    goalTiming?.intervals.map((interval) => ({
      color: interval.rank === 1 ? "var(--color-accent-gold)" : "var(--color-accent-green-muted)",
      label: interval.interval,
      rank: interval.rank,
      share: interval.share,
      value: interval.goals,
    })) ?? [];
  const peakInterval = goalTiming?.intervals.find((interval) => interval.rank === 1);

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
            Preview only: added-time goals and full interval values live on the Goal Timing page.
          </p>
        ) : null
      }
      chart={
        goalTiming ? (
          <div className="overview-goal-preview compact">
            <div className="overview-goal-summary" aria-label="Peak goal timing summary">
              <strong>{peakInterval ? formatPercent(peakInterval.share) : "N/A"}</strong>
              <p>
                of all goals scored in{" "}
                <span>{goalTiming.peak_interval ?? "the peak interval"}</span>
              </p>
            </div>
            <DistributionBarChart data={chartData} height={122} valueLabel="Goals" />
          </div>
        ) : null
      }
      className="featured-insight overview-goal-card"
      emptyMessage="Goal timing insight is unavailable for this season yet."
      eyebrow="Featured Insight"
      isEmpty={!goalTiming && loadState !== "loading"}
      isLoading={!goalTiming && loadState === "loading"}
      legend={
        goalTiming ? (
          <ChartLegend
            items={[
              { color: "var(--color-accent-green-muted)", label: "Regular window" },
              { color: "var(--color-accent-gold)", label: "Peak window" },
            ]}
          />
        ) : null
      }
      text="Most goals are scored between 61-75 minutes. Late goals continue to decide matches."
      title="Goal Timing: The Decisive Minutes"
      largeMetric={null}
    />
  );
}
