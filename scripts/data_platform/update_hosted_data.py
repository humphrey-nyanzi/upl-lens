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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CURRENT_SEASON, season_key


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

    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _display_path(path: Path) -> str:
    """Return a readable path, preferring repo-relative paths."""

    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _python_command(script_name: str, *extra_args: str) -> list[str]:
    """Build a data-platform script command using this Python executable."""

    return [sys.executable, str(SCRIPT_DIR / script_name), *extra_args]


def _run_step(step_name: str, command: list[str], log_dir: Path) -> Path:
    """Run one subprocess, stream output, and save a per-step log."""

    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{_timestamp_slug()}_{step_name}.log"

    print(f"\n[hosted-update] Starting {step_name}", flush=True)
    print(f"[hosted-update] Command: {' '.join(command)}", flush=True)
    print(f"[hosted-update] Log: {_display_path(log_path)}", flush=True)

    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write(f"Step: {step_name}\n")
        log_file.write(f"Command: {' '.join(command)}\n\n")
        process = subprocess.Popen(
            command,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
            log_file.write(line)
            log_file.flush()

    exit_code = process.wait()
    if exit_code != 0:
        raise HostedUpdateStepError(step_name, log_path, exit_code)

    print(f"[hosted-update] Finished {step_name}", flush=True)
    return log_path


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


def _build_update_current_season_command(args: argparse.Namespace, season: str) -> list[str]:
    """Translate operator options into the existing one-season pipeline command."""

    mode = "artifact-only" if args.run_type == "artifact-only" else "full"
    command = _python_command("update_current_season.py", "--season", season, "--mode", mode)

    if args.run_type == "rebuild-from-existing-raw":
        command.extend(["--skip-scrape", "--skip-raw-load"])
    if not args.apply_migrations:
        command.append("--skip-migrations")
    if args.use_cache:
        command.append("--use-cache")
    if args.force_full_scrape:
        command.append("--disable-postgres-change-detection")
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
            _run_step("apply_db_migrations", _python_command("apply_db_migrations.py"), log_dir)
        )
    else:
        print("\n[hosted-update] Skipping migrations.")

    step_logs["build_staging_from_raw"] = _display_path(
        _run_step("build_staging_from_raw", _python_command("build_staging_from_raw.py"), log_dir)
    )
    step_logs["verify_staging_outputs"] = _display_path(
        _run_step("verify_staging_outputs", _python_command("verify_staging_outputs.py"), log_dir)
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
        command = _build_update_current_season_command(args, season)
        step_logs[step_name] = _display_path(_run_step(step_name, command, season_log_dir))


def _write_summary(
    *,
    args: argparse.Namespace,
    seasons: list[str],
    log_dir: Path,
    step_logs: dict[str, str],
    status: str,
    failure: str | None = None,
) -> Path:
    """Write a compact summary for GitHub artifacts and local troubleshooting."""

    log_dir.mkdir(parents=True, exist_ok=True)
    summary_path = log_dir / f"{_timestamp_slug()}_hosted_update_summary.json"
    payload = {
        "status": status,
        "season_scope": args.season_scope,
        "run_type": args.run_type,
        "seasons": seasons,
        "apply_migrations": args.apply_migrations,
        "use_cache": args.use_cache,
        "force_full_scrape": args.force_full_scrape,
        "step_logs": step_logs,
        "failure": failure,
    }
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"\n[hosted-update] Summary artifact: {_display_path(summary_path)}")
    return summary_path


def main() -> None:
    """Run the selected hosted data update."""

    args = parse_args()
    seasons = _resolve_target_seasons(args)
    log_dir = args.log_dir / _scope_slug(args, seasons)
    step_logs: dict[str, str] = {}

    print("UPL Match Intelligence - Hosted Data Update")
    print(f"Season scope: {args.season_scope}")
    print(f"Run type: {args.run_type}")
    print(f"Target seasons: {', '.join(seasons)}")
    print(f"Apply migrations: {args.apply_migrations}")
    print(f"Use cache: {args.use_cache}")
    print(f"Force full scrape: {args.force_full_scrape}")

    try:
        if args.run_type == "rebuild-from-existing-raw" and args.season_scope == "all":
            _run_rebuild_all_from_existing_raw(args=args, log_dir=log_dir, step_logs=step_logs)
        else:
            _run_per_season_pipeline(args=args, seasons=seasons, log_dir=log_dir, step_logs=step_logs)
    except HostedUpdateStepError as error:
        _write_summary(
            args=args,
            seasons=seasons,
            log_dir=log_dir,
            step_logs=step_logs,
            status="failed",
            failure=str(error),
        )
        raise SystemExit(error.exit_code) from error

    _write_summary(
        args=args,
        seasons=seasons,
        log_dir=log_dir,
        step_logs=step_logs,
        status="success",
    )
    print("\n[ok] Hosted data update finished.")


if __name__ == "__main__":
    main()
