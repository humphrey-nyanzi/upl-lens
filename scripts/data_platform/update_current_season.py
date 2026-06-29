"""Run the current-season operations update pipeline.

This script is the small conductor for the routine data-refresh workflow. It
reuses the existing scraper, Postgres loader, staging builder, and verification
scripts instead of creating a second version of the data pipeline.

Usage examples
--------------
python scripts/data_platform/update_current_season.py
python scripts/data_platform/update_current_season.py --season 2025-26
python scripts/data_platform/update_current_season.py --mode artifact-only
python scripts/data_platform/update_current_season.py --skip-scrape
python scripts/data_platform/update_current_season.py --skip-scrape --skip-raw-load
python scripts/data_platform/update_current_season.py --use-cache
python scripts/data_platform/update_current_season.py --skip-migrations
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    CURRENT_SEASON,
    RAW_TABLE_FILE_PREFIXES,
    raw_season_dir,
    raw_season_failed_matches_file,
    raw_season_file,
    raw_season_load_safety_file,
    raw_season_source_preflight_file,
    season_key,
)
from src.operations.command_runner import display_path, run_logged_step, timestamp_slug

SCRIPT_DIR = PROJECT_ROOT / "scripts" / "data_platform"
DEFAULT_LOG_DIR = PROJECT_ROOT / "outputs" / "automation"
RAW_SUMMARY_TABLES = (*RAW_TABLE_FILE_PREFIXES.keys(), "failed_matches")
LOAD_COUNT_PATTERN = re.compile(
    r"^\s+(?P<table>[a-z_]+): (?P<count>\d+) in-season rows processed\s*$"
)
STAGING_COUNT_PATTERN = re.compile(
    r"^\s+staging\.(?P<table>[a-z_]+): (?P<count>\d+) rows\s*$"
)
EVENT_TYPE_COUNT_PATTERN = re.compile(
    r"^\s+(?P<season>\d{4}_\d{2})\s+(?P<event_type>[a-z_]+)\s+(?P<count>\d+)\s*$"
)


@dataclass
class OperationsStepError(Exception):
    """Raised when one operations stage fails after writing its step log."""

    step_name: str
    log_path: Path
    exit_code: int

    def __str__(self) -> str:
        return (
            f"\n[error] Operations step failed: {self.step_name}. "
            f"Exit code: {self.exit_code}. Review {self.log_path}."
        )


def parse_args() -> argparse.Namespace:
    """Parse command-line options for the current-season update run."""

    parser = argparse.ArgumentParser(
        description="Run the current-season scraper and optional Postgres refresh pipeline."
    )
    parser.add_argument(
        "--season",
        default=CURRENT_SEASON,
        help=f"Season to update, for example 2025-26. Defaults to {CURRENT_SEASON}.",
    )
    parser.add_argument(
        "--mode",
        choices=("full", "artifact-only"),
        default="full",
        help=(
            "full runs scraper, Postgres loading, staging rebuild, and verification. "
            "artifact-only only refreshes raw scraped files for CI artifacts."
        ),
    )
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Reuse existing raw season files and start at the database steps.",
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help=(
            "Allow the scraper to reuse cached HTML and checkpoint state. "
            "By default, routine operations refresh from the live source."
        ),
    )
    parser.add_argument(
        "--disable-postgres-change-detection",
        action="store_true",
        help=(
            "Scrape every calendar match instead of using raw Postgres rows to "
            "skip already-complete matches. Use this for investigation or a full "
            "scrape rebuild."
        ),
    )
    parser.add_argument(
        "--skip-raw-verification",
        action="store_true",
        help="Skip the raw CSV versus Postgres count check.",
    )
    parser.add_argument(
        "--skip-raw-load",
        action="store_true",
        help=(
            "Skip loading raw CSVs into Postgres and reuse the existing raw database rows. "
            "Use with --skip-scrape when retrying staging after a successful raw load."
        ),
    )
    parser.add_argument(
        "--skip-staging-verification",
        action="store_true",
        help="Skip the staging validation summary check.",
    )
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help=(
            "Skip database migrations in full mode. Use this for routine "
            "scheduled refreshes that run with a least-privilege loader role."
        ),
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=DEFAULT_LOG_DIR,
        help="Directory where command logs should be written.",
    )
    parser.add_argument(
        "--fail-on-remaining-failed-matches",
        action="store_true",
        help=(
            "Exit with an error if the season still has failed match URLs after "
            "the update. Useful for strict scheduled jobs."
        ),
    )
    return parser.parse_args()


def _timestamp_slug() -> str:
    """Return a compact UTC timestamp for log filenames."""

    return timestamp_slug()


def _display_path(path: Path) -> str:
    """Return a readable path, preferring repo-relative paths when possible."""

    return display_path(path, PROJECT_ROOT)


def _run_step(step_name: str, command: list[str], log_dir: Path) -> Path:
    """Run one pipeline step, stream output, and save a log file.

    The log file matters in automation because GitHub Actions output can be
    noisy. A separate file makes failed scrapes or validation errors easier to
    download and inspect after the run.
    """

    return run_logged_step(
        step_name=step_name,
        command=command,
        log_dir=log_dir,
        project_root=PROJECT_ROOT,
        log_prefix="[operations]",
        error_type=OperationsStepError,
    )


def _python_command(script_name: str, *extra_args: str) -> list[str]:
    """Build a script command using the same Python executable as this run."""

    return [
        sys.executable,
        str(SCRIPT_DIR / script_name),
        *extra_args,
    ]


def _read_failed_matches(season: str) -> list[dict[str, str]]:
    """Return remaining failed-match rows for a season, if the manifest exists."""

    failed_matches_path = raw_season_failed_matches_file(season)
    if not failed_matches_path.exists():
        return []

    with failed_matches_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _count_csv_rows(csv_path: Path) -> int | None:
    """Return CSV data-row count, or None when the file is absent.

    GitHub Actions artifacts already contain these files. Printing the same
    counts at the end of the run gives a fast, human-readable confirmation
    without requiring someone to download artifacts just to check row totals.
    """

    if not csv_path.exists():
        return None

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def _raw_csv_counts(season: str) -> dict[str, int | None]:
    """Return row counts for the season-scoped raw CSV files."""

    counts = {
        table_name: _count_csv_rows(raw_season_file(season, table_name))
        for table_name in RAW_TABLE_FILE_PREFIXES
    }
    counts["failed_matches"] = _count_csv_rows(raw_season_failed_matches_file(season))
    return counts


def _extract_raw_load_counts(log_path: Path | None) -> dict[str, int]:
    """Read raw-loader row totals back from its step log."""

    if log_path is None or not log_path.exists():
        return {}

    counts: dict[str, int] = {}
    with log_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = LOAD_COUNT_PATTERN.match(line)
            if match:
                counts[match.group("table")] = int(match.group("count"))
    return counts


def _extract_staging_row_counts(log_path: Path | None) -> dict[str, int]:
    """Read staging row totals back from the staging-build step log."""

    if log_path is None or not log_path.exists():
        return {}

    counts: dict[str, int] = {}
    with log_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = STAGING_COUNT_PATTERN.match(line)
            if match:
                counts[match.group("table")] = int(match.group("count"))
    return counts


def _extract_event_type_counts(log_path: Path | None) -> dict[str, int]:
    """Read event-type totals back from the staging verification step log."""

    if log_path is None or not log_path.exists():
        return {}

    counts: dict[str, int] = {}
    in_event_counts = False
    with log_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("Event type counts:"):
                in_event_counts = True
                continue
            if in_event_counts and not line.strip():
                in_event_counts = False
                continue
            if not in_event_counts:
                continue
            match = EVENT_TYPE_COUNT_PATTERN.match(line)
            if match:
                counts[match.group("event_type")] = int(match.group("count"))
    return counts


def _print_table_counts(title: str, counts: dict[str, int | None]) -> None:
    """Print a compact table-count block for the final automation summary."""

    print(f"\n{title}:")
    for table_name in RAW_SUMMARY_TABLES:
        row_count = counts.get(table_name)
        if row_count is None:
            print(f"  {table_name:<14} missing")
        else:
            print(f"  {table_name:<14} {row_count}")


def _staging_verification_status(log_path: Path | None) -> str:
    """Return a short status for the staging validation step."""

    if log_path is None:
        return "skipped"
    if not log_path.exists():
        return "completed; log file missing"

    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    if (
        "[ok] Staging verification finished without error-level validation issues."
        in log_text
    ):
        return "passed without error-level validation issues"
    return "completed; review log for validation details"


def _print_final_success_summary(
    *,
    season: str,
    mode: str,
    use_cache: bool,
    skip_migrations: bool,
    failed_count: int,
    step_logs: dict[str, Path],
    raw_verification_ran: bool,
    staging_verification_ran: bool,
) -> None:
    """Print the human-facing success summary for CI logs."""

    raw_counts = _raw_csv_counts(season)
    raw_load_counts = _extract_raw_load_counts(step_logs.get("load_raw_to_postgres"))
    staging_row_counts = _extract_staging_row_counts(
        step_logs.get("build_staging_from_raw")
    )
    event_type_counts = _extract_event_type_counts(
        step_logs.get("verify_staging_outputs") if staging_verification_ran else None
    )
    staging_status = _staging_verification_status(
        step_logs.get("verify_staging_outputs") if staging_verification_ran else None
    )

    print("\n[operations] Final run summary")
    print(f"  Season: {season}")
    print(f"  Mode: {mode}")
    print(
        f"  Source: {'cached HTML/checkpoints allowed' if use_cache else 'fresh live-source refresh'}"
    )
    print(f"  Migrations: {'skipped' if skip_migrations else 'applied'}")
    print(f"  Raw verification: {'completed' if raw_verification_ran else 'skipped'}")
    print(f"  Staging rebuild: completed")
    print(f"  Staging verification: {staging_status}")
    print(f"  Remaining failed matches: {failed_count}")

    _print_table_counts("Raw CSV rows prepared for artifacts", raw_counts)
    if raw_load_counts:
        _print_table_counts("Raw rows processed by Postgres loader", raw_load_counts)
    if staging_row_counts:
        _print_table_counts("Staging rows written", staging_row_counts)
    if event_type_counts:
        _print_table_counts("Staging event type counts", event_type_counts)

    print("\nStep logs:")
    for step_name, log_path in step_logs.items():
        print(f"  {step_name:<28} {_display_path(log_path)}")


def _run_summary_payload(
    *,
    season: str,
    mode: str,
    use_cache: bool,
    skip_migrations: bool,
    failed_count: int,
    step_logs: dict[str, Path],
    raw_verification_ran: bool,
    staging_verification_ran: bool,
) -> dict[str, object]:
    """Return the structured final run summary written beside step logs."""

    raw_counts = _raw_csv_counts(season)
    raw_load_counts = _extract_raw_load_counts(step_logs.get("load_raw_to_postgres"))
    staging_row_counts = _extract_staging_row_counts(
        step_logs.get("build_staging_from_raw")
    )
    event_type_counts = _extract_event_type_counts(
        step_logs.get("verify_staging_outputs") if staging_verification_ran else None
    )
    staging_status = _staging_verification_status(
        step_logs.get("verify_staging_outputs") if staging_verification_ran else None
    )

    return {
        "status": "success",
        "season": season,
        "mode": mode,
        "source": (
            "cached HTML/checkpoints allowed"
            if use_cache
            else "fresh live-source refresh"
        ),
        "migrations": "skipped" if skip_migrations else "applied",
        "raw_verification": "completed" if raw_verification_ran else "skipped",
        "staging_rebuild": "completed",
        "staging_verification": staging_status,
        "remaining_failed_matches": failed_count,
        "raw_csv_rows": raw_counts,
        "raw_loader_rows": raw_load_counts,
        "staging_rows": staging_row_counts,
        "staging_event_type_counts": event_type_counts,
        "step_logs": {
            step_name: _display_path(log_path)
            for step_name, log_path in step_logs.items()
        },
    }


def _read_json_artifact(path: Path) -> dict[str, object] | None:
    """Read a JSON artifact without hiding the original pipeline failure."""

    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _failure_evidence_payload(
    *,
    season: str,
    step_logs: dict[str, Path],
    failed_stage: str,
) -> dict[str, object]:
    """Merge source and loader guard evidence across subprocess boundaries."""

    source = _read_json_artifact(raw_season_source_preflight_file(season)) or {}
    raw_load = (
        _read_json_artifact(raw_season_load_safety_file(season)) or {}
        if failed_stage == "load_raw_to_postgres"
        else {}
    )
    raw_completed = "load_raw_to_postgres" in step_logs
    staging_completed = "build_staging_from_raw" in step_logs
    skipped_write_stages = []
    if not raw_completed:
        skipped_write_stages.append("raw")
    if not staging_completed:
        skipped_write_stages.extend(["staging", "analytics"])

    return {
        "source_url": source.get("source_url") or raw_load.get("source_url"),
        "failure_reason": raw_load.get("failure_reason")
        or source.get("failure_reason"),
        "observed_link_count": source.get("observed_link_count"),
        "minimum_link_count": source.get("minimum_link_count"),
        "expected_match_count": raw_load.get("expected_match_rows")
        or source.get("expected_match_count"),
        "incoming_match_count": raw_load.get("incoming_match_rows"),
        "existing_hosted_count": raw_load.get("existing_match_rows"),
        "target_season": season,
        "override_enabled": bool(raw_load.get("override_enabled", False)),
        "database_write_stages_skipped": skipped_write_stages,
        "failed_stage": failed_stage,
        "source_preflight_report": _display_path(
            raw_season_source_preflight_file(season)
        ),
        "raw_load_safety_report": _display_path(raw_season_load_safety_file(season)),
    }


def _partial_artifacts_payload(
    *,
    season: str,
    log_dir: Path,
    step_logs: dict[str, Path],
    failed_stage_log: Path | None = None,
) -> dict[str, object]:
    """Return artifact paths and row counts that may help debug a failed run."""

    raw_dir = raw_season_dir(season)
    raw_counts = _raw_csv_counts(season)
    raw_files = {
        table_name: {
            "path": _display_path(raw_season_file(season, table_name)),
            "exists": raw_season_file(season, table_name).exists(),
            "row_count": raw_counts.get(table_name),
        }
        for table_name in RAW_TABLE_FILE_PREFIXES
    }
    failed_matches_path = raw_season_failed_matches_file(season)
    raw_files["failed_matches"] = {
        "path": _display_path(failed_matches_path),
        "exists": failed_matches_path.exists(),
        "row_count": raw_counts.get("failed_matches"),
    }

    return {
        "raw_season_dir": _display_path(raw_dir),
        "raw_season_dir_exists": raw_dir.exists(),
        "raw_files": raw_files,
        "automation_log_dir": _display_path(log_dir),
        "automation_log_dir_exists": log_dir.exists(),
        "completed_step_logs": {
            step_name: _display_path(log_path)
            for step_name, log_path in step_logs.items()
        },
        "failed_stage_log": (
            _display_path(failed_stage_log) if failed_stage_log is not None else None
        ),
        "source_preflight_report": _display_path(
            raw_season_source_preflight_file(season)
        ),
        "raw_load_safety_report": _display_path(raw_season_load_safety_file(season)),
    }


def _failed_run_summary_payload(
    *,
    season: str,
    mode: str,
    use_cache: bool,
    skip_migrations: bool,
    skip_raw_load: bool,
    skip_raw_verification: bool,
    skip_staging_verification: bool,
    step_logs: dict[str, Path],
    log_dir: Path,
    failed_stage: str,
    failed_stage_log: Path | None,
    exit_code: int | None,
    failure_reason: str,
) -> dict[str, object]:
    """Return the structured summary for an operations run that did not finish."""

    return {
        "status": "failed",
        "season": season,
        "mode": mode,
        "source": (
            "cached HTML/checkpoints allowed"
            if use_cache
            else "fresh live-source refresh"
        ),
        "migrations": (
            "skipped"
            if skip_migrations
            else _stage_state(
                "apply_db_migrations",
                step_logs,
                failed_stage,
            )
        ),
        "raw_load": (
            "skipped"
            if skip_raw_load
            else _stage_state(
                "load_raw_to_postgres",
                step_logs,
                failed_stage,
            )
        ),
        "raw_verification": _verification_state(
            step_name="verify_raw_postgres_counts",
            skipped=skip_raw_load or skip_raw_verification,
            step_logs=step_logs,
            failed_stage=failed_stage,
        ),
        "staging_rebuild": _stage_state(
            "build_staging_from_raw",
            step_logs,
            failed_stage,
        ),
        "staging_verification": _verification_state(
            step_name="verify_staging_outputs",
            skipped=skip_staging_verification,
            step_logs=step_logs,
            failed_stage=failed_stage,
        ),
        "failed_stage": failed_stage,
        "failed_stage_log": (
            _display_path(failed_stage_log) if failed_stage_log is not None else None
        ),
        "exit_code": exit_code,
        "failure_reason": failure_reason,
        "failure_evidence": _failure_evidence_payload(
            season=season,
            step_logs=step_logs,
            failed_stage=failed_stage,
        ),
        "partial_artifacts": _partial_artifacts_payload(
            season=season,
            log_dir=log_dir,
            step_logs=step_logs,
            failed_stage_log=failed_stage_log,
        ),
    }


def _stage_state(
    step_name: str,
    step_logs: dict[str, Path],
    failed_stage: str,
) -> str:
    """Return whether a pipeline stage completed, failed, or had not started."""

    if step_name in step_logs:
        return "completed"
    if step_name == failed_stage:
        return "failed"
    return "not_started"


def _verification_state(
    *,
    step_name: str,
    skipped: bool,
    step_logs: dict[str, Path],
    failed_stage: str,
) -> str:
    """Return a concise status for a verification stage."""

    if skipped and step_name not in step_logs and step_name != failed_stage:
        return "skipped"
    return _stage_state(step_name, step_logs, failed_stage)


def _write_failed_run_summary_json(
    *,
    season: str,
    mode: str,
    use_cache: bool,
    skip_migrations: bool,
    skip_raw_load: bool,
    skip_raw_verification: bool,
    skip_staging_verification: bool,
    step_logs: dict[str, Path],
    log_dir: Path,
    failed_stage: str,
    failed_stage_log: Path | None,
    exit_code: int | None,
    failure_reason: str,
) -> Path:
    """Write a machine-readable run summary before a failed operation exits."""

    log_dir.mkdir(parents=True, exist_ok=True)
    summary_path = log_dir / f"{_timestamp_slug()}_run_summary_failed.json"
    payload = _failed_run_summary_payload(
        season=season,
        mode=mode,
        use_cache=use_cache,
        skip_migrations=skip_migrations,
        skip_raw_load=skip_raw_load,
        skip_raw_verification=skip_raw_verification,
        skip_staging_verification=skip_staging_verification,
        step_logs=step_logs,
        log_dir=log_dir,
        failed_stage=failed_stage,
        failed_stage_log=failed_stage_log,
        exit_code=exit_code,
        failure_reason=failure_reason,
    )
    summary_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"\n[operations] Failed run summary artifact: {_display_path(summary_path)}")
    return summary_path


def _write_run_summary_json(
    *,
    season: str,
    mode: str,
    use_cache: bool,
    skip_migrations: bool,
    failed_count: int,
    step_logs: dict[str, Path],
    raw_verification_ran: bool,
    staging_verification_ran: bool,
    log_dir: Path,
) -> Path:
    """Write a machine-readable run summary for artifacts and troubleshooting."""

    log_dir.mkdir(parents=True, exist_ok=True)
    summary_path = log_dir / f"{_timestamp_slug()}_run_summary.json"
    payload = _run_summary_payload(
        season=season,
        mode=mode,
        use_cache=use_cache,
        skip_migrations=skip_migrations,
        failed_count=failed_count,
        step_logs=step_logs,
        raw_verification_ran=raw_verification_ran,
        staging_verification_ran=staging_verification_ran,
    )
    summary_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"\n[operations] Run summary artifact: {_display_path(summary_path)}")
    return summary_path


def _print_failed_match_summary(season: str, *, max_rows: int = 10) -> int:
    """Print the data-completeness state for the current season update."""

    failed_matches = _read_failed_matches(season)
    failed_count = len(failed_matches)

    print("\n[operations] Data completeness summary")
    if failed_count == 0:
        print("[ok] No remaining failed matches were recorded for this season.")
        return 0

    print(f"[warning] {failed_count} match URL(s) still need a future retry.")
    for failed_match in failed_matches[:max_rows]:
        match_url = failed_match.get("match_url", "<missing match_url>")
        attempt_count = failed_match.get("attempt_count", "")
        last_error = failed_match.get("last_error", "")
        print(f"  - {match_url}")
        if attempt_count or last_error:
            print(
                f"    attempts={attempt_count or 'unknown'} last_error={last_error or 'unknown'}"
            )

    if failed_count > max_rows:
        print(f"  ... and {failed_count - max_rows} more")

    return failed_count


def _enforce_failed_match_policy(failed_count: int, *, fail_on_remaining: bool) -> None:
    """Fail the job only when the caller requested strict completeness."""

    if failed_count and fail_on_remaining:
        raise SystemExit(
            "\n[error] Current-season update finished with remaining failed matches."
        )


def _coerce_exit_code(exit_code: object) -> int | None:
    """Return an integer process exit code when SystemExit provides one."""

    if exit_code is None:
        return 1
    if isinstance(exit_code, int):
        return exit_code
    return None


def _run_update_pipeline(
    *,
    args: argparse.Namespace,
    season: str,
    log_dir: Path,
    step_logs: dict[str, Path],
) -> None:
    """Run the selected operations pipeline after argument parsing."""

    if not args.skip_scrape:
        scrape_command = _python_command("scrape_upl_matches.py", "--season", season)
        if not args.use_cache:
            scrape_command.append("--refresh-source")
        if args.mode == "full" and not args.disable_postgres_change_detection:
            scrape_command.append("--postgres-change-detection")

        step_logs["scrape_current_season"] = _run_step(
            "scrape_current_season",
            scrape_command,
            log_dir,
        )
    else:
        print("\n[operations] Skipping scraper and reusing existing raw season files.")

    if args.mode == "artifact-only":
        failed_count = _print_failed_match_summary(season)
        _enforce_failed_match_policy(
            failed_count,
            fail_on_remaining=args.fail_on_remaining_failed_matches,
        )
        print("\n[ok] Artifact-only update finished.")
        print(
            "[ok] Raw files are ready for upload as workflow artifacts, "
            "but no Postgres tables were changed."
        )
        return

    if args.skip_migrations:
        print(
            "\n[operations] Skipping database migrations. "
            "This is expected for routine least-privilege update runs."
        )
    else:
        step_logs["apply_db_migrations"] = _run_step(
            "apply_db_migrations",
            _python_command("apply_db_migrations.py"),
            log_dir,
        )

    if args.skip_raw_load:
        print(
            "\n[operations] Skipping raw Postgres load and reusing existing raw database rows.",
            flush=True,
        )
    else:
        step_logs["load_raw_to_postgres"] = _run_step(
            "load_raw_to_postgres",
            _python_command("load_raw_to_postgres.py", "--season", season),
            log_dir,
        )

    if args.skip_raw_load:
        print(
            "\n[operations] Skipping raw verification because raw loading was skipped.",
            flush=True,
        )
    elif not args.skip_raw_verification:
        step_logs["verify_raw_postgres_counts"] = _run_step(
            "verify_raw_postgres_counts",
            _python_command("verify_raw_postgres_counts.py", "--season", season),
            log_dir,
        )

    step_logs["build_staging_from_raw"] = _run_step(
        "build_staging_from_raw",
        _python_command("build_staging_from_raw.py", "--season", season),
        log_dir,
    )

    if not args.skip_staging_verification:
        step_logs["verify_staging_outputs"] = _run_step(
            "verify_staging_outputs",
            _python_command("verify_staging_outputs.py", "--season", season),
            log_dir,
        )

    failed_count = _print_failed_match_summary(season)
    _enforce_failed_match_policy(
        failed_count,
        fail_on_remaining=args.fail_on_remaining_failed_matches,
    )

    _print_final_success_summary(
        season=season,
        mode=args.mode,
        use_cache=args.use_cache,
        skip_migrations=args.skip_migrations,
        failed_count=failed_count,
        step_logs=step_logs,
        raw_verification_ran=not args.skip_raw_load and not args.skip_raw_verification,
        staging_verification_ran=not args.skip_staging_verification,
    )
    _write_run_summary_json(
        season=season,
        mode=args.mode,
        use_cache=args.use_cache,
        skip_migrations=args.skip_migrations,
        failed_count=failed_count,
        step_logs=step_logs,
        raw_verification_ran=not args.skip_raw_load and not args.skip_raw_verification,
        staging_verification_ran=not args.skip_staging_verification,
        log_dir=log_dir,
    )

    print("\n[ok] Full current-season update finished.")
    print("[ok] The scraper, raw Postgres load, staging rebuild, and checks completed.")


def main() -> None:
    """Run the selected current-season update pipeline."""

    args = parse_args()
    season = args.season
    normalized_season = season_key(season)
    log_dir = args.log_dir / normalized_season

    print("UPL Lens - Current Season Operations Update")
    print(f"Season: {season}")
    print(f"Mode: {args.mode}")
    print(f"Raw season folder: {raw_season_dir(season).relative_to(PROJECT_ROOT)}")
    step_logs: dict[str, Path] = {}

    try:
        _run_update_pipeline(
            args=args,
            season=season,
            log_dir=log_dir,
            step_logs=step_logs,
        )
    except OperationsStepError as error:
        _write_failed_run_summary_json(
            season=season,
            mode=args.mode,
            use_cache=args.use_cache,
            skip_migrations=args.skip_migrations,
            skip_raw_load=args.skip_raw_load,
            skip_raw_verification=args.skip_raw_verification,
            skip_staging_verification=args.skip_staging_verification,
            step_logs=step_logs,
            log_dir=log_dir,
            failed_stage=error.step_name,
            failed_stage_log=error.log_path,
            exit_code=error.exit_code,
            failure_reason=str(error),
        )
        raise SystemExit(error.exit_code) from error
    except SystemExit as error:
        exit_code = _coerce_exit_code(error.code)
        _write_failed_run_summary_json(
            season=season,
            mode=args.mode,
            use_cache=args.use_cache,
            skip_migrations=args.skip_migrations,
            skip_raw_load=args.skip_raw_load,
            skip_raw_verification=args.skip_raw_verification,
            skip_staging_verification=args.skip_staging_verification,
            step_logs=step_logs,
            log_dir=log_dir,
            failed_stage="operations_policy",
            failed_stage_log=None,
            exit_code=exit_code,
            failure_reason=str(error),
        )
        raise


if __name__ == "__main__":
    main()
