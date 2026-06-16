"""FastAPI entrypoint for the UPL Lens read backend."""

from __future__ import annotations

from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import events, health, insights, matches, officials, overview, players, seasons, teams, trends
from src.db.connection import close_api_connection_pool


load_dotenv()

DEFAULT_ALLOWED_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
)


def get_allowed_origins() -> list[str]:
    """Return browser origins allowed to call the API.

    CORS is a browser safety rule. The API can be public, but the browser still
    needs FastAPI to explicitly say which frontend websites may call it. Local
    development works from the defaults; deployment can add the hosted frontend
    URL through `ALLOWED_ORIGINS`.
    """

    configured_origins = os.getenv("ALLOWED_ORIGINS")
    if configured_origins is None or not configured_origins.strip():
        return list(DEFAULT_ALLOWED_ORIGINS)

    origins = [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]
    return origins or list(DEFAULT_ALLOWED_ORIGINS)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Clean up the API database pool when the web process shuts down."""

    yield
    close_api_connection_pool()


app = FastAPI(
    title="UPL Lens API",
    description=(
        "Read-first API over the cleaned Postgres staging tables for Uganda "
        "Premier League match intelligence."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# The React pilot runs on Vite's local dev server, which is a different origin
# from FastAPI. In production, set ALLOWED_ORIGINS to the deployed frontend
# origin, for example: https://upl-match-intelligence.pages.dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(seasons.router)
app.include_router(matches.router)
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(events.router)
app.include_router(officials.router)
app.include_router(insights.router)
app.include_router(trends.router)
app.include_router(overview.router)
