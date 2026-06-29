"""Tests for source calendar preflight behavior."""

from __future__ import annotations

import json

import pytest
import requests

from src.config import UPL_CALENDAR_URL
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


def _valid_calendar_html(match_count: int) -> str:
    source_url = UPL_CALENDAR_URL.format(season="2025-26")
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
        fetch_match_urls(
            client, "2025-26", minimum_match_links=2, report_path=report_path
        )

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert error.value.report.failure_reason == "http_failure: 415 Client Error"
    assert payload["status"] == "failed"
    assert payload["observed_link_count"] == 0


def test_fetch_match_urls_rejects_plausible_links_without_calendar_structure() -> None:
    """A generic HTML page cannot pass by merely containing event-like links."""

    links = "".join(
        f'<a href="https://upl.co.ug/event/{index}/">Event</a>' for index in range(3)
    )
    client = FakeClient(f"<html><body>{links}</body></html>")

    with pytest.raises(SourceCalendarPreflightError) as error:
        fetch_match_urls(client, "2025-26", minimum_match_links=2)

    assert error.value.report.failure_reason == "unexpected_calendar_structure"
    assert error.value.match_count == 3


def test_fetch_match_urls_rejects_non_html_content() -> None:
    """A successful status with the wrong content type is still unsafe."""

    client = FakeClient(_valid_calendar_html(2), content_type="application/json")

    with pytest.raises(SourceCalendarPreflightError) as error:
        fetch_match_urls(client, "2025-26", minimum_match_links=2)

    assert (
        error.value.report.failure_reason == "unexpected_content_type: application/json"
    )


def test_fetch_match_urls_accepts_valid_upl_calendar_and_writes_contract(
    tmp_path,
) -> None:
    """Valid source structure and links should produce a loader contract."""

    report_path = tmp_path / "source.json"
    client = FakeClient(_valid_calendar_html(2))

    assert fetch_match_urls(
        client,
        "2025-26",
        minimum_match_links=2,
        report_path=report_path,
    ) == [
        "https://upl.co.ug/event/0/",
        "https://upl.co.ug/event/1/",
    ]
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["status"] == "passed"
    assert payload["source_structure_valid"] is True
    assert payload["expected_match_count"] == 2
