"""Season list endpoint."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException

from src.api.queries import get_season_overview, list_seasons
from src.api.schemas import SeasonOverviewResponse, SeasonResponse


router = APIRouter(prefix="/seasons", tags=["seasons"])


@router.get("", response_model=list[SeasonResponse])
def get_seasons() -> list[SeasonResponse]:
    """Return seasons currently available in staging."""

    return [SeasonResponse(**row) for row in list_seasons()]


@router.get("/{season}/overview", response_model=SeasonOverviewResponse)
def get_season_dashboard_overview(season: str) -> SeasonOverviewResponse:
    """Return one season summary for the React League Overview."""

    row = get_season_overview(season)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Season {season} was not found.")
    return SeasonOverviewResponse(**row)
