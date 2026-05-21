"""Insight endpoints promoted from notebook research."""

from __future__ import annotations

from fastapi import APIRouter

from src.api.queries import get_goal_timing_insight
from src.api.schemas import GoalTimingInsightResponse


router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/goal-timing", response_model=GoalTimingInsightResponse)
def get_goal_timing(season: str) -> GoalTimingInsightResponse:
    """Return the Feature 1 goal timing distribution for one season."""

    row = get_goal_timing_insight(season)
    return GoalTimingInsightResponse(**row)
