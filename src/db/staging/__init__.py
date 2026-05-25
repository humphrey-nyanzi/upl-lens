"""Staging rebuild package for raw-to-application Postgres modeling.

The package keeps the public staging pipeline split by responsibility:
normalization, raw reads, transformations, validation, database writes,
analytics refreshes, and orchestration. The older `src.db.staging_loader`
module re-exports these names for compatibility with existing scripts/tests.
"""

from src.db.staging.models import StagingBuildResult, StagingValidationError
from src.db.staging.pipeline import build_staging_from_raw

__all__ = [
    "StagingBuildResult",
    "StagingValidationError",
    "build_staging_from_raw",
]
