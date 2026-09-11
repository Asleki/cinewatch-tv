#!/usr/bin/env python3
"""Static policy gate for CWTV.V1.2.6 OpenAPI and typed contracts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "packages/contracts/openapi/cinewatch-v1.openapi.json",
    "packages/contracts/src/generated/openapi.d.ts",
    "packages/contracts/src/index.d.ts",
    "scripts/export_openapi_contract.py",
    "scripts/update_api_contracts.sh",
    "scripts/check_contract_runtime.sh",
    "docs/architecture/CineWatch_TV_V1_OpenAPI_and_Typed_Contract_Foundation_001.md",
    "docs/architecture/decisions/CWTV_ADR_0005_OpenAPI_Canonical_Contract_and_Type_Generation.md",
    "services/api/tests/test_contract_snapshot.py",
]


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail("missing contract foundation paths: " + ", ".join(missing))
    print("PASS  OpenAPI and typed contract foundation paths")

    root_pkg = json.loads(read("package.json"))
    contract_pkg = json.loads(read("packages/contracts/package.json"))
    web_pkg = json.loads(read("apps/web/package.json"))

    if contract_pkg.get("devDependencies", {}).get("openapi-typescript") != "7.13.0":
        fail("openapi-typescript must be pinned to 7.13.0")
    if contract_pkg.get("types") != "./src/index.d.ts":
        fail("@cinewatch/contracts must expose the governed declaration entry point")
    if web_pkg.get("dependencies", {}).get("@cinewatch/contracts") != "0.0.0":
        fail("frontend must consume the local @cinewatch/contracts workspace")
    scripts = root_pkg.get("scripts", {})
    for name in ("check:contracts", "contracts:update", "contracts:check", "contracts:generate"):
        if name not in scripts:
            fail(f"root package script missing: {name}")
    print("PASS  npm workspace contract authority")

    runtime_gate = read("scripts/check_contract_runtime.sh")
    for forbidden in (
        './node_modules/openapi-typescript/package.json',
        './node_modules/.bin/openapi-typescript',
    ):
        if forbidden in runtime_gate:
            fail(
                "contract runtime gate must not assume root npm hoisting: "
                f"{forbidden}"
            )
    if "npm exec --workspace @cinewatch/contracts --" not in runtime_gate:
        fail(
            "contract runtime gate must resolve openapi-typescript through "
            "@cinewatch/contracts workspace authority"
        )
    print("PASS  workspace-resolved contract runtime tool policy")

    pyproject = read("services/api/pyproject.toml")
    for requirement in (
        '"fastapi==0.141.1"',
        '"pydantic==2.13.5"',
        '"pydantic-settings==2.15.0"',
    ):
        if requirement not in pyproject:
            fail(f"schema-producing dependency is not exact: {requirement}")
    print("PASS  deterministic schema-producing dependency policy")

    system_routes = read("services/api/cinewatch_api/api/system.py")
    v1_routes = read("services/api/cinewatch_api/api/v1/system.py")
    for operation_id in ("system_health", "system_status"):
        if f'operation_id="{operation_id}"' not in system_routes:
            fail(f"stable operation ID missing: {operation_id}")
    if 'operation_id="v1_system_status"' not in v1_routes:
        fail("stable operation ID missing: v1_system_status")
    if 'openapi_version="3.1.0"' not in read(
        "services/api/cinewatch_api/application.py"
    ):
        fail("FastAPI OpenAPI version must be explicitly locked to 3.1.0")
    print("PASS  stable OpenAPI version and operation identity")

    schema = json.loads(
        read("packages/contracts/openapi/cinewatch-v1.openapi.json")
    )
    if schema.get("openapi") != "3.1.0":
        fail("canonical schema must be OpenAPI 3.1.0")

    expected = {
        "/health": "system_health",
        "/status": "system_status",
        "/api/v1/status": "v1_system_status",
    }
    paths = schema.get("paths", {})
    missing_foundation_paths = set(expected) - set(paths)
    if missing_foundation_paths:
        fail(
            "canonical schema lost required foundation paths: "
            + ", ".join(sorted(missing_foundation_paths))
        )
    for path, operation_id in expected.items():
        if paths[path]["get"].get("operationId") != operation_id:
            fail(f"operation ID drift for {path}")
    print("PASS  canonical OpenAPI foundation surface")

    generated = read("packages/contracts/src/generated/openapi.d.ts")
    for token in (
        "export interface paths",
        "export interface components",
        "system_health",
        "v1_system_status",
    ):
        if token not in generated:
            fail(f"generated TypeScript contract missing token: {token}")

    index = read("packages/contracts/src/index.d.ts")
    for alias in ("HealthResponse", "StatusResponse"):
        if f"export type {alias}" not in index:
            fail(f"governed contract alias missing: {alias}")

    client = read("apps/web/src/lib/api/system-client.ts")
    if 'from "@cinewatch/contracts"' not in client:
        fail("frontend system client must import generated contract types")
    if re.search(
        r"(?:interface|type)\s+"
        r"(?:HealthResponse|StatusResponse|CineWatchEnvironment)\b",
        client,
    ):
        fail("frontend must not hand-maintain duplicate system API response types")
    print("PASS  frontend generated-type consumption boundary")

    combined = "\n".join(
        read(path)
        for path in (
            "packages/contracts/README.md",
            "docs/architecture/CineWatch_TV_V1_OpenAPI_and_Typed_Contract_Foundation_001.md",
            "docs/architecture/decisions/CWTV_ADR_0005_OpenAPI_Canonical_Contract_and_Type_Generation.md",
        )
    ).lower()
    for forbidden in (
        "tmdb api key",
        "youtube api key",
        "aws_access_key_id",
        "database password",
    ):
        if forbidden in combined:
            fail(
                "forbidden secret-like material in contract documentation: "
                f"{forbidden}"
            )
    print("PASS  contract secret-exclusion policy")

    for public_path in paths:
        lowered = public_path.lower()
        if "/tmdb" in lowered or "/omdb" in lowered:
            fail(
                "public API contract must not expose upstream-provider route "
                f"identity: {public_path}"
            )
    print("PASS  public contract upstream-provider isolation")
    print("PASS  product-route extensibility preserves foundation invariants")

    print("PASS  CWTV.V1.2.6 OpenAPI and typed contract foundation policy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
