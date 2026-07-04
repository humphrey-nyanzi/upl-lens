"""Season-level scraper orchestration.

This module coordinates the HTTP client, parser, checkpoint state, optional
Postgres change detection, and output DataFrame shaping for one season run.
"""

from __future__ import annotations

import datetime as dt
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import pandas as pd

from src.config import (
    CHECKPOINT_EVERY,
    DATA_CACHE,
    MAX_CONCURRENT_REQUESTS,
    RATE_LIMIT_SECONDS,
    USE_HTML_CACHE,
    USER_AGENT,
    raw_season_source_preflight_file,
    season_key,
)
from src.scraping.upl.client import RateLimiter, ScraperClient, fetch_match_urls
from src.scraping.upl.constants import TABLE_COLUMNS, TABLE_NAMES
from src.scraping.upl.dataframes import (
    _build_output_dataframe,
    _filter_tables_to_requested_season,
)
from src.scraping.upl.models import PostgresScrapePlan
from src.scraping.upl.parsing import parse_match_page
from src.scraping.upl.postgres import _build_postgres_scrape_plan
from src.scraping.upl.state import (
    _append_match_payload,
    _empty_scraped_tables,
    _load_checkpoint,
    _remove_match_rows,
    _save_checkpoint,
)


def _fetch_and_parse_match(
    client: ScraperClient, url: str
) -> tuple[str, dict[str, Any]]:
    """
    Download one match page and return all normalized table rows for that match.

    A small random sleep is added before the request starts.
    This jitter makes concurrent workers less likely to synchronize into bursts.
    """
    time.sleep(random.uniform(0.0, 0.25))
    match_html = client.get(url)
    return url, parse_match_page(match_html, url)


def _canonical_refresh_value(column: str, value: Any) -> Any:
    """Normalize scraper and Postgres values for match-payload comparison."""
    if value is None or (not isinstance(value, (list, dict)) and pd.isna(value)):
        return None
    if column == "date":
        try:
            return pd.Timestamp(value).date().isoformat()
        except (TypeError, ValueError):
            pass
    if column == "time":
        try:
            parsed = (
                value if isinstance(value, dt.time) else pd.Timestamp(str(value)).time()
            )
            return parsed.isoformat(timespec="minutes")
        except (TypeError, ValueError):
            pass
    if isinstance(value, (dt.date, dt.datetime, dt.time, pd.Timestamp)):
        return value.isoformat()
    return value.strip() if isinstance(value, str) else value


def _canonical_match_rows(rows: list[dict[str, Any]]) -> list[str]:
    """Return stable row signatures independent of database row ordering."""
    signatures = []
    for row in rows:
        canonical = {
            column: _canonical_refresh_value(column, value)
            for column, value in row.items()
        }
        signatures.append(
            json.dumps(canonical, sort_keys=True, default=str, separators=(",", ":"))
        )
    return sorted(signatures)


def _match_payload_changed(
    existing_tables: dict[str, list[dict[str, Any]]],
    match_payload: dict[str, Any],
    match_url: str,
) -> bool:
    """Return whether a fetched match differs from its hosted raw payload."""
    for table_name in TABLE_NAMES:
        existing_rows = [
            row
            for row in existing_tables[table_name]
            if row.get("match_url") == match_url
        ]
        incoming_rows = match_payload.get(table_name, [])
        if _canonical_match_rows(existing_rows) != _canonical_match_rows(incoming_rows):
            return True
    return False


def scrape_season(
    season: str,
    *,
    refresh_source: bool = False,
    use_postgres_change_detection: bool = False,
    recent_completed_limit: int = 10,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    """
    Scrape all structured match data for a season.

    Speed improvements used here:
    - shared requests session
    - HTTP retries with backoff
    - bounded concurrency
    - cache of raw HTML
    - checkpointing for restart safety

    Returns
    -------
    tuple[dict[str, pd.DataFrame], dict[str, Any]]
        Structured raw tables plus run metadata for the season
    """
    headers = {"User-Agent": USER_AGENT}
    cache_dir = DATA_CACHE / "match_html" / season_key(season)
    rate_limiter = RateLimiter(RATE_LIMIT_SECONDS)
    use_cache = USE_HTML_CACHE and not refresh_source
    client = ScraperClient(
        headers=headers,
        cache_dir=cache_dir,
        rate_limiter=rate_limiter,
        use_cache=use_cache,
    )

    if refresh_source:
        print("[ok] Refresh source enabled: bypassing cached HTML and checkpoint state")

    match_urls = fetch_match_urls(
        client,
        season,
        report_path=raw_season_source_preflight_file(season),
    )
    postgres_plan: PostgresScrapePlan | None = None
    if use_postgres_change_detection:
        postgres_plan = _build_postgres_scrape_plan(
            season,
            match_urls,
            recent_completed_limit=recent_completed_limit,
        )
        completed_urls = postgres_plan.skip_urls.copy()
        all_tables = postgres_plan.existing_tables
        failed_urls = {}
        print("[ok] Postgres change detection enabled")
        print(
            f"[ok] Existing complete matches in Postgres: {postgres_plan.complete_match_count}"
        )
        print(
            f"[ok] Existing incomplete/unplayed matches in Postgres: {postgres_plan.incomplete_match_count}"
        )
        print(
            f"[ok] Previously failed matches in Postgres: {postgres_plan.failed_match_count}"
        )
        print(
            f"[ok] Recent completed matches selected for refresh: {postgres_plan.recent_refresh_count}"
        )
    elif refresh_source:
        completed_urls, all_tables, failed_urls = set(), _empty_scraped_tables(), {}
    else:
        completed_urls, all_tables, failed_urls = _load_checkpoint(season)
    starting_completed_count = len(completed_urls)
    pending_urls = [url for url in match_urls if url not in completed_urls]
    attempted_urls = set(pending_urls)
    affected_match_urls: set[str] = set()
    retry_first_urls = [url for url in pending_urls if url in failed_urls]
    new_pending_urls = [url for url in pending_urls if url not in failed_urls]
    pending_urls = retry_first_urls + new_pending_urls

    print(f"\nScraping {len(match_urls)} matches...")
    if use_postgres_change_detection:
        print(f"[ok] Skipping {len(completed_urls)} complete matches from Postgres")
    elif completed_urls:
        print(
            f"[ok] Skipping {len(completed_urls)} matches already saved in checkpoint"
        )
    print(f"[ok] {len(pending_urls)} matches left to fetch")
    if postgres_plan and postgres_plan.pending_reasons:
        reason_counts: dict[str, int] = {}
        for reason in postgres_plan.pending_reasons.values():
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        print("[ok] Postgres scrape reasons:")
        for reason, row_count in sorted(reason_counts.items()):
            print(f"  {reason}: {row_count}")
    if retry_first_urls:
        print(f"[ok] Prioritizing {len(retry_first_urls)} previously failed matches")

    if pending_urls:
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
            future_to_url = {
                executor.submit(_fetch_and_parse_match, client, url): url
                for url in pending_urls
            }

            for index, future in enumerate(as_completed(future_to_url), start=1):
                url = future_to_url[future]

                try:
                    completed_url, match_payload = future.result()
                    if postgres_plan is None or _match_payload_changed(
                        all_tables, match_payload, completed_url
                    ):
                        affected_match_urls.add(completed_url)
                    _remove_match_rows(all_tables, completed_url)
                    _append_match_payload(all_tables, match_payload)
                    completed_urls.add(completed_url)
                    failed_urls.pop(completed_url, None)
                except Exception as exc:
                    print(f"  [error] Error processing {url}: {exc}")
                    current_attempt_count = failed_urls.get(url, {}).get(
                        "attempt_count", 0
                    )
                    failed_urls[url] = {
                        "attempt_count": current_attempt_count + 1,
                        "last_error": str(exc),
                        "last_attempt_at_utc": pd.Timestamp.now("UTC").isoformat(),
                    }
                    continue

                processed_count = len(completed_urls)
                if processed_count % 10 == 0:
                    print(
                        f"  [ok] Processed {processed_count}/{len(match_urls)} matches"
                    )

                if index % CHECKPOINT_EVERY == 0:
                    _save_checkpoint(season, completed_urls, all_tables, failed_urls)
                    print(
                        f"  [ok] Checkpoint saved after {processed_count} completed matches"
                    )

    _save_checkpoint(season, completed_urls, all_tables, failed_urls)
    season_tables = {
        table_name: _build_output_dataframe(
            all_tables[table_name], TABLE_COLUMNS[table_name]
        )
        for table_name in TABLE_NAMES
    }
    season_tables, spill_counts = _filter_tables_to_requested_season(
        season, season_tables
    )
    scrape_summary = {
        "match_urls_found": len(match_urls),
        "starting_completed_matches": starting_completed_count,
        "completed_matches": len(completed_urls),
        "successful_fetches": len(completed_urls) - starting_completed_count,
        "failed_matches": len(failed_urls),
        "affected_match_urls": sorted(affected_match_urls),
        "attempted_match_urls": sorted(attempted_urls),
        "failed_match_urls": sorted(failed_urls),
        "spill_rows_filtered": spill_counts,
    }
    return season_tables, scrape_summary
