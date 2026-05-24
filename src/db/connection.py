"""Connection helpers for Postgres.

These helpers keep connection setup consistent across migration, ingestion, and
future API/query code.
"""

from __future__ import annotations

from contextlib import contextmanager
import os
from queue import Empty, LifoQueue
import threading
from typing import Iterator

import psycopg
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool

from src.db.settings import DatabaseSettings, get_database_settings


class ApiConnectionPool:
    """Small thread-safe psycopg pool for FastAPI read queries."""

    def __init__(
        self,
        conninfo: str,
        *,
        max_size: int = 5,
        timeout_seconds: float = 5.0,
        autocommit: bool = True,
    ) -> None:
        self.conninfo = conninfo
        self.max_size = max(1, max_size)
        self.timeout_seconds = max(0.1, timeout_seconds)
        self.autocommit = autocommit
        self._available: LifoQueue[psycopg.Connection] = LifoQueue()
        self._created_count = 0
        self._lock = threading.Lock()
        self._closed = False

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection]:
        """Borrow one connection from the pool and return it cleanly."""

        connection = self._acquire()
        discard = False
        try:
            yield connection
        except Exception as exc:
            discard = isinstance(exc, psycopg.Error) or self._rollback_failed_transaction(connection)
            raise
        finally:
            self._release(connection, discard=discard)

    def close(self) -> None:
        """Close every idle connection and prevent future checkouts."""

        with self._lock:
            self._closed = True
            while True:
                try:
                    connection = self._available.get_nowait()
                except Empty:
                    break
                self._close_connection(connection)
            self._created_count = 0

    def _acquire(self) -> psycopg.Connection:
        if self._closed:
            raise RuntimeError("API database connection pool is closed.")

        while True:
            try:
                connection = self._available.get_nowait()
            except Empty:
                connection = None

            if connection is not None:
                if not connection.closed:
                    return connection
                self._forget_closed_connection()
                continue

            with self._lock:
                if self._created_count < self.max_size:
                    self._created_count += 1
                    should_create = True
                else:
                    should_create = False

            if should_create:
                try:
                    return psycopg.connect(self.conninfo, autocommit=self.autocommit)
                except Exception:
                    self._forget_closed_connection()
                    raise

            try:
                connection = self._available.get(timeout=self.timeout_seconds)
            except Empty as exc:
                raise TimeoutError(
                    "Timed out waiting for an API database connection from the pool."
                ) from exc
            if not connection.closed:
                return connection
            self._forget_closed_connection()
            continue

    def _release(self, connection: psycopg.Connection, *, discard: bool) -> None:
        if discard or self._closed or connection.closed:
            self._close_connection(connection)
            self._forget_closed_connection()
            return
        self._available.put(connection)

    def _rollback_failed_transaction(self, connection: psycopg.Connection) -> bool:
        if self.autocommit or connection.closed:
            return connection.closed
        try:
            connection.rollback()
        except psycopg.Error:
            return True
        return False

    def _close_connection(self, connection: psycopg.Connection) -> None:
        try:
            connection.close()
        except psycopg.Error:
            pass

    def _forget_closed_connection(self) -> None:
        with self._lock:
            self._created_count = max(0, self._created_count - 1)


_api_pool: ApiConnectionPool | None = None
_api_pool_key: tuple[str, int, float] | None = None
_api_pool_lock = threading.Lock()


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


def get_api_connection_pool(settings: DatabaseSettings | None = None) -> ApiConnectionPool:
    """Return the shared API connection pool, creating it on first use."""

    global _api_pool, _api_pool_key

    resolved_settings = settings or get_database_settings()
    max_size = int(os.getenv("POSTGRES_API_POOL_MAX_SIZE", "5"))
    timeout_seconds = float(os.getenv("POSTGRES_API_POOL_TIMEOUT_SECONDS", "5"))
    pool_key = (resolved_settings.psycopg_conninfo, max_size, timeout_seconds)

    with _api_pool_lock:
        if _api_pool is None or _api_pool_key != pool_key:
            if _api_pool is not None:
                _api_pool.close()
            _api_pool = ApiConnectionPool(
                resolved_settings.psycopg_conninfo,
                max_size=max_size,
                timeout_seconds=timeout_seconds,
                autocommit=True,
            )
            _api_pool_key = pool_key
        return _api_pool


@contextmanager
def get_api_psycopg_connection(settings: DatabaseSettings | None = None) -> Iterator[psycopg.Connection]:
    """Yield a pooled psycopg connection for FastAPI read requests."""

    with get_api_connection_pool(settings=settings).connection() as connection:
        yield connection


def close_api_connection_pool() -> None:
    """Close the shared API connection pool during application shutdown."""

    global _api_pool, _api_pool_key

    with _api_pool_lock:
        if _api_pool is not None:
            _api_pool.close()
        _api_pool = None
        _api_pool_key = None


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
