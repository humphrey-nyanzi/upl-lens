"""Tests for Supabase IO mitigation changes."""

from __future__ import annotations

from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_PROXY = PROJECT_ROOT / "frontend" / "functions" / "api" / "[[path]].js"
IO_MIGRATION = PROJECT_ROOT / "database" / "migrations" / "011_add_io_mitigation_indexes.sql"
SCHEMA_SQL = PROJECT_ROOT / "database" / "schema.sql"


def test_pages_api_proxy_declares_edge_cache_rules() -> None:
    """The Cloudflare proxy should cache repeat public GET reads at the edge."""

    script = CACHE_PROXY.read_text(encoding="utf-8")

    assert "caches.default" in script
    assert "cache.match" in script
    assert "cache.put" in script
    assert "s-maxage=${cacheSeconds}" in script
    assert "x-upl-lens-cache" in script
    assert "authorization" in script
    assert "cookie" in script


def test_pages_api_proxy_cache_rule_helpers_work_in_node() -> None:
    """Route cache TTLs should be testable without Cloudflare runtime access."""

    node_script = f"""
      const mod = await import({str(CACHE_PROXY.as_uri())!r});
      const {{ cacheSecondsFor, canUseEdgeCache }} = mod.testExports;
      const request = new Request('https://upl-lens.pages.dev/api/seasons', {{ method: 'GET' }});
      const privateRequest = new Request('https://upl-lens.pages.dev/api/seasons', {{
        method: 'GET',
        headers: {{ authorization: 'Bearer test' }},
      }});
      if (cacheSecondsFor('seasons') !== 600) process.exit(1);
      if (cacheSecondsFor('matches/31687') !== 1800) process.exit(2);
      if (cacheSecondsFor('unknown') !== 0) process.exit(3);
      if (!canUseEdgeCache(request, 'seasons')) process.exit(4);
      if (canUseEdgeCache(privateRequest, 'seasons')) process.exit(5);
    """

    subprocess.run(["node", "--input-type=module", "--eval", node_script], check=True)


def test_io_mitigation_migration_targets_repeated_filters() -> None:
    """Indexes should match the raw refresh and public API query shapes."""

    sql = IO_MIGRATION.read_text(encoding="utf-8")

    assert "idx_raw_matches_season_key_order" in sql
    assert "REPLACE(REPLACE(season, '-', '_'), '/', '_')" in sql
    assert "idx_staging_matches_app_safe_season_date" in sql
    assert "WHERE is_source_anomaly IS NOT TRUE" in sql
    assert "idx_staging_events_season_match_type" in sql
    assert "idx_staging_lineups_season_player_match" in sql
    assert "idx_staging_events_season_sub_in_match" in sql
    assert "idx_staging_events_season_sub_out_match" in sql


def test_schema_bundle_includes_io_mitigation_migration() -> None:
    """The readable schema bundle should include the new IO mitigation migration."""

    assert r"\i migrations/011_add_io_mitigation_indexes.sql" in SCHEMA_SQL.read_text(encoding="utf-8")
