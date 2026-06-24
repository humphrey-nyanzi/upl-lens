"""Tests for source calendar preflight behavior."""

from __future__ import annotations

import pytest

from src.scraping.upl.client import SourceCalendarPreflightError, fetch_match_urls


class FakeClient:
    """Minimal scraper-client stand-in for calendar parsing tests."""

    def __init__(self, html: str) -> None:
        self.html = html.encode("utf-8")

    def get(self, url: str) -> bytes:
        return self.html


def test_fetch_match_urls_rejects_calendar_with_no_match_links() -> None:
    """Unexpected source content should fail before raw files can be trusted."""

    client = FakeClient("<html><title>not the UPL calendar</title></html>")

    with pytest.raises(SourceCalendarPreflightError) as error:
        fetch_match_urls(client, "2025-26", minimum_match_links=1)

    assert error.value.match_count == 0
    assert "expected at least 1" in str(error.value)


def test_fetch_match_urls_accepts_plausible_calendar() -> None:
    """A calendar with enough event links should return sorted unique match URLs."""

    client = FakeClient(
        """
        <a href="https://upl.co.ug/event/2/">Match 2</a>
        <a href="https://upl.co.ug/event/1/">Match 1</a>
        <a href="https://upl.co.ug/event/1/">Duplicate Match 1</a>
        """
    )

    assert fetch_match_urls(client, "2025-26", minimum_match_links=2) == [
        "https://upl.co.ug/event/1/",
        "https://upl.co.ug/event/2/",
    ]
