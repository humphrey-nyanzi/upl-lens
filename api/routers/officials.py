"""Official assignment endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query

from src.api.queries import DEFAULT_LIMIT, list_officials
from src.api.schemas import OfficialResponse


router = APIRouter(prefix="/officials", tags=["officials"])


@router.get("", response_model=list[OfficialResponse])
def get_officials(
    season: str | None = None,
    match_day: int | None = None,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[OfficialResponse]:
    """Return official assignments from `staging.officials`."""

    rows = list_officials(season=season, match_day=match_day, limit=limit, offset=offset)
    return [OfficialResponse(**row) for row in rows]

