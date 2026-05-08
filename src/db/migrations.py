"""Helpers for applying SQL migration files in order."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from psycopg import sql

from src.db.connection import get_psycopg_connection
from src.db.settings import DatabaseSettings


MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "database" / "migrations"
MIGRATION_SCHEMA = "app_meta"
MIGRATION_TABLE = "schema_migrations"


@dataclass(frozen=True)
class MigrationResult:
    """Outcome information for one migration file."""

    filename: str
    applied: bool


def _ensure_migration_table(connection) -> None:
    """Create the migration tracking schema and table if they do not exist yet.

    We avoid the `public` schema here because many Postgres installations keep
    `public` locked down for non-superuser roles.
    """

    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(
                sql.Identifier(MIGRATION_SCHEMA)
            )
        )
        cursor.execute(
            sql.SQL(
                """
            CREATE TABLE IF NOT EXISTS {}.{} (
                filename TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
            ).format(
                sql.Identifier(MIGRATION_SCHEMA),
                sql.Identifier(MIGRATION_TABLE),
            )
        )


def _list_migration_files() -> list[Path]:
    """Return SQL migration files in sorted order."""

    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def apply_pending_migrations(settings: DatabaseSettings | None = None) -> list[MigrationResult]:
    """Apply SQL files that have not yet been recorded in `schema_migrations`.

    Parameters
    ----------
    settings : DatabaseSettings | None, optional
        Preloaded database settings object.

    Returns
    -------
    list[MigrationResult]
        One result per discovered migration file.
    """

    results: list[MigrationResult] = []

    with get_psycopg_connection(settings=settings) as connection:
        _ensure_migration_table(connection)

        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("SELECT filename FROM {}.{};").format(
                    sql.Identifier(MIGRATION_SCHEMA),
                    sql.Identifier(MIGRATION_TABLE),
                )
            )
            applied_files = {row[0] for row in cursor.fetchall()}

        for migration_path in _list_migration_files():
            if migration_path.name in applied_files:
                results.append(MigrationResult(filename=migration_path.name, applied=False))
                continue

            sql_text = migration_path.read_text(encoding="utf-8")
            with connection.cursor() as cursor:
                cursor.execute(sql_text)
                cursor.execute(
                    sql.SQL("INSERT INTO {}.{} (filename) VALUES (%s);").format(
                        sql.Identifier(MIGRATION_SCHEMA),
                        sql.Identifier(MIGRATION_TABLE),
                    ),
                    (migration_path.name,),
                )

            results.append(MigrationResult(filename=migration_path.name, applied=True))

        connection.commit()

    return results
