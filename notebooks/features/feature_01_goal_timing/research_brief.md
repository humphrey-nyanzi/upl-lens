# Research Brief: Feature 01 - Goal Timing

This file captures the football thinking behind Feature 1. The production
implementation details live in `product_plan.md`.

## Status

promoted

## Feature Question

When in a Uganda Premier League match are goals most likely to be scored?

## Why This Matters

The official UPL website stores individual match pages. This feature turns those
match timelines into a league-level pattern that is difficult to see by reading
match pages one by one.

## Data Used In Research

Research source:

- Older processed goal timing data under `data/processed/`.
- Structured scraper event data where available.
- Notebook research in `analysis.ipynb` and `analysis_v2.ipynb`.

Production feature source:

- Cleaned Postgres `staging.events`.

Seasons included:

- The original pilot covered completed seasons from `2019_20` through `2024_25`.
- The promoted API endpoint is season-filtered and can also serve current
  staging seasons such as `2025_26`.

Filters used in the promoted slice:

- `event_type` in `goal`, `own_goal`, `penalty_goal`
- `minute_total` between `1` and `90`
- `is_added_time IS NOT TRUE`

## Final Finding

The original pilot found that the highest-volume regular-time goal window across
the historical study period was `46-60`, the first 15 minutes after halftime.
At finer resolution, the pilot also highlighted `51-60` and `56-60` as peak
windows.

## Metric Definitions

```text
regular_time_goal = goal event with minute_total between 1 and 90 and not added time
interval_goals = count of regular_time_goal rows in a 15-minute interval
interval_share = interval_goals / total_regular_time_goals
peak_interval = interval with the highest interval_goals
```

Intervals:

```text
0-15
16-30
31-45
46-60
61-75
76-90
```

## Caveats

- Added-time goals are excluded from the interval distribution.
- The product endpoint currently returns one season at a time.
- The first promoted slice is season-level only; team-level and home/away
  filters can be added later.
- Current-season results can change after each scheduled data refresh.

## Evidence

Notebook evidence:

```text
analysis.ipynb - Timing Patterns / Regular Time Goals
analysis.ipynb - 15-minute, 10-minute, and 5-minute interval sections
analysis_v2.ipynb - later exploratory match-state ideas
```

Reference outputs:

```text
outputs/features/feature_01_goal_timing/goal_timing_upl.png
outputs/features/feature_01_goal_timing/gqr_gtsi_trends.png
```
