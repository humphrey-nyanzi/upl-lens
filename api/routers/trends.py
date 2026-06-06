"""Historical trend endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from src.api.queries import get_season_trends
from src.api.schemas import SeasonTrendsResponse


router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/seasons", response_model=SeasonTrendsResponse)
def get_season_trend_rows() -> SeasonTrendsResponse:
    """Return season-by-season trend data for chart-ready frontend views."""

    return SeasonTrendsResponse(**get_season_trends())

