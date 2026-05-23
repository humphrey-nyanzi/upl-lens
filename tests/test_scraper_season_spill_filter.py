"""Unit tests for scraper season-boundary protections."""

from __future__ import annotations

import pandas as pd

from scripts.data_platform.scrape_upl_matches import _filter_tables_to_requested_season


def test_filter_tables_to_requested_season_removes_calendar_spill_rows() -> None:
    """Rows leaked by the source calendar should not be written to the target season folder."""

    season_tables = {
        "matches": pd.DataFrame(
            [
                {"match_id": 1, "season": "2024/25", "home_team": "A"},
                {"match_id": 2, "season": "2025/26", "home_team": "C"},
            ]
        ),
        "events": pd.DataFrame(
            [
                {"match_id": 1, "season": "2024/25", "event_index": 1},
                {"match_id": 2, "season": "2025/26", "event_index": 1},
                {"match_id": 2, "season": "2025/26", "event_index": 2},
            ]
        ),
        "lineups": pd.DataFrame(columns=["match_id", "season"]),
    }

    filtered_tables, spill_counts = _filter_tables_to_requested_season("2024-25", season_tables)

    assert filtered_tables["matches"]["match_id"].tolist() == [1]
    assert filtered_tables["events"]["match_id"].tolist() == [1]
    assert filtered_tables["lineups"].empty
    assert spill_counts == {
        "matches": 1,
        "events": 2,
        "lineups": 0,
    }
