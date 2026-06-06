"""Team endpoints derived from staging matches."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from src.api.queries import DEFAULT_LIMIT, get_team_profile, list_teams
from src.api.schemas import TeamProfileResponse, TeamResponse


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


@router.get("/{team_slug}/profile", response_model=TeamProfileResponse)
def get_team_profile_by_slug(team_slug: str, season: str | None = None) -> TeamProfileResponse:
    """Return one team intelligence profile by app-safe slug."""

    row = get_team_profile(team_slug=team_slug, season=season)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Team {team_slug} was not found.")
    return TeamProfileResponse(**row)
