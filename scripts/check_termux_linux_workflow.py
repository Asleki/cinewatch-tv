#!/usr/bin/env python3
"""Static policy gate for CWTV.V1.2.7 Termux/Linux engineering workflow."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

EXPECTED_WINDOWS = [
    "api", "web", "postgres", "tests", "contracts",
    "extract", "git", "aws", "chronicle",
]

REQUIRED = [
    "docs/architecture/CineWatch_TV_V1_Termux_Linux_Engineering_Workflow_001.md",
    "docs/architecture/decisions/CWTV_ADR_0006_Termux_Host_Linux_Runtime_and_Named_Sessions.md",
    "scripts/termux/cwtv-session",
    "scripts/termux/cwtv-session-status",
    "scripts/termux/cwtv-enter-linux",
    "scripts/termux/cwtv-linux-bootstrap",
    "scripts/termux/cwtv-window-bootstrap",
    "scripts/termux/install_cwtv_commands.sh",
    "scripts/termux/config/postgres.env.example",
    "scripts/termux/config/aws.env.example",
    "scripts/check_termux_linux_workflow.py",
    "scripts/check_termux_linux_runtime.sh",
    "tests/repository/test_termux_linux_workflow.py",
]

SHELL_FILES = [
    "scripts/termux/cwtv-session",
    "scripts/termux/cwtv-session-status",
    "scripts/termux/cwtv-enter-linux",
    "scripts/termux/cwtv-linux-bootstrap",
    "scripts/termux/cwtv-window-bootstrap",
    "scripts/termux/install_cwtv_commands.sh",
    "scripts/check_termux_linux_runtime.sh",
]

WORKFLOW_FILES = [
    *SHELL_FILES,
    "scripts/termux/config/postgres.env.example",
    "scripts/termux/config/aws.env.example",
    "docs/architecture/CineWatch_TV_V1_Termux_Linux_Engineering_Workflow_001.md",
    "docs/architecture/decisions/CWTV_ADR_0006_Termux_Host_Linux_Runtime_and_Named_Sessions.md",
]


def pass_line(message: str) -> None:
    print(f"PASS  {message}")


def fail(message: str) -> None:
    raise ValueError(message)


def read(repo: Path, relative: str) -> str:
    return (repo / relative).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo = args.repo.resolve()

    try:
        for relative in REQUIRED:
            if not (repo / relative).is_file():
                fail(f"required workflow path missing: {relative}")
        pass_line("Termux/Linux workflow foundation paths")

        session = read(repo, "scripts/termux/cwtv-session")
        status = read(repo, "scripts/termux/cwtv-session-status")
        enter_linux = read(repo, "scripts/termux/cwtv-enter-linux")
        linux_bootstrap = read(repo, "scripts/termux/cwtv-linux-bootstrap")
        native_bootstrap = read(repo, "scripts/termux/cwtv-window-bootstrap")
        installer = read(repo, "scripts/termux/install_cwtv_commands.sh")
        architecture = read(repo, "docs/architecture/CineWatch_TV_V1_Termux_Linux_Engineering_Workflow_001.md")
        adr = read(repo, "docs/architecture/decisions/CWTV_ADR_0006_Termux_Host_Linux_Runtime_and_Named_Sessions.md")

        for shell_file in SHELL_FILES:
            completed = subprocess.run(
                ["bash", "-n", str(repo / shell_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                fail(f"shell syntax failed for {shell_file}: {completed.stderr.strip()}")
        pass_line("workflow shell syntax")

        if "EXPECTED=(api web postgres tests contracts extract git aws chronicle)" not in session:
            fail("launcher does not declare the locked nine-window order")
        for window in EXPECTED_WINDOWS:
            if window not in status:
                fail(f"status script does not recognize window: {window}")
        pass_line("locked nine-window tmux session contract")

        if "api|web|tests|contracts" not in enter_linux:
            fail("Linux role boundary is missing")
        if "postgres|extract|git|aws|chronicle" not in native_bootstrap:
            fail("native Termux role boundary is missing")
        if "/root/.venvs/cinewatch-api" not in linux_bootstrap:
            fail("CineWatch API venv authority is missing")
        if "/opt/node-v24.18.0-linux-arm64" not in linux_bootstrap:
            fail("governed Linux Node authority is missing")
        if "PGDATABASE=cinewatch_dev" not in read(repo, "scripts/termux/config/postgres.env.example"):
            fail("cinewatch_dev identity is missing from PostgreSQL template")
        pass_line("Termux host and Linux runtime separation")

        if "CWTV_API_PORT=8000" not in linux_bootstrap:
            fail("API development port contract is missing")
        if "CWTV_WEB_PORT=3000" not in linux_bootstrap:
            fail("web development port contract is missing")
        if "CWTV_CHRONICLE_PORT=8785" not in native_bootstrap:
            fail("Chronicle development port contract is missing")
        pass_line("development port ownership")

        pg_example = read(repo, "scripts/termux/config/postgres.env.example")
        aws_example = read(repo, "scripts/termux/config/aws.env.example")
        if "PGPASSWORD=" in pg_example:
            fail("PostgreSQL example must not contain PGPASSWORD assignment")
        for key in ("AWS_ACCESS_KEY_ID=", "AWS_SECRET_ACCESS_KEY=", "AWS_SESSION_TOKEN="):
            if key in aws_example:
                fail(f"AWS example must not contain credential assignment: {key[:-1]}")
        if "AWS_PROFILE=cinewatch-dev" not in aws_example:
            fail("AWS named profile contract is missing")
        pass_line("non-secret user configuration boundary")

        if "exec /bin/bash --noprofile --norc -i" not in linux_bootstrap:
            fail("Linux bootstrap must avoid uncontrolled profile re-import")
        if "exec bash --noprofile --norc -i" not in native_bootstrap:
            fail("native bootstrap must avoid uncontrolled profile re-import")
        for secret in (
            "unset PGPASSWORD",
            "unset GH_TOKEN",
            "unset GITHUB_TOKEN",
            "unset AWS_ACCESS_KEY_ID",
            "unset AWS_SECRET_ACCESS_KEY",
            "unset AWS_SESSION_TOKEN",
        ):
            if secret not in enter_linux or secret not in native_bootstrap:
                fail(f"secret-environment isolation missing: {secret}")
        pass_line("secret environment isolation")

        if "ln -sfn" not in installer or "$PREFIX/bin" not in installer:
            fail("Termux command installation policy is incomplete")
        pass_line("one-command launcher installation policy")

        combined = "\n".join(read(repo, path) for path in WORKFLOW_FILES)
        forbidden_patterns = {
            "AWS access-key token": r"\bAKIA[0-9A-Z]{16}\b",
            "GitHub token": r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b",
            "credential-bearing PostgreSQL URL": r"postgres(?:ql)?://[^:\s/]+:[^@\s]+@",
            "embedded AWS RDS hostname": r"\b[a-zA-Z0-9.-]+\.rds\.amazonaws\.com\b",
            "NPP database identity": r"\bnpp_dev\b",
            "NPP admin identity": r"\bnpp_admin\b",
            "NPP RDS identifier": r"\bnpp-postgres-dev\b",
        }
        for label, pattern in forbidden_patterns.items():
            if re.search(pattern, combined):
                fail(f"workflow contains forbidden {label}")
        pass_line("CineWatch/NPP and credential-value isolation")

        launcher_combined = "\n".join((session, enter_linux, linux_bootstrap, native_bootstrap))
        if re.search(r"/(?:discover|watch|explore|auth)\b", launcher_combined, re.IGNORECASE):
            fail("product feature route leaked into engineering launcher")
        pass_line("no product/provider/auth feature route scope")

        for token in (
            "Termux",
            "Ubuntu PRoot",
            "cwtv-linux",
            "cinewatch-tv",
            "cwtv-session",
            "cwtv-session-status",
            "cinewatch_dev",
            ".pgpass",
            "AWS profile",
            "NPP",
            "No servers are auto-started",
        ):
            if token not in architecture:
                fail(f"architecture document missing required token: {token}")
        if "Accepted" not in adr or "CWTV.V1.2.7" not in adr:
            fail("ADR acceptance identity is incomplete")
        pass_line("workflow architecture and ADR authority")

        test_text = read(repo, "tests/repository/test_termux_linux_workflow.py")
        if "check_termux_linux_workflow.py" not in test_text:
            fail("repository regression does not invoke workflow checker")
        pass_line("repository regression coverage")

        pass_line("CWTV.V1.2.7 Termux/Linux Engineering Workflow Foundation policy")
        return 0
    except (OSError, ValueError) as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
