from fastapi.testclient import TestClient


EXPECTED_OPERATIONS = {
    "/health": "system_health",
    "/status": "system_status",
    "/api/v1/status": "v1_system_status",
}


def test_openapi_exposes_only_skeleton_routes(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]

    assert schema["openapi"] == "3.1.0"
    assert set(paths) == set(EXPECTED_OPERATIONS)
    assert not any("discover" in path.lower() for path in paths)
    assert not any("watch" in path.lower() for path in paths)
    assert not any("explore" in path.lower() for path in paths)


def test_openapi_operation_ids_are_explicit_and_stable(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    for path, operation_id in EXPECTED_OPERATIONS.items():
        assert schema["paths"][path]["get"]["operationId"] == operation_id
