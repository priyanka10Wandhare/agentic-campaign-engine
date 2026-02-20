from fastapi import FastAPI
import structlog

from app.api.middleware import tenant_context_middleware
from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)

app.middleware("http")(tenant_context_middleware)
app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    logger.info("app.startup", environment=settings.app_env)


@app.on_event("shutdown")
def on_shutdown() -> None:
    logger.info("app.shutdown")
