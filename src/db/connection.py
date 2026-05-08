"""Connection helpers for Postgres.

These helpers keep connection setup consistent across migration, ingestion, and
future API/query code.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool

from src.db.settings import DatabaseSettings, get_database_settings


def create_sqlalchemy_engine(settings: DatabaseSettings | None = None) -> Engine:
    """Create a SQLAlchemy engine for Postgres."""
    resolved_settings = settings or get_database_settings()
    return create_engine(resolved_settings.sqlalchemy_url, future=True, poolclass=NullPool)


@contextmanager
def get_psycopg_connection(
    settings: DatabaseSettings | None = None,
    autocommit: bool = False,
) -> Iterator[psycopg.Connection]:
    """Yield a psycopg connection that closes cleanly after use.

    Parameters
    ----------
    settings : DatabaseSettings | None, optional
        Preloaded settings object. If omitted, the helper reads from `.env`.
    autocommit : bool, default=False
        Whether the connection should commit each statement immediately.
    """

    resolved_settings = settings or get_database_settings()
    with psycopg.connect(resolved_settings.psycopg_conninfo, autocommit=autocommit) as connection:
        yield connection


def test_database_connection(settings: DatabaseSettings | None = None) -> tuple[str, str]:
    """Run a tiny query to confirm that Postgres is reachable.

    Returns
    -------
    tuple[str, str]
        Database name and Postgres version string.
    """

    with get_psycopg_connection(settings=settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), version();")
            database_name, version_text = cursor.fetchone()
    return str(database_name), str(version_text)
