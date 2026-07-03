"""Command-line entry point for scraping one UPL season."""

from __future__ import annotations

import argparse
import json

from src.config import (
    DATA_RAW,
    raw_season_dir,
    raw_season_file,
    raw_season_refresh_plan_file,
    season_key,
)
from src.dataset import save_dataframe
from src.scraping.upl.constants import TABLE_NAMES
from src.scraping.upl.dataframes import (
    _build_legacy_goal_dataframe,
    _save_structured_outputs,
)
from src.scraping.upl.pipeline import scrape_season


def _write_refresh_plan(
    season: str,
    season_tables,
    scrape_summary: dict[str, object],
) -> None:
    """Persist the successful match-level delta for routine raw loading."""
    affected_urls = set(scrape_summary["affected_match_urls"])
    match_rows = season_tables["matches"]
    affected_ids = sorted(
        {
            int(match_id)
            for match_id in match_rows.loc[
                match_rows["match_url"].isin(affected_urls), "match_id"
            ].dropna()
        }
    )
    plan_path = raw_season_refresh_plan_file(season)
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(
        json.dumps(
            {
                "version": 1,
                "season": season_key(season),
                "mode": "routine-incremental",
                "affected_match_ids": affected_ids,
                "affected_match_urls": sorted(affected_urls),
                "attempted_match_urls": scrape_summary["attempted_match_urls"],
                "failed_match_urls": scrape_summary["failed_match_urls"],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print(
        "[ok] Raw refresh plan: "
        f"{len(affected_ids)} affected match(es) -> {plan_path}"
    )


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Scrape structured UPL event data")
    parser.add_argument(
        "--season", type=str, default="2025-26", help="Season to scrape (e.g., 2025-26)"
    )
    parser.add_argument(
        "--refresh-source",
        action="store_true",
        help="Bypass cached HTML and checkpoint state so the season is scraped from the live source.",
    )
    parser.add_argument(
        "--postgres-change-detection",
        action="store_true",
        help=(
            "Query Postgres raw tables first and scrape only missing, incomplete, "
            "previously failed, or recent completed matches."
        ),
    )
    parser.add_argument(
        "--recent-completed-limit",
        type=int,
        default=10,
        help=(
            "When --postgres-change-detection is enabled, refresh this many recent "
            "completed matches as updated-data candidates. Defaults to 10."
        ),
    )
    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print(f"UPL Structured Data Scraper - Season {args.season}")
    print(f"{'=' * 60}\n")

    try:
        season_tables, scrape_summary = scrape_season(
            args.season,
            refresh_source=args.refresh_source,
            use_postgres_change_detection=args.postgres_change_detection,
            recent_completed_limit=args.recent_completed_limit,
        )
        if args.postgres_change_detection:
            _write_refresh_plan(args.season, season_tables, scrape_summary)

        season_outputs_exist = all(
            raw_season_file(args.season, table_name).exists()
            for table_name in TABLE_NAMES
        )
        legacy_goals_path = DATA_RAW / f"upl_goals_{season_key(args.season)}.csv"
        total_spill_rows = sum(scrape_summary["spill_rows_filtered"].values())
        should_write_structured_outputs = (
            scrape_summary["successful_fetches"] > 0
            or total_spill_rows > 0
            or not season_outputs_exist
        )
        should_write_legacy_goals = (
            scrape_summary["successful_fetches"] > 0
            or total_spill_rows > 0
            or not legacy_goals_path.exists()
        )

        if should_write_structured_outputs:
            _save_structured_outputs(args.season, season_tables)

        if should_write_legacy_goals:
            legacy_goals_df = _build_legacy_goal_dataframe(season_tables["events"])
            save_dataframe(legacy_goals_df, legacy_goals_path)
        if not should_write_structured_outputs and not should_write_legacy_goals:
            print(
                "[ok] No newly completed matches; kept existing season outputs and updated failed-match manifest only"
            )

        # Legacy single-table output kept here for reference while raw scraping
        # now writes season-scoped tables under data/raw/<season>/.
        # legacy_events_path = DATA_RAW / f"upl_events_{season_key(args.season)}.csv"
        # save_dataframe(season_tables["events"], legacy_events_path)

        print("\n[ok] Scraping complete!")
        print(f"  Season folder: {raw_season_dir(args.season)}")
        for table_name in TABLE_NAMES:
            print(f"  {table_name}: {len(season_tables[table_name])} rows")
        print(f"  Successful fetches this run: {scrape_summary['successful_fetches']}")
        print(f"  Remaining failed matches: {scrape_summary['failed_matches']}")
        if total_spill_rows:
            print("  Cross-season spill rows filtered before CSV write:")
            for table_name, row_count in scrape_summary["spill_rows_filtered"].items():
                if row_count:
                    print(f"    {table_name}: {row_count}")
        print(f"  Legacy goals export: {legacy_goals_path}")
        return 0

    except Exception as exc:
        print(f"\n[error] Scraping failed: {exc}")
        return 1
