"""HTTP client, cache, and rate limiting for polite source scraping."""

from __future__ import annotations

import hashlib
import threading
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import (
    MAX_CONCURRENT_REQUESTS,
    REQUEST_TIMEOUT,
    RETRY_BACKOFF_SECONDS,
    SCRAPE_RETRY_ATTEMPTS,
    SCRAPER_STATUS_FORCELIST,
    UPL_CALENDAR_URL,
    UPL_EVENT_URL_PREFIX,
)


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

