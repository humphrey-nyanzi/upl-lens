"""Validation checks for staging rebuild safety and data caveats.

The validation layer records evidence before risky writes. Error-level issues
block staging inserts; warnings and info rows preserve caveats for later review.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src import config
from src.db.staging.constants import RAW_REQUIRED_COLUMNS
from src.db.staging.normalization import _clean_text, _season_key_series


def _issue(
    run_id: str,
    severity: str,
    check_name: str,
    schema_name: str,
    table_name: str,
    issue_message: str,
    season: Any = None,
    match_id: Any = None,
    row_key: Any = None,
    column_name: str | None = None,
    issue_value: Any = None,
) -> dict[str, Any]:
    """Create one validation issue row."""

    return {
        "run_id": run_id,
        "severity": severity,
        "check_name": check_name,
        "schema_name": schema_name,
        "table_name": table_name,
        "season": _clean_text(season),
        "match_id": int(match_id) if pd.notna(match_id) else None,
        "row_key": _clean_text(row_key),
        "column_name": column_name,
        "issue_message": issue_message,
        "issue_value": _clean_text(issue_value),
    }


def _validate_required_columns(raw_tables: dict[str, pd.DataFrame], run_id: str) -> list[dict[str, Any]]:
    """Check that expected raw columns are available before transformation."""

    issues: list[dict[str, Any]] = []
    for table_name, required_columns in RAW_REQUIRED_COLUMNS.items():
        missing_columns = sorted(required_columns.difference(raw_tables[table_name].columns))
        for column_name in missing_columns:
            issues.append(
                _issue(
                    run_id=run_id,
                    severity="error",
                    check_name="required_columns",
                    schema_name="raw",
                    table_name=table_name,
                    column_name=column_name,
                    issue_message="Required raw column is missing.",
                )
            )
    return issues


def _validate_raw_season_consistency(
    raw_tables: dict[str, pd.DataFrame],
    seasons: list[str],
    run_id: str,
) -> list[dict[str, Any]]:
    """Confirm raw season values match the requested season slice."""

    expected_seasons = set(seasons)
    issues: list[dict[str, Any]] = []
    for table_name, df in raw_tables.items():
        if df.empty or "season" not in df.columns:
            continue
        normalized = _season_key_series(df["season"])
        bad_rows = df.loc[~normalized.isin(expected_seasons)]
        for _, row in bad_rows.head(200).iterrows():
            issues.append(
                _issue(
                    run_id=run_id,
                    severity="error",
                    check_name="season_consistency",
                    schema_name="raw",
                    table_name=table_name,
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get(f"{table_name[:-1]}_row_key"),
                    column_name="season",
                    issue_message="Raw row season does not match the requested staging season slice.",
                    issue_value=row.get("season"),
                )
            )
    return issues


def _validate_duplicates(staging_tables: dict[str, pd.DataFrame], run_id: str) -> list[dict[str, Any]]:
    """Log duplicate risks in natural keys used for staging tables."""

    duplicate_rules = {
        "matches": ["match_id"],
        "events": ["match_id", "event_index"],
        "lineups": ["lineup_row_key"],
        "staff": ["staff_row_key"],
        "officials": ["official_row_key"],
        "stats": ["match_id", "statistic_name"],
    }
    issues: list[dict[str, Any]] = []
    for table_name, key_columns in duplicate_rules.items():
        df = staging_tables[table_name]
        if df.empty:
            continue
        duplicate_rows = df.loc[df.duplicated(subset=key_columns, keep=False)]
        for _, row in duplicate_rows.head(200).iterrows():
            issues.append(
                _issue(
                    run_id=run_id,
                    severity="error",
                    check_name="duplicate_risk",
                    schema_name="staging",
                    table_name=table_name,
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get(f"{table_name[:-1]}_row_key"),
                    issue_message=f"Duplicate natural key risk on columns: {', '.join(key_columns)}.",
                    issue_value=" | ".join(str(row.get(column)) for column in key_columns),
                )
            )
    return issues


def _validate_key_fields(staging_tables: dict[str, pd.DataFrame], run_id: str) -> list[dict[str, Any]]:
    """Validate core IDs, match references, dates, sides, and minute parsing."""

    issues: list[dict[str, Any]] = []
    matches = staging_tables["matches"]
    match_ids = set(matches["match_id"].dropna().astype(int)) if not matches.empty else set()

    if not matches.empty:
        for column_name in ("match_id", "match_url", "season"):
            missing_rows = matches.loc[matches[column_name].isna()]
            for _, row in missing_rows.head(200).iterrows():
                issues.append(
                    _issue(
                        run_id,
                        "error",
                        "key_field_quality",
                        "staging",
                        "matches",
                        f"Required match field `{column_name}` is missing after cleaning.",
                        season=row.get("season"),
                        match_id=row.get("match_id"),
                        column_name=column_name,
                    )
                )
        for column_name in ("home_team", "away_team"):
            missing_rows = matches.loc[matches[column_name].isna()]
            for _, row in missing_rows.head(200).iterrows():
                issues.append(
                    _issue(
                        run_id,
                        "warning",
                        "missing_team_player_values",
                        "staging",
                        "matches",
                        f"Match is missing `{column_name}` after cleaning.",
                        season=row.get("season"),
                        match_id=row.get("match_id"),
                        column_name=column_name,
                    )
                )
        invalid_dates = matches.loc[matches["match_date"].isna()]
        for _, row in invalid_dates.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "key_field_quality",
                    "staging",
                    "matches",
                    "Match date could not be parsed with day-first parsing.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    column_name="match_date",
                    issue_value=row.get("match_date"),
                )
            )
        anomalous_dates = matches.loc[matches["is_source_anomaly"]]
        for _, row in anomalous_dates.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "source_match_anomaly",
                    "staging",
                    "matches",
                    "Match date falls outside the plausible window for its source season.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    column_name="match_date",
                    issue_value=row.get("source_anomaly_reason"),
                )
            )

    for table_name in ("events", "lineups", "staff", "officials", "stats"):
        df = staging_tables[table_name]
        if df.empty:
            continue
        missing_match = df.loc[~df["match_id"].isin(match_ids)]
        for _, row in missing_match.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "error",
                    "key_field_quality",
                    "staging",
                    table_name,
                    "Row references a match_id that is not present in staging.matches.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get(f"{table_name[:-1]}_row_key"),
                    column_name="match_id",
                    issue_value=row.get("match_id"),
                )
            )

    events = staging_tables["events"]
    if not events.empty:
        bad_sides = events.loc[events["team_side"].notna() & ~events["team_side"].isin({config.SIDE_HOME, config.SIDE_AWAY})]
        for _, row in bad_sides.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "key_field_quality",
                    "staging",
                    "events",
                    "Event team_side is not home or away.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get("event_row_key"),
                    column_name="team_side",
                    issue_value=row.get("team_side"),
                )
            )

        missing_minute = events.loc[events["event_minute_text"].isna()]
        for _, row in missing_minute.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "info",
                    "key_field_quality",
                    "staging",
                    "events",
                    "Event minute is blank in the source and is marked unknown.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get("event_row_key"),
                    column_name="event_minute_text",
                )
            )

        failed_minutes = events.loc[events["event_minute_text"].notna() & events["minute_total"].isna()]
        for _, row in failed_minutes.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "key_field_quality",
                    "staging",
                    "events",
                    "Event minute text could not be parsed into a numeric minute.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get("event_row_key"),
                    column_name="event_minute_text",
                    issue_value=row.get("event_minute_text"),
                )
            )

    return issues


def _validate_missing_team_player_values(
    staging_tables: dict[str, pd.DataFrame],
    run_id: str,
) -> list[dict[str, Any]]:
    """Check missing team/player values where they matter for analysis."""

    issues: list[dict[str, Any]] = []
    events = staging_tables["events"]
    if not events.empty:
        player_event_mask = events["event_type"].isin({"goal", "yellow_card", "red_card"})
        player_missing = events.loc[player_event_mask & events["player_name"].isna()]
        for _, row in player_missing.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "missing_team_player_values",
                    "staging",
                    "events",
                    "Goal/card event is missing player_name.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get("event_row_key"),
                    column_name="player_name",
                )
            )
        team_missing = events.loc[events["event_type"].notna() & events["team_name"].isna()]
        for _, row in team_missing.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "missing_team_player_values",
                    "staging",
                    "events",
                    "Event is missing a resolvable team name.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get("event_row_key"),
                    column_name="team_name",
                    issue_value=row.get("team_side"),
                )
            )

    for table_name, person_column in (("lineups", "player_name"), ("staff", "person_name")):
        df = staging_tables[table_name]
        if df.empty:
            continue
        missing_team = df.loc[df["team_name"].isna()]
        for _, row in missing_team.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "missing_team_player_values",
                    "staging",
                    table_name,
                    "Row is missing team_name.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get(f"{table_name[:-1]}_row_key"),
                    column_name="team_name",
                )
            )
        missing_person = df.loc[df[person_column].isna()]
        for _, row in missing_person.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "missing_team_player_values",
                    "staging",
                    table_name,
                    f"Row is missing {person_column}.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get(f"{table_name[:-1]}_row_key"),
                    column_name=person_column,
                )
            )

    officials = staging_tables["officials"]
    if not officials.empty:
        missing_official = officials.loc[officials["official_name"].isna()]
        for _, row in missing_official.head(200).iterrows():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "missing_team_player_values",
                    "staging",
                    "officials",
                    "Official assignment is missing official_name.",
                    season=row.get("season"),
                    match_id=row.get("match_id"),
                    row_key=row.get("official_row_key"),
                    column_name="official_name",
                )
            )

    return issues


def _validate_man_of_match_quality(
    raw_tables: dict[str, pd.DataFrame],
    staging_tables: dict[str, pd.DataFrame],
    run_id: str,
) -> list[dict[str, Any]]:
    """Validate Man of the Match extraction without failing historical rebuilds."""

    issues: list[dict[str, Any]] = []
    matches = staging_tables["matches"]
    if matches.empty:
        return issues

    motm_with_no_team = matches.loc[
        matches["man_of_the_match"].notna() & matches["man_of_the_match_team"].isna()
    ]
    for _, row in motm_with_no_team.head(200).iterrows():
        issues.append(
            _issue(
                run_id,
                "warning",
                "man_of_match_quality",
                "staging",
                "matches",
                "Man of the Match name was kept, but no valid team could be confirmed.",
                season=row.get("season"),
                match_id=row.get("match_id"),
                column_name="man_of_the_match_team",
                issue_value=row.get("man_of_the_match"),
            )
        )

    motm_bad_team = matches.loc[
        matches["man_of_the_match_team"].notna()
        & (matches["man_of_the_match_team"] != matches["home_team"])
        & (matches["man_of_the_match_team"] != matches["away_team"])
    ]
    for _, row in motm_bad_team.head(200).iterrows():
        issues.append(
            _issue(
                run_id,
                "error",
                "man_of_match_quality",
                "staging",
                "matches",
                "Man of the Match team is not one of the two teams in the match.",
                season=row.get("season"),
                match_id=row.get("match_id"),
                column_name="man_of_the_match_team",
                issue_value=row.get("man_of_the_match_team"),
            )
        )

    raw_matches = raw_tables["matches"]
    if raw_matches.empty:
        return issues

    compare_columns = ["match_id", "man_of_the_match"]
    raw_motm = raw_matches.loc[:, compare_columns].rename(columns={"man_of_the_match": "raw_man_of_the_match"})
    motm_compare = raw_motm.merge(
        matches.loc[:, ["match_id", "season", "man_of_the_match"]],
        on="match_id",
        how="left",
    )
    raw_had_text = motm_compare["raw_man_of_the_match"].map(_clean_text).notna()
    staging_missing = motm_compare["man_of_the_match"].isna()
    for _, row in motm_compare.loc[raw_had_text & staging_missing].head(200).iterrows():
        issues.append(
            _issue(
                run_id,
                "info",
                "man_of_match_quality",
                "staging",
                "matches",
                "Raw Man of the Match text was not accepted as a strict player/team award.",
                season=row.get("season"),
                match_id=row.get("match_id"),
                column_name="man_of_the_match",
                issue_value=row.get("raw_man_of_the_match"),
            )
        )

    return issues


def _validate_scoreline_timeline_goal_consistency(
    staging_tables: dict[str, pd.DataFrame],
    run_id: str,
) -> list[dict[str, Any]]:
    """Flag matches where official scoreline goals differ from timeline goals.

    Administrative results and forfeits can make the match score say 3-0 even
    when the match timeline has fewer actual goal events. That is valid source
    behavior, but analytical features should know about it and use timeline
    goals when they mean actual scored goals.
    """

    issues: list[dict[str, Any]] = []
    matches = staging_tables["matches"]
    events = staging_tables["events"]
    if matches.empty:
        return issues

    if events.empty:
        event_goal_counts = pd.DataFrame(columns=["match_id", "timeline_goal_count"])
    else:
        goal_events = events.loc[events["event_type"].isin({"goal", "own_goal", "penalty_goal"})]
        event_goal_counts = (
            goal_events.groupby("match_id")
            .size()
            .reset_index(name="timeline_goal_count")
        )

    compare = matches.loc[
        matches["total_goals"].notna(),
        ["match_id", "season", "home_team", "away_team", "total_goals"],
    ].merge(event_goal_counts, on="match_id", how="left")
    compare["timeline_goal_count"] = compare["timeline_goal_count"].fillna(0).astype(int)
    compare["scoreline_goal_count"] = compare["total_goals"].astype(int)
    mismatches = compare.loc[compare["scoreline_goal_count"] != compare["timeline_goal_count"]]

    for _, row in mismatches.head(200).iterrows():
        issue_value = (
            f"scoreline_goals={row['scoreline_goal_count']}; "
            f"timeline_goals={row['timeline_goal_count']}"
        )
        issues.append(
            _issue(
                run_id,
                "warning",
                "scoreline_timeline_goal_mismatch",
                "staging",
                "matches",
                (
                    "Scoreline goals differ from timeline goal events. "
                    "Treat as a possible forfeit/admin result or source timeline gap; "
                    "use timeline goals for actual-goals analytics."
                ),
                season=row.get("season"),
                match_id=row.get("match_id"),
                column_name="total_goals",
                issue_value=issue_value,
            )
        )

    return issues


def _validate_timeline_coverage(staging_tables: dict[str, pd.DataFrame], run_id: str) -> list[dict[str, Any]]:
    """Warn when a match timeline is missing events implied by scoreline/stats."""

    issues: list[dict[str, Any]] = []
    matches = staging_tables["matches"]
    if matches.empty or "timeline_status" not in matches.columns:
        return issues

    partial_matches = matches.loc[matches["timeline_status"] == "partial"]
    for _, row in partial_matches.head(200).iterrows():
        issue_value = row.get("timeline_note")
        if pd.isna(issue_value):
            issue_value = f"timeline_issue_count={row.get('timeline_issue_count')}"
        issues.append(
            _issue(
                run_id,
                "warning",
                "partial_timeline_coverage",
                "staging",
                "matches",
                (
                    "Parsed timeline does not fully match scoreline/stat evidence. "
                    "Show the timeline as partial and avoid treating it as exhaustive."
                ),
                season=row.get("season"),
                match_id=row.get("match_id"),
                column_name="timeline_status",
                issue_value=issue_value,
            )
        )

    unavailable_matches = matches.loc[
        (matches["timeline_status"] == "unavailable") & matches["scoreline_goal_count"].notna()
    ]
    for _, row in unavailable_matches.head(200).iterrows():
        issues.append(
            _issue(
                run_id,
                "info",
                "timeline_unavailable",
                "staging",
                "matches",
                "No parsed timeline events are available for a match with a recorded scoreline.",
                season=row.get("season"),
                match_id=row.get("match_id"),
                column_name="timeline_status",
                issue_value=row.get("timeline_note"),
            )
        )

    return issues


def _validate_fixture_completeness(
    staging_tables: dict[str, pd.DataFrame],
    run_id: str,
) -> list[dict[str, Any]]:
    """Warn when a near-complete season is missing team fixture rows."""

    issues: list[dict[str, Any]] = []
    matches = staging_tables["matches"]
    if matches.empty:
        return issues

    app_safe_matches = matches.loc[~matches["is_source_anomaly"].fillna(False)].copy()
    if app_safe_matches.empty:
        return issues

    team_rows = pd.concat(
        [
            app_safe_matches.loc[:, ["season", "home_team", "match_id"]].rename(columns={"home_team": "team_name"}),
            app_safe_matches.loc[:, ["season", "away_team", "match_id"]].rename(columns={"away_team": "team_name"}),
        ],
        ignore_index=True,
    ).dropna(subset=["season", "team_name"])

    if team_rows.empty:
        return issues

    for season, season_team_rows in team_rows.groupby("season"):
        team_count = int(season_team_rows["team_name"].nunique())
        if team_count < 2:
            continue

        expected_matches = (team_count - 1) * 2
        expected_season_fixtures = team_count * (team_count - 1)
        recorded_season_fixtures = int(app_safe_matches.loc[app_safe_matches["season"] == season, "match_id"].nunique())

        # Early in an active season, every club is below its final fixture total.
        # Warn only once coverage looks close enough that missing rows are likely
        # scraper/source completeness issues rather than normal season progress.
        if recorded_season_fixtures < int(expected_season_fixtures * 0.9):
            continue

        team_counts = season_team_rows.groupby("team_name")["match_id"].nunique()
        incomplete_teams = team_counts.loc[team_counts < expected_matches]
        for team_name, recorded_matches in incomplete_teams.head(200).items():
            issues.append(
                _issue(
                    run_id,
                    "warning",
                    "fixture_completeness",
                    "staging",
                    "matches",
                    "Team has fewer recorded app-safe fixtures than expected for a double round-robin season.",
                    season=season,
                    column_name="team_name",
                    issue_value=(
                        f"team={team_name}; recorded={int(recorded_matches)}; "
                        f"expected={expected_matches}; season_fixtures={recorded_season_fixtures}/{expected_season_fixtures}"
                    ),
                )
            )

    return issues


def _validate_staging_tables(
    raw_tables: dict[str, pd.DataFrame],
    staging_tables: dict[str, pd.DataFrame],
    seasons: list[str],
    run_id: str,
) -> pd.DataFrame:
    """Run Phase 2 validation checks and return issue rows."""

    issues: list[dict[str, Any]] = []
    issues.extend(_validate_required_columns(raw_tables, run_id))
    issues.extend(_validate_raw_season_consistency(raw_tables, seasons, run_id))
    issues.extend(_validate_duplicates(staging_tables, run_id))
    issues.extend(_validate_key_fields(staging_tables, run_id))
    issues.extend(_validate_missing_team_player_values(staging_tables, run_id))
    issues.extend(_validate_man_of_match_quality(raw_tables, staging_tables, run_id))
    issues.extend(_validate_scoreline_timeline_goal_consistency(staging_tables, run_id))
    issues.extend(_validate_timeline_coverage(staging_tables, run_id))
    issues.extend(_validate_fixture_completeness(staging_tables, run_id))
    return pd.DataFrame(issues)


def _has_error_level_issues(issues_df: pd.DataFrame) -> bool:
    """Return whether validation found issues that should block staging writes."""

    if issues_df.empty or "severity" not in issues_df.columns:
        return False
    return bool((issues_df["severity"] == "error").any())

