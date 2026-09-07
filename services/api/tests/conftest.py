from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from cinewatch_api.application import create_app
from cinewatch_api.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        environment="local",
        app_name="CineWatch TV",
        service_name="cinewatch-api",
        log_level="CRITICAL",
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client
