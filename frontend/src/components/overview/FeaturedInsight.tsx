import type { GoalTimingInsightResponse } from "../../api/types";
import type { LoadState, PageKey } from "../../app/types";
import { ChartLegend, GoalTimingHeatmap } from "../charts/ChartPrimitives";
import { EmptyState } from "../common/EmptyState";

type FeaturedInsightProps = {
  goalTiming: GoalTimingInsightResponse | null;
  loadState: LoadState;
  onPageChange: (page: PageKey) => void;
};

export function FeaturedInsight({ goalTiming, loadState, onPageChange }: FeaturedInsightProps) {
  const chartData =
    goalTiming?.intervals.map((interval) => ({
      color: interval.rank === 1 ? "#f5b82e" : "#16a34a",
      label: interval.interval,
      value: interval.goals,
    })) ?? [];

  return (
    <section className="featured-insight overview-goal-card" aria-labelledby="featured-insight-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Featured insight</p>
          <h2 id="featured-insight-title">When do UPL goals arrive?</h2>
          <p>
            The current flagship insight compares regular-time scoring windows and points readers toward the periods that
            shape a season.
          </p>
        </div>
        <button className="text-button dark" type="button" onClick={() => onPageChange("goal-timing")}>
          Open Goal Timing
        </button>
      </div>

      {goalTiming ? (
        <div className="overview-goal-layout">
          <div className="insight-stat">
            <span>Peak scoring window</span>
            <strong>{goalTiming.peak_interval ?? "Unavailable"}</strong>
            <p>{goalTiming.total_regular_time_goals.toLocaleString()} regular-time goals counted.</p>
          </div>
          <GoalTimingHeatmap data={chartData} height={240} valueLabel="Goals" />
          <ChartLegend
            items={[
              { color: "#16a34a", label: "Regular window" },
              { color: "#f5b82e", label: "Peak window" },
            ]}
          />
          <p className="caveat">Data note: added-time goals are excluded from this period comparison.</p>
        </div>
      ) : (
        <EmptyState message={loadState === "loading" ? "Loading the goal timing insight." : "No goal timing insight returned yet."} />
      )}
    </section>
  );
}
