from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "cinewatch-api"}
    assert response.headers["X-Request-ID"]


def test_root_status(client: TestClient) -> None:
    response = client.get("/status")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "cinewatch-api",
        "application": "CineWatch TV",
        "environment": "local",
        "api_version": "v1",
    }


def test_v1_status_matches_root_status(client: TestClient) -> None:
    assert client.get("/api/v1/status").json() == client.get("/status").json()
