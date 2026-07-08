"""Tests for source calendar preflight behavior."""

from __future__ import annotations

import json

import pytest
import requests

from src.config import (
    TRUSTED_SEASON_CALENDAR_BASELINES,
    UPL_CALENDAR_URL,
    UPL_MAX_SEASON_MATCH_COUNT,
)
from src.scraping.upl.client import (
    SourceCalendarPreflightError,
    SourceDocument,
    fetch_match_urls,
)


class FakeClient:
    """Scraper-client stand-in with response metadata."""

    def __init__(
        self,
        html: str = "",
        *,
        status_code: int = 200,
        content_type: str = "text/html; charset=UTF-8",
        final_url: str | None = None,
        failure: Exception | None = None,
    ) -> None:
        self.html = html.encode("utf-8")
        self.status_code = status_code
        self.content_type = content_type
        self.final_url = final_url
        self.failure = failure

    def get_source_document(self, url: str) -> SourceDocument:
        if self.failure is not None:
            raise self.failure
        return SourceDocument(
            requested_url=url,
            final_url=self.final_url or url,
            status_code=self.status_code,
            content_type=self.content_type,
            content=self.html,
            from_cache=False,
        )


def _valid_calendar_html(match_count: int, season: str = "2025-26") -> str:
    source_url = UPL_CALENDAR_URL.format(season=season)
    links = "".join(
        f'<h4 class="sp-event-title"><a href="https://upl.co.ug/event/{index}/">Match</a></h4>'
        for index in range(match_count)
    )
    return (
        f'<html><head><link rel="canonical" href="{source_url}"></head>'
        f'<body><div class="sp-template-event-blocks">{links}</div></body></html>'
    )


def test_fetch_match_urls_reports_http_failure(tmp_path) -> None:
    """HTTP failures should become structured source-health evidence."""

    report_path = tmp_path / "source.json"
    client = FakeClient(failure=requests.HTTPError("415 Client Error"))

    with pytest.raises(SourceCalendarPreflightError) as error:
        fetch_match_urls(client, "2025-26", report_path=report_path)

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert error.value.report.failure_reason == "http_failure: 415 Client Error"
    assert payload["status"] == "failed"
    assert payload["observed_link_count"] == 0
    assert payload["expected_match_count"] == UPL_MAX_SEASON_MATCH_COUNT


def test_fetch_match_urls_rejects_plausible_links_without_calendar_structure() -> None:
    """A generic HTML page cannot pass by merely containing event-like links."""

    links = "".join(
        f'<a href="https://upl.co.ug/event/{index}/">Event</a>'
        for index in range(UPL_MAX_SEASON_MATCH_COUNT)
    )
    client = FakeClient(f"<html><body>{links}</body></html>")

    with pytest.raises(SourceCalendarPreflightError) as error:
        fetch_match_urls(client, "2025-26")

    assert error.value.report.failure_reason == "unexpected_calendar_structure"
    assert error.value.match_count == UPL_MAX_SEASON_MATCH_COUNT


def test_fetch_match_urls_rejects_non_html_content() -> None:
    """A successful status with the wrong content type is still unsafe."""

    client = FakeClient(
        _valid_calendar_html(UPL_MAX_SEASON_MATCH_COUNT),
        content_type="application/json",
    )

    with pytest.raises(SourceCalendarPreflightError) as error:
        fetch_match_urls(client, "2025-26")

    assert (
        error.value.report.failure_reason == "unexpected_content_type: application/json"
    )


def test_early_season_calendar_can_pass_without_rotating_baseline(tmp_path) -> None:
    """A valid early-season calendar may contain far fewer than 240 fixtures."""

    trusted_before = dict(TRUSTED_SEASON_CALENDAR_BASELINES["2025_26"])
    report_path = tmp_path / "source.json"

    urls = fetch_match_urls(
        FakeClient(_valid_calendar_html(8)),
        "2025-26",
        report_path=report_path,
    )

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert len(urls) == 8
    assert payload["status"] == "passed"
    assert payload["observed_link_count"] == 8
    assert payload["expected_match_count"] == UPL_MAX_SEASON_MATCH_COUNT
    assert payload["minimum_link_count"] == 1
    assert payload["baseline_version"] == "2026-07-08"
    assert TRUSTED_SEASON_CALENDAR_BASELINES["2025_26"] == trusted_before


def test_configured_baseline_above_league_maximum_fails_closed(monkeypatch) -> None:
    """A typo above the 240-match UPL ceiling must not authorize a scrape."""

    monkeypatch.setitem(
        TRUSTED_SEASON_CALENDAR_BASELINES,
        "2025_26",
        {
            "expected_match_count": UPL_MAX_SEASON_MATCH_COUNT + 1,
            "version": "test-over-max",
            "evidence": "intentional invalid test baseline",
        },
    )

    with pytest.raises(SourceCalendarPreflightError) as error:
        fetch_match_urls(
            FakeClient(_valid_calendar_html(UPL_MAX_SEASON_MATCH_COUNT)),
            "2025-26",
        )

    assert (
        error.value.report.failure_reason
        == "trusted_season_baseline_above_league_maximum"
    )


def test_missing_trusted_baseline_fails_closed() -> None:
    """Runtime source responses cannot create a baseline for a new season."""

    with pytest.raises(SourceCalendarPreflightError) as error:
        fetch_match_urls(
            FakeClient(
                _valid_calendar_html(UPL_MAX_SEASON_MATCH_COUNT, season="2026-27")
            ),
            "2026-27",
        )

    assert error.value.report.failure_reason == "trusted_season_baseline_missing"
    assert error.value.report.expected_match_count == 0


def test_source_calendar_above_league_maximum_fails_closed() -> None:
    """The official calendar should never authorize more than 240 UPL matches."""

    with pytest.raises(SourceCalendarPreflightError) as error:
        fetch_match_urls(
            FakeClient(_valid_calendar_html(UPL_MAX_SEASON_MATCH_COUNT + 1)),
            "2025-26",
        )

    assert error.value.report.failure_reason == "match_link_count_above_trusted_maximum"


def test_fetch_match_urls_accepts_trusted_240_link_snapshot(tmp_path) -> None:
    """The validated full 2025-26 snapshot size should pass the reviewed baseline."""

    report_path = tmp_path / "source.json"
    urls = fetch_match_urls(
        FakeClient(_valid_calendar_html(UPL_MAX_SEASON_MATCH_COUNT)),
        "2025-26",
        report_path=report_path,
    )

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert len(urls) == UPL_MAX_SEASON_MATCH_COUNT
    assert payload["status"] == "passed"
    assert payload["source_structure_valid"] is True
    assert payload["observed_link_count"] == UPL_MAX_SEASON_MATCH_COUNT
    assert payload["expected_match_count"] == UPL_MAX_SEASON_MATCH_COUNT
    assert payload["minimum_link_count"] == 1
