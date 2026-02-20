from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database objects required for creator matching."""

    # ensure model metadata is loaded
    import app.models  # noqa: F401

    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE OR REPLACE FUNCTION match_creators(
                    p_tenant_id VARCHAR,
                    p_embedding vector(1536),
                    p_limit INTEGER DEFAULT 5
                )
                RETURNS TABLE (
                    id INTEGER,
                    tenant_id VARCHAR,
                    niche VARCHAR,
                    followers INTEGER,
                    engagement_rate DOUBLE PRECISION,
                    similarity DOUBLE PRECISION
                )
                LANGUAGE SQL
                AS $$
                    SELECT
                        c.id,
                        c.tenant_id,
                        c.niche,
                        c.followers,
                        c.engagement_rate,
                        1 - (c.embedding <=> p_embedding) AS similarity
                    FROM creators c
                    WHERE c.tenant_id = p_tenant_id
                    ORDER BY c.embedding <=> p_embedding
                    LIMIT p_limit;
                $$;
                """
            )
        )
