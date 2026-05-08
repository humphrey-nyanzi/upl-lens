"""Season list endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from src.api.queries import list_seasons
from src.api.schemas import SeasonResponse


router = APIRouter(prefix="/seasons", tags=["seasons"])


@router.get("", response_model=list[SeasonResponse])
def get_seasons() -> list[SeasonResponse]:
    """Return seasons currently available in staging."""

    return [SeasonResponse(**row) for row in list_seasons()]

