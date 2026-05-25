"""Tests for the simplified hosted data update wrapper."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from scripts.data_platform import update_hosted_data
from src.config import CURRENT_SEASON


def _args(**overrides):
    """Return a small argparse-like object for wrapper helper tests."""

    values = {
        "season_scope": "current",
        "custom_seasons": "",
        "run_type": "routine-refresh",
        "apply_migrations": False,
        "use_cache": False,
        "force_full_scrape": False,
        "fail_on_remaining_failed_matches": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_resolve_current_scope_uses_current_season() -> None:
    """The default workflow path should target the configured current season."""

    assert update_hosted_data._resolve_target_seasons(_args()) == [CURRENT_SEASON]


def test_resolve_custom_scope_parses_comma_separated_seasons() -> None:
    """GitHub's single text input can still drive multi-season custom runs."""

    args = _args(season_scope="custom", custom_seasons="2024-25, 2025-26")

    assert update_hosted_data._resolve_target_seasons(args) == ["2024-25", "2025-26"]


def test_custom_scope_requires_custom_seasons() -> None:
    """A custom run should fail clearly instead of silently doing nothing."""

    with pytest.raises(ValueError):
        update_hosted_data._resolve_target_seasons(_args(season_scope="custom"))


def test_rebuild_from_existing_raw_translates_to_safe_skip_flags() -> None:
    """Hosted rebuilds should reuse raw DB rows and skip admin migrations by default."""

    command = update_hosted_data._build_update_current_season_command(
        _args(run_type="rebuild-from-existing-raw"),
        "2025-26",
    )

    assert "--mode" in command
    assert "full" in command
    assert "--skip-scrape" in command
    assert "--skip-raw-load" in command
    assert "--skip-migrations" in command


def test_force_full_scrape_disables_postgres_change_detection() -> None:
    """The operator-facing boolean should map to the lower-level scraper flag."""

    command = update_hosted_data._build_update_current_season_command(
        _args(force_full_scrape=True),
        "2025-26",
    )

    assert "--disable-postgres-change-detection" in command
