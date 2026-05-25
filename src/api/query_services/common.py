"""Shared database helpers for API read queries."""

from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row

from src.db.connection import get_api_psycopg_connection


DEFAULT_LIMIT = 50
MAX_LIMIT = 200


def clamp_pagination(limit: int, offset: int) -> tuple[int, int]:
    """Return safe pagination values for list endpoints."""

    safe_limit = max(1, min(limit, MAX_LIMIT))
    safe_offset = max(0, offset)
    return safe_limit, safe_offset


def _team_like(team: str | None) -> str | None:
    """Return a case-insensitive pattern for simple team-name filtering."""

    if team is None or not team.strip():
        return None
    return f"%{team.strip()}%"


def _fetch_all(
    query: str,
    params: dict[str, Any] | None = None,
    connection: psycopg.Connection | None = None,
) -> list[dict[str, Any]]:
    """Run a read query and return dictionaries ready for Pydantic models."""

    if connection is None:
        with get_api_psycopg_connection() as pooled_connection:
            return _fetch_all(query, params=params, connection=pooled_connection)

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query, params or {})
        return [dict(row) for row in cursor.fetchall()]


def _fetch_one(
    query: str,
    params: dict[str, Any] | None = None,
    connection: psycopg.Connection | None = None,
) -> dict[str, Any] | None:
    """Run a read query and return one dictionary, or None when no row exists."""

    if connection is None:
        with get_api_psycopg_connection() as pooled_connection:
            return _fetch_one(query, params=params, connection=pooled_connection)

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query, params or {})
        row = cursor.fetchone()
        return None if row is None else dict(row)

