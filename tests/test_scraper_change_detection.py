"""Unit tests for scraper change-detection helpers."""

from __future__ import annotations

from src.scraping.upl.pipeline import _match_payload_changed

from scripts.data_platform.scrape_upl_matches import (
    _filter_existing_tables_to_calendar,
    _is_complete_match,
    _recent_completed_urls,
    _remove_match_rows,
)


def test_is_complete_match_requires_both_scores() -> None:
    """A match without both scores should stay eligible for refresh."""

    assert _is_complete_match({"home_score": 2, "away_score": 1}) is True
    assert _is_complete_match({"home_score": 2, "away_score": None}) is False
    assert _is_complete_match({"home_score": None, "away_score": 1}) is False


def test_recent_completed_urls_selects_latest_complete_matches() -> None:
    """Recent completed matches are practical candidates for source updates."""

    rows = [
        {
            "match_url": "old",
            "date": "2025-01-01",
            "match_day": 1,
            "match_id": 1,
            "home_score": 1,
            "away_score": 0,
        },
        {
            "match_url": "new",
            "date": "2025-02-01",
            "match_day": 2,
            "match_id": 2,
            "home_score": 2,
            "away_score": 2,
        },
        {
            "match_url": "future",
            "date": "2025-03-01",
            "match_day": 3,
            "match_id": 3,
            "home_score": None,
            "away_score": None,
        },
    ]

    assert _recent_completed_urls(rows, limit=1) == {"new"}


def test_remove_match_rows_replaces_stale_payload_rows() -> None:
    """Refreshing one match should not leave duplicate old rows in memory."""

    tables = {
        "matches": [{"match_url": "keep"}, {"match_url": "refresh"}],
        "events": [
            {"match_url": "refresh", "event_index": 1},
            {"match_url": "keep", "event_index": 1},
        ],
    }

    _remove_match_rows(tables, "refresh")

    assert tables == {
        "matches": [{"match_url": "keep"}],
        "events": [{"match_url": "keep", "event_index": 1}],
    }


def test_filter_existing_tables_to_calendar_drops_removed_source_matches() -> None:
    """Rows from DB should not survive if the current calendar no longer lists them."""

    tables = {
        "matches": [{"match_url": "listed"}, {"match_url": "removed"}],
        "events": [
            {"match_url": "listed", "event_index": 1},
            {"match_url": "removed", "event_index": 1},
        ],
    }

    assert _filter_existing_tables_to_calendar(tables, ["listed"]) == {
        "matches": [{"match_url": "listed"}],
        "events": [{"match_url": "listed", "event_index": 1}],
    }


def test_match_payload_comparison_treats_equivalent_values_as_unchanged() -> None:
    """Database date/time types should compare equal to scraper text values."""
    url = "https://upl.co.ug/event/7/"
    existing = {
        "matches": [
            {
                "match_id": 7,
                "match_url": url,
                "date": "2026-07-03",
                "time": "15:00:00",
                "home_score": 1,
            }
        ],
        "events": [],
        "lineups": [],
        "staff": [],
        "officials": [],
        "stats": [],
    }
    incoming = {
        **{table_name: [] for table_name in existing},
        "matches": [
            {
                "match_id": 7,
                "match_url": url,
                "date": "2026-07-03",
                "time": "15:00",
                "home_score": 1,
            }
        ],
    }

    assert _match_payload_changed(existing, incoming, url) is False


def test_match_payload_comparison_detects_changed_child_rows() -> None:
    """A changed event should put only that match into the loader plan."""
    url = "https://upl.co.ug/event/7/"
    existing = {
        "matches": [{"match_id": 7, "match_url": url}],
        "events": [{"match_id": 7, "match_url": url, "event_type": "yellow_card"}],
        "lineups": [],
        "staff": [],
        "officials": [],
        "stats": [],
    }
    incoming = {
        **{table_name: list(rows) for table_name, rows in existing.items()},
        "events": [{"match_id": 7, "match_url": url, "event_type": "red_card"}],
    }

    assert _match_payload_changed(existing, incoming, url) is True
