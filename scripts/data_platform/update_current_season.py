"""Run the Phase 5 current-season update pipeline.

This script is the small conductor for the automation phase. It reuses the
existing scraper, Postgres loader, staging builder, and verification scripts
instead of creating a second version of the data pipeline.

Usage examples
--------------
python scripts/data_platform/update_current_season.py
python scripts/data_platform/update_current_season.py --season 2025-26
python scripts/data_platform/update_current_season.py --mode artifact-only
python scripts/data_platform/update_current_season.py --skip-scrape
python scripts/data_platform/update_current_season.py --use-cache
python scripts/data_platform/update_current_season.py --skip-migrations
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    CURRENT_SEASON,
    raw_season_dir,
    raw_season_failed_matches_file,
    season_key,
)


SCRIPT_DIR = PROJECT_ROOT / "scripts" / "data_platform"
DEFAULT_LOG_DIR = PROJECT_ROOT / "outputs" / "automation"


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
            "By default, Phase 5 refreshes from the live source."
        ),
    )
    parser.add_argument(
        "--skip-raw-verification",
        action="store_true",
        help="Skip the raw CSV versus Postgres count check.",
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

    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _run_step(step_name: str, command: list[str], log_dir: Path) -> None:
    """Run one pipeline step, stream output, and save a log file.

    The log file matters in automation because GitHub Actions output can be
    noisy. A separate file makes failed scrapes or validation errors easier to
    download and inspect after the run.
    """

    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{_timestamp_slug()}_{step_name}.log"

    print(f"\n[phase5] Starting {step_name}")
    print(f"[phase5] Command: {' '.join(command)}")
    print(f"[phase5] Log: {log_path.relative_to(PROJECT_ROOT)}")

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
            print(line, end="")
            log_file.write(line)

    if process.wait() != 0:
        raise SystemExit(
            f"\n[error] Phase 5 step failed: {step_name}. Review {log_path}."
        )

    print(f"[phase5] Finished {step_name}")


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


def _print_failed_match_summary(season: str, *, max_rows: int = 10) -> int:
    """Print the data-completeness state for the current season update."""

    failed_matches = _read_failed_matches(season)
    failed_count = len(failed_matches)

    print("\n[phase5] Data completeness summary")
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
            print(f"    attempts={attempt_count or 'unknown'} last_error={last_error or 'unknown'}")

    if failed_count > max_rows:
        print(f"  ... and {failed_count - max_rows} more")

    return failed_count


def _enforce_failed_match_policy(failed_count: int, *, fail_on_remaining: bool) -> None:
    """Fail the job only when the caller requested strict completeness."""

    if failed_count and fail_on_remaining:
        raise SystemExit(
            "\n[error] Current-season update finished with remaining failed matches."
        )


def main() -> None:
    """Run the selected current-season update pipeline."""

    args = parse_args()
    season = args.season
    normalized_season = season_key(season)
    log_dir = args.log_dir / normalized_season

    print("UPL Match Intelligence - Phase 5 Current Season Update")
    print(f"Season: {season}")
    print(f"Mode: {args.mode}")
    print(f"Raw season folder: {raw_season_dir(season).relative_to(PROJECT_ROOT)}")

    if not args.skip_scrape:
        scrape_command = _python_command("scrape_upl_matches.py", "--season", season)
        if not args.use_cache:
            scrape_command.append("--refresh-source")

        _run_step(
            "scrape_current_season",
            scrape_command,
            log_dir,
        )
    else:
        print("\n[phase5] Skipping scraper and reusing existing raw season files.")

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
            "\n[phase5] Skipping database migrations. "
            "This is expected for routine least-privilege update runs."
        )
    else:
        _run_step("apply_db_migrations", _python_command("apply_db_migrations.py"), log_dir)

    _run_step(
        "load_raw_to_postgres",
        _python_command("load_raw_to_postgres.py", "--season", season),
        log_dir,
    )

    if not args.skip_raw_verification:
        _run_step(
            "verify_raw_postgres_counts",
            _python_command("verify_raw_postgres_counts.py", "--season", season),
            log_dir,
        )

    _run_step(
        "build_staging_from_raw",
        _python_command("build_staging_from_raw.py", "--season", season),
        log_dir,
    )

    if not args.skip_staging_verification:
        _run_step(
            "verify_staging_outputs",
            _python_command("verify_staging_outputs.py", "--season", season),
            log_dir,
        )

    failed_count = _print_failed_match_summary(season)
    _enforce_failed_match_policy(
        failed_count,
        fail_on_remaining=args.fail_on_remaining_failed_matches,
    )

    print("\n[ok] Full current-season update finished.")
    print("[ok] The scraper, raw Postgres load, staging rebuild, and checks completed.")


if __name__ == "__main__":
    main()
