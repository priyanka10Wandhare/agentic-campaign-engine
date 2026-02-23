import pytest

from app.api.routes.health import health_check
from app.api.routes.system import missing_resource
from app.core.config import Settings
from app.errors.exceptions import ResourceNotFoundError


def test_health_check_returns_status_and_environment() -> None:
    settings = Settings(APP_ENV="test", APP_DEBUG=False)

    response = health_check(settings)

    assert response == {"status": "ok", "environment": "test"}


def test_missing_resource_raises_domain_error() -> None:
    with pytest.raises(ResourceNotFoundError) as exc_info:
        missing_resource()

    assert exc_info.value.code == "resource_not_found"
    assert exc_info.value.status_code == 404
