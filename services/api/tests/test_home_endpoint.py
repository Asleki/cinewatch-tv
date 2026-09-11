from __future__ import annotations

from fastapi.testclient import TestClient

from cinewatch_api.application import create_app
from cinewatch_api.contracts.home import HomeResponse, HomeSections
from cinewatch_api.home.aggregation import HomepageAggregator
from cinewatch_api.providers.errors import ProviderUnavailableError
from cinewatch_api.settings import Settings


def _client() -> TestClient:
    return TestClient(
        create_app(
            Settings(
                environment="local",
                app_name="CineWatch TV",
                service_name="cinewatch-api",
                log_level="CRITICAL",
                _env_file=None,
            )
        )
    )


def test_home_endpoint_returns_cinewatch_contract(monkeypatch) -> None:
    async def fake_build(self: HomepageAggregator) -> HomeResponse:
        del self
        return HomeResponse(sections=HomeSections())

    monkeypatch.setattr(HomepageAggregator, "build", fake_build)

    with _client() as client:
        response = client.get("/api/v1/home")

    assert response.status_code == 200
    assert response.json() == {
        "schema_version": "1.0",
        "primary_provider": "tmdb",
        "hero": None,
        "sections": {
            "trending": [],
            "popular_movies": [],
            "popular_tv": [],
            "trending_people": [],
        },
    }


def test_home_endpoint_normalizes_provider_failure(monkeypatch) -> None:
    async def fake_build(self: HomepageAggregator) -> HomeResponse:
        del self
        raise ProviderUnavailableError(
            provider="tmdb",
            code="TMDB_UNAVAILABLE",
            message="TMDb returned a server failure.",
            status_code=503,
        )

    monkeypatch.setattr(HomepageAggregator, "build", fake_build)

    with _client() as client:
        response = client.get("/api/v1/home")

    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "HOMEPAGE_DATA_UNAVAILABLE"
    assert body["error"]["message"] == "Homepage data is temporarily unavailable."
    assert body["error"]["request_id"]
    assert "tmdb" not in body["error"]["message"].lower()
