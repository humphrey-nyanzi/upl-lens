"""Operator-friendly hosted data update workflow.

This wrapper keeps GitHub Actions inputs simple while reusing the existing data
platform scripts underneath. Use it when you want one manual run to update the
hosted database for the current season, all seasons, or a small custom list.

Usage examples
--------------
python scripts/data_platform/update_hosted_data.py
python scripts/data_platform/update_hosted_data.py --season-scope all --run-type rebuild-from-existing-raw
python scripts/data_platform/update_hosted_data.py --season-scope custom --custom-seasons 2024-25,2025-26
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    CURRENT_SEASON,
    raw_season_load_safety_file,
    raw_season_refresh_plan_file,
    raw_season_source_preflight_file,
    season_key,
)
from src.operations.command_runner import display_path, run_logged_step, timestamp_slug
from scripts.data_platform.update_current_season import (
    _extract_raw_load_counts,
    _extract_staging_row_counts,
    _staging_verification_status,
)

SCRIPT_DIR = PROJECT_ROOT / "scripts" / "data_platform"
DEFAULT_LOG_DIR = PROJECT_ROOT / "outputs" / "automation"
ALL_KNOWN_SEASONS = (
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
)


class HostedUpdateStepError(Exception):
    """Raised when one hosted-update step fails after writing a log."""

    def __init__(self, step_name: str, log_path: Path, exit_code: int) -> None:
        self.step_name = step_name
        self.log_path = log_path
        self.exit_code = exit_code
        super().__init__(
            f"Hosted update step failed: {step_name}. "
            f"Exit code: {exit_code}. Review {log_path}."
        )


def parse_args() -> argparse.Namespace:
    """Parse the operator-level hosted update options."""

    parser = argparse.ArgumentParser(
        description="Run a simplified hosted/local UPL data update workflow."
    )
    parser.add_argument(
        "--season-scope",
        choices=("current", "all", "custom"),
        default="current",
        help="Use the current season, every known season, or a comma-separated custom list.",
    )
    parser.add_argument(
        "--custom-seasons",
        default="",
        help="Comma-separated seasons used only when --season-scope custom, e.g. 2024-25,2025-26.",
    )
    parser.add_argument(
        "--run-type",
        choices=("routine-refresh", "rebuild-from-existing-raw", "artifact-only"),
        default="routine-refresh",
        help=(
            "routine-refresh scrapes and refreshes Postgres; rebuild-from-existing-raw "
            "rebuilds staging/analytics from hosted raw rows; artifact-only scrapes raw files only."
        ),
    )
    parser.add_argument(
        "--apply-migrations",
        action="store_true",
        help="Apply database migrations before data refresh steps.",
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Allow scraper cached HTML/checkpoints instead of forcing a live-source refresh.",
    )
    parser.add_argument(
        "--force-full-scrape",
        action="store_true",
        help="Disable Postgres change detection and scrape every calendar match.",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=DEFAULT_LOG_DIR,
        help="Directory where step logs and run summaries should be written.",
    )
    parser.add_argument(
        "--fail-on-remaining-failed-matches",
        action="store_true",
        help="Fail if any season ends with failed match URLs.",
    )
    return parser.parse_args()


def _timestamp_slug() -> str:
    """Return a compact UTC timestamp for log filenames."""

    return timestamp_slug()


def _display_path(path: Path) -> str:
    """Return a readable path, preferring repo-relative paths."""

    return display_path(path, PROJECT_ROOT)


def _python_command(script_name: str, *extra_args: str) -> list[str]:
    """Build a data-platform script command using this Python executable."""

    return [sys.executable, str(SCRIPT_DIR / script_name), *extra_args]


def _run_step(step_name: str, command: list[str], log_dir: Path) -> Path:
    """Run one subprocess, stream output, and save a per-step log."""

    return run_logged_step(
        step_name=step_name,
        command=command,
        log_dir=log_dir,
        project_root=PROJECT_ROOT,
        log_prefix="[hosted-update]",
        error_type=HostedUpdateStepError,
    )


def _parse_custom_seasons(value: str) -> list[str]:
    """Return normalized custom seasons from a comma-separated input."""

    seasons = [season.strip() for season in value.split(",") if season.strip()]
    if not seasons:
        raise ValueError("--custom-seasons is required when --season-scope custom.")
    return seasons


def _resolve_target_seasons(args: argparse.Namespace) -> list[str]:
    """Return the concrete season list for operator-level actions."""

    if args.season_scope == "current":
        return [CURRENT_SEASON]
    if args.season_scope == "all":
        return list(ALL_KNOWN_SEASONS)
    return _parse_custom_seasons(args.custom_seasons)


def _scope_slug(args: argparse.Namespace, seasons: list[str]) -> str:
    """Return a compact slug for logs and artifact names."""

    if args.season_scope == "all":
        return "all-seasons"
    if args.season_scope == "current":
        return season_key(seasons[0])
    return "custom-" + "-".join(season_key(season) for season in seasons)


def _season_args(seasons: list[str]) -> list[str]:
    """Return repeated --season arguments for scripts that accept them."""

    args: list[str] = []
    for season in seasons:
        args.extend(["--season", season])
    return args


def _build_update_current_season_command(
    args: argparse.Namespace, season: str, *, log_dir: Path | None = None
) -> list[str]:
    """Translate operator options into the existing one-season pipeline command."""

    mode = "artifact-only" if args.run_type == "artifact-only" else "full"
    command = _python_command(
        "update_current_season.py", "--season", season, "--mode", mode
    )

    if args.run_type == "rebuild-from-existing-raw":
        command.extend(["--skip-scrape", "--skip-raw-load"])
    if not args.apply_migrations:
        command.append("--skip-migrations")
    if args.use_cache:
        command.append("--use-cache")
    if args.force_full_scrape:
        command.extend(["--disable-postgres-change-detection", "--full-raw-rebuild"])
    if log_dir is not None:
        command.extend(["--log-dir", str(log_dir)])
    if args.fail_on_remaining_failed_matches:
        command.append("--fail-on-remaining-failed-matches")
    return command


def _run_rebuild_all_from_existing_raw(
    *,
    args: argparse.Namespace,
    log_dir: Path,
    step_logs: dict[str, str],
) -> None:
    """Rebuild staging/analytics for every hosted raw season in one command."""

    if args.apply_migrations:
        step_logs["apply_db_migrations"] = _display_path(
            _run_step(
                "apply_db_migrations",
                _python_command("apply_db_migrations.py"),
                log_dir,
            )
        )
    else:
        print("\n[hosted-update] Skipping migrations.")

    step_logs["build_staging_from_raw"] = _display_path(
        _run_step(
            "build_staging_from_raw",
            _python_command("build_staging_from_raw.py"),
            log_dir,
        )
    )
    step_logs["verify_staging_outputs"] = _display_path(
        _run_step(
            "verify_staging_outputs",
            _python_command("verify_staging_outputs.py"),
            log_dir,
        )
    )


def _run_per_season_pipeline(
    *,
    args: argparse.Namespace,
    seasons: list[str],
    log_dir: Path,
    step_logs: dict[str, str],
) -> None:
    """Run the existing one-season pipeline once for each selected season."""

    for season in seasons:
        season_log_dir = log_dir / season_key(season)
        step_name = f"{args.run_type}_{season_key(season)}"
        command = _build_update_current_season_command(args, season, log_dir=log_dir)
        step_logs[step_name] = _display_path(
            _run_step(step_name, command, season_log_dir)
        )


def _read_json_artifact(path: Path) -> dict[str, Any] | None:
    """Read a JSON artifact and return only object payloads."""

    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _displayed_path_to_path(value: str | None) -> Path | None:
    """Resolve a repo-relative display path back to a local Path when possible."""

    if not value:
        return None
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def _latest_json_artifact(
    search_roots: list[Path], patterns: tuple[str, ...]
) -> tuple[Path, dict[str, Any]] | None:
    """Return the newest JSON payload matching any pattern under allowed roots."""

    matches: list[Path] = []
    for root in search_roots:
        if not root.exists():
            continue
        for pattern in patterns:
            matches.extend(root.rglob(pattern))
    for path in sorted(
        set(matches), key=lambda item: item.stat().st_mtime, reverse=True
    ):
        payload = _read_json_artifact(path)
        if payload is not None:
            return path, payload
    return None


def _current_step_roots(
    *, log_dir: Path, step_logs: dict[str, str], season: str | None = None
) -> list[Path]:
    """Return artifact search roots proven to belong to this wrapper run."""

    roots: list[Path] = []
    target_key = season_key(season) if season else None
    for displayed_path in step_logs.values():
        path = _displayed_path_to_path(displayed_path)
        if path is None:
            continue
        parent = path.parent
        if target_key and target_key not in parent.parts and parent != log_dir:
            continue
        if parent not in roots:
            roots.append(parent)
    return roots


def _latest_child_run_summary(
    log_dir: Path,
    *,
    failed: bool,
    season: str | None = None,
    search_roots: list[Path] | None = None,
) -> dict[str, Any] | None:
    """Return the newest child operations summary from current-run roots only."""

    patterns = (
        ("*_run_summary_failed.json", "*_failed_run_summary.json")
        if failed
        else ("*_run_summary.json",)
    )
    if search_roots is None:
        search_roots = [log_dir / season_key(season)] if season else [log_dir]
    result = _latest_json_artifact(search_roots, patterns)
    if result is None:
        return None
    path, payload = result
    if not failed and path.name.endswith("_hosted_update_summary.json"):
        return None
    payload = dict(payload)
    payload["path"] = _display_path(path)
    return payload


def _int_or_none(value: object) -> int | None:
    """Return an integer for count-like values without raising in summaries."""

    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _list_count(payload: dict[str, Any] | None, key: str) -> int | None:
    """Return the length of a list field when the artifact supplies one."""

    if not payload:
        return None
    value = payload.get(key)
    return len(value) if isinstance(value, list) else None


def _list_sample(
    payload: dict[str, Any] | None, key: str, *, limit: int = 20
) -> list[object]:
    """Return a bounded sample of a list field for artifact readability."""

    if not payload:
        return []
    value = payload.get(key)
    if not isinstance(value, list):
        return []
    return value[:limit]


def _sum_counts(counts: object) -> int:
    """Sum dictionary count values while ignoring missing or non-numeric entries."""

    if not isinstance(counts, dict):
        return 0
    return sum(int(value) for value in counts.values() if isinstance(value, int))


def _artifact_is_current(path: Path, current_run_started_at: float | None) -> bool:
    """Return whether a persistent artifact was written during this wrapper run."""

    if not path.exists():
        return False
    if current_run_started_at is None:
        return True
    try:
        return path.stat().st_mtime >= current_run_started_at - 1.0
    except OSError:
        return False


def _extract_staging_metadata(log_path: Path | None) -> dict[str, Any]:
    """Read lightweight staging run metadata from the staging build log."""

    metadata: dict[str, Any] = {
        "run_id": None,
        "target_seasons": [],
        "validation_issue_counts": {},
        "verification_status": _staging_verification_status(log_path),
    }
    if log_path is None or not log_path.exists():
        return metadata

    in_issue_counts = False
    with log_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped.startswith("Run ID:"):
                metadata["run_id"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Target seasons:"):
                seasons = stripped.split(":", 1)[1].strip()
                metadata["target_seasons"] = [
                    season.strip() for season in seasons.split(",") if season.strip()
                ]
            elif stripped == "Validation issues logged to staging.validation_issues:":
                in_issue_counts = True
            elif in_issue_counts and not stripped:
                in_issue_counts = False
            elif in_issue_counts and ":" in stripped:
                severity, count = stripped.split(":", 1)
                parsed_count = _int_or_none(count.strip())
                if parsed_count is not None:
                    metadata["validation_issue_counts"][severity.strip()] = parsed_count
    return metadata


def _staging_aggregate_payload(step_logs: dict[str, str]) -> dict[str, Any]:
    """Return top-level staging evidence for all-season aggregate rebuilds."""

    staging_log = _displayed_path_to_path(step_logs.get("build_staging_from_raw"))
    staging_rows = _extract_staging_row_counts(staging_log)
    staging_metadata = _extract_staging_metadata(staging_log)
    return {
        "log_path": _display_path(staging_log) if staging_log else None,
        "scope": "aggregate" if staging_log else None,
        "row_counts_by_table": staging_rows,
        "row_count_total": _sum_counts(staging_rows),
        "staging_run": staging_metadata,
    }


def _season_observability_payload(
    *,
    season: str,
    child_summary: dict[str, Any] | None,
    child_failure_summary: dict[str, Any] | None,
    current_run_started_at: float | None = None,
) -> dict[str, Any]:
    """Assemble one season's hosted-refresh evidence from existing artifacts."""

    source = _read_json_artifact(raw_season_source_preflight_file(season))
    safety_path = raw_season_load_safety_file(season)
    raw_safety = _read_json_artifact(safety_path)
    safety_is_current = _artifact_is_current(safety_path, current_run_started_at)
    safety = raw_safety if safety_is_current else None
    stale_safety = raw_safety if raw_safety and not safety_is_current else None
    refresh_plan = _read_json_artifact(raw_season_refresh_plan_file(season))
    failure_evidence = (
        child_failure_summary.get("failure_evidence") if child_failure_summary else None
    )
    if not isinstance(failure_evidence, dict):
        failure_evidence = {}

    child_step_logs = child_summary.get("step_logs") if child_summary else {}
    if not isinstance(child_step_logs, dict):
        child_step_logs = {}
    raw_load_log = _displayed_path_to_path(child_step_logs.get("load_raw_to_postgres"))
    staging_log = _displayed_path_to_path(child_step_logs.get("build_staging_from_raw"))
    raw_loader_rows = (
        child_summary.get("raw_loader_rows")
        if child_summary and isinstance(child_summary.get("raw_loader_rows"), dict)
        else _extract_raw_load_counts(raw_load_log)
    )
    staging_rows = (
        child_summary.get("staging_rows")
        if child_summary and isinstance(child_summary.get("staging_rows"), dict)
        else _extract_staging_row_counts(staging_log)
    )
    staging_metadata = _extract_staging_metadata(staging_log)
    source_url = (
        (source or {}).get("source_url")
        or failure_evidence.get("source_url")
        or (safety or {}).get("source_url")
    )

    affected_ids = _list_sample(refresh_plan, "affected_match_ids", limit=50)
    affected_urls = _list_sample(refresh_plan, "affected_match_urls", limit=20)
    attempted_count = _list_count(refresh_plan, "attempted_match_urls") or 0
    affected_count = _list_count(refresh_plan, "affected_match_urls") or 0
    failed_count = _list_count(refresh_plan, "failed_match_urls") or 0
    skipped_unchanged_count = max(0, attempted_count - affected_count - failed_count)

    return {
        "season": season,
        "source": {
            "report_path": _display_path(raw_season_source_preflight_file(season)),
            "status": (source or {}).get("status"),
            "source_url": source_url,
            "final_source_url": (source or {}).get("final_source_url"),
            "http_status": (source or {}).get("http_status"),
            "content_type": (source or {}).get("content_type"),
            "observed_link_count": (source or {}).get("observed_link_count"),
            "minimum_link_count": (source or {}).get("minimum_link_count"),
            "expected_match_count": (source or {}).get("expected_match_count")
            or (safety or {}).get("expected_match_rows")
            or failure_evidence.get("expected_match_count"),
            "failure_reason": (source or {}).get("failure_reason")
            or failure_evidence.get("failure_reason"),
            "source_structure_valid": (source or {}).get("source_structure_valid"),
            "baseline_version": (source or {}).get("baseline_version"),
        },
        "hosted_safety": {
            "report_path": _display_path(safety_path),
            "report_is_current": safety_is_current,
            "previous_report_status": (stale_safety or {}).get("status"),
            "status": (safety or {}).get("status"),
            "failure_reason": (safety or {}).get("failure_reason")
            or failure_evidence.get("failure_reason"),
            "existing_match_count": (safety or {}).get("existing_match_rows")
            or failure_evidence.get("existing_hosted_count"),
            "incoming_match_count": (safety or {}).get("incoming_match_rows")
            or failure_evidence.get("incoming_match_count"),
            "incoming_distinct_match_count": (safety or {}).get(
                "incoming_distinct_match_urls"
            )
            or failure_evidence.get("incoming_distinct_match_count"),
            "duplicate_match_rows": (safety or {}).get("duplicate_match_rows")
            or failure_evidence.get("duplicate_match_rows"),
            "missing_existing_match_url_count": (safety or {}).get(
                "missing_existing_match_url_count"
            )
            or failure_evidence.get("missing_existing_match_url_count"),
            "missing_existing_match_url_sample": (safety or {}).get(
                "missing_existing_match_url_sample"
            )
            or failure_evidence.get("missing_existing_match_url_sample"),
            "override_enabled": bool(
                (safety or {}).get("override_enabled")
                or failure_evidence.get("override_enabled", False)
            ),
            "database_write_stages_skipped": (safety or {}).get(
                "database_write_stages_skipped"
            )
            or failure_evidence.get("database_write_stages_skipped")
            or [],
        },
        "refresh_plan": {
            "report_path": _display_path(raw_season_refresh_plan_file(season)),
            "mode": (refresh_plan or {}).get("mode"),
            "affected_match_count": affected_count,
            "affected_match_ids": affected_ids,
            "affected_match_url_sample": affected_urls,
            "attempted_match_url_count": attempted_count,
            "failed_match_url_count": failed_count,
            "skipped_unchanged_match_url_count": skipped_unchanged_count,
        },
        "failed_matches": {
            "remaining_count": (
                child_summary.get("remaining_failed_matches") if child_summary else None
            ),
            "failed_match_url_count": failed_count,
            "failed_match_url_sample": _list_sample(refresh_plan, "failed_match_urls"),
        },
        "row_mutations": {
            "raw": {
                "processed_rows_by_table": raw_loader_rows,
                "processed_rows_total": _sum_counts(raw_loader_rows),
                "inserted_or_updated_rows_by_table": raw_loader_rows,
                "inserted_or_updated_rows_total": _sum_counts(raw_loader_rows),
                "delete_scope_match_count": affected_count,
                "exact_insert_update_split_available": False,
            },
            "staging": {
                "rebuilt_rows_by_table": staging_rows,
                "rebuilt_rows_total": _sum_counts(staging_rows),
                "inserted_rows_by_table": staging_rows,
                "inserted_rows_total": _sum_counts(staging_rows),
                "deleted_and_rebuilt_season_slice": bool(staging_rows),
                "stage_state": (
                    child_summary.get("staging_rebuild")
                    if child_summary
                    else ("completed" if staging_log else None)
                ),
            },
            "analytics": {
                "refreshed_with_staging_rebuild": bool(staging_rows),
                "row_counts_available": False,
            },
        },
        "staging_run": staging_metadata,
    }


def _classify_outcome(
    *,
    args: argparse.Namespace,
    status: str,
    season_summaries: list[dict[str, Any]],
    child_failure_summary: dict[str, Any] | None,
) -> str:
    """Return the operator-facing hosted refresh outcome bucket."""

    if status == "failed":
        if any(
            summary["source"].get("status") == "failed" for summary in season_summaries
        ):
            return "source-health failure"
        if any(
            summary["hosted_safety"].get("status") == "blocked"
            for summary in season_summaries
        ):
            return "guard blocked write"
        failed_stage = (child_failure_summary or {}).get("failed_stage")
        if failed_stage == "scrape_current_season":
            return "source-health failure"
        return "failed"
    if args.run_type == "rebuild-from-existing-raw" or args.force_full_scrape:
        return "admin rebuild"
    affected = sum(
        _int_or_none(summary["refresh_plan"].get("affected_match_count")) or 0
        for summary in season_summaries
    )
    raw_processed = sum(
        _int_or_none(summary["row_mutations"]["raw"].get("processed_rows_total")) or 0
        for summary in season_summaries
    )
    if affected == 0 and raw_processed == 0:
        return "no changes"
    return "routine updates applied"


def _hosted_observability_payload(
    *,
    args: argparse.Namespace,
    seasons: list[str],
    log_dir: Path,
    step_logs: dict[str, str],
    status: str,
    failure: str | None,
    current_run_started_at: float | None = None,
) -> dict[str, Any]:
    """Build the full hosted summary payload uploaded by GitHub Actions."""

    child_failure_summary = (
        _latest_child_failure_summary(
            log_dir,
            search_roots=_current_step_roots(log_dir=log_dir, step_logs=step_logs),
        )
        if status == "failed"
        else None
    )
    child_summaries = {
        season: _latest_child_run_summary(
            log_dir,
            failed=False,
            season=season,
            search_roots=_current_step_roots(
                log_dir=log_dir, step_logs=step_logs, season=season
            ),
        )
        for season in seasons
    }
    latest_child_summary = _latest_child_run_summary(
        log_dir,
        failed=False,
        search_roots=_current_step_roots(log_dir=log_dir, step_logs=step_logs),
    )
    season_summaries = [
        _season_observability_payload(
            season=season,
            child_summary=(
                child_summaries[season]
                if child_summaries[season]
                and child_summaries[season].get("season") == season
                else None
            ),
            child_failure_summary=child_failure_summary,
            current_run_started_at=current_run_started_at,
        )
        for season in seasons
    ]
    outcome = _classify_outcome(
        args=args,
        status=status,
        season_summaries=season_summaries,
        child_failure_summary=child_failure_summary,
    )
    return {
        "status": status,
        "outcome": outcome,
        "season_scope": args.season_scope,
        "run_type": args.run_type,
        "seasons": seasons,
        "apply_migrations": args.apply_migrations,
        "use_cache": args.use_cache,
        "force_full_scrape": args.force_full_scrape,
        "io_verification": {
            "routine_uses_live_source": not args.use_cache,
            "routine_skips_migrations": not args.apply_migrations,
            "force_full_scrape": args.force_full_scrape,
            "unsafe_reload_override_exposed_by_wrapper": False,
            "artifacts_uploaded_by_workflow": "outputs/automation/ and data/raw/",
        },
        "step_logs": step_logs,
        "failure": failure,
        "child_run_summary": latest_child_summary,
        "child_run_summaries": child_summaries,
        "child_failure_summary": child_failure_summary,
        "staging_aggregate": _staging_aggregate_payload(step_logs),
        "season_summaries": season_summaries,
    }


def _format_count(value: object) -> str:
    """Return a readable count for Markdown summaries."""

    return "unknown" if value is None else str(value)


def _write_markdown_summary(summary_path: Path, payload: dict[str, Any]) -> Path:
    """Write a human-readable hosted update summary beside the JSON artifact."""

    markdown_path = summary_path.with_suffix(".md")
    lines = [
        "# Hosted Data Update Summary",
        "",
        f"- Status: {payload['status']}",
        f"- Outcome: {payload['outcome']}",
        f"- Season scope: {payload['season_scope']}",
        f"- Run type: {payload['run_type']}",
        f"- Seasons: {', '.join(payload['seasons'])}",
        f"- Migrations: {'applied' if payload['apply_migrations'] else 'skipped'}",
        f"- Cache: {'allowed' if payload['use_cache'] else 'bypassed for live source'}",
        f"- Force full scrape: {payload['force_full_scrape']}",
        "",
    ]
    if payload.get("failure"):
        lines.extend(["## Failure", "", str(payload["failure"]), ""])

    aggregate = payload.get("staging_aggregate") or {}
    if aggregate.get("row_counts_by_table"):
        lines.extend(
            [
                "## Aggregate Staging Rebuild",
                "",
                f"- Scope: {aggregate.get('scope') or 'unknown'}",
                f"- Log: {aggregate.get('log_path') or 'unknown'}",
                f"- Staging rows: {aggregate.get('row_count_total')} across {aggregate.get('row_counts_by_table') or {}}",
                f"- Staging run ID: {(aggregate.get('staging_run') or {}).get('run_id') or 'unknown'}",
                "",
            ]
        )

    for summary in payload["season_summaries"]:
        source = summary["source"]
        safety = summary["hosted_safety"]
        plan = summary["refresh_plan"]
        raw = summary["row_mutations"]["raw"]
        staging = summary["row_mutations"]["staging"]
        staging_run = summary["staging_run"]
        lines.extend(
            [
                f"## Season {summary['season']}",
                "",
                f"- Source URL: {source.get('source_url') or 'unknown'}",
                f"- Source status: {source.get('status') or 'unknown'}; HTTP {source.get('http_status') or 'unknown'}; links { _format_count(source.get('observed_link_count')) } of expected { _format_count(source.get('expected_match_count')) }",
                f"- Source failure reason: {source.get('failure_reason') or 'none'}",
                f"- Hosted existing matches: {_format_count(safety.get('existing_match_count'))}",
                f"- Incoming distinct matches: {_format_count(safety.get('incoming_distinct_match_count'))}",
                f"- Safety status: {safety.get('status') or 'unknown'}; skipped stages: {', '.join(safety.get('database_write_stages_skipped') or []) or 'none'}",
                f"- Missing hosted URLs: {_format_count(safety.get('missing_existing_match_url_count'))}",
                f"- Affected match IDs: {plan.get('affected_match_count')} total; sample {plan.get('affected_match_ids') or []}",
                f"- Attempted URLs: {plan.get('attempted_match_url_count')}; failed URLs: {plan.get('failed_match_url_count')}; skipped unchanged URLs: {plan.get('skipped_unchanged_match_url_count')}",
                f"- Raw rows inserted/updated: {raw.get('inserted_or_updated_rows_total')} across {raw.get('inserted_or_updated_rows_by_table') or {}}; delete match scope: {raw.get('delete_scope_match_count')}",
                f"- Staging rows inserted after rebuild: {staging.get('inserted_rows_total')} across {staging.get('inserted_rows_by_table') or {}}",
                f"- Staging run ID: {staging_run.get('run_id') or 'unknown'}; verification: {staging_run.get('verification_status')}",
                "",
            ]
        )

    lines.extend(["## Step Logs", ""])
    if payload["step_logs"]:
        for step_name, log_path in payload["step_logs"].items():
            lines.append(f"- {step_name}: {log_path}")
    else:
        lines.append("- none recorded")
    lines.append("")

    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return markdown_path


def _latest_child_failure_summary(
    log_dir: Path, *, search_roots: list[Path] | None = None
) -> dict[str, object] | None:
    """Return the newest child failure summary produced before subprocess exit."""

    payload = _latest_child_run_summary(log_dir, failed=True, search_roots=search_roots)
    if payload is None:
        return None
    return {
        "path": payload.get("path"),
        "failure_evidence": payload.get("failure_evidence"),
        "failed_stage": payload.get("failed_stage"),
        "failure_reason": payload.get("failure_reason"),
    }


def _write_summary(
    *,
    args: argparse.Namespace,
    seasons: list[str],
    log_dir: Path,
    step_logs: dict[str, str],
    status: str,
    failure: str | None = None,
    current_run_started_at: float | None = None,
) -> Path:
    """Write JSON and Markdown summaries for hosted troubleshooting."""

    log_dir.mkdir(parents=True, exist_ok=True)
    summary_path = log_dir / f"{_timestamp_slug()}_hosted_update_summary.json"
    payload = _hosted_observability_payload(
        args=args,
        seasons=seasons,
        log_dir=log_dir,
        step_logs=step_logs,
        status=status,
        failure=failure,
        current_run_started_at=current_run_started_at,
    )
    markdown_path = _write_markdown_summary(summary_path, payload)
    payload["readable_summary_path"] = _display_path(markdown_path)
    summary_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"\n[hosted-update] Summary artifact: {_display_path(summary_path)}")
    print(f"[hosted-update] Readable summary: {_display_path(markdown_path)}")
    return summary_path


def main() -> None:
    """Run the selected hosted data update."""

    args = parse_args()
    seasons = _resolve_target_seasons(args)
    log_dir = args.log_dir / _scope_slug(args, seasons) / _timestamp_slug()
    current_run_started_at = time.time()
    step_logs: dict[str, str] = {}

    print("UPL Lens - Hosted Data Update")
    print(f"Season scope: {args.season_scope}")
    print(f"Run type: {args.run_type}")
    print(f"Target seasons: {', '.join(seasons)}")
    print(f"Apply migrations: {args.apply_migrations}")
    print(f"Use cache: {args.use_cache}")
    print(f"Force full scrape: {args.force_full_scrape}")

    try:
        if args.run_type == "rebuild-from-existing-raw" and args.season_scope == "all":
            _run_rebuild_all_from_existing_raw(
                args=args, log_dir=log_dir, step_logs=step_logs
            )
        else:
            _run_per_season_pipeline(
                args=args, seasons=seasons, log_dir=log_dir, step_logs=step_logs
            )
    except HostedUpdateStepError as error:
        step_logs.setdefault(error.step_name, _display_path(error.log_path))
        _write_summary(
            args=args,
            seasons=seasons,
            log_dir=log_dir,
            step_logs=step_logs,
            status="failed",
            failure=str(error),
            current_run_started_at=current_run_started_at,
        )
        raise SystemExit(error.exit_code) from error

    _write_summary(
        args=args,
        seasons=seasons,
        log_dir=log_dir,
        step_logs=step_logs,
        status="success",
        current_run_started_at=current_run_started_at,
    )
    print("\n[ok] Hosted data update finished.")


if __name__ == "__main__":
    main()
