"""Match endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from src.api.queries import DEFAULT_LIMIT, get_match, list_match_intelligence, list_matches
from src.api.schemas import MatchDetail, MatchIntelligenceSummary, MatchSummary


router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=list[MatchSummary])
def get_matches(
    season: str | None = None,
    team: str | None = None,
    match_day: int | None = None,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[MatchSummary]:
    """Return matches from `staging.matches` with simple filters."""

    rows = list_matches(season=season, team=team, match_day=match_day, limit=limit, offset=offset)
    return [MatchSummary(**row) for row in rows]


@router.get("/intelligence", response_model=list[MatchIntelligenceSummary])
def get_match_intelligence(
    season: str | None = None,
    team: str | None = None,
    match_day: int | None = None,
    signal: str | None = None,
    sort: str = "interest",
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[MatchIntelligenceSummary]:
    """Return matches with precomputed signals for smarter exploration."""

    rows = list_match_intelligence(
        season=season,
        team=team,
        match_day=match_day,
        signal=signal,
        sort=sort,
        limit=limit,
        offset=offset,
    )
    return [MatchIntelligenceSummary(**row) for row in rows]


@router.get("/{match_id}", response_model=MatchDetail)
def get_match_by_id(match_id: int) -> MatchDetail:
    """Return one match plus its timeline, officials, and stats."""

    row = get_match(match_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Match {match_id} was not found.")
    return MatchDetail(**row)
