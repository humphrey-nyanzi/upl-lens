"""Compatibility facade for FastAPI read query helpers.

The query implementation is split under `src.api.query_services` by domain so
route modules can stay thin without growing one large SQL file. Existing imports
from `src.api.queries` remain supported.
"""

from __future__ import annotations

from src.api.query_services.common import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    _fetch_all,
    _fetch_one,
    _team_like,
    clamp_pagination,
)
from src.api.query_services.events import list_events
from src.api.query_services.health import get_health_status
from src.api.query_services.insights import get_goal_timing_insight
from src.api.query_services.matches import get_match, list_match_intelligence, list_matches
from src.api.query_services.officials import list_officials
from src.api.query_services.overview import get_overview_intelligence
from src.api.query_services.players import get_player, get_player_leaderboards, list_players
from src.api.query_services.seasons import _event_type_label, get_season_overview, list_seasons
from src.api.query_services.teams import get_team_profile, list_teams
from src.api.query_services.trends import get_season_trends
