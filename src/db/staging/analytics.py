"""Analytics-table refreshes derived from rebuilt staging rows."""

from __future__ import annotations

from sqlalchemy import text

from src.db.staging.models import ProgressCallback


def _refresh_team_season_summary(
    connection,
    seasons: list[str],
    progress: ProgressCallback | None = None,
) -> None:
    """Refresh stored team summaries for the rebuilt staging seasons.

    The aggregation SQL is owned by the database function created in migration
    006. Python only tells Postgres which season slice was rebuilt.
    """

    if progress:
        progress("Refreshing analytics.team_season_summary")
    connection.execute(
        text("SELECT analytics.refresh_team_season_summary(CAST(:seasons AS TEXT[]))"),
        {"seasons": seasons},
    )
    if progress:
        progress("Refreshed analytics.team_season_summary")

