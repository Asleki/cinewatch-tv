from fastapi.testclient import TestClient


def test_openapi_exposes_only_skeleton_routes(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    paths = set(schema["paths"])

    assert {"/health", "/status", "/api/v1/status"}.issubset(paths)
    assert not any("discover" in path.lower() for path in paths)
    assert not any("watch" in path.lower() for path in paths)
    assert not any("explore" in path.lower() for path in paths)
