"""Tests for the simplified hosted data update wrapper."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
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


def test_child_command_uses_wrapper_log_dir_and_summary_is_found(
    monkeypatch, tmp_path
) -> None:
    """Child run summaries should be written and found under the current run root."""

    log_dir = tmp_path / "current-run"
    command = update_hosted_data._build_update_current_season_command(
        _args(), "2025-26", log_dir=log_dir
    )

    assert "--log-dir" in command
    assert command[command.index("--log-dir") + 1] == str(log_dir)

    _patch_season_artifacts(
        monkeypatch,
        tmp_path,
        source={"status": "passed"},
        safety={"status": "passed", "database_write_stages_skipped": []},
        refresh_plan={
            "affected_match_ids": [1],
            "affected_match_urls": ["https://upl.co.ug/event/1/"],
            "attempted_match_urls": ["https://upl.co.ug/event/1/"],
            "failed_match_urls": [],
        },
    )
    child_dir = log_dir / "2025_26"
    _write_json(
        child_dir / "20260717_run_summary.json",
        {
            "status": "success",
            "season": "2025-26",
            "raw_loader_rows": {"matches": 7},
            "staging_rows": {"matches": 208},
            "step_logs": {},
        },
    )

    payload = update_hosted_data._hosted_observability_payload(
        args=_args(),
        seasons=["2025-26"],
        log_dir=log_dir,
        step_logs={"routine-refresh_2025_26": str(child_dir / "wrapper-step.log")},
        status="success",
        failure=None,
    )

    assert payload["child_run_summaries"]["2025-26"]["season"] == "2025-26"
    season_summary = payload["season_summaries"][0]
    assert season_summary["row_mutations"]["raw"]["processed_rows_total"] == 7


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


def _write_json(path, payload):
    """Write a compact JSON fixture for hosted summary tests."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _patch_season_artifacts(monkeypatch, tmp_path, *, source, safety, refresh_plan):
    """Point hosted summary helpers at temporary raw evidence artifacts."""

    source_path = _write_json(tmp_path / "source.json", source)
    safety_path = _write_json(tmp_path / "safety.json", safety)
    plan_path = _write_json(tmp_path / "refresh_plan.json", refresh_plan)
    monkeypatch.setattr(
        update_hosted_data,
        "raw_season_source_preflight_file",
        lambda season: source_path,
    )
    monkeypatch.setattr(
        update_hosted_data,
        "raw_season_load_safety_file",
        lambda season: safety_path,
    )
    monkeypatch.setattr(
        update_hosted_data,
        "raw_season_refresh_plan_file",
        lambda season: plan_path,
    )
    return source_path, safety_path, plan_path


def test_hosted_summary_writes_json_and_markdown_for_routine_updates(
    monkeypatch, tmp_path
) -> None:
    """Hosted runs should upload one machine and one readable summary artifact."""

    _patch_season_artifacts(
        monkeypatch,
        tmp_path,
        source={
            "status": "passed",
            "source_url": "https://upl.co.ug/calendar/2025-26-fixtures-results/",
            "http_status": 200,
            "observed_link_count": 240,
            "minimum_link_count": 1,
            "expected_match_count": 240,
            "failure_reason": None,
            "source_structure_valid": True,
            "baseline_version": "test-baseline",
        },
        safety={
            "status": "passed",
            "existing_match_rows": 238,
            "incoming_match_rows": 240,
            "incoming_distinct_match_urls": 240,
            "duplicate_match_rows": 0,
            "missing_existing_match_url_count": 0,
            "override_enabled": False,
            "database_write_stages_skipped": [],
        },
        refresh_plan={
            "mode": "routine-incremental",
            "affected_match_ids": [239, 240],
            "affected_match_urls": [
                "https://upl.co.ug/event/239/",
                "https://upl.co.ug/event/240/",
            ],
            "attempted_match_urls": [
                "https://upl.co.ug/event/236/",
                "https://upl.co.ug/event/237/",
                "https://upl.co.ug/event/238/",
                "https://upl.co.ug/event/239/",
                "https://upl.co.ug/event/240/",
            ],
            "failed_match_urls": [],
        },
    )
    log_dir = tmp_path / "logs"
    staging_log = log_dir / "staging.log"
    staging_log.parent.mkdir(parents=True)
    staging_log.write_text(
        "Run ID: staging-test\nTarget seasons: 2025_26\n"
        "[ok] Staging verification finished without error-level validation issues.\n",
        encoding="utf-8",
    )
    _write_json(
        log_dir / "2025_26" / "20260716_run_summary.json",
        {
            "status": "success",
            "season": "2025-26",
            "remaining_failed_matches": 0,
            "raw_loader_rows": {"matches": 2, "events": 11},
            "staging_rows": {"matches": 240, "events": 3431},
            "staging_rebuild": "completed",
            "step_logs": {"build_staging_from_raw": str(staging_log)},
        },
    )

    summary_path = update_hosted_data._write_summary(
        args=_args(),
        seasons=["2025-26"],
        log_dir=log_dir,
        step_logs={"routine-refresh_2025_26": str(log_dir / "2025_26" / "step.log")},
        status="success",
    )

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    markdown_path = tmp_path / "logs" / Path(payload["readable_summary_path"]).name
    assert payload["outcome"] == "routine updates applied"
    assert payload["io_verification"]["routine_skips_migrations"] is True
    season_summary = payload["season_summaries"][0]
    assert season_summary["source"]["observed_link_count"] == 240
    assert season_summary["hosted_safety"]["existing_match_count"] == 238
    assert season_summary["refresh_plan"]["affected_match_ids"] == [239, 240]
    assert season_summary["refresh_plan"]["skipped_unchanged_match_url_count"] == 3
    assert season_summary["row_mutations"]["raw"]["processed_rows_total"] == 13
    assert season_summary["row_mutations"]["staging"]["rebuilt_rows_total"] == 3671
    assert season_summary["staging_run"]["run_id"] == "staging-test"
    assert markdown_path.exists()
    assert "Outcome: routine updates applied" in markdown_path.read_text(
        encoding="utf-8"
    )


def test_hosted_summary_classifies_guard_blocked_write(monkeypatch, tmp_path) -> None:
    """A raw safety block should be visible at hosted-wrapper level."""

    _patch_season_artifacts(
        monkeypatch,
        tmp_path,
        source={
            "status": "passed",
            "source_url": "https://upl.co.ug/calendar/2025-26-fixtures-results/",
            "observed_link_count": 240,
            "minimum_link_count": 1,
            "expected_match_count": 240,
            "failure_reason": None,
        },
        safety={
            "status": "blocked",
            "failure_reason": "incoming match set would remove existing hosted matches",
            "existing_match_rows": 240,
            "incoming_match_rows": 220,
            "incoming_distinct_match_urls": 220,
            "missing_existing_match_url_count": 20,
            "missing_existing_match_url_sample": ["https://upl.co.ug/event/221/"],
            "override_enabled": False,
            "database_write_stages_skipped": ["raw", "staging", "analytics"],
        },
        refresh_plan={
            "mode": "routine-incremental",
            "affected_match_ids": [],
            "affected_match_urls": [],
            "attempted_match_urls": [],
            "failed_match_urls": [],
        },
    )
    log_dir = tmp_path / "logs"
    _write_json(
        log_dir / "2025_26" / "20260716_run_summary_failed.json",
        {
            "status": "failed",
            "failed_stage": "load_raw_to_postgres",
            "failure_reason": "unsafe raw load blocked",
            "failure_evidence": {
                "database_write_stages_skipped": ["raw", "staging", "analytics"]
            },
        },
    )

    payload = update_hosted_data._hosted_observability_payload(
        args=_args(),
        seasons=["2025-26"],
        log_dir=log_dir,
        step_logs={},
        status="failed",
        failure="Hosted update step failed",
    )

    assert payload["outcome"] == "guard blocked write"
    safety = payload["season_summaries"][0]["hosted_safety"]
    assert safety["existing_match_count"] == 240
    assert safety["incoming_distinct_match_count"] == 220
    assert safety["missing_existing_match_url_count"] == 20
    assert safety["database_write_stages_skipped"] == [
        "raw",
        "staging",
        "analytics",
    ]


def test_hosted_summary_distinguishes_source_failure_no_changes_and_admin_rebuild(
    monkeypatch, tmp_path
) -> None:
    """The hosted outcome vocabulary should cover the issue's triage buckets."""

    _patch_season_artifacts(
        monkeypatch,
        tmp_path,
        source={"status": "failed", "failure_reason": "unexpected_calendar_structure"},
        safety={},
        refresh_plan={
            "affected_match_ids": [],
            "affected_match_urls": [],
            "attempted_match_urls": [],
            "failed_match_urls": [],
        },
    )
    source_failure = update_hosted_data._hosted_observability_payload(
        args=_args(),
        seasons=["2025-26"],
        log_dir=tmp_path / "source-failure",
        step_logs={},
        status="failed",
        failure="source failed",
    )
    assert source_failure["outcome"] == "source-health failure"

    _patch_season_artifacts(
        monkeypatch,
        tmp_path,
        source={
            "status": "passed",
            "observed_link_count": 240,
            "expected_match_count": 240,
        },
        safety={"status": "passed", "database_write_stages_skipped": []},
        refresh_plan={
            "affected_match_ids": [],
            "affected_match_urls": [],
            "attempted_match_urls": ["https://upl.co.ug/event/240/"],
            "failed_match_urls": [],
        },
    )
    no_changes = update_hosted_data._hosted_observability_payload(
        args=_args(),
        seasons=["2025-26"],
        log_dir=tmp_path / "no-changes",
        step_logs={},
        status="success",
        failure=None,
    )
    assert no_changes["outcome"] == "no changes"

    admin_rebuild = update_hosted_data._hosted_observability_payload(
        args=_args(run_type="rebuild-from-existing-raw"),
        seasons=["2025-26"],
        log_dir=tmp_path / "admin-rebuild",
        step_logs={},
        status="success",
        failure=None,
    )
    assert admin_rebuild["outcome"] == "admin rebuild"


def test_hosted_summary_uses_matching_child_summary_per_season(
    monkeypatch, tmp_path
) -> None:
    """Custom multi-season runs should not reuse the newest child summary for all seasons."""

    _patch_season_artifacts(
        monkeypatch,
        tmp_path,
        source={
            "status": "passed",
            "observed_link_count": 10,
            "expected_match_count": 240,
        },
        safety={"status": "passed", "database_write_stages_skipped": []},
        refresh_plan={
            "affected_match_ids": [10],
            "affected_match_urls": ["https://upl.co.ug/event/10/"],
            "attempted_match_urls": ["https://upl.co.ug/event/10/"],
            "failed_match_urls": [],
        },
    )
    log_dir = tmp_path / "logs"
    _write_json(
        log_dir / "2024_25" / "20260716_run_summary.json",
        {
            "status": "success",
            "season": "2024-25",
            "raw_loader_rows": {"matches": 4},
            "staging_rows": {"matches": 200},
            "step_logs": {},
        },
    )
    _write_json(
        log_dir / "2025_26" / "20260716_run_summary.json",
        {
            "status": "success",
            "season": "2025-26",
            "raw_loader_rows": {"matches": 6},
            "staging_rows": {"matches": 240},
            "step_logs": {},
        },
    )

    payload = update_hosted_data._hosted_observability_payload(
        args=_args(season_scope="custom", custom_seasons="2024-25,2025-26"),
        seasons=["2024-25", "2025-26"],
        log_dir=log_dir,
        step_logs={
            "routine-refresh_2024_25": str(log_dir / "2024_25" / "step.log"),
            "routine-refresh_2025_26": str(log_dir / "2025_26" / "step.log"),
        },
        status="success",
        failure=None,
    )

    by_season = {item["season"]: item for item in payload["season_summaries"]}
    assert by_season["2024-25"]["row_mutations"]["raw"]["processed_rows_total"] == 4
    assert by_season["2025-26"]["row_mutations"]["raw"]["processed_rows_total"] == 6


def test_hosted_summary_does_not_classify_load_raw_failure_as_guard_without_blocked_safety(
    monkeypatch, tmp_path
) -> None:
    """A load failure is only a guard block when safety explicitly says blocked."""

    _patch_season_artifacts(
        monkeypatch,
        tmp_path,
        source={"status": "passed"},
        safety={"status": "passed", "database_write_stages_skipped": []},
        refresh_plan={
            "affected_match_ids": [],
            "affected_match_urls": [],
            "attempted_match_urls": [],
            "failed_match_urls": [],
        },
    )
    log_dir = tmp_path / "logs"
    failed_summary = _write_json(
        log_dir / "2025_26" / "20260716_run_summary_failed.json",
        {
            "status": "failed",
            "failed_stage": "load_raw_to_postgres",
            "failure_reason": "connection dropped",
            "failure_evidence": {"failure_reason": "connection dropped"},
        },
    )

    payload = update_hosted_data._hosted_observability_payload(
        args=_args(),
        seasons=["2025-26"],
        log_dir=log_dir,
        step_logs={"routine-refresh_2025_26": str(failed_summary.with_suffix(".log"))},
        status="failed",
        failure="Hosted update step failed",
    )

    assert payload["outcome"] == "failed"
    assert payload["child_failure_summary"]["failed_stage"] == "load_raw_to_postgres"


def test_hosted_summary_ignores_stale_blocked_safety_when_current_load_fails(
    monkeypatch, tmp_path
) -> None:
    """A stale blocked safety artifact must not classify a new loader failure."""

    _, safety_path, _ = _patch_season_artifacts(
        monkeypatch,
        tmp_path,
        source={"status": "passed"},
        safety={
            "status": "blocked",
            "failure_reason": "old guard block",
            "existing_match_rows": 240,
            "incoming_match_rows": 200,
            "database_write_stages_skipped": ["raw", "staging", "analytics"],
        },
        refresh_plan={
            "affected_match_ids": [],
            "affected_match_urls": [],
            "attempted_match_urls": [],
            "failed_match_urls": [],
        },
    )
    current_run_started_at = time.time()
    stale_time = current_run_started_at - 3600
    os.utime(safety_path, (stale_time, stale_time))
    log_dir = tmp_path / "logs"
    failed_summary = _write_json(
        log_dir / "2025_26" / "20260717_run_summary_failed.json",
        {
            "status": "failed",
            "failed_stage": "load_raw_to_postgres",
            "failure_reason": "permission denied",
            "failure_evidence": {"failure_reason": "permission denied"},
        },
    )

    payload = update_hosted_data._hosted_observability_payload(
        args=_args(),
        seasons=["2025-26"],
        log_dir=log_dir,
        step_logs={"routine-refresh_2025_26": str(failed_summary.with_suffix(".log"))},
        status="failed",
        failure="Hosted update step failed",
        current_run_started_at=current_run_started_at,
    )

    safety = payload["season_summaries"][0]["hosted_safety"]
    assert payload["outcome"] == "failed"
    assert safety["status"] is None
    assert safety["report_is_current"] is False
    assert safety["previous_report_status"] == "blocked"


def test_hosted_summary_ignores_stale_child_artifacts_without_current_step_root(
    monkeypatch, tmp_path
) -> None:
    """Early wrapper failures should not reuse summaries from older invocations."""

    _patch_season_artifacts(
        monkeypatch,
        tmp_path,
        source={"status": "passed"},
        safety={"status": "passed", "database_write_stages_skipped": []},
        refresh_plan={
            "affected_match_ids": [],
            "affected_match_urls": [],
            "attempted_match_urls": [],
            "failed_match_urls": [],
        },
    )
    log_dir = tmp_path / "logs"
    _write_json(
        log_dir / "old-run" / "2025_26" / "20260716_run_summary_failed.json",
        {
            "status": "failed",
            "failed_stage": "load_raw_to_postgres",
            "failure_reason": "old guard block",
            "failure_evidence": {"failure_reason": "old guard block"},
        },
    )

    payload = update_hosted_data._hosted_observability_payload(
        args=_args(),
        seasons=["2025-26"],
        log_dir=log_dir,
        step_logs={},
        status="failed",
        failure="wrapper failed before child summary",
    )

    assert payload["child_failure_summary"] is None
    assert payload["outcome"] == "failed"


def test_all_season_rebuild_uses_top_level_staging_log(monkeypatch, tmp_path) -> None:
    """All-season rebuild summaries should report top-level staging evidence."""

    _patch_season_artifacts(
        monkeypatch,
        tmp_path,
        source={"status": "passed"},
        safety={"status": "passed", "database_write_stages_skipped": []},
        refresh_plan={
            "affected_match_ids": [],
            "affected_match_urls": [],
            "attempted_match_urls": [],
            "failed_match_urls": [],
        },
    )
    log_dir = tmp_path / "logs"
    staging_log = log_dir / "20260716_build_staging_from_raw.log"
    staging_log.parent.mkdir(parents=True)
    staging_log.write_text(
        "Run ID: all-season-staging\n"
        "Target seasons: 2024_25, 2025_26\n"
        "  staging.matches: 440 rows\n"
        "  staging.events: 6123 rows\n"
        "[ok] Staging verification finished without error-level validation issues.\n",
        encoding="utf-8",
    )

    payload = update_hosted_data._hosted_observability_payload(
        args=_args(season_scope="all", run_type="rebuild-from-existing-raw"),
        seasons=["2024-25", "2025-26"],
        log_dir=log_dir,
        step_logs={"build_staging_from_raw": str(staging_log)},
        status="success",
        failure=None,
    )

    for season_summary in payload["season_summaries"]:
        assert season_summary["row_mutations"]["staging"]["rebuilt_rows_total"] == 0
        assert season_summary["row_mutations"]["staging"]["rebuilt_rows_by_table"] == {}
        assert season_summary["staging_run"]["run_id"] is None

    aggregate = payload["staging_aggregate"]
    assert aggregate["scope"] == "aggregate"
    assert aggregate["row_count_total"] == 6563
    assert aggregate["row_counts_by_table"] == {"matches": 440, "events": 6123}
    assert aggregate["staging_run"]["run_id"] == "all-season-staging"
    assert aggregate["staging_run"]["target_seasons"] == ["2024_25", "2025_26"]
