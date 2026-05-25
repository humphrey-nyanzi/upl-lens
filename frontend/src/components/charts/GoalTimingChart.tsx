import type { GoalTimingInsightResponse } from "../../api/types";
import { formatPercent } from "../../utils/format";

export function GoalTimingChart({ goalTiming }: { goalTiming: GoalTimingInsightResponse }) {
  const maxGoals = Math.max(...goalTiming.intervals.map((interval) => interval.goals), 1);

  return (
    <div className="goal-timing-chart" aria-label="Regular-time goals by 15-minute interval">
      {goalTiming.intervals.map((interval) => {
        const width = `${Math.max((interval.goals / maxGoals) * 100, interval.goals > 0 ? 8 : 0)}%`;

        return (
          <div className="goal-timing-row" key={interval.interval}>
            <span>{interval.interval}</span>
            <div className="goal-timing-bar-track">
              <div className={interval.rank === 1 ? "goal-timing-bar peak" : "goal-timing-bar"} style={{ width }} />
            </div>
            <strong>
              {interval.goals.toLocaleString()} ({formatPercent(interval.share)})
            </strong>
          </div>
        );
      })}
    </div>
  );
}
