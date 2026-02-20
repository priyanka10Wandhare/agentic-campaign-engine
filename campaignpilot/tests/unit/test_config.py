from app.core.config import Settings


def test_database_url_from_settings() -> None:
    settings = Settings(
        POSTGRES_USER="user",
        POSTGRES_PASSWORD="password",
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5433,
        POSTGRES_DB="campaign",
    )

    assert settings.database_url == "postgresql+psycopg://user:password@localhost:5433/campaign"
