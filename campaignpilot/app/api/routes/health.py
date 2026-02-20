from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.dependencies.providers import get_settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Health endpoint for readiness checks."""

    return {"status": "ok", "environment": settings.app_env}
