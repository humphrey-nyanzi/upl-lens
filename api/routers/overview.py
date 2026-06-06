"""Overview intelligence endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.queries import get_overview_intelligence
from src.api.schemas import OverviewIntelligenceResponse


router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("/intelligence", response_model=OverviewIntelligenceResponse)
def get_overview_intelligence_response(season: str | None = None) -> OverviewIntelligenceResponse:
    """Return overview modules that turn raw season facts into product signals."""

    row = get_overview_intelligence(season=season)
    if row is None:
        detail = f"Season {season} was not found." if season else "Overview intelligence is unavailable."
        raise HTTPException(status_code=404, detail=detail)
    return OverviewIntelligenceResponse(**row)

