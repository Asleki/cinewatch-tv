from __future__ import annotations

from fastapi.testclient import TestClient

from cinewatch_api.application import create_app
from cinewatch_api.catalog.service import CatalogService
from cinewatch_api.contracts.catalog import CatalogBrowseResponse, CatalogTitleResponse
from cinewatch_api.settings import Settings


def _client() -> TestClient:
    return TestClient(create_app(Settings(environment="local", app_name="CineWatch TV", service_name="cinewatch-api", log_level="CRITICAL", _env_file=None)))


def test_catalog_title_endpoint_is_stable(monkeypatch) -> None:
    async def fake_title(self: CatalogService, media_type: str, provider_id: int, *, watch_region=None) -> CatalogTitleResponse:
        del self, watch_region
        return CatalogTitleResponse(provider_id=provider_id, media_type=media_type, title="Example")  # type: ignore[arg-type]
    monkeypatch.setattr(CatalogService, "title", fake_title)
    with _client() as client:
        response = client.get("/api/v1/catalog/title/movie/42")
    assert response.status_code == 200
    assert response.json()["title"] == "Example"


def test_catalog_browse_endpoint_keeps_filters_inside_cinewatch_contract(monkeypatch) -> None:
    async def fake_browse(self: CatalogService, kind: str, slug: str, **kwargs) -> CatalogBrowseResponse:
        del self
        return CatalogBrowseResponse(kind=kind, slug=slug, title="Drama", page=kwargs["page"], total_pages=1, total_results=0, media_type=kwargs["media_type"], year=kwargs["year"], language=kwargs["language"], sort=kwargs["sort"], items=[])  # type: ignore[arg-type]
    monkeypatch.setattr(CatalogService, "browse", fake_browse)
    with _client() as client:
        response = client.get("/api/v1/catalog/browse/genre/drama", params={"media_type": "tv", "year": 2026, "language": "en"})
    assert response.status_code == 200
    body = response.json()
    assert body["media_type"] == "tv"
    assert body["year"] == 2026
    assert body["language"] == "en"
