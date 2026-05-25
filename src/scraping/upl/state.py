"""Checkpoint and in-memory table state for resumable scraping."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import DATA_CACHE, raw_season_failed_matches_file, season_key
from src.dataset import save_dataframe
from src.scraping.upl.constants import FAILED_MATCH_COLUMNS, TABLE_NAMES
from src.scraping.upl.dataframes import _build_output_dataframe


def _empty_scraped_tables() -> dict[str, list[dict[str, Any]]]:
    """Return an empty in-memory container for all output tables."""
    return {table_name: [] for table_name in TABLE_NAMES}


def _checkpoint_path(season: str) -> Path:
    """Store progress metadata per season so interrupted runs can resume."""
    return DATA_CACHE / f"upl_events_{season_key(season)}_checkpoint.json"


def _failed_matches_path(season: str) -> Path:
    """Return the human-readable failed-match manifest path for a season."""
    return raw_season_failed_matches_file(season)


def _build_failed_matches_dataframe(season: str, failed_urls: dict[str, dict[str, Any]]) -> pd.DataFrame:
    """Create a stable dataframe of failed URLs for one season."""
    rows = []
    for url, details in sorted(
        failed_urls.items(),
        key=lambda item: (
            -(item[1].get("attempt_count", 0) or 0),
            item[1].get("last_attempt_at_utc") or "",
            item[0],
        ),
    ):
        rows.append(
            {
                "match_url": url,
                "season": season,
                "attempt_count": details.get("attempt_count", 0),
                "last_error": details.get("last_error"),
                "last_attempt_at_utc": details.get("last_attempt_at_utc"),
            }
        )

    return _build_output_dataframe(rows, FAILED_MATCH_COLUMNS)


def _save_failed_matches_manifest(season: str, failed_urls: dict[str, dict[str, Any]]) -> None:
    """Persist failed match URLs so the next run can prioritize them."""
    manifest_path = _failed_matches_path(season)
    failed_df = _build_failed_matches_dataframe(season, failed_urls)
    save_dataframe(failed_df, manifest_path)


def _load_checkpoint(season: str) -> tuple[set[str], dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    """
    Load saved progress from disk if it exists.

    The new checkpoint format stores all structured tables together. Legacy
    checkpoints from the event-only scraper are ignored so the scraper can
    rebuild everything cleanly from cached HTML.
    """
    checkpoint_path = _checkpoint_path(season)
    if not checkpoint_path.exists():
        return set(), _empty_scraped_tables(), {}

    payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    if "tables" not in payload:
        print("[warn] Legacy checkpoint detected; rebuilding structured tables from cached HTML")
        return set(), _empty_scraped_tables(), {}

    completed_urls = set(payload.get("completed_urls", []))
    tables = _empty_scraped_tables()
    saved_tables = payload.get("tables", {})
    for table_name in TABLE_NAMES:
        tables[table_name] = saved_tables.get(table_name, [])
    failed_urls = payload.get("failed_urls", {})

    print(f"[ok] Resuming from checkpoint with {len(completed_urls)} completed matches")
    return completed_urls, tables, failed_urls


def _save_checkpoint(
    season: str,
    completed_urls: set[str],
    tables: dict[str, list[dict[str, Any]]],
    failed_urls: dict[str, dict[str, Any]],
) -> None:
    """Persist current progress so long runs can safely resume."""
    checkpoint_path = _checkpoint_path(season)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "completed_urls": sorted(completed_urls),
        "tables": tables,
        "failed_urls": failed_urls,
    }
    checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")
    _save_failed_matches_manifest(season, failed_urls)


def _append_match_payload(aggregated_tables: dict[str, list[dict[str, Any]]], match_payload: dict[str, Any]) -> None:
    """Append one parsed match payload into the aggregated table store."""
    aggregated_tables["matches"].append(match_payload["match"])
    for table_name in TABLE_NAMES:
        if table_name == "matches":
            continue
        aggregated_tables[table_name].extend(match_payload[table_name])


def _remove_match_rows(aggregated_tables: dict[str, list[dict[str, Any]]], match_url: str) -> None:
    """Remove stale rows for one match before appending its refreshed payload."""

    for table_name in list(aggregated_tables):
        aggregated_tables[table_name] = [
            row
            for row in aggregated_tables[table_name]
            if row.get("match_url") != match_url
        ]

