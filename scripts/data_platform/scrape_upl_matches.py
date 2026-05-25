#!/usr/bin/env python
"""Compatibility wrapper for the structured UPL scraper.

The scraper implementation now lives under `src.scraping.upl` so network,
parsing, checkpointing, Postgres change detection, and CLI orchestration are
separate. This historical script remains the command and import front door.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.scraping.upl.cli import main
from src.scraping.upl.client import RateLimiter, ScraperClient, fetch_match_urls
from src.scraping.upl.constants import (
    EVENT_COLUMNS,
    FAILED_MATCH_COLUMNS,
    LEGACY_GOAL_COLUMNS,
    LINEUP_COLUMNS,
    MATCH_COLUMNS,
    OFFICIAL_COLUMNS,
    RAW_DATABASE_TABLE_COLUMNS,
    STAFF_COLUMNS,
    STAT_COLUMNS,
    TABLE_COLUMNS,
    TABLE_NAMES,
)
from src.scraping.upl.dataframes import (
    _build_legacy_goal_dataframe,
    _build_output_dataframe,
    _filter_tables_to_requested_season,
    _save_structured_outputs,
)
from src.scraping.upl.models import PostgresScrapePlan
from src.scraping.upl.parsing import (
    _build_event_row,
    _clean_player_name,
    _extract_lineups_and_staff,
    _extract_match_post_id,
    _extract_match_row,
    _extract_officials,
    _extract_player_from_icon,
    _extract_player_from_segment,
    _extract_stats,
    _extract_substitution_players,
    _extract_team_links,
    _extract_timeline_events,
    _first_anchor_info,
    _infer_team_side,
    _normalize_key,
    _normalize_whitespace,
    _parse_goal_type,
    _safe_text,
    _segment_text,
    _split_node_segments,
    parse_match_page,
)
from src.scraping.upl.pipeline import _fetch_and_parse_match, scrape_season
from src.scraping.upl.postgres import (
    _build_postgres_scrape_plan,
    _filter_existing_tables_to_calendar,
    _is_complete_match,
    _load_existing_raw_tables_from_postgres,
    _query_failed_match_urls,
    _query_raw_match_refresh_state,
    _query_raw_table_rows,
    _recent_completed_urls,
)
from src.scraping.upl.state import (
    _append_match_payload,
    _build_failed_matches_dataframe,
    _checkpoint_path,
    _empty_scraped_tables,
    _failed_matches_path,
    _load_checkpoint,
    _remove_match_rows,
    _save_checkpoint,
    _save_failed_matches_manifest,
)


if __name__ == "__main__":
    sys.exit(main())
