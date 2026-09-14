from __future__ import annotations

from fastapi.testclient import TestClient

from cinewatch_api.application import create_app
from cinewatch_api.contracts.home_experience import (
    HomeGenresResponse,
    HomeHeroExperience,
    HomeSearchResponse,
)
from cinewatch_api.home.experience import HomepageExperienceService
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


def test_home_search_endpoint_returns_bounded_cinewatch_contract(monkeypatch) -> None:
    async def fake_search(self: HomepageExperienceService, query: str) -> HomeSearchResponse:
        del self
        return HomeSearchResponse(query=query, suggestions=[])

    monkeypatch.setattr(HomepageExperienceService, "search", fake_search)

    with _client() as client:
        response = client.get("/api/v1/home/search", params={"q": "Moana"})

    assert response.status_code == 200
    assert response.json() == {"query": "Moana", "suggestions": []}


def test_home_genres_endpoint_returns_cinewatch_contract(monkeypatch) -> None:
    async def fake_genres(self: HomepageExperienceService) -> HomeGenresResponse:
        del self
        return HomeGenresResponse(genres=[])

    monkeypatch.setattr(HomepageExperienceService, "genres", fake_genres)

    with _client() as client:
        response = client.get("/api/v1/home/genres")

    assert response.status_code == 200
    assert response.json() == {"genres": []}


def test_home_hero_endpoint_returns_optional_enrichment(monkeypatch) -> None:
    async def fake_hero(
        self: HomepageExperienceService,
        media_type: str,
        provider_id: int,
    ) -> HomeHeroExperience:
        del self
        return HomeHeroExperience(
            media_type=media_type,  # type: ignore[arg-type]
            provider_id=provider_id,
        )

    monkeypatch.setattr(HomepageExperienceService, "hero", fake_hero)

    with _client() as client:
        response = client.get("/api/v1/home/hero/tv/42")

    assert response.status_code == 200
    assert response.json() == {
        "provider_id": 42,
        "media_type": "tv",
        "writers": [],
        "ratings": [],
        "trailer": None,
        "quote": None,
    }


def test_unknown_lazy_rail_returns_stable_not_found_error() -> None:
    with _client() as client:
        response = client.get("/api/v1/home/rails/not-a-real-rail")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "HOMEPAGE_RAIL_NOT_FOUND"
    assert body["error"]["request_id"]
