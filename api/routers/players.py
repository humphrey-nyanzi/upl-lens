"""Player endpoints derived from staging lineups and events."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from src.api.queries import DEFAULT_LIMIT, get_player, get_player_leaderboards, list_players
from src.api.schemas import PlayerDetail, PlayerLeaderboardsResponse, PlayerSummary


router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=list[PlayerSummary])
def get_players(
    season: str | None = None,
    player: str | None = None,
    sort: Literal["goals", "assists", "appearances", "starts", "cards", "goal_contributions", "bench_impact", "name"] = "goals",
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[PlayerSummary]:
    """Return player leaderboard rows from cleaned lineup and event data."""

    rows = list_players(season=season, player=player, sort=sort, limit=limit, offset=offset)
    return [PlayerSummary(**row) for row in rows]


@router.get("/leaderboards", response_model=PlayerLeaderboardsResponse)
def get_player_leaderboard_groups(
    season: str | None = None,
    limit: int = Query(10, ge=1, le=50),
) -> PlayerLeaderboardsResponse:
    """Return grouped player leaderboard slices for the Players page."""

    return PlayerLeaderboardsResponse(**get_player_leaderboards(season=season, limit=limit))


@router.get("/{player_slug}", response_model=PlayerDetail)
def get_player_by_slug(player_slug: str, season: str | None = None) -> PlayerDetail:
    """Return one player profile by the app-safe name slug."""

    row = get_player(player_slug=player_slug, season=season)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Player {player_slug} was not found.")
    return PlayerDetail(**row)
