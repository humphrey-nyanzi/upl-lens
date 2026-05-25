"""Top-level orchestration for rebuilding staging from raw Postgres tables."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.db.connection import create_sqlalchemy_engine
from src.db.raw_loader import resolve_seasons
from src.db.settings import DatabaseSettings
from src.db.staging.analytics import _refresh_team_season_summary
from src.db.staging.constants import STAGING_INSERT_ORDER
from src.db.staging.io import _discover_raw_database_seasons, _read_raw_tables
from src.db.staging.models import ProgressCallback, StagingBuildResult, StagingValidationError
from src.db.staging.transforms import _build_staging_tables
from src.db.staging.validation import _has_error_level_issues, _validate_staging_tables
from src.db.staging.writers import (
    _configure_staging_session,
    _delete_staging_season_rows,
    _write_staging_tables,
    _write_validation_issues,
    _write_validation_run,
)


def build_staging_from_raw(
    seasons: list[str] | None = None,
    settings: DatabaseSettings | None = None,
    progress: ProgressCallback | None = None,
) -> StagingBuildResult:
    """Rebuild Phase 2 staging tables from Postgres raw tables.

    Parameters
    ----------
    seasons : list[str] | None, optional
        Season keys to rebuild. If omitted, the pipeline uses all discovered
        raw season folders.
    settings : DatabaseSettings | None, optional
        Preloaded database settings.
    progress : Callable[[str], None] | None, optional
        Callback used by scripts and automation to expose long-running rebuild
        stages in logs.

    Returns
    -------
    StagingBuildResult
        Rebuild run ID, row counts, and validation issue counts.
    """

    run_id = f"staging-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    if progress:
        progress(f"Created staging run_id={run_id}")
        progress("Creating SQLAlchemy engine")
    engine = create_sqlalchemy_engine(settings=settings)
    validation_error: StagingValidationError | None = None

    with engine.begin() as connection:
        _configure_staging_session(connection, progress)
        if progress:
            progress("Resolving target seasons")
        season_names = resolve_seasons(seasons) if seasons else _discover_raw_database_seasons(connection)
        if progress:
            progress(f"Target seasons: {', '.join(season_names)}")
        raw_tables = _read_raw_tables(connection, season_names, progress)
        if progress:
            progress("Transforming raw tables into staging tables")
        staging_tables = _build_staging_tables(raw_tables)
        if progress:
            for table_name, table_df in staging_tables.items():
                progress(f"Prepared staging.{table_name}: {len(table_df)} rows")
            progress("Running staging validation checks")
        validation_issues = _validate_staging_tables(raw_tables, staging_tables, season_names, run_id)
        if progress:
            progress(f"Prepared validation issues: {len(validation_issues)} rows")

        if _has_error_level_issues(validation_issues):
            if progress:
                progress("Validation found error-level issues; recording evidence before staging writes")
            row_counts = {table_name: 0 for table_name in STAGING_INSERT_ORDER}
            issue_counts = _write_validation_issues(connection, validation_issues, progress)
            _write_validation_run(connection, run_id, season_names, row_counts, issue_counts, progress)
            validation_error = StagingValidationError(
                run_id=run_id,
                seasons=season_names,
                issue_counts=issue_counts,
            )
            if progress:
                progress("Skipping staging table writes because validation errors were recorded")
        else:
            _delete_staging_season_rows(connection, season_names, progress)
            row_counts = _write_staging_tables(connection, staging_tables, progress)
            _refresh_team_season_summary(connection, season_names, progress)
            issue_counts = _write_validation_issues(connection, validation_issues, progress)
            _write_validation_run(connection, run_id, season_names, row_counts, issue_counts, progress)

    if progress:
        progress("Disposing SQLAlchemy engine")
    engine.dispose()

    if validation_error is not None:
        raise validation_error

    return StagingBuildResult(
        run_id=run_id,
        seasons=season_names,
        row_counts=row_counts,
        issue_counts=issue_counts,
    )
