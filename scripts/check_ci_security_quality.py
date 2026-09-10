#!/usr/bin/env python3
"""Static CI/security/quality policy gate for CWTV.V1.2.8."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CHECKOUT_SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"
SETUP_NODE_SHA = "820762786026740c76f36085b0efc47a31fe5020"
SETUP_PYTHON_SHA = "5fda3b95a4ea91299a34e894583c3862153e4b97"

REQUIRED = [
    ".github/workflows/ci.yml",
    ".github/dependabot.yml",
    "SECURITY.md",
    "docs/architecture/CineWatch_TV_V1_CI_Security_Quality_Foundation_001.md",
    "docs/architecture/decisions/CWTV_ADR_0007_Linux_CI_Least_Privilege_and_Supply_Chain_Gates.md",
    "scripts/check_ci_security_quality.py",
    "scripts/check_ci_security_quality_runtime.sh",
    "tests/repository/test_ci_security_quality.py",
]


def ok(message: str) -> None:
    print(f"PASS  {message}")


def fail(message: str) -> None:
    raise ValueError(message)


def read(repo: Path, rel: str) -> str:
    return (repo / rel).read_text(encoding="utf-8")


def repository_files(repo: Path) -> list[Path]:
    if (repo / ".git").exists():
        completed = subprocess.run(
            ["git", "-C", str(repo), "ls-files"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if completed.returncode == 0:
            return [
                repo / line
                for line in completed.stdout.splitlines()
                if line and (repo / line).is_file()
            ]

    files: list[Path] = []
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo)
        if any(part in {".git", "node_modules", ".next", "__pycache__"} for part in rel.parts):
            continue
        files.append(path)
    return files


def scan_repository(repo: Path) -> None:
    forbidden_paths = {
        ".env",
        ".aws/credentials",
        ".pgpass",
    }
    secret_patterns = {
        "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
        "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "credential PostgreSQL URL": re.compile(
            r"postgres(?:ql)?://[^:\s/]+:[^@\s]+@", re.IGNORECASE
        ),
        "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    }
    assignment_patterns = {
        "AWS secret key assignment": re.compile(
            r"(?m)^\s*AWS_SECRET_ACCESS_KEY\s*[:=]\s*[\"']?[^<\s#][^\s#]{15,}"
        ),
        "AWS session token assignment": re.compile(
            r"(?m)^\s*AWS_SESSION_TOKEN\s*[:=]\s*[\"']?[^<\s#][^\s#]{20,}"
        ),
        "PostgreSQL password assignment": re.compile(
            r"(?m)^\s*PGPASSWORD\s*[:=]\s*[\"']?[^<\s#][^\s#]{5,}"
        ),
    }

    for path in repository_files(repo):
        rel = path.relative_to(repo).as_posix()
        if rel in forbidden_paths:
            fail(f"forbidden tracked secret file: {rel}")

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for label, pattern in secret_patterns.items():
            if pattern.search(text):
                fail(f"{label} pattern detected in {rel}")

        # Documentation and the checker itself may name secret variable keys.
        # Only concrete assignment-looking values are prohibited.
        for label, pattern in assignment_patterns.items():
            if pattern.search(text):
                fail(f"{label} detected in {rel}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scan-repository", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()

    try:
        for rel in REQUIRED:
            if not (repo / rel).is_file():
                fail(f"required CI/security path missing: {rel}")
        ok("CI/security/quality foundation paths")

        workflow = read(repo, ".github/workflows/ci.yml")
        dependabot = read(repo, ".github/dependabot.yml")
        gitignore = read(repo, ".gitignore") if (repo / ".gitignore").exists() else ""
        security_md = read(repo, "SECURITY.md")
        root_package = json.loads(read(repo, "package.json"))

        for token in ("push:", "pull_request:", "workflow_dispatch:"):
            if token not in workflow:
                fail(f"CI trigger missing: {token}")
        if "pull_request_target:" in workflow:
            fail("pull_request_target is prohibited")
        if "branches:\n      - main" not in workflow:
            fail("main branch CI authority is missing")
        ok("push/pull-request/manual CI trigger authority")

        if not re.search(r"(?m)^permissions:\s*\n\s+contents:\s+read\s*$", workflow):
            fail("top-level contents: read permission is missing")
        forbidden_permissions = (
            "write-all",
            "contents: write",
            "pull-requests: write",
            "security-events: write",
            "id-token: write",
        )
        for token in forbidden_permissions:
            if token in workflow:
                fail(f"forbidden workflow permission: {token}")
        if "persist-credentials: false" not in workflow:
            fail("checkout credential persistence is not disabled")
        ok("least-privilege workflow and checkout credential policy")

        action_refs = re.findall(r"(?m)^\s*uses:\s*([^@\s]+)@([0-9A-Fa-f]+)", workflow)
        if len(action_refs) < 6:
            fail("expected pinned action references are missing")
        for action, sha in action_refs:
            if len(sha) != 40:
                fail(f"action is not pinned to a full-length SHA: {action}")
        expected = {
            ("actions/checkout", CHECKOUT_SHA),
            ("actions/setup-node", SETUP_NODE_SHA),
            ("actions/setup-python", SETUP_PYTHON_SHA),
        }
        if not expected.issubset(set(action_refs)):
            fail("verified GitHub action SHA authority is incomplete")
        ok("full-length GitHub Action SHA pinning")

        if 'runs-on: ubuntu-24.04' not in workflow:
            fail("Ubuntu 24.04 runner authority is missing")
        if 'python-version: "3.14"' not in workflow:
            fail("Python 3.14 CI authority is missing")
        if 'node-version: "24.18.0"' not in workflow:
            fail("Node 24.18.0 CI authority is missing")
        ok("Linux runtime parity policy")

        required_quality = (
            "check_repository_tree.py",
            "check_backend_skeleton.py",
            "check_frontend_skeleton.py",
            "check_database_foundation.py",
            "check_contract_foundation.py",
            "check_termux_linux_workflow.py",
            "check_engineering_chronicle.py",
            "check_nexvox_engineering_corpus.py",
            "unittest discover -s tests/repository",
            "export_openapi_contract.py --check",
            "check_contract_runtime.sh",
            "check_backend_runtime.sh",
            "check_frontend_runtime.sh",
            "check_database_migrations.sh",
            "git diff --exit-code",
        )
        for token in required_quality:
            if token not in workflow:
                fail(f"quality gate missing: {token}")
        if "check_termux_linux_runtime.sh" in workflow:
            fail("Termux-only runtime checker must not run in GitHub-hosted CI")
        ok("Linux-portable quality and runtime gate coverage")

        if "${{ secrets." in workflow:
            fail("workflow must not consume repository/application secrets")
        forbidden_env = (
            "PGPASSWORD:",
            "AWS_ACCESS_KEY_ID:",
            "AWS_SECRET_ACCESS_KEY:",
            "AWS_SESSION_TOKEN:",
            "DATABASE_URL:",
        )
        for token in forbidden_env:
            if token in workflow:
                fail(f"workflow credential environment is prohibited: {token}")
        ok("untrusted pull-request secret exclusion")

        for token in (
            "python -m pip check",
            "pip-audit==2.10.1",
            "python -m pip_audit --strict services/api",
            "npm audit --omit=dev --audit-level=high",
            "Full npm advisory report",
            "continue-on-error: true",
            "npm audit --audit-level=high",
            "--scan-repository",
        ):
            if token not in workflow:
                fail(f"security gate missing: {token}")
        ok("blocking runtime dependency gates and informational toolchain advisory reporting")

        overrides = root_package.get("overrides", {})
        if "js-yaml" in overrides or "@redocly/openapi-core" in overrides:
            fail("obsolete V1.2.8 js-yaml override experiment must be removed")
        ok("no obsolete V1.2.8 dependency override remains")

        for ecosystem, directory in (
            ("npm", "/"),
            ("pip", "/services/api"),
            ("github-actions", "/"),
        ):
            if f"package-ecosystem: {ecosystem}" not in dependabot:
                fail(f"Dependabot ecosystem missing: {ecosystem}")
            if f"directory: {directory}" not in dependabot:
                fail(f"Dependabot directory missing: {directory}")
        if dependabot.count("interval: weekly") != 3:
            fail("Dependabot weekly cadence is incomplete")
        ok("Dependabot npm/pip/GitHub-Actions authority")

        required_ignore = (
            ".env",
            "*.key",
            "secrets/",
            ".aws/",
            "__pycache__/",
            ".venv/",
            "node_modules/",
        )
        for token in required_ignore:
            if token not in gitignore:
                fail(f".gitignore secret/artifact exclusion missing: {token}")
        ok("existing repository secret/artifact ignore policy")

        for token in (
            "database passwords",
            "GitHub personal access tokens",
            "AWS access keys",
            "Pull-request CI is read-only",
        ):
            if token not in security_md:
                fail(f"SECURITY.md policy token missing: {token}")
        ok("private V1 security reporting and repository policy")

        scan_repository(repo)
        ok("tracked secret-pattern and forbidden-file scan")

        test_text = read(repo, "tests/repository/test_ci_security_quality.py")
        if "check_ci_security_quality.py" not in test_text:
            fail("repository regression does not invoke CI/security checker")
        ok("repository regression coverage")

        ok("CWTV.V1.2.8 scope and storage hygiene policy")
        ok("CWTV.V1.2.8 CI / Security / Quality Foundation policy")
        return 0
    except (OSError, ValueError) as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
