"""Health endpoint for API and Postgres connectivity."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.queries import get_health_status
from src.api.schemas import HealthResponse


router = APIRouter(tags=["health"])


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

