"""FastAPI entrypoint for the UPL Match Intelligence read backend."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import events, health, matches, officials, seasons, teams


app = FastAPI(
    title="UPL Match Intelligence API",
    description=(
        "Read-first API over the cleaned Postgres staging tables for Uganda "
        "Premier League match intelligence."
    ),
    version="0.1.0",
)

# The React pilot runs on Vite's local dev server, which is a different origin
# from FastAPI. CORS lets the browser call the API during local development
# while keeping the allowed origins explicit and easy to review.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(seasons.router)
app.include_router(matches.router)
app.include_router(teams.router)
app.include_router(events.router)
app.include_router(officials.router)
