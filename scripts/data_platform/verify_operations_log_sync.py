"""Compare hosted GitHub Actions operations output with local operations output.

This script does not need hosted database credentials. It treats GitHub Actions
logs as the hosted evidence, then compares them with the local operations run
summary under `outputs/automation/<season>/`.

Usage examples
--------------
python scripts/data_platform/verify_operations_log_sync.py --season 2025-26 --hosted-log hosted.log
python scripts/data_platform/verify_operations_log_sync.py --season 2025-26 --latest-github-run
python scripts/data_platform/verify_operations_log_sync.py --season 2025-26 --latest-github-run --run-local-update
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RAW_TABLE_FILE_PREFIXES, season_key


DEFAULT_LOG_DIR = PROJECT_ROOT / "outputs" / "automation"
DEFAULT_REPORT_DIR = PROJECT_ROOT / "outputs" / "sync"
DEFAULT_GITHUB_REPO = "humphrey-nyanzi/UPL-goal-timing"
DEFAULT_WORKFLOW = "current-season-update.yml"
RAW_TABLES = (*RAW_TABLE_FILE_PREFIXES.keys(), "failed_matches")

TIMESTAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T[^\s]+\s+")
KEY_VALUE_PATTERN = re.compile(r"^\s*(?P<key>[A-Za-z ]+):\s+(?P<value>.+?)\s*$")
TABLE_COUNT_PATTERN = re.compile(
    r"^\s*(?P<table>[a-z_]+)\s+(?P<count>\d+|missing)\s*$"
)
STAGING_VERIFY_COUNT_PATTERN = re.compile(
    r"^\s*staging\.(?P<table>[a-z_]+)\s+(?P<season>\d{4}_\d{2}):\s+(?P<count>\d+)\s*$"
)
VALIDATION_ISSUE_PATTERN = re.compile(
    r"^\s*(?P<severity>info|warning|error|fatal)\s+.+?\s+(?P<count>\d+)\s*$"
)


@dataclass(frozen=True)
class OperationsEvidence:
    """Comparable evidence extracted from one operations run."""

    source: str
    season: str | None
    mode: str | None
    source_refresh: str | None
    migrations: str | None
    raw_verification: str | None
    staging_rebuild: str | None
    staging_verification: str | None
    remaining_failed_matches: int | None
    raw_csv_rows: dict[str, int | None]
    raw_loader_rows: dict[str, int]
    staging_rows: dict[str, int]
    validation_issue_counts: dict[str, int]
    summary_path: str | None = None
    run_id: str | None = None


def parse_args() -> argparse.Namespace:
    """Parse command-line options for log-based sync verification."""

    parser = argparse.ArgumentParser(
        description=(
            "Compare GitHub Actions hosted operations evidence with local "
            "operations evidence, without hosted database credentials."
        )
    )
    parser.add_argument("--season", required=True, help="Season to compare, for example 2025-26.")
    parser.add_argument(
        "--hosted-log",
        type=Path,
        help="Path to a saved GitHub Actions job log for the hosted run.",
    )
    parser.add_argument(
        "--latest-github-run",
        action="store_true",
        help="Use gh CLI to fetch the latest successful GitHub Actions run for the season.",
    )
    parser.add_argument(
        "--github-repo",
        default=DEFAULT_GITHUB_REPO,
        help=f"GitHub repository used with gh CLI. Defaults to {DEFAULT_GITHUB_REPO}.",
    )
    parser.add_argument(
        "--workflow",
        default=DEFAULT_WORKFLOW,
        help=f"Workflow file/name used with gh CLI. Defaults to {DEFAULT_WORKFLOW}.",
    )
    parser.add_argument(
        "--local-summary",
        type=Path,
        help="Path to a local *_run_summary.json file. Defaults to the latest success summary for the season.",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=DEFAULT_LOG_DIR,
        help="Local automation log root. Defaults to outputs/automation.",
    )
    parser.add_argument(
        "--run-local-update",
        action="store_true",
        help="Run the local update first, then compare the newly produced local summary.",
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="When --run-local-update is used, allow cached scraper HTML/checkpoints locally.",
    )
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="When --run-local-update is used, reuse existing local raw files.",
    )
    parser.add_argument(
        "--skip-raw-load",
        action="store_true",
        help="When --run-local-update is used, reuse existing local raw database rows.",
    )
    parser.add_argument(
        "--strict-artifacts",
        action="store_true",
        help="Treat raw CSV artifact row-count differences as out-of-sync instead of warnings.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional report path. Defaults to outputs/sync/<timestamp>_<season>_sync_report.json.",
    )
    return parser.parse_args()


def _timestamp_slug() -> str:
    """Return a compact UTC timestamp for report filenames."""

    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _strip_log_prefix(line: str) -> str:
    """Remove GitHub's timestamp prefix from one log line."""

    match = TIMESTAMP_PATTERN.search(line)
    if match:
        return line[match.end():].strip("\n")
    return line.strip("\n")


def _normalize_status(value: str | None) -> str | None:
    """Normalize equivalent status wording across JSON summaries and job logs."""

    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered == "completed":
        return "completed"
    if "passed without error-level validation issues" in lowered:
        return "passed"
    if "without error-level validation issues" in lowered:
        return "passed"
    return lowered


def _parse_int(value: str | None) -> int | None:
    """Parse an integer from optional text."""

    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _parse_table_count_line(line: str) -> tuple[str, int | None] | None:
    """Parse a compact table-count line from a summary block."""

    match = TABLE_COUNT_PATTERN.match(line)
    if not match:
        return None
    table_name = match.group("table")
    if table_name not in RAW_TABLES:
        return None
    count_text = match.group("count")
    return table_name, None if count_text == "missing" else int(count_text)


def _parse_github_log(text: str, *, source: str, run_id: str | None = None) -> OperationsEvidence:
    """Extract comparable operations evidence from GitHub Actions job logs."""

    summary_values: dict[str, str] = {}
    raw_csv_rows: dict[str, int | None] = {}
    raw_loader_rows: dict[str, int] = {}
    staging_rows: dict[str, int] = {}
    validation_issue_counts: dict[str, int] = {}
    active_block: str | None = None

    for original_line in text.splitlines():
        line = _strip_log_prefix(original_line)

        if "Raw CSV rows prepared for artifacts:" in line:
            active_block = "raw_csv"
            continue
        if "Raw rows processed by Postgres loader:" in line:
            active_block = "raw_loader"
            continue
        if "Staging rows written:" in line or "Staging row counts:" in line:
            active_block = "staging"
            continue
        if "Validation summary for run_id=" in line:
            active_block = "validation"
            continue
        if line.startswith("Step logs:") or line.startswith("[operations] Run summary"):
            active_block = None
            continue

        key_value_match = KEY_VALUE_PATTERN.match(line)
        if key_value_match:
            key = key_value_match.group("key").strip().lower().replace(" ", "_")
            summary_values[key] = key_value_match.group("value").strip()

        if active_block in {"raw_csv", "raw_loader"}:
            table_count = _parse_table_count_line(line)
            if table_count is None:
                continue
            table_name, row_count = table_count
            if active_block == "raw_csv":
                raw_csv_rows[table_name] = row_count
            elif row_count is not None:
                raw_loader_rows[table_name] = row_count
            continue

        if active_block == "staging":
            table_count = _parse_table_count_line(line)
            if table_count is not None:
                table_name, row_count = table_count
                if row_count is not None:
                    staging_rows[table_name] = row_count
                continue
            staging_match = STAGING_VERIFY_COUNT_PATTERN.match(line)
            if staging_match:
                staging_rows[staging_match.group("table")] = int(staging_match.group("count"))
            continue

        if active_block == "validation":
            issue_match = VALIDATION_ISSUE_PATTERN.match(line)
            if issue_match:
                severity = issue_match.group("severity")
                validation_issue_counts[severity] = (
                    validation_issue_counts.get(severity, 0)
                    + int(issue_match.group("count"))
                )

    return OperationsEvidence(
        source=source,
        season=summary_values.get("season"),
        mode=summary_values.get("mode"),
        source_refresh=summary_values.get("source"),
        migrations=summary_values.get("migrations"),
        raw_verification=summary_values.get("raw_verification"),
        staging_rebuild=summary_values.get("staging_rebuild"),
        staging_verification=summary_values.get("staging_verification"),
        remaining_failed_matches=_parse_int(summary_values.get("remaining_failed_matches")),
        raw_csv_rows=raw_csv_rows,
        raw_loader_rows=raw_loader_rows,
        staging_rows=staging_rows,
        validation_issue_counts=validation_issue_counts,
        run_id=run_id,
    )


def _evidence_from_local_summary(summary_path: Path) -> OperationsEvidence:
    """Load comparable evidence from a local operations JSON summary."""

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    return OperationsEvidence(
        source="local",
        season=payload.get("season"),
        mode=payload.get("mode"),
        source_refresh=payload.get("source"),
        migrations=payload.get("migrations"),
        raw_verification=payload.get("raw_verification"),
        staging_rebuild=payload.get("staging_rebuild"),
        staging_verification=payload.get("staging_verification"),
        remaining_failed_matches=payload.get("remaining_failed_matches"),
        raw_csv_rows=payload.get("raw_csv_rows", {}),
        raw_loader_rows=payload.get("raw_loader_rows", {}),
        staging_rows=payload.get("staging_rows", {}),
        validation_issue_counts={},
        summary_path=str(summary_path),
    )


def _latest_local_summary(season: str, log_dir: Path) -> Path:
    """Return the latest successful local run summary for one season."""

    season_dir = log_dir / season_key(season)
    summaries = sorted(
        path
        for path in season_dir.glob("*_run_summary.json")
        if not path.name.endswith("_run_summary_failed.json")
    )
    if not summaries:
        raise FileNotFoundError(
            f"No local success summary found under {season_dir}. "
            "Run update_current_season.py locally first, or pass --run-local-update."
        )
    return summaries[-1]


def _run_local_update(args: argparse.Namespace) -> None:
    """Run the local current-season update so local evidence is fresh."""

    command = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "data_platform" / "update_current_season.py"),
        "--season",
        args.season,
        "--skip-migrations",
    ]
    if args.use_cache:
        command.append("--use-cache")
    if args.skip_scrape:
        command.append("--skip-scrape")
    if args.skip_raw_load:
        command.append("--skip-raw-load")

    print(f"[sync] Running local update: {' '.join(command)}")
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def _run_gh_json(command: list[str]) -> Any:
    """Run gh CLI and parse JSON output."""

    try:
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        raise RuntimeError("GitHub CLI is not installed or not on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "GitHub CLI command failed. Run `gh auth login` if needed, then retry. "
            f"stderr: {exc.stderr.strip()}"
        ) from exc
    return json.loads(completed.stdout)


def _latest_successful_github_run_id(
    *,
    repo: str,
    workflow: str,
    season: str,
) -> str:
    """Return the latest successful GitHub Actions run id that mentions a season."""

    runs = _run_gh_json(
        [
            "gh",
            "run",
            "list",
            "--repo",
            repo,
            "--workflow",
            workflow,
            "--limit",
            "50",
            "--json",
            "databaseId,conclusion,status,createdAt,displayTitle,event",
        ]
    )
    for run in runs:
        if run.get("status") != "completed" or run.get("conclusion") != "success":
            continue
        run_id = str(run["databaseId"])
        log_text = _github_run_log(repo=repo, run_id=run_id)
        if f"UPDATE_SEASON: {season}" in log_text or f"Season: {season}" in log_text:
            return run_id
    raise RuntimeError(f"No successful GitHub Actions run found for season {season}.")


def _github_run_log(*, repo: str, run_id: str) -> str:
    """Return GitHub Actions run log text through gh CLI."""

    try:
        completed = subprocess.run(
            ["gh", "run", "view", run_id, "--repo", repo, "--log"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        raise RuntimeError("GitHub CLI is not installed or not on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Could not read GitHub Actions logs. Run `gh auth login` if needed, "
            f"then retry. stderr: {exc.stderr.strip()}"
        ) from exc
    return completed.stdout


def _compare_counts(
    *,
    name: str,
    hosted: dict[str, int | None],
    local: dict[str, int | None],
) -> list[str]:
    """Return mismatch messages for table-count dictionaries."""

    mismatches: list[str] = []
    for table_name in sorted(set(hosted) | set(local)):
        hosted_count = hosted.get(table_name)
        local_count = local.get(table_name)
        if hosted_count != local_count:
            mismatches.append(
                f"{name}.{table_name}: hosted={hosted_count}, local={local_count}"
            )
    return mismatches


def _comparison_payload(
    hosted: OperationsEvidence,
    local: OperationsEvidence,
    *,
    strict_artifacts: bool = False,
) -> dict[str, Any]:
    """Return a sync report comparing hosted and local operations evidence."""

    mismatches: list[str] = []
    warnings: list[str] = []

    scalar_fields = (
        ("season", hosted.season, local.season),
        ("mode", hosted.mode, local.mode),
        (
            "raw_verification",
            _normalize_status(hosted.raw_verification),
            _normalize_status(local.raw_verification),
        ),
        (
            "staging_rebuild",
            _normalize_status(hosted.staging_rebuild),
            _normalize_status(local.staging_rebuild),
        ),
        (
            "staging_verification",
            _normalize_status(hosted.staging_verification),
            _normalize_status(local.staging_verification),
        ),
        (
            "remaining_failed_matches",
            hosted.remaining_failed_matches,
            local.remaining_failed_matches,
        ),
    )
    for field_name, hosted_value, local_value in scalar_fields:
        if hosted_value != local_value:
            mismatches.append(
                f"{field_name}: hosted={hosted_value}, local={local_value}"
            )

    mismatches.extend(
        _compare_counts(
            name="raw_loader_rows",
            hosted=hosted.raw_loader_rows,
            local=local.raw_loader_rows,
        )
    )
    mismatches.extend(
        _compare_counts(
            name="staging_rows",
            hosted=hosted.staging_rows,
            local=local.staging_rows,
        )
    )

    raw_csv_drift = _compare_counts(
        name="raw_csv_rows",
        hosted=hosted.raw_csv_rows,
        local=local.raw_csv_rows,
    )
    if strict_artifacts:
        mismatches.extend(raw_csv_drift)
    else:
        warnings.extend(raw_csv_drift)

    status = "in_sync"
    if mismatches:
        status = "out_of_sync"
    elif warnings:
        status = "warning"

    return {
        "status": status,
        "mismatch_count": len(mismatches),
        "warning_count": len(warnings),
        "mismatches": mismatches,
        "warnings": warnings,
        "hosted": asdict(hosted),
        "local": asdict(local),
    }


def _print_report(payload: dict[str, Any]) -> None:
    """Print a concise sync report."""

    print("\nUPL Match Intelligence - Hosted/Local Operations Sync")
    print(f"Status: {payload['status']}")
    print(f"Mismatches: {payload['mismatch_count']}")
    print(f"Warnings: {payload['warning_count']}")

    if payload["mismatches"]:
        print("\nMismatches:")
        for mismatch in payload["mismatches"]:
            print(f"  - {mismatch}")

    if payload["warnings"]:
        print("\nWarnings:")
        for warning in payload["warnings"]:
            print(f"  - {warning}")

    if payload["status"] == "in_sync":
        print("\n[ok] Hosted and local operations evidence match.")
    elif payload["status"] == "warning":
        print("\n[warning] Core loaded/staging data matches, but raw artifacts differ.")
    else:
        print("\n[error] Hosted and local operations evidence are out of sync.")


def main() -> None:
    """Run hosted/local operations sync verification."""

    args = parse_args()
    hosted_sources = [args.hosted_log is not None, args.latest_github_run]
    if sum(hosted_sources) != 1:
        raise SystemExit("Choose exactly one hosted source: --hosted-log or --latest-github-run.")

    if args.run_local_update:
        _run_local_update(args)

    local_summary_path = args.local_summary or _latest_local_summary(args.season, args.log_dir)
    local_evidence = _evidence_from_local_summary(local_summary_path)

    if args.hosted_log:
        hosted_log_text = args.hosted_log.read_text(encoding="utf-8", errors="replace")
        hosted_evidence = _parse_github_log(
            hosted_log_text,
            source=f"hosted-log:{args.hosted_log}",
        )
    else:
        run_id = _latest_successful_github_run_id(
            repo=args.github_repo,
            workflow=args.workflow,
            season=args.season,
        )
        hosted_log_text = _github_run_log(repo=args.github_repo, run_id=run_id)
        hosted_evidence = _parse_github_log(
            hosted_log_text,
            source=f"github:{args.github_repo}",
            run_id=run_id,
        )

    payload = _comparison_payload(
        hosted_evidence,
        local_evidence,
        strict_artifacts=args.strict_artifacts,
    )
    _print_report(payload)

    report_path = args.json_output
    if report_path is None:
        report_path = (
            DEFAULT_REPORT_DIR
            / f"{_timestamp_slug()}_{season_key(args.season)}_operations_sync.json"
        )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"\n[sync] Report written to: {report_path}")

    if payload["mismatches"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
