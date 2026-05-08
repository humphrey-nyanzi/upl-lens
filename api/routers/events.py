"""Event endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query

from src.api.queries import DEFAULT_LIMIT, list_events
from src.api.schemas import EventResponse


router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
def get_events(
    season: str | None = None,
    team: str | None = None,
    match_day: int | None = None,
    event_type: str | None = None,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[EventResponse]:
    """Return cleaned timeline events from `staging.events`."""

    rows = list_events(
        season=season,
        team=team,
        match_day=match_day,
        event_type=event_type,
        limit=limit,
        offset=offset,
    )
    return [EventResponse(**row) for row in rows]

