from fastapi import FastAPI

from app.api.router import api_router
from app.bootstrap.middleware import register_middlewares
from app.core.config import Settings, get_settings
from app.core.container import AppContainer
from app.core.logging import configure_logging
from app.errors.handlers import register_exception_handlers


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)
    container = AppContainer.build(settings)

    app = FastAPI(title=settings.app_name, debug=settings.app_debug)
    app.state.container = container

    register_middlewares(app)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.on_event("startup")
    def on_startup() -> None:
        container.logger.info("app.startup", environment=settings.app_env)

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        container.logger.info("app.shutdown")
        container.engine.dispose()

    return app
