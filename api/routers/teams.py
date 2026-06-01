"""Team endpoints derived from staging matches."""

from __future__ import annotations

from fastapi import APIRouter, Query

from src.api.queries import DEFAULT_LIMIT, list_teams
from src.api.schemas import TeamResponse


router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[TeamResponse])
def get_teams(
    season: str | None = None,
    team: str | None = None,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[TeamResponse]:
    """Return teams with basic match-record summaries."""

    rows = list_teams(season=season, team=team, limit=limit, offset=offset)
    return [TeamResponse(**row) for row in rows]
