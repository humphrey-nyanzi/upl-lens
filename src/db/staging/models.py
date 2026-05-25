"""Shared staging pipeline data types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


ProgressCallback = Callable[[str], None]


@dataclass(frozen=True)
class StagingBuildResult:
    """Summary returned after rebuilding staging tables."""

    run_id: str
    seasons: list[str]
    row_counts: dict[str, int]
    issue_counts: dict[str, int]


@dataclass(frozen=True)
class StagingValidationError(Exception):
    """Raised after validation evidence is recorded for an unsafe staging build."""

    run_id: str
    seasons: list[str]
    issue_counts: dict[str, int]

    def __str__(self) -> str:
        return (
            "Staging validation found error-level issues before table writes. "
            f"Run ID: {self.run_id}."
        )
