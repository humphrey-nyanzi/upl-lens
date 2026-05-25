"""Shared subprocess runner for operational data-platform scripts.

GitHub Actions and local update scripts both need the same behavior: print the
command, stream output live, save a downloadable log, and raise a structured
error with the failed step name. Keeping that machinery here prevents the local
and hosted workflows from drifting as the operations layer grows.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeVar


StepErrorT = TypeVar("StepErrorT", bound=Exception)


def timestamp_slug() -> str:
    """Return a compact UTC timestamp suitable for log filenames."""

    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def display_path(path: Path, root: Path) -> str:
    """Return a readable path, preferring paths relative to the project root."""

    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def run_logged_step(
    *,
    step_name: str,
    command: list[str],
    log_dir: Path,
    project_root: Path,
    log_prefix: str,
    error_type: type[StepErrorT],
) -> Path:
    """Run one subprocess, stream output, write a log, and raise on failure.

    Parameters
    ----------
    step_name : str
        Human-readable stage name used in logs and failure summaries.
    command : list[str]
        Subprocess command as an argument list. Passing a list avoids shell
        quoting surprises in local Windows runs and hosted Linux runs.
    log_dir : Path
        Directory where the per-step log should be written.
    project_root : Path
        Working directory for the subprocess and root used for readable paths.
    log_prefix : str
        Prefix printed in console logs, such as ``[operations]``.
    error_type : type[Exception]
        Exception class constructed as ``error_type(step_name, log_path, code)``.

    Returns
    -------
    Path
        Path to the completed step log.
    """

    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{timestamp_slug()}_{step_name}.log"

    print(f"\n{log_prefix} Starting {step_name}", flush=True)
    print(f"{log_prefix} Command: {' '.join(command)}", flush=True)
    print(f"{log_prefix} Log: {display_path(log_path, project_root)}", flush=True)

    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write(f"Step: {step_name}\n")
        log_file.write(f"Command: {' '.join(command)}\n\n")
        process = subprocess.Popen(
            command,
            cwd=project_root,
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
        raise error_type(step_name, log_path, exit_code)

    print(f"{log_prefix} Finished {step_name}", flush=True)
    return log_path
