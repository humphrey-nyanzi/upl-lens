"""Health endpoint for API and Postgres connectivity."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.queries import get_health_status
from src.api.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health/live")
def liveness_check() -> dict[str, str]:
    """Confirm that the FastAPI process is running.

    Hosting platforms use this kind of check to decide whether the web process
    should stay up. It intentionally does not touch Postgres; `/health` remains
    the deeper API-plus-database readiness check.
    """

    return {"status": "ok", "api": "ok"}


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Confirm that FastAPI can connect to Postgres."""

    try:
        return HealthResponse(**get_health_status())
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "api": "ok",
                "database": "error",
                "message": str(exc),
            },
        ) from exc
