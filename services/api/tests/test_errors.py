from fastapi import FastAPI
from fastapi.testclient import TestClient

from cinewatch_api.application import create_app
from cinewatch_api.errors import ApiError
from cinewatch_api.settings import Settings


def _settings() -> Settings:
    return Settings(log_level="CRITICAL")


def test_api_error_envelope() -> None:
    app = create_app(_settings())

    def fail() -> None:
        raise ApiError(code="TEST_ERROR", message="Test failure.", status_code=409)

    app.add_api_route("/__test/api-error", fail, methods=["GET"], include_in_schema=False)

    with TestClient(app) as client:
        response = client.get("/__test/api-error", headers={"X-Request-ID": "error-request-1"})

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "TEST_ERROR",
            "message": "Test failure.",
            "request_id": "error-request-1",
        }
    }


def test_unhandled_error_envelope() -> None:
    app: FastAPI = create_app(_settings())

    def fail() -> None:
        raise RuntimeError("private diagnostic text")

    app.add_api_route("/__test/unhandled", fail, methods=["GET"], include_in_schema=False)

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/__test/unhandled", headers={"X-Request-ID": "error-request-2"})

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "The service could not complete the request.",
            "request_id": "error-request-2",
        }
    }
    assert "private diagnostic text" not in response.text
