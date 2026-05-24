"""Database settings loaded from environment variables.

This module keeps Postgres connection details in one place so scraper, loader,
and future API code can share the same configuration logic.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from urllib.parse import quote_plus

from dotenv import load_dotenv


@dataclass(frozen=True)
class DatabaseSettings:
    """Simple container for Postgres connection settings.

    Attributes
    ----------
    host : str
        Database server hostname.
    port : int
        Database server port.
    database : str
        Database name to connect to.
    user : str
        Database username.
    password : str
        Database password.
    sslmode : str
        SSL preference passed through to Postgres drivers.
    """

    host: str
    port: int
    database: str
    user: str
    password: str
    sslmode: str = "prefer"

    @property
    def sqlalchemy_url(self) -> str:
        """Return a SQLAlchemy connection URL for Postgres."""
        encoded_user = quote_plus(self.user)
        encoded_password = quote_plus(self.password)
        return (
            f"postgresql+psycopg://{encoded_user}:{encoded_password}"
            f"@{self.host}:{self.port}/{self.database}?sslmode={self.sslmode}"
        )

    @property
    def psycopg_conninfo(self) -> str:
        """Return a psycopg-compatible connection string."""
        return (
            f"host={self.host} "
            f"port={self.port} "
            f"dbname={self.database} "
            f"user={self.user} "
            f"password={self.password} "
            f"sslmode={self.sslmode}"
        )


@lru_cache(maxsize=1)
def get_database_settings() -> DatabaseSettings:
    """Load database settings from `.env` and process environment variables.

    Returns
    -------
    DatabaseSettings
        Parsed settings object ready for connection helpers.

    Raises
    ------
    ValueError
        Raised when one or more required variables are missing.
    """

    load_dotenv()

    values = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "database": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "sslmode": os.getenv("POSTGRES_SSLMODE", "prefer"),
    }
    values = {
        key: value.strip() if isinstance(value, str) else value
        for key, value in values.items()
    }

    missing = [name for name in ("database", "user", "password") if not values[name]]
    if missing:
        missing_text = ", ".join(f"POSTGRES_{name.upper()}" for name in missing)
        raise ValueError(
            "Missing required database environment variables: "
            f"{missing_text}. Update your .env file before running database commands."
        )

    return DatabaseSettings(
        host=values["host"],
        port=int(values["port"]),
        database=str(values["database"]),
        user=str(values["user"]),
        password=str(values["password"]),
        sslmode=str(values["sslmode"]),
    )


def clear_database_settings_cache() -> None:
    """Clear cached settings after tests or tools modify database environment."""

    get_database_settings.cache_clear()
