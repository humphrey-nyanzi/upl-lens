#!/usr/bin/env python
"""
Scrape structured UPL match data from the official website.

Usage:
    python scripts/data_platform/scrape_upl_matches.py --season 2025-26
"""

import sys
import argparse
import hashlib
import json
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    CHECKPOINT_EVERY,
    DATA_CACHE,
    DATA_RAW,
    MAX_CONCURRENT_REQUESTS,
    RATE_LIMIT_SECONDS,
    REQUEST_TIMEOUT,
    RETRY_BACKOFF_SECONDS,
    SCRAPE_RETRY_ATTEMPTS,
    SCRAPER_STATUS_FORCELIST,
    UPL_CALENDAR_URL,
    UPL_EVENT_URL_PREFIX,
    USE_HTML_CACHE,
    USER_AGENT,
    raw_season_failed_matches_file,
    raw_season_dir,
    raw_season_file,
    season_key,
)
from src.dataset import save_dataframe


TABLE_NAMES = ("matches", "events", "lineups", "staff", "officials", "stats")
FAILED_MATCH_COLUMNS = [
    "match_url",
    "season",
    "attempt_count",
    "last_error",
    "last_attempt_at_utc",
]

MATCH_COLUMNS = [
    "match_id",
    "match_url",
    "source_page_title",
    "date",
    "time",
    "league",
    "season",
    "match_day",
    "home_team",
    "home_team_url",
    "away_team",
    "away_team_url",
    "ground_name",
    "ground_address",
    "man_of_the_match",
    "man_of_the_match_team",
    "home_score",
    "away_score",
    "home_first_half_goals",
    "away_first_half_goals",
    "home_second_half_goals",
    "away_second_half_goals",
    "has_timeline",
    "has_lineups",
    "has_officials",
    "has_stats",
]

EVENT_COLUMNS = [
    "match_id",
    "match_url",
    "date",
    "time",
    "league",
    "season",
    "match_day",
    "home_team",
    "away_team",
    "event_index",
    "event_type",
    "event_minute",
    "team_side",
    "player_name",
    "player_url",
    "goal_type",
    "sub_out_player_name",
    "sub_out_player_url",
    "sub_in_player_name",
    "sub_in_player_url",
]

LINEUP_COLUMNS = [
    "match_id",
    "match_url",
    "season",
    "match_day",
    "home_team",
    "away_team",
    "team_name",
    "team_side",
    "squad_role",
    "shirt_number",
    "player_name",
    "player_url",
    "player_position",
    "is_player_of_match",
    "swap_badge_type",
    "linked_player_name",
    "linked_shirt_number",
]

STAFF_COLUMNS = [
    "match_id",
    "match_url",
    "season",
    "match_day",
    "home_team",
    "away_team",
    "team_name",
    "team_side",
    "role",
    "person_name",
    "person_url",
]

OFFICIAL_COLUMNS = [
    "match_id",
    "match_url",
    "season",
    "match_day",
    "home_team",
    "away_team",
    "role",
    "official_name",
]

STAT_COLUMNS = [
    "match_id",
    "match_url",
    "season",
    "match_day",
    "home_team",
    "away_team",
    "statistic_name",
    "home_value",
    "away_value",
]

TABLE_COLUMNS = {
    "matches": MATCH_COLUMNS,
    "events": EVENT_COLUMNS,
    "lineups": LINEUP_COLUMNS,
    "staff": STAFF_COLUMNS,
    "officials": OFFICIAL_COLUMNS,
    "stats": STAT_COLUMNS,
}

LEGACY_GOAL_COLUMNS = [
    "Date",
    "Time",
    "League",
    "Season",
    "Match Day",
    "home_team",
    "away_team",
    "goal_minute",
    "team_side",
    "player_name",
    "goal_type",
]


class RateLimiter:
    """
    Small thread-safe rate limiter for polite scraping.

    Why this exists:
    - We want some parallelism so the scraper is faster.
    - We also want to avoid bursts of requests that could look abusive.
    - This limiter enforces a minimum gap between request start times
      across all worker threads.
    """

    def __init__(self, min_interval_seconds: float) -> None:
        self.min_interval_seconds = max(0.0, min_interval_seconds)
        self._lock = threading.Lock()
        self._next_allowed_time = 0.0

    def wait(self) -> None:
        """Block until the next request is allowed to start."""
        if self.min_interval_seconds <= 0:
            return

        with self._lock:
            now = time.monotonic()
            wait_seconds = max(0.0, self._next_allowed_time - now)
            self._next_allowed_time = max(self._next_allowed_time, now) + self.min_interval_seconds

        if wait_seconds > 0:
            time.sleep(wait_seconds)


class ScraperClient:
    """
    Network helper that combines retries, rate limiting, and HTML caching.

    This class keeps the HTTP concerns in one place so the scraping logic
    can focus on parsing and shaping the data.
    """

    def __init__(
        self,
        headers: dict[str, str],
        cache_dir: Path,
        rate_limiter: RateLimiter,
        use_cache: bool = True,
    ) -> None:
        self.headers = headers
        self.cache_dir = cache_dir
        self.rate_limiter = rate_limiter
        self.use_cache = use_cache
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        """
        Create one reusable session.

        Reusing a session is faster than calling requests.get repeatedly
        because TCP connections can be reused instead of reopened every time.
        """
        session = requests.Session()
        session.headers.update(self.headers)

        retry = Retry(
            total=SCRAPE_RETRY_ATTEMPTS,
            backoff_factor=RETRY_BACKOFF_SECONDS,
            status_forcelist=SCRAPER_STATUS_FORCELIST,
            allowed_methods=frozenset({"GET"}),
            respect_retry_after_header=True,
        )

        adapter = HTTPAdapter(max_retries=retry, pool_connections=MAX_CONCURRENT_REQUESTS, pool_maxsize=MAX_CONCURRENT_REQUESTS)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _cache_path_for_url(self, url: str) -> Path:
        """
        Convert a URL into a stable cache filename.

        We hash the full URL so the filename is safe on all filesystems
        and stays short even for long URLs.
        """
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{url_hash}.html"

    def get(self, url: str) -> bytes:
        """
        Fetch one URL with optional cache support.

        Cache flow:
        - If we already saved the HTML locally, read it from disk.
        - Otherwise, wait for the rate limiter, make the request, then save it.
        """
        cache_path = self._cache_path_for_url(url)

        if self.use_cache and cache_path.exists():
            return cache_path.read_bytes()

        self.rate_limiter.wait()
        response = self.session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        content = response.content

        if self.use_cache:
            cache_path.write_bytes(content)

        return content


def _empty_scraped_tables() -> dict[str, list[dict[str, Any]]]:
    """Return an empty in-memory container for all output tables."""
    return {table_name: [] for table_name in TABLE_NAMES}


def _normalize_whitespace(value: str | None) -> str | None:
    """Collapse repeated whitespace and strip surrounding spaces."""
    if value is None:
        return None

    normalized = re.sub(r"\s+", " ", value).strip()
    return normalized or None


def _normalize_key(value: str) -> str:
    """Convert header text into a snake_case key."""
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _safe_text(node: Tag | None) -> str | None:
    """Safely return stripped text from a tag."""
    if node is None:
        return None
    return _normalize_whitespace(node.get_text(" ", strip=True))


def _first_anchor_info(node: Tag | None) -> tuple[str | None, str | None]:
    """Extract the first anchor's text and href from a tag."""
    if node is None:
        return None, None

    anchor = node.select_one("a")
    if anchor is None:
        return None, None

    return _normalize_whitespace(anchor.get_text(" ", strip=True)), anchor.get("href")


def fetch_match_urls(client: ScraperClient, season: str) -> list[str]:
    """
    Fetch all match URLs for a given season.

    Parameters
    ----------
    client : ScraperClient
        Reusable HTTP client with caching and rate limiting.
    season : str
        Season string (e.g., "2025-26")

    Returns
    -------
    list[str]
        Sorted list of unique match URLs
    """
    calendar_url = UPL_CALENDAR_URL.format(season=season)
    print(f"Fetching match calendar from: {calendar_url}")

    try:
        response_content = client.get(calendar_url)
        print("[ok] Calendar fetched successfully")
    except Exception as exc:
        print(f"[error] Failed to fetch calendar: {exc}")
        raise

    soup = BeautifulSoup(response_content, "html.parser")
    match_urls = []

    for link in soup.select(f'a[href^="{UPL_EVENT_URL_PREFIX}"]'):
        url = link.get("href")
        if url:
            match_urls.append(url)

    unique_match_urls = sorted(set(match_urls))
    print(f"[ok] Found {len(unique_match_urls)} unique matches")
    return unique_match_urls


def _split_node_segments(node: Tag) -> list[list[Any]]:
    """
    Split a tag's children into <br>-separated segments.

    The UPL timeline uses the same content arranged in different orders
    on the home and away side. Segmenting by <br> lets us map each player
    to the matching icon regardless of that ordering.
    """
    segments: list[list[Any]] = [[]]

    for child in node.children:
        if isinstance(child, NavigableString):
            if child.strip():
                segments[-1].append(child)
            continue

        if getattr(child, "name", None) == "br":
            if segments[-1]:
                segments.append([])
            continue

        segments[-1].append(child)

    return [segment for segment in segments if _segment_text(segment)]


def _segment_text(segment: list[Any]) -> str:
    """Return the normalized text content of a segment."""
    parts = []
    for item in segment:
        if isinstance(item, NavigableString):
            text = _normalize_whitespace(str(item))
        elif isinstance(item, Tag):
            text = _normalize_whitespace(item.get_text(" ", strip=True))
        else:
            text = None

        if text:
            parts.append(text)

    return _normalize_whitespace(" ".join(parts)) or ""


def _clean_player_name(player_name: str | None) -> str | None:
    """Normalize player text scraped from the timeline."""
    if not player_name:
        return None

    cleaned_player_name = re.sub(r"^\s*\d+\.*\s*", "", player_name).strip()
    return cleaned_player_name or None


def _extract_player_from_segment(segment: list[Any]) -> tuple[str | None, str | None]:
    """Extract player name and URL from one segment."""
    for item in segment:
        if isinstance(item, Tag) and item.name == "a":
            return _clean_player_name(_safe_text(item)), item.get("href")

    return _clean_player_name(_segment_text(segment)), None


def _extract_player_from_icon(icon: Tag) -> tuple[str | None, str | None]:
    """Extract the player attached to a specific timeline icon."""
    icon_td = icon.find_parent("td")
    if icon_td is None:
        return None, None

    for segment in _split_node_segments(icon_td):
        if any(item is icon for item in segment):
            return _extract_player_from_segment(segment)

    return None, None


def _extract_substitution_players(cell: Tag) -> tuple[str | None, str | None, str | None, str | None]:
    """
    Extract outgoing and incoming players from a substitution cell.

    Home and away timeline cells arrange anchors and icons differently, so
    this parser looks at each <br>-separated segment independently instead
    of assuming a fixed icon-before-name order.
    """
    sub_out_player_name = None
    sub_out_player_url = None
    sub_in_player_name = None
    sub_in_player_url = None

    for segment in _split_node_segments(cell):
        titles = [
            (item.get("title") or "").strip().lower()
            for item in segment
            if isinstance(item, Tag) and item.name == "i"
        ]
        player_name, player_url = _extract_player_from_segment(segment)

        if any("sub out" in title for title in titles):
            sub_out_player_name = player_name
            sub_out_player_url = player_url
        elif any("sub in" in title for title in titles):
            sub_in_player_name = player_name
            sub_in_player_url = player_url

    return sub_out_player_name, sub_out_player_url, sub_in_player_name, sub_in_player_url


def _build_event_row(
    match_row: dict[str, Any],
    event_index: int,
    event_type: str,
    minute: str | None,
    team_side: str,
    player_name: str | None,
    player_url: str | None = None,
    goal_type: str | None = None,
    sub_out_player_name: str | None = None,
    sub_out_player_url: str | None = None,
    sub_in_player_name: str | None = None,
    sub_in_player_url: str | None = None,
) -> dict[str, Any]:
    """Create one normalized event row."""
    cleaned_minute = None
    if isinstance(minute, str) and minute.strip():
        cleaned_minute = minute.replace("'", "").strip()

    return {
        "match_id": match_row.get("match_id"),
        "match_url": match_row.get("match_url"),
        "date": match_row.get("date"),
        "time": match_row.get("time"),
        "league": match_row.get("league"),
        "season": match_row.get("season"),
        "match_day": match_row.get("match_day"),
        "home_team": match_row.get("home_team"),
        "away_team": match_row.get("away_team"),
        "event_index": event_index,
        "event_type": event_type,
        "event_minute": cleaned_minute,
        "team_side": team_side,
        "player_name": player_name,
        "player_url": player_url,
        "goal_type": goal_type,
        "sub_out_player_name": sub_out_player_name,
        "sub_out_player_url": sub_out_player_url,
        "sub_in_player_name": sub_in_player_name,
        "sub_in_player_url": sub_in_player_url,
    }


def _parse_goal_type(icon_title: str, minute: str | None) -> str:
    """Infer the goal subtype from icon metadata and minute text."""
    normalized_title = icon_title.strip().lower()
    minute_text = (minute or "").upper()

    if normalized_title == "own goals" or "own goal" in normalized_title or "OG" in minute_text:
        return "Own Goal"
    if "(P)" in minute_text or minute_text.endswith("P"):
        return "Penalty"
    return "Regular"


def _extract_timeline_events(soup: BeautifulSoup, match_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract timeline events from a match page."""
    timeline = soup.select_one("div.sp-template-event-timeline")
    if timeline is None:
        return []

    events: list[dict[str, Any]] = []
    event_index = 0

    for row in timeline.select("tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        minute = _normalize_whitespace(cells[1].get_text(strip=True))
        row_cells = [
            ("home", cells[0]),
            ("away", cells[2]),
        ]

        for team_side, cell in row_cells:
            if not _normalize_whitespace(cell.get_text(" ", strip=True)):
                continue

            icons = cell.find_all("i")
            for icon in icons:
                class_names = set(icon.get("class", []))
                icon_title = (icon.get("title") or "").strip()

                if "sp-icon-soccerball" in class_names:
                    player_name, player_url = _extract_player_from_icon(icon)
                    event_index += 1
                    events.append(
                        _build_event_row(
                            match_row=match_row,
                            event_index=event_index,
                            event_type="goal",
                            minute=minute,
                            team_side=team_side,
                            player_name=player_name,
                            player_url=player_url,
                            goal_type=_parse_goal_type(icon_title, minute),
                        )
                    )
                elif "sp-icon-shoe" in class_names:
                    player_name, player_url = _extract_player_from_icon(icon)
                    event_index += 1
                    events.append(
                        _build_event_row(
                            match_row=match_row,
                            event_index=event_index,
                            event_type="assist",
                            minute=minute,
                            team_side=team_side,
                            player_name=player_name,
                            player_url=player_url,
                        )
                    )
                elif "sp-icon-card" in class_names:
                    lower_title = icon_title.lower()
                    if "yellow" in lower_title:
                        event_type = "yellow_card"
                    elif "red" in lower_title:
                        event_type = "red_card"
                    else:
                        continue

                    player_name, player_url = _extract_player_from_icon(icon)
                    event_index += 1
                    events.append(
                        _build_event_row(
                            match_row=match_row,
                            event_index=event_index,
                            event_type=event_type,
                            minute=minute,
                            team_side=team_side,
                            player_name=player_name,
                            player_url=player_url,
                        )
                    )
                elif "dashicons" in class_names and "sub out" in icon_title.lower():
                    sub_out_player_name, sub_out_player_url, sub_in_player_name, sub_in_player_url = _extract_substitution_players(cell)
                    event_index += 1
                    events.append(
                        _build_event_row(
                            match_row=match_row,
                            event_index=event_index,
                            event_type="substitution",
                            minute=minute,
                            team_side=team_side,
                            player_name=None,
                            sub_out_player_name=sub_out_player_name,
                            sub_out_player_url=sub_out_player_url,
                            sub_in_player_name=sub_in_player_name,
                            sub_in_player_url=sub_in_player_url,
                        )
                    )

    return events


def _extract_match_post_id(soup: BeautifulSoup) -> str | None:
    """Extract the WordPress post ID from the article or body classes."""
    article = soup.select_one("article[id^='post-']")
    if article and article.get("id"):
        return article["id"].replace("post-", "")

    body = soup.select_one("body")
    if body:
        for class_name in body.get("class", []):
            match = re.match(r"postid-(\d+)", class_name)
            if match:
                return match.group(1)

    return None


def _extract_team_links(soup: BeautifulSoup) -> list[tuple[str | None, str | None]]:
    """Extract the home and away team links from results or logos."""
    team_links = []

    for row in soup.select("table.sp-event-results tbody tr"):
        team_name, team_url = _first_anchor_info(row.select_one("td.data-name"))
        if team_name:
            team_links.append((team_name, team_url))

    if team_links:
        return team_links[:2]

    for logo in soup.select("div.sp-event-logos span.sp-team-logo"):
        team_name = _safe_text(logo.select_one("strong.sp-team-name"))
        team_url = None
        anchor = logo.select_one("a")
        if anchor is not None:
            team_url = anchor.get("href")
            if team_name is None:
                team_name = _safe_text(anchor.select_one("strong.sp-team-name")) or _safe_text(anchor)

        if team_name:
            team_links.append((team_name, team_url))

    return team_links[:2]


def _extract_match_row(soup: BeautifulSoup, match_url: str) -> dict[str, Any]:
    """Extract match-level metadata from a match page."""
    match_row: dict[str, Any] = {column: None for column in MATCH_COLUMNS}
    match_row["match_id"] = _extract_match_post_id(soup)
    match_row["match_url"] = match_url
    match_row["source_page_title"] = _safe_text(soup.select_one("h1.entry-title"))

    if match_row["source_page_title"] and " vs " in match_row["source_page_title"]:
        teams = match_row["source_page_title"].split(" vs ", maxsplit=1)
        match_row["home_team"] = _normalize_whitespace(teams[0])
        match_row["away_team"] = _normalize_whitespace(teams[1])

    team_links = _extract_team_links(soup)
    if team_links:
        home_team_name, home_team_url = team_links[0]
        away_team_name, away_team_url = team_links[1] if len(team_links) > 1 else (None, None)

        match_row["home_team"] = match_row["home_team"] or home_team_name
        match_row["away_team"] = match_row["away_team"] or away_team_name
        match_row["home_team_url"] = home_team_url
        match_row["away_team_url"] = away_team_url

    event_details_table = soup.select_one("table.sp-event-details")
    if event_details_table is not None:
        headers = [_normalize_key(th.get_text(strip=True)) for th in event_details_table.select("thead th")]
        data = [_normalize_whitespace(td.get_text(strip=True)) for td in event_details_table.select("tbody td")]
        for key, value in zip(headers, data):
            match_row[key] = value

    venue_table = soup.select_one("table.sp-event-venue")
    if venue_table is not None:
        match_row["ground_name"] = _safe_text(venue_table.select_one("thead th"))
        match_row["ground_address"] = _safe_text(venue_table.select_one("tr.sp-event-venue-address-row td"))

    excerpt = _safe_text(soup.select_one("p.sp-excerpt"))
    if excerpt:
        man_of_the_match_match = re.search(r"Man of The Match:\s*(.*?)\s*\((.*?)\)", excerpt)
        if man_of_the_match_match:
            match_row["man_of_the_match"] = man_of_the_match_match.group(1).strip()
            match_row["man_of_the_match_team"] = man_of_the_match_match.group(2).strip()
        else:
            match_row["man_of_the_match"] = excerpt

    for index, row in enumerate(soup.select("table.sp-event-results tbody tr")[:2]):
        side = "home" if index == 0 else "away"
        match_row[f"{side}_score"] = _safe_text(row.select_one("td.data-goals"))
        match_row[f"{side}_first_half_goals"] = _safe_text(row.select_one("td.data-firsthalf"))
        match_row[f"{side}_second_half_goals"] = _safe_text(row.select_one("td.data-secondhalf"))

    return match_row


def _infer_team_side(team_name: str | None, match_row: dict[str, Any], section_index: int) -> str | None:
    """Infer whether a team section belongs to the home or away team."""
    if team_name and match_row.get("home_team") and team_name == match_row["home_team"]:
        return "home"
    if team_name and match_row.get("away_team") and team_name == match_row["away_team"]:
        return "away"
    return "home" if section_index == 0 else "away"


def _extract_lineups_and_staff(soup: BeautifulSoup, match_row: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Extract team lineups and staff from the performance sections."""
    lineups: list[dict[str, Any]] = []
    staff_rows: list[dict[str, Any]] = []

    team_sections = soup.select("div.sp-event-performance-tables > div.sp-template-event-performance")

    for section_index, section in enumerate(team_sections):
        team_name = _safe_text(section.select_one("h4.sp-table-caption"))
        team_side = _infer_team_side(team_name, match_row, section_index)

        for row in section.select("table.sp-event-performance tbody tr"):
            row_classes = set(row.get("class", []))
            if "lineup" in row_classes:
                squad_role = "starting_xi"
            elif "sub" in row_classes:
                squad_role = "bench"
            else:
                squad_role = "unknown"

            player_cell = row.select_one("td.data-name")
            player_name, player_url = _first_anchor_info(player_cell)

            swap_badge = player_cell.select_one("span.sub-in, span.sub-out") if player_cell else None
            swap_badge_type = None
            linked_player_name = None
            linked_shirt_number = None

            if swap_badge is not None:
                swap_badge_type = "sub_in" if "sub-in" in swap_badge.get("class", []) else "sub_out"
                linked_player_name = _normalize_whitespace(swap_badge.get("title"))
                linked_shirt_number = _normalize_whitespace(swap_badge.get_text(strip=True))

            lineups.append(
                {
                    "match_id": match_row.get("match_id"),
                    "match_url": match_row.get("match_url"),
                    "season": match_row.get("season"),
                    "match_day": match_row.get("match_day"),
                    "home_team": match_row.get("home_team"),
                    "away_team": match_row.get("away_team"),
                    "team_name": team_name,
                    "team_side": team_side,
                    "squad_role": squad_role,
                    "shirt_number": _safe_text(row.select_one("td.data-number")),
                    "player_name": player_name,
                    "player_url": player_url,
                    "player_position": _safe_text(player_cell.select_one("small.sp-player-position")) if player_cell else None,
                    "is_player_of_match": bool(player_cell and player_cell.select_one("span.sp-event-stars")),
                    "swap_badge_type": swap_badge_type,
                    "linked_player_name": linked_player_name,
                    "linked_shirt_number": linked_shirt_number,
                }
            )

        staff_container = section.select_one("div.sp-template-event-staff p.sp-event-staff")
        if staff_container is None:
            continue

        for segment in _split_node_segments(staff_container):
            segment_text = _segment_text(segment)
            if not segment_text or ":" not in segment_text:
                continue

            role, _ = segment_text.split(":", maxsplit=1)
            person_name, person_url = _extract_player_from_segment(segment)
            staff_rows.append(
                {
                    "match_id": match_row.get("match_id"),
                    "match_url": match_row.get("match_url"),
                    "season": match_row.get("season"),
                    "match_day": match_row.get("match_day"),
                    "home_team": match_row.get("home_team"),
                    "away_team": match_row.get("away_team"),
                    "team_name": team_name,
                    "team_side": team_side,
                    "role": _normalize_whitespace(role),
                    "person_name": person_name,
                    "person_url": person_url,
                }
            )

    return lineups, staff_rows


def _extract_officials(soup: BeautifulSoup, match_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract match officials from the officials table."""
    officials_table = soup.select_one("table.sp-event-officials")
    if officials_table is None:
        return []

    headers = [_safe_text(th) for th in officials_table.select("thead th")]
    cells = officials_table.select("tbody tr td")
    officials: list[dict[str, Any]] = []

    for role, cell in zip(headers, cells):
        for official_name in [_normalize_whitespace(text) for text in cell.stripped_strings]:
            if official_name:
                officials.append(
                    {
                        "match_id": match_row.get("match_id"),
                        "match_url": match_row.get("match_url"),
                        "season": match_row.get("season"),
                        "match_day": match_row.get("match_day"),
                        "home_team": match_row.get("home_team"),
                        "away_team": match_row.get("away_team"),
                        "role": role,
                        "official_name": official_name,
                    }
                )

    return officials


def _extract_stats(soup: BeautifulSoup, match_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract the summary stat tables shown below the lineups."""
    stats_container = soup.select_one("div.sp-template-event-statistics")
    if stats_container is None:
        return []

    stats_rows: list[dict[str, Any]] = []

    for label in stats_container.select("strong.sp-statistic-label"):
        table = label.find_next_sibling("table")
        if table is None:
            continue

        values = table.select("td.sp-statistic-value")
        home_value = _safe_text(values[0]) if len(values) > 0 else None
        away_value = _safe_text(values[1]) if len(values) > 1 else None

        stats_rows.append(
            {
                "match_id": match_row.get("match_id"),
                "match_url": match_row.get("match_url"),
                "season": match_row.get("season"),
                "match_day": match_row.get("match_day"),
                "home_team": match_row.get("home_team"),
                "away_team": match_row.get("away_team"),
                "statistic_name": _safe_text(label),
                "home_value": home_value,
                "away_value": away_value,
            }
        )

    return stats_rows


def parse_match_page(match_html: bytes, match_url: str) -> dict[str, Any]:
    """
    Extract structured tables from one match page.

    Output shape:
    - one match row
    - zero or more related rows for each secondary table
    """
    soup = BeautifulSoup(match_html, "html.parser")

    match_row = _extract_match_row(soup, match_url)
    events = _extract_timeline_events(soup, match_row)
    lineups, staff_rows = _extract_lineups_and_staff(soup, match_row)
    officials = _extract_officials(soup, match_row)
    stats_rows = _extract_stats(soup, match_row)

    match_row["has_timeline"] = bool(events)
    match_row["has_lineups"] = bool(lineups)
    match_row["has_officials"] = bool(officials)
    match_row["has_stats"] = bool(stats_rows)

    return {
        "match": match_row,
        "events": events,
        "lineups": lineups,
        "staff": staff_rows,
        "officials": officials,
        "stats": stats_rows,
    }


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


def _fetch_and_parse_match(client: ScraperClient, url: str) -> tuple[str, dict[str, Any]]:
    """
    Download one match page and return all normalized table rows for that match.

    A small random sleep is added before the request starts.
    This jitter makes concurrent workers less likely to synchronize into bursts.
    """
    time.sleep(random.uniform(0.0, 0.25))
    match_html = client.get(url)
    return url, parse_match_page(match_html, url)


def _build_output_dataframe(rows: list[dict[str, Any]], columns: list[str]) -> pd.DataFrame:
    """Create a dataframe with a stable column order for one output table."""
    if not rows:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(rows)
    for column in columns:
        if column not in df.columns:
            df[column] = None

    return df[columns]


def _build_legacy_goal_dataframe(events_df: pd.DataFrame) -> pd.DataFrame:
    """Create the legacy goal-only export used by the existing cleaning step."""
    if events_df.empty:
        return pd.DataFrame(columns=LEGACY_GOAL_COLUMNS)

    goal_events = events_df.loc[events_df["event_type"] == "goal"].copy()
    if goal_events.empty:
        return pd.DataFrame(columns=LEGACY_GOAL_COLUMNS)

    goal_events = goal_events.rename(
        columns={
            "date": "Date",
            "time": "Time",
            "league": "League",
            "season": "Season",
            "match_day": "Match Day",
            "event_minute": "goal_minute",
        }
    )

    for column in LEGACY_GOAL_COLUMNS:
        if column not in goal_events.columns:
            goal_events[column] = None

    return goal_events[LEGACY_GOAL_COLUMNS]


def scrape_season(
    season: str,
    *,
    refresh_source: bool = False,
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

    match_urls = fetch_match_urls(client, season)
    if refresh_source:
        completed_urls, all_tables, failed_urls = set(), _empty_scraped_tables(), {}
    else:
        completed_urls, all_tables, failed_urls = _load_checkpoint(season)
    starting_completed_count = len(completed_urls)
    pending_urls = [url for url in match_urls if url not in completed_urls]
    retry_first_urls = [url for url in pending_urls if url in failed_urls]
    new_pending_urls = [url for url in pending_urls if url not in failed_urls]
    pending_urls = retry_first_urls + new_pending_urls

    print(f"\nScraping {len(match_urls)} matches...")
    if completed_urls:
        print(f"[ok] Skipping {len(completed_urls)} matches already saved in checkpoint")
    print(f"[ok] {len(pending_urls)} matches left to fetch")
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
                    _append_match_payload(all_tables, match_payload)
                    completed_urls.add(completed_url)
                    failed_urls.pop(completed_url, None)
                except Exception as exc:
                    print(f"  [error] Error processing {url}: {exc}")
                    current_attempt_count = failed_urls.get(url, {}).get("attempt_count", 0)
                    failed_urls[url] = {
                        "attempt_count": current_attempt_count + 1,
                        "last_error": str(exc),
                        "last_attempt_at_utc": pd.Timestamp.now("UTC").isoformat(),
                    }
                    continue

                processed_count = len(completed_urls)
                if processed_count % 10 == 0:
                    print(f"  [ok] Processed {processed_count}/{len(match_urls)} matches")

                if index % CHECKPOINT_EVERY == 0:
                    _save_checkpoint(season, completed_urls, all_tables, failed_urls)
                    print(f"  [ok] Checkpoint saved after {processed_count} completed matches")

    _save_checkpoint(season, completed_urls, all_tables, failed_urls)
    season_tables = {
        table_name: _build_output_dataframe(all_tables[table_name], TABLE_COLUMNS[table_name])
        for table_name in TABLE_NAMES
    }
    scrape_summary = {
        "match_urls_found": len(match_urls),
        "starting_completed_matches": starting_completed_count,
        "completed_matches": len(completed_urls),
        "successful_fetches": len(completed_urls) - starting_completed_count,
        "failed_matches": len(failed_urls),
    }
    return season_tables, scrape_summary


def _save_structured_outputs(season: str, season_tables: dict[str, pd.DataFrame]) -> None:
    """Save all structured raw tables into data/raw/<season>/."""
    season_dir = raw_season_dir(season)
    season_dir.mkdir(parents=True, exist_ok=True)

    for table_name in TABLE_NAMES:
        output_path = raw_season_file(season, table_name)
        save_dataframe(season_tables[table_name], output_path)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Scrape structured UPL event data")
    parser.add_argument("--season", type=str, default="2025-26", help="Season to scrape (e.g., 2025-26)")
    parser.add_argument(
        "--refresh-source",
        action="store_true",
        help="Bypass cached HTML and checkpoint state so the season is scraped from the live source.",
    )
    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print(f"UPL Structured Data Scraper - Season {args.season}")
    print(f"{'=' * 60}\n")

    try:
        season_tables, scrape_summary = scrape_season(
            args.season,
            refresh_source=args.refresh_source,
        )

        season_outputs_exist = all(raw_season_file(args.season, table_name).exists() for table_name in TABLE_NAMES)
        legacy_goals_path = DATA_RAW / f"upl_goals_{season_key(args.season)}.csv"
        should_write_structured_outputs = scrape_summary["successful_fetches"] > 0 or not season_outputs_exist
        should_write_legacy_goals = scrape_summary["successful_fetches"] > 0 or not legacy_goals_path.exists()

        if should_write_structured_outputs:
            _save_structured_outputs(args.season, season_tables)

        if should_write_legacy_goals:
            legacy_goals_df = _build_legacy_goal_dataframe(season_tables["events"])
            save_dataframe(legacy_goals_df, legacy_goals_path)
        if not should_write_structured_outputs and not should_write_legacy_goals:
            print("[ok] No newly completed matches; kept existing season outputs and updated failed-match manifest only")

        # Legacy single-table output kept here for reference while raw scraping
        # now writes season-scoped tables under data/raw/<season>/.
        # legacy_events_path = DATA_RAW / f"upl_events_{season_key(args.season)}.csv"
        # save_dataframe(season_tables["events"], legacy_events_path)

        print("\n[ok] Scraping complete!")
        print(f"  Season folder: {raw_season_dir(args.season)}")
        for table_name in TABLE_NAMES:
            print(f"  {table_name}: {len(season_tables[table_name])} rows")
        print(f"  Successful fetches this run: {scrape_summary['successful_fetches']}")
        print(f"  Remaining failed matches: {scrape_summary['failed_matches']}")
        print(f"  Legacy goals export: {legacy_goals_path}")
        return 0

    except Exception as exc:
        print(f"\n[error] Scraping failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
