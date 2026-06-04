"""Notebook-promoted football insight queries."""

from __future__ import annotations

from typing import Any

from src.api.query_services.common import _fetch_all, _fetch_one


def get_goal_timing_insight(season: str | None = None) -> dict[str, Any]:
    """Return a scope-aware regular-time goal distribution for Feature 1.

    The original notebook separated added-time goals from the interval analysis.
    This production query follows the same rule by keeping only non-added-time
    goal events between minutes 1 and 90. When ``season`` is omitted, the
    response aggregates across every available season.
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
            SELECT events.minute_total
            FROM staging.events AS events
            INNER JOIN staging.matches AS matches
                ON matches.match_id = events.match_id
            WHERE (%(season)s::text IS NULL OR events.season = %(season)s::text)
                AND event_type IN ('goal', 'own_goal', 'penalty_goal')
                AND events.minute_total BETWEEN 1 AND 90
                AND events.is_added_time IS NOT TRUE
                AND matches.is_source_anomaly IS NOT TRUE
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

    scope_meta = _fetch_one(
        """
        SELECT
            COUNT(DISTINCT season)::integer AS season_count,
            MIN(match_date) AS first_match_date,
            MAX(match_date) AS last_match_date
        FROM staging.matches
        WHERE (%(season)s::text IS NULL OR season = %(season)s::text)
            AND is_source_anomaly IS NOT TRUE;
        """,
        {"season": season},
    )

    if scope_meta is None:
        scope_meta = {"season_count": 0, "first_match_date": None, "last_match_date": None}
    if season is not None and scope_meta["season_count"] == 0:
        raise ValueError(f"Season {season} was not found.")

    total_regular_time_goals = sum(row["goals"] for row in interval_rows)
    ranked_intervals = [row for row in interval_rows if row["rank"] == 1]
    peak_interval = ranked_intervals[0]["interval"] if ranked_intervals else None

    return {
        "season": season or "all",
        "scope_key": season or "all",
        "season_count": scope_meta["season_count"],
        "first_match_date": scope_meta["first_match_date"],
        "last_match_date": scope_meta["last_match_date"],
        "total_regular_time_goals": total_regular_time_goals,
        "peak_interval": peak_interval,
        "intervals": interval_rows,
    }

