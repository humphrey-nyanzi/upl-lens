"""Insight endpoints promoted from notebook research."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.queries import get_goal_timing_insight
from src.api.schemas import GoalTimingInsightResponse


router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/goal-timing", response_model=GoalTimingInsightResponse)
def get_goal_timing(season: str | None = None) -> GoalTimingInsightResponse:
    """Return the Feature 1 goal timing distribution for one season or all seasons."""

    try:
        row = get_goal_timing_insight(season)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return GoalTimingInsightResponse(**row)
