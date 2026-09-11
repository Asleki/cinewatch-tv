from fastapi.testclient import TestClient


FOUNDATION_OPERATIONS = {
    "/health": "system_health",
    "/status": "system_status",
    "/api/v1/status": "v1_system_status",
}


def test_openapi_preserves_required_foundation_routes(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]

    assert schema["openapi"] == "3.1.0"
    assert set(FOUNDATION_OPERATIONS).issubset(paths)


def test_openapi_foundation_operation_ids_are_explicit_and_stable(
    client: TestClient,
) -> None:
    schema = client.get("/openapi.json").json()

    for path, operation_id in FOUNDATION_OPERATIONS.items():
        assert schema["paths"][path]["get"]["operationId"] == operation_id
