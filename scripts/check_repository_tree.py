#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    ".editorconfig",
    ".env.example",
    ".gitattributes",
    ".gitignore",
    ".npmrc",
    ".nvmrc",
    ".python-version",
    "README.md",
    "package.json",
    "package-lock.json",
    "apps/web/package.json",
    "apps/web/README.md",
    "services/api/pyproject.toml",
    "services/api/README.md",
    "packages/contracts/package.json",
    "packages/contracts/README.md",
    "scripts/check_runtime.sh",
    "scripts/build_nexvox_engineering_corpus.py",
    "scripts/check_nexvox_engineering_corpus.py",
    "scripts/build_nexvox_engineering_pdf.py",
    "nexvox/engineering/README.md",
    "nexvox/engineering/authority/CineWatch_NexVox_Engineering_Knowledge_Authority_001.md",
    "nexvox/engineering/policy/corpus-policy.yaml",
    "nexvox/engineering/schemas/records.schema.yaml",
    "nexvox/engineering/datasets/knowledge-records.jsonl",
    "nexvox/engineering/datasets/history-records.jsonl",
    "nexvox/engineering/checksums.sha256",
    "tests/repository/test_nexvox_engineering_corpus.py",
    "tests/repository/test_repository_tree.py",
    "docs/architecture/CineWatch_TV_V1_Engineering_Architecture_Selection_001.md",
    "docs/architecture/CineWatch_TV_V1_Repository_Tree_and_Toolchain_Foundation_001.md",
    "docs/architecture/decisions/CWTV_ADR_0001_Repository_Service_Boundary_Naming.md",
)

FORBIDDEN_PATHS = (
    "pnpm-lock.yaml",
    "pnpm-workspace.yaml",
)

EXPECTED_WORKSPACES = ["apps/web", "packages/contracts"]
EXPECTED_PACKAGE_MANAGER = "npm@12.0.2"


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON: {path.relative_to(ROOT)}: {exc}")


def main() -> int:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).is_file()]
    if missing:
        fail("missing required paths: " + ", ".join(missing))

    forbidden = [path for path in FORBIDDEN_PATHS if (ROOT / path).exists()]
    if forbidden:
        fail("forbidden package-manager artifacts present: " + ", ".join(forbidden))

    root_package = load_json(ROOT / "package.json")
    if root_package.get("private") is not True:
        fail("root package.json must set private=true")
    if root_package.get("packageManager") != EXPECTED_PACKAGE_MANAGER:
        fail(f"root packageManager must be {EXPECTED_PACKAGE_MANAGER}")
    if root_package.get("workspaces") != EXPECTED_WORKSPACES:
        fail(f"root workspaces must be {EXPECTED_WORKSPACES}")

    web_package = load_json(ROOT / "apps/web/package.json")
    contracts_package = load_json(ROOT / "packages/contracts/package.json")
    if web_package.get("name") != "@cinewatch/web":
        fail("unexpected web workspace name")
    if contracts_package.get("name") != "@cinewatch/contracts":
        fail("unexpected contracts workspace name")

    lock = load_json(ROOT / "package-lock.json")
    if lock.get("lockfileVersion") != 3:
        fail("package-lock.json must use lockfileVersion 3")
    if lock.get("packages", {}).get("") is None:
        fail("package-lock.json is missing root workspace metadata")

    try:
        api_project = tomllib.loads(
            (ROOT / "services/api/pyproject.toml").read_text(encoding="utf-8")
        )
    except (OSError, tomllib.TOMLDecodeError) as exc:
        fail(f"invalid services/api/pyproject.toml: {exc}")

    project = api_project.get("project", {})
    if project.get("name") != "cinewatch-api":
        fail("unexpected Python API project name")
    if project.get("requires-python") != ">=3.14,<3.15":
        fail("API Python policy must remain >=3.14,<3.15")

    nvmrc = (ROOT / ".nvmrc").read_text(encoding="utf-8").strip()
    python_version = (ROOT / ".python-version").read_text(encoding="utf-8").strip()
    if nvmrc != "24.18.0":
        fail(".nvmrc must declare the qualified Node 24.18.0 baseline")
    if python_version != "3.14.6":
        fail(".python-version must declare the qualified Python 3.14.6 baseline")

    print("PASS  required repository paths")
    print("PASS  npm workspace authority")
    print("PASS  package-lock authority")
    print("PASS  Python service metadata")
    print("PASS  runtime declarations")
    print("PASS  no pnpm authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
