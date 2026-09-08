#!/usr/bin/env python
"""Qualify the enduring backend skeleton while permitting milestone-owned persistence."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "services" / "api"

REQUIRED = (
    API / "pyproject.toml",
    API / "README.md",
    API / "cinewatch_api" / "__init__.py",
    API / "cinewatch_api" / "main.py",
    API / "cinewatch_api" / "application.py",
    API / "cinewatch_api" / "settings.py",
    API / "cinewatch_api" / "logging.py",
    API / "cinewatch_api" / "errors.py",
    API / "cinewatch_api" / "middleware" / "request_id.py",
    API / "cinewatch_api" / "contracts" / "system.py",
    API / "cinewatch_api" / "contracts" / "errors.py",
    API / "cinewatch_api" / "api" / "system.py",
    API / "cinewatch_api" / "api" / "v1" / "router.py",
    API / "cinewatch_api" / "api" / "v1" / "system.py",
    API / "tests" / "test_system_endpoints.py",
    API / "tests" / "test_request_id.py",
    API / "tests" / "test_errors.py",
    API / "tests" / "test_openapi.py",
    API / "tests" / "test_settings.py",
)

FORBIDDEN_DEPENDENCY_MARKERS = (
    "boto",
    "cognito",
    "authlib",
    "tmdb",
    "youtube",
)


def fail(message: str) -> None:
    print(f"FAIL  {message}")
    raise SystemExit(1)


missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.is_file()]
if missing:
    fail("missing backend paths: " + ", ".join(missing))
print("PASS  backend skeleton paths")

with (API / "pyproject.toml").open("rb") as handle:
    project = tomllib.load(handle)

dependencies = [item.lower() for item in project["project"].get("dependencies", [])]
joined = "\n".join(dependencies)
for required in ("fastapi", "pydantic-settings", "uvicorn"):
    if not any(item.startswith(required) for item in dependencies):
        fail(f"missing backend dependency: {required}")
print("PASS  FastAPI runtime dependencies")

for forbidden in FORBIDDEN_DEPENDENCY_MARKERS:
    if forbidden in joined:
        fail(f"premature auth/provider/cloud dependency introduced: {forbidden}")
print("PASS  no premature auth/provider/cloud dependencies")

application = (API / "cinewatch_api" / "application.py").read_text(encoding="utf-8")
system = (API / "cinewatch_api" / "api" / "system.py").read_text(encoding="utf-8")
constants = (API / "cinewatch_api" / "constants.py").read_text(encoding="utf-8")
if '"/health"' not in system or '"/status"' not in system:
    fail("system endpoint contract missing")
if 'API_V1_PREFIX = "/api/v1"' not in constants:
    fail("V1 API prefix missing")
if "RequestIdMiddleware" not in application:
    fail("request ID middleware not installed")
print("PASS  system and V1 routing contracts")

print("PASS  enduring CineWatch backend skeleton policy")
sys.exit(0)
