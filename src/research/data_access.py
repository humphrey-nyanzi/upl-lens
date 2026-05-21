"""Read-only SQL helpers for feature research notebooks.

Research notebooks should usually read cleaned `staging.*` tables. This module
keeps that access pattern small and repeatable, while adding a guardrail against
accidental write statements in notebooks.
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd
from sqlalchemy import text

from src.db.connection import create_sqlalchemy_engine
from src.db.settings import DatabaseSettings


READ_ONLY_STARTERS = {"select", "with", "explain"}
WRITE_KEYWORDS = {
    "alter",
    "create",
    "delete",
    "drop",
    "grant",
    "insert",
    "revoke",
    "truncate",
    "update",
}


def _first_sql_word(query: str) -> str:
    """Return the first meaningful SQL word from a query string."""

    without_block_comments = re.sub(r"/\*.*?\*/", " ", query, flags=re.DOTALL)
    lines = [
        line
        for line in without_block_comments.splitlines()
        if not line.strip().startswith("--")
    ]
    cleaned = "\n".join(lines).strip()
    match = re.match(r"([A-Za-z_]+)", cleaned)
    return "" if match is None else match.group(1).lower()


def _validate_read_only_query(query: str) -> None:
    """Raise a clear error when a notebook query looks unsafe."""

    lowered = query.lower()
    blocked = [keyword for keyword in WRITE_KEYWORDS if re.search(rf"\b{keyword}\b", lowered)]
    if blocked:
        blocked_text = ", ".join(sorted(blocked))
        raise ValueError(
            "Research notebooks should not run write or permission SQL. "
            f"Blocked keyword(s): {blocked_text}."
        )

    first_word = _first_sql_word(query)
    if first_word not in READ_ONLY_STARTERS:
        allowed = ", ".join(sorted(READ_ONLY_STARTERS))
        raise ValueError(
            "Research notebooks should use read-only SQL. "
            f"Expected the query to start with one of: {allowed}."
        )


def read_sql(
    query: str,
    params: dict[str, Any] | None = None,
    settings: DatabaseSettings | None = None,
) -> pd.DataFrame:
    """Run a read-only SQL query and return a pandas DataFrame.

    Parameters
    ----------
    query : str
        A `SELECT`, `WITH`, or `EXPLAIN` query. Write statements are blocked so
        feature notebooks do not accidentally modify app data.
    params : dict[str, Any] | None, optional
        Query parameters passed safely to SQLAlchemy and psycopg.
    settings : DatabaseSettings | None, optional
        Optional database settings for tests or alternate connections. When
        omitted, settings are loaded from `.env`.

    Returns
    -------
    pandas.DataFrame
        Query results.
    """

    _validate_read_only_query(query)
    engine = create_sqlalchemy_engine(settings=settings)

    with engine.connect() as connection:
        # This is a second safety rail. The database should reject writes even if
        # a future notebook helper accidentally loosens the Python validation.
        connection.execute(text("SET TRANSACTION READ ONLY;"))
        return pd.read_sql_query(text(query), connection, params=params or {})
