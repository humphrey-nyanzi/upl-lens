"""Compatibility facade for the staging rebuild package.

The implementation now lives under `src.db.staging` so each stage of the raw to
staging workflow has a focused module. Existing scripts and tests can continue
importing from `src.db.staging_loader` while newer code imports from the
package modules directly.
"""

from __future__ import annotations

from src.db.staging.analytics import _refresh_team_season_summary
from src.db.staging.constants import (
    RAW_REQUIRED_COLUMNS,
    RAW_TABLES,
    STAGING_COLUMNS,
    STAGING_INSERT_ORDER,
    STAGING_RELOAD_ORDER,
)
from src.db.staging.io import _discover_raw_database_seasons, _read_raw_table, _read_raw_tables
from src.db.staging.models import ProgressCallback, StagingBuildResult, StagingValidationError
from src.db.staging.normalization import (
    _clean_person_name,
    _clean_text,
    _extract_man_of_match,
    _is_forfeit_text,
    _minute_period,
    _normalize_goal_type,
    _normalize_person,
    _normalize_team,
    _parse_dates,
    _parse_minute,
    _season_date_anomaly_reason,
    _season_date_window,
    _season_key_series,
    _standardize_label,
    _team_from_side,
    _team_matches_match,
)
from src.db.staging.pipeline import build_staging_from_raw
from src.db.staging.transforms import (
    _build_staging_tables,
    _clean_event_rows,
    _clean_match_rows,
    _clean_official_rows,
    _clean_stat_rows,
    _clean_team_person_table,
)
from src.db.staging.validation import (
    _has_error_level_issues,
    _issue,
    _validate_duplicates,
    _validate_fixture_completeness,
    _validate_key_fields,
    _validate_man_of_match_quality,
    _validate_missing_team_player_values,
    _validate_raw_season_consistency,
    _validate_required_columns,
    _validate_scoreline_timeline_goal_consistency,
    _validate_staging_tables,
)
from src.db.staging.writers import (
    _configure_staging_session,
    _delete_staging_season_rows,
    _write_staging_tables,
    _write_validation_issues,
    _write_validation_run,
)
