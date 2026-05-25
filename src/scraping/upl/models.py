"""Shared scraper data models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PostgresScrapePlan:
    """Database-backed decision about which match pages need refreshing."""

    existing_tables: dict[str, list[dict[str, Any]]]
    skip_urls: set[str]
    pending_reasons: dict[str, str]
    complete_match_count: int
    incomplete_match_count: int
    failed_match_count: int
    recent_refresh_count: int

