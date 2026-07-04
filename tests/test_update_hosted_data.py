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
    assert "--full-raw-rebuild" in command


def test_routine_command_cannot_enable_unsafe_reload() -> None:
    """The routine wrapper exposes no path to the destructive admin override."""

    command = update_hosted_data._build_update_current_season_command(
        _args(run_type="routine-refresh"),
        "2025-26",
    )

    assert "--allow-unsafe-season-reload" not in command


def test_weekly_workflow_does_not_expose_unsafe_reload() -> None:
    """Scheduled and dispatch workflow inputs must not include the admin flag."""

    workflow = (
        update_hosted_data.PROJECT_ROOT
        / ".github"
        / "workflows"
        / "current-season-update.yml"
    ).read_text(encoding="utf-8")

    assert "allow-unsafe-season-reload" not in workflow
    assert "--allow-unsafe-season-reload" not in workflow


def test_weekly_workflow_uses_node24_action_majors() -> None:
    """Hosted automation should use native Node 24 actions without a force flag."""

    workflow = (
        update_hosted_data.PROJECT_ROOT
        / ".github"
        / "workflows"
        / "current-season-update.yml"
    ).read_text(encoding="utf-8")

    assert "actions/checkout@v6" in workflow
    assert "actions/setup-python@v6" in workflow
    assert workflow.count("actions/upload-artifact@v6") == 2
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24" not in workflow


def test_hosted_wrapper_reads_child_failure_evidence(tmp_path) -> None:
    """Child guard evidence should survive the hosted subprocess boundary."""

    summary_path = tmp_path / "2025_26" / "test_failed_run_summary.json"
    summary_path.parent.mkdir(parents=True)
    summary_path.write_text(
        '{"failed_stage":"load_raw_to_postgres",'
        '"failure_reason":"blocked",'
        '"failure_evidence":{"incoming_match_count":20}}',
        encoding="utf-8",
    )

    payload = update_hosted_data._latest_child_failure_summary(tmp_path)

    assert payload is not None
    assert payload["failed_stage"] == "load_raw_to_postgres"
    assert payload["failure_evidence"] == {"incoming_match_count": 20}
