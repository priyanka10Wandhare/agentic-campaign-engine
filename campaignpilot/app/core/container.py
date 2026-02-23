from dataclasses import dataclass

import structlog
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.core.database import create_db_engine, create_session_factory


@dataclass(frozen=True)
class AppContainer:
    """Simple dependency container for core application resources."""

    settings: Settings
    engine: Engine
    session_factory: sessionmaker[Session]
    logger: structlog.stdlib.BoundLogger

    @classmethod
    def build(cls, settings: Settings) -> "AppContainer":
        engine = create_db_engine(settings)
        session_factory = create_session_factory(engine)
        logger = structlog.get_logger("campaignpilot")
        return cls(settings=settings, engine=engine, session_factory=session_factory, logger=logger)
