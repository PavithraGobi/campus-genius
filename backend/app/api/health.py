"""Health check endpoint - used to verify the API is running."""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "env": settings.app_env,
    }
