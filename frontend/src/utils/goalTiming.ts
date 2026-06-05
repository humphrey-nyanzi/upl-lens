import type { GoalTimingInterval } from "../api/types";

export const REGULAR_TIME_WINDOWS = ["0-15", "16-30", "31-45", "46-60", "61-75", "76-90"] as const;

function normalizeIntervalLabel(label: string) {
  return label.replace(/\s/g, "").replace("–", "-");
}

export function getRegularTimeIntervals(intervals: GoalTimingInterval[]) {
  const intervalMap = new Map(intervals.map((interval) => [normalizeIntervalLabel(interval.interval), interval]));

  return REGULAR_TIME_WINDOWS.map((windowLabel) => {
    const interval = intervalMap.get(windowLabel);

    return (
      interval ?? {
        end_minute: Number(windowLabel.split("-")[1]),
        goals: 0,
        interval: windowLabel,
        rank: null,
        share: 0,
        start_minute: Number(windowLabel.split("-")[0]),
      }
    );
  });
}

export function getPeakRegularTimeInterval(intervals: GoalTimingInterval[]) {
  const regularIntervals = getRegularTimeIntervals(intervals);

  return regularIntervals.reduce<GoalTimingInterval | null>((peak, interval) => {
    if (!peak || interval.goals > peak.goals) return interval;
    return peak;
  }, null);
}
