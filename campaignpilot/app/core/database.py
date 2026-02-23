from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import Settings

Base = declarative_base()


def create_db_engine(settings: Settings) -> Engine:
    """Create the SQLAlchemy engine from application settings."""

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        future=True,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create the SQLAlchemy session factory."""

    return sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def get_db_session(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""

    db = session_factory()
    try:
        yield db
    finally:
        db.close()
