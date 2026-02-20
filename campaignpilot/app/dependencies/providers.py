from collections.abc import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.container import AppContainer
from app.core.database import get_db_session


def get_container(request: Request) -> AppContainer:
    """Resolve the application dependency container from app state."""

    return request.app.state.container


def get_settings(container: AppContainer = Depends(get_container)):
    return container.settings


def get_logger(container: AppContainer = Depends(get_container)):
    return container.logger


def get_db(container: AppContainer = Depends(get_container)) -> Generator[Session, None, None]:
    yield from get_db_session(container.session_factory)
