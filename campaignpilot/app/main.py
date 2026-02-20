from fastapi import FastAPI
import structlog

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("app.startup", environment=settings.app_env)


@app.on_event("shutdown")
def on_shutdown() -> None:
    logger.info("app.shutdown")
