from fastapi import APIRouter

from app.api.routes.campaigns import router as campaigns_router
from app.api.routes.tenants import router as tenants_router
from app.api.routes.users import router as users_router

api_router = APIRouter()


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


api_router.include_router(tenants_router)
api_router.include_router(users_router)
api_router.include_router(campaigns_router)
