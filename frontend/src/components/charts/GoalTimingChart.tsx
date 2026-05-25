import type { CSSProperties } from "react";

import type { GoalTimingInsightResponse } from "../../api/types";
import { formatPercent } from "../../utils/format";

export function GoalTimingChart({ goalTiming }: { goalTiming: GoalTimingInsightResponse }) {
  const maxGoals = Math.max(...goalTiming.intervals.map((interval) => interval.goals), 1);

  return (
    <div className="goal-heatmap" aria-label="Regular-time goals by 15-minute interval">
      <div className="heatmap-grid" role="list" aria-label="Goal timing heatmap values">
        {goalTiming.intervals.map((interval) => {
          const intensity = interval.goals / maxGoals;
          const cellStyle = {
            "--heat-intensity": intensity.toFixed(2),
          } as CSSProperties;

          return (
            <div className={interval.rank === 1 ? "heatmap-cell peak" : "heatmap-cell"} key={interval.interval} role="listitem" style={cellStyle}>
              <span>{interval.interval}</span>
              <strong>{interval.goals.toLocaleString()}</strong>
              <small>{formatPercent(interval.share)}</small>
            </div>
          );
        })}
      </div>
      <div className="heatmap-legend" aria-hidden="true">
        <span>Low</span>
        <div>
          <i />
          <i />
          <i />
          <i />
        </div>
        <span>High</span>
      </div>
    </div>
  );
}
