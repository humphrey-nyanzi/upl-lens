"""Notebook-promoted football insight queries."""

from __future__ import annotations

from typing import Any

from src.api.query_services.common import _fetch_all


def get_goal_timing_insight(season: str) -> dict[str, Any]:
    """Return regular-time goal distribution for the Feature 1 insight.

    The original notebook separated added-time goals from the interval analysis.
    This production query follows the same rule by keeping only non-added-time
    goal events between minutes 1 and 90.
    """

    interval_rows = _fetch_all(
        """
        WITH intervals AS (
            SELECT *
            FROM (
                VALUES
                    ('0-15', 1, 15, 1),
                    ('16-30', 16, 30, 2),
                    ('31-45', 31, 45, 3),
                    ('46-60', 46, 60, 4),
                    ('61-75', 61, 75, 5),
                    ('76-90', 76, 90, 6)
            ) AS interval_definitions(interval, start_minute, end_minute, display_order)
        ),
        goal_events AS (
            SELECT minute_total
            FROM staging.events
            WHERE season = %(season)s::text
                AND event_type IN ('goal', 'own_goal', 'penalty_goal')
                AND minute_total BETWEEN 1 AND 90
                AND is_added_time IS NOT TRUE
        ),
        interval_counts AS (
            SELECT
                intervals.interval,
                intervals.start_minute,
                intervals.end_minute,
                intervals.display_order,
                COUNT(goal_events.minute_total) AS goals
            FROM intervals
            LEFT JOIN goal_events
                ON goal_events.minute_total BETWEEN intervals.start_minute AND intervals.end_minute
            GROUP BY
                intervals.interval,
                intervals.start_minute,
                intervals.end_minute,
                intervals.display_order
        ),
        totals AS (
            SELECT COALESCE(SUM(goals), 0) AS total_regular_time_goals
            FROM interval_counts
        )
        SELECT
            interval_counts.interval,
            interval_counts.start_minute,
            interval_counts.end_minute,
            interval_counts.goals,
            CASE
                WHEN totals.total_regular_time_goals = 0 THEN 0
                ELSE ROUND(
                    interval_counts.goals::numeric / totals.total_regular_time_goals::numeric,
                    4
                )
            END AS share,
            CASE
                WHEN interval_counts.goals = 0 THEN NULL
                ELSE RANK() OVER (
                    ORDER BY interval_counts.goals DESC, interval_counts.display_order
                )
            END AS rank
        FROM interval_counts
        CROSS JOIN totals
        ORDER BY interval_counts.display_order;
        """,
        {"season": season},
    )

    total_regular_time_goals = sum(row["goals"] for row in interval_rows)
    ranked_intervals = [row for row in interval_rows if row["rank"] == 1]
    peak_interval = ranked_intervals[0]["interval"] if ranked_intervals else None

    return {
        "season": season,
        "total_regular_time_goals": total_regular_time_goals,
        "peak_interval": peak_interval,
        "intervals": interval_rows,
    }

