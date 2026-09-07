from fastapi.testclient import TestClient


def test_safe_request_id_is_propagated(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "cw-request-001"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "cw-request-001"


def test_invalid_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "not safe / value"})

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]
    assert request_id != "not safe / value"
    assert len(request_id) == 32
