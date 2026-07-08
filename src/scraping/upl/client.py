"""HTTP client, cache, and rate limiting for polite source scraping."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import (
    MAX_CONCURRENT_REQUESTS,
    MIN_CALENDAR_MATCH_LINKS,
    REQUEST_TIMEOUT,
    RETRY_BACKOFF_SECONDS,
    SCRAPE_RETRY_ATTEMPTS,
    SCRAPER_STATUS_FORCELIST,
    TRUSTED_SEASON_CALENDAR_BASELINES,
    UPL_MAX_SEASON_MATCH_COUNT,
    UPL_CALENDAR_URL,
    UPL_EVENT_URL_PREFIX,
    season_key,
)


class SourceCalendarPreflightError(RuntimeError):
    """Raised when a season calendar response is not safe to scrape from."""

    def __init__(self, report: "SourceCalendarPreflightReport") -> None:
        self.report = report
        self.calendar_url = report.source_url
        self.match_count = report.observed_link_count
        self.minimum_count = report.minimum_link_count
        super().__init__(
            f"Source calendar preflight failed for {report.source_url}: "
            f"{report.failure_reason} (observed links={report.observed_link_count}, "
            f"expected/minimum links={report.minimum_link_count})."
        )


@dataclass(frozen=True)
class SourceDocument:
    """HTTP response metadata and body used by source preflight validation."""

    requested_url: str
    final_url: str
    status_code: int
    content_type: str
    content: bytes
    from_cache: bool


@dataclass(frozen=True)
class SourceCalendarPreflightReport:
    """Machine-readable evidence for one source calendar validation."""

    status: str
    target_season: str
    source_url: str
    final_source_url: str | None
    http_status: int | None
    content_type: str | None
    observed_link_count: int
    minimum_link_count: int
    expected_match_count: int
    failure_reason: str | None
    source_structure_valid: bool
    override_enabled: bool
    match_urls: list[str]
    baseline_version: str | None
    baseline_evidence: str | None
    checked_at_utc: str


def _normalized_source_url(url: str) -> str:
    """Normalize a source URL for strict host and path comparison."""

    parts = urlsplit(url)
    normalized_path = parts.path.rstrip("/") + "/"
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), normalized_path, "", "")
    )


def _write_preflight_report(
    report: SourceCalendarPreflightReport,
    report_path: Path | None,
) -> None:
    """Persist source evidence when the caller supplied an artifact path."""

    if report_path is None:
        return
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"[source-preflight] Report: {report_path}")


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
            self._next_allowed_time = (
                max(self._next_allowed_time, now) + self.min_interval_seconds
            )

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

        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=MAX_CONCURRENT_REQUESTS,
            pool_maxsize=MAX_CONCURRENT_REQUESTS,
        )
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
        """Fetch one URL and return its body."""

        return self.get_source_document(url).content

    def get_source_document(self, url: str) -> SourceDocument:
        """Fetch one URL while retaining response metadata for validation."""

        cache_path = self._cache_path_for_url(url)
        if self.use_cache and cache_path.exists():
            return SourceDocument(
                requested_url=url,
                final_url=url,
                status_code=200,
                content_type="text/html",
                content=cache_path.read_bytes(),
                from_cache=True,
            )

        self.rate_limiter.wait()
        response = self.session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        document = SourceDocument(
            requested_url=url,
            final_url=response.url,
            status_code=response.status_code,
            content_type=response.headers.get("Content-Type", ""),
            content=response.content,
            from_cache=False,
        )
        if self.use_cache:
            cache_path.write_bytes(document.content)
        return document


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


def fetch_match_urls(
    client: ScraperClient,
    season: str,
    *,
    minimum_match_links: int = MIN_CALENDAR_MATCH_LINKS,
    report_path: Path | None = None,
) -> list[str]:
    """Fetch and validate official match URLs against a trusted season baseline."""

    calendar_url = UPL_CALENDAR_URL.format(season=season)
    checked_at = datetime.now(timezone.utc).isoformat()
    baseline = TRUSTED_SEASON_CALENDAR_BASELINES.get(season_key(season))
    expected_match_count = int(baseline["expected_match_count"]) if baseline else 0
    minimum_authorized_count = minimum_match_links
    baseline_version = str(baseline["version"]) if baseline else None
    baseline_evidence = str(baseline["evidence"]) if baseline else None
    print(f"Fetching match calendar from: {calendar_url}")

    try:
        if hasattr(client, "get_source_document"):
            document = client.get_source_document(calendar_url)
        else:
            document = SourceDocument(
                requested_url=calendar_url,
                final_url=calendar_url,
                status_code=200,
                content_type="text/html",
                content=client.get(calendar_url),
                from_cache=False,
            )
        print("[ok] Calendar fetched successfully")
    except Exception as exc:
        report = SourceCalendarPreflightReport(
            status="failed",
            target_season=season,
            source_url=calendar_url,
            final_source_url=None,
            http_status=getattr(getattr(exc, "response", None), "status_code", None),
            content_type=None,
            observed_link_count=0,
            minimum_link_count=minimum_authorized_count,
            expected_match_count=expected_match_count,
            failure_reason=f"http_failure: {exc}",
            source_structure_valid=False,
            override_enabled=False,
            match_urls=[],
            baseline_version=baseline_version,
            baseline_evidence=baseline_evidence,
            checked_at_utc=checked_at,
        )
        _write_preflight_report(report, report_path)
        print(f"[error] Failed to fetch calendar: {exc}")
        raise SourceCalendarPreflightError(report) from exc

    failure_reason: str | None = None
    accepted_content_types = {"text/html", "application/xhtml+xml"}
    response_content_type = document.content_type.lower().split(";", 1)[0].strip()
    if document.status_code < 200 or document.status_code >= 300:
        failure_reason = f"http_status_not_success: {document.status_code}"
    elif response_content_type not in accepted_content_types:
        failure_reason = (
            f"unexpected_content_type: {document.content_type or '<missing>'}"
        )
    elif _normalized_source_url(document.final_url) != _normalized_source_url(
        calendar_url
    ):
        failure_reason = f"unexpected_source_url: {document.final_url}"

    soup = BeautifulSoup(document.content, "html.parser")
    canonical = soup.select_one('link[rel="canonical"][href]')
    canonical_url = canonical.get("href") if canonical is not None else None
    calendar_container = soup.select_one(
        "div.sp-template-event-blocks, table.sp-event-calendar, table.sp-calendar"
    )
    structure_valid = (
        canonical_url is not None
        and _normalized_source_url(str(canonical_url))
        == _normalized_source_url(calendar_url)
        and calendar_container is not None
    )
    if failure_reason is None and not structure_valid:
        failure_reason = "unexpected_calendar_structure"

    link_scope = calendar_container if calendar_container is not None else soup
    match_urls = [
        str(link.get("href"))
        for link in link_scope.select(f'a[href^="{UPL_EVENT_URL_PREFIX}"]')
        if link.get("href")
    ]
    unique_match_urls = sorted(set(match_urls))
    print(f"[ok] Found {len(unique_match_urls)} unique matches")
    if failure_reason is None and baseline is None:
        failure_reason = "trusted_season_baseline_missing"
    elif failure_reason is None and expected_match_count > UPL_MAX_SEASON_MATCH_COUNT:
        failure_reason = "trusted_season_baseline_above_league_maximum"
    elif failure_reason is None and len(unique_match_urls) < minimum_authorized_count:
        failure_reason = "match_link_count_below_minimum"
    elif failure_reason is None and len(unique_match_urls) > expected_match_count:
        failure_reason = "match_link_count_above_trusted_maximum"

    report = SourceCalendarPreflightReport(
        status="failed" if failure_reason else "passed",
        target_season=season,
        source_url=calendar_url,
        final_source_url=document.final_url,
        http_status=document.status_code,
        content_type=document.content_type,
        observed_link_count=len(unique_match_urls),
        minimum_link_count=minimum_authorized_count,
        expected_match_count=expected_match_count,
        failure_reason=failure_reason,
        source_structure_valid=structure_valid,
        override_enabled=False,
        match_urls=unique_match_urls,
        baseline_version=baseline_version,
        baseline_evidence=baseline_evidence,
        checked_at_utc=checked_at,
    )
    _write_preflight_report(report, report_path)
    if failure_reason:
        print(
            "[error] Source calendar preflight failed: "
            f"{failure_reason}; found {len(unique_match_urls)} match link(s), "
            f"trusted maximum={expected_match_count}, minimum={minimum_authorized_count}."
        )
        raise SourceCalendarPreflightError(report)
    return unique_match_urls
