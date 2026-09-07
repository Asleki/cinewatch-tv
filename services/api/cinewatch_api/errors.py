"""Application error types and HTTP exception handlers."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from cinewatch_api.contracts.errors import ErrorBody, ErrorEnvelope

logger = logging.getLogger("cinewatch.api.errors")


class ApiError(Exception):
    """Expected API failure with a stable public code and status."""

    def __init__(self, *, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _request_id(request: Request) -> str:
    return str(getattr(request.state, "request_id", "unavailable"))


def _response(*, request: Request, code: str, message: str, status_code: int) -> JSONResponse:
    envelope = ErrorEnvelope(
        error=ErrorBody(code=code, message=message, request_id=_request_id(request))
    )
    return JSONResponse(status_code=status_code, content=envelope.model_dump(mode="json"))


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return _response(
        request=request,
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    del exc
    return _response(
        request=request,
        code="REQUEST_VALIDATION_FAILED",
        message="Request validation failed.",
        status_code=422,
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled API exception",
        exc_info=exc,
        extra={"event": "request.unhandled_error", "request_id": _request_id(request)},
    )
    return _response(
        request=request,
        code="INTERNAL_SERVER_ERROR",
        message="The service could not complete the request.",
        status_code=500,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, api_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_error_handler)
