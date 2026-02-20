from fastapi import APIRouter

from app.api.routes.evaluation import router as evaluation_router

api_router = APIRouter()
api_router.include_router(evaluation_router)


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Health endpoint for readiness checks."""

    return {"status": "ok"}
