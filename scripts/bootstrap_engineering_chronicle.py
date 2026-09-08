#!/usr/bin/env python3
"""Create the initial CineWatch engineering chronicle from proven repository history and preserved project evidence."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

from chronicle_core import append_event, ledger_path, repo_root_from_script

BASELINE = "678500c0160ac002f8e8585ab4f7560ea22e4d6e"
FOUNDATION_GENERATED_AT = "2026-09-08T02:12:28Z"

COMMITS = {
    "56c4ffd": "CWTV.V1.1",
    "fd6e885": "CWTV.V1.2.1",
    "d050344": "CWTV.V1.2.2",
    "c0324fc": "CWTV.V1.2.3",
    "7b6a839": "CWTV.V1.2.4",
    "678500c": "CWTV.V1.2.5",
}


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def commit_info(repo: Path, short_sha: str) -> tuple[str, str, str]:
    full_sha = git(repo, "rev-parse", f"{short_sha}^{{commit}}")
    occurred_at = git(repo, "show", "-s", "--format=%cI", full_sha)
    subject = git(repo, "show", "-s", "--format=%s", full_sha)
    return full_sha, occurred_at, subject


def add(path: Path, **kwargs: Any) -> None:
    append_event(path, **kwargs)


def unknown(path: Path, *, milestone: str, event_type: str, result: str, summary: str, component: str = "", correction: str | None = None, evidence: list[str] | None = None, artifact_name: str | None = None, artifact_sha256: str | None = None, details: dict[str, Any] | None = None) -> None:
    add(
        path,
        milestone=milestone,
        event_type=event_type,
        component=component,
        result=result,
        summary=summary,
        occurred_at=None,
        timestamp_precision="unknown",
        timestamp_source="historical_backfill",
        correction=correction,
        evidence=evidence,
        artifact_name=artifact_name,
        artifact_sha256=artifact_sha256,
        details=details,
    )


def commit_and_qualify(path: Path, repo: Path, short_sha: str, milestone: str) -> None:
    full_sha, occurred_at, subject = commit_info(repo, short_sha)
    add(
        path,
        milestone=milestone,
        event_type="COMMIT_CREATED",
        component="repository",
        result="PASS",
        summary=subject,
        occurred_at=occurred_at,
        timestamp_precision="commit-derived",
        timestamp_source="git_commit",
        commit=full_sha,
    )
    add(
        path,
        milestone=milestone,
        event_type="MILESTONE_QUALIFIED",
        component="governance",
        result="QUALIFIED",
        summary=f"{milestone} closed and qualified at repository commit {short_sha}.",
        occurred_at=occurred_at,
        timestamp_precision="commit-derived",
        timestamp_source="git_commit",
        commit=full_sha,
        evidence=["Qualification time is commit-derived; unrelated activity times are not inferred from it."],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=repo_root_from_script(__file__))
    args = parser.parse_args()
    repo = args.repo.resolve()
    ledger = ledger_path(repo)

    if ledger.exists():
        print(f"FAIL  chronicle ledger already exists: {ledger}", file=sys.stderr)
        return 1

    try:
        head = git(repo, "rev-parse", "HEAD")
    except subprocess.CalledProcessError as exc:
        print(f"FAIL  unable to read Git repository: {exc}", file=sys.stderr)
        return 1
    if head != BASELINE:
        print(f"FAIL  bootstrap requires baseline {BASELINE}; found {head}", file=sys.stderr)
        return 1

    # CWTV.V1.1
    unknown(path=ledger, milestone="CWTV.V1.1", event_type="MILESTONE_STARTED", result="INFO", summary="CineWatch TV V1 governance foundation work began; exact start time was not preserved.")
    add(
        ledger,
        milestone="CWTV.V1.1",
        event_type="GOVERNANCE_APPROVED",
        component="blueprint",
        result="PASS",
        summary="CWTV-V1-BLUEPRINT-001 Revision 001 approved.",
        occurred_at="2026-09-07T10:32:59+02:00",
        timestamp_precision="exact",
        timestamp_source="preserved_project_record",
        evidence=["Approval code DEV_SIG007353F was preserved in the project record."],
    )
    commit_and_qualify(ledger, repo, "56c4ffd", "CWTV.V1.1")

    # CWTV.V1.2.1
    unknown(path=ledger, milestone="CWTV.V1.2.1", event_type="MILESTONE_STARTED", result="INFO", summary="Engineering architecture selection began; exact start time was not preserved.")
    add(
        ledger,
        milestone="CWTV.V1.2.1",
        event_type="ARCHITECTURE_APPROVED",
        component="engineering-architecture",
        result="PASS",
        summary="CWTV-V1-ENG-ARCH-001 R1 approved.",
        occurred_at="2026-09-07T20:10:58+02:00",
        timestamp_precision="exact",
        timestamp_source="preserved_project_record",
        evidence=["Approved architecture: Next.js App Router + TypeScript, FastAPI + Python, PostgreSQL, npm workspaces."],
    )
    commit_and_qualify(ledger, repo, "fd6e885", "CWTV.V1.2.1")

    # CWTV.V1.2.2
    unknown(path=ledger, milestone="CWTV.V1.2.2", event_type="MILESTONE_STARTED", result="INFO", summary="Repository tree and toolchain foundation began; exact start time was not preserved.")
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.2",
        event_type="RUNTIME_QUALIFICATION_PASSED",
        component="termux-toolchain",
        result="PASS",
        summary="Repository/runtime qualification passed on the Android Termux development environment.",
        evidence=["Git 2.55.0", "Python 3.14.6", "Node 24.18.0", "npm 12.0.2", "psql client 18.2", "repository test passed"],
    )
    commit_and_qualify(ledger, repo, "d050344", "CWTV.V1.2.2")

    # CWTV.V1.2.3
    unknown(path=ledger, milestone="CWTV.V1.2.3", event_type="MILESTONE_STARTED", result="INFO", summary="Backend service skeleton implementation began; exact start time was not preserved.")
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.3",
        event_type="DEPENDENCY_INSTALL_FAILED",
        component="native-termux-python",
        result="FAILED",
        summary="Native Termux installation fell back to building pydantic-core and failed on the Android Rust target boundary.",
        evidence=["PyPI wheel unavailable for cpython-314-aarch64-linux-android", "aarch64-unknown-linux-android target was not available through the attempted Rust toolchain path"],
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.3",
        event_type="ROOT_CAUSE_IDENTIFIED",
        component="runtime-boundary",
        result="INFO",
        summary="Backend native-extension runtime was separated from native Termux and assigned to Ubuntu PRoot Linux userland.",
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.3",
        event_type="CORRECTION_APPLIED",
        component="runtime-boundary",
        result="PASS",
        summary="Ubuntu 26.04 ARM64 PRoot with external Python virtualenv established as the phone backend runtime.",
        correction="CWTV.V1.2.3_RUNTIME_BOUNDARY_REFINEMENT",
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.3",
        event_type="RUNTIME_QUALIFICATION_PASSED",
        component="fastapi-runtime",
        result="PASS",
        summary="Backend tests and live Uvicorn smoke passed in Ubuntu PRoot.",
        evidence=["10 passed, 2 warnings", "live /health PASS", "request ID propagation PASS", "live /status PASS", "live /api/v1/status PASS"],
    )
    commit_and_qualify(ledger, repo, "c0324fc", "CWTV.V1.2.3")

    # CWTV.V1.2.4
    unknown(path=ledger, milestone="CWTV.V1.2.4", event_type="MILESTONE_STARTED", result="INFO", summary="Frontend application skeleton implementation began; exact start time was not preserved.")
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.4",
        event_type="ARTIFACT_GENERATED",
        component="delivery",
        result="PASS",
        summary="Initial frontend application skeleton delivery package generated.",
        artifact_name="CWTV.V1.2.4_Frontend_Application_Skeleton_001.zip",
        artifact_sha256="3c1d4f08f89e89d40675dac41471fe47b5d820f478d25cc9776af2b28618b416",
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.4",
        event_type="LINT_FAILED",
        component="eslint",
        result="FAILED",
        summary="ESLint 10.10.0 failed while loading react/display-name because the React plugin called a removed context filename API.",
        correction="CWTV.V1.2.4_R1",
        evidence=["TypeError: contextOrFilename.getFilename is not a function"],
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.4",
        event_type="CORRECTION_GENERATED",
        component="eslint",
        result="PASS",
        summary="R1 pinned ESLint 9.39.5 and corrected EOF whitespace defects.",
        correction="CWTV.V1.2.4_R1",
        artifact_name="CWTV.V1.2.4_R1_ESLint_Compatibility_Correction.zip",
        artifact_sha256="383e858bdb9f7a002566c25dbbac523acda82f343bcbfde111fb08c9489791f0",
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.4",
        event_type="DEPENDENCY_TREE_FAILED",
        component="npm-workspace-lock",
        result="FAILED",
        summary="A stale workspace-local ESLint 10.10.0 lock resolution remained after the source package pin and made npm report ELSPROBLEMS.",
        correction="CWTV.V1.2.4_R1_LOCK_RECONCILIATION",
        evidence=["apps/web/node_modules/eslint => 10.10.0 invalid", "root node_modules/eslint => 9.39.5"],
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.4",
        event_type="CORRECTION_APPLIED",
        component="npm-workspace-lock",
        result="PASS",
        summary="npm workspace lock was explicitly reconciled to ESLint 9.39.5 and a clean npm ci removed the invalid local resolution.",
        correction="CWTV.V1.2.4_R1_LOCK_RECONCILIATION",
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.4",
        event_type="RUNTIME_QUALIFICATION_PASSED",
        component="nextjs-runtime",
        result="PASS",
        summary="Frontend lint, typecheck, production build and live static-route smoke all passed.",
        evidence=["frontend lint PASS", "frontend typecheck PASS", "frontend production build PASS", "live / PASS", "live /robots.txt PASS", "live /manifest.webmanifest PASS"],
    )
    commit_and_qualify(ledger, repo, "7b6a839", "CWTV.V1.2.4")

    # CWTV.V1.2.5
    unknown(path=ledger, milestone="CWTV.V1.2.5", event_type="MILESTONE_STARTED", result="INFO", summary="PostgreSQL and migration foundation implementation began; exact start time was not preserved.")
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.5",
        event_type="ARTIFACT_GENERATED",
        component="delivery",
        result="PASS",
        summary="Initial PostgreSQL and migration foundation delivery package generated.",
        artifact_name="CWTV.V1.2.5_PostgreSQL_Migration_Foundation_001.zip",
        artifact_sha256="966f1fe111236d799e3001ccebbee1abc8251e09a47e1aa4a5c074770b9d5613",
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.5",
        event_type="API_TESTS_PASSED",
        component="database-foundation",
        result="PASS",
        summary="Full backend suite passed before the migration qualification wrapper ran.",
        evidence=["16 passed, 2 warnings"],
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.5",
        event_type="MIGRATION_QUALIFICATION_FAILED",
        component="offline-migration-environment",
        result="FAILED",
        summary="Offline migration qualification exported DATABASE_URL into the later settings test and violated the optional-database configuration contract.",
        correction="CWTV.V1.2.5_R1",
        evidence=["1 failed, 5 passed", "SecretStr('**********') was present where None was expected"],
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.5",
        event_type="ROOT_CAUSE_IDENTIFIED",
        component="offline-migration-environment",
        result="INFO",
        summary="The migration qualification script contaminated its own downstream test environment by exporting the offline-only DATABASE_URL globally.",
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.5",
        event_type="CORRECTION_GENERATED",
        component="offline-migration-environment",
        result="PASS",
        summary="R1 isolated the placeholder database URL to the Alembic command and added regression checks for environment isolation.",
        correction="CWTV.V1.2.5_R1",
        artifact_name="CWTV.V1.2.5_R1_Offline_Migration_Environment_Isolation_Correction.zip",
        artifact_sha256="73b233e12bb687b0195576790e3727a5c67eecfbf4fb613d4ac34a4dc63b25c5",
    )
    unknown(
        path=ledger,
        milestone="CWTV.V1.2.5",
        event_type="RUNTIME_QUALIFICATION_PASSED",
        component="database-and-backend-runtime",
        result="PASS",
        summary="Database migration qualification and backend runtime regression passed after R1.",
        evidence=["16 passed, 2 warnings", "Alembic single-head PASS", "offline PostgreSQL SQL generation PASS", "6 migration tests passed", "live backend smoke PASS"],
    )
    commit_and_qualify(ledger, repo, "678500c", "CWTV.V1.2.5")

    # Current chronicle milestone begins with an exact delivery-generation timestamp.
    add(
        ledger,
        milestone="CWTV.V1.2.5.1",
        event_type="MILESTONE_STARTED",
        component="engineering-chronicle",
        result="INFO",
        summary="Engineering Chronicle & Progress Dashboard Foundation began.",
        occurred_at=FOUNDATION_GENERATED_AT,
        timestamp_precision="exact",
        timestamp_source="delivery_generation",
        details={"planned_complexity": 2.5},
    )
    print(f"PASS  bootstrapped engineering chronicle with {len(open(ledger, encoding='utf-8').read().splitlines())} events")
    print("PASS  historical unknown timestamps remain explicitly unknown")
    print("PASS  Git commit timestamps were read from the local repository")
    return 0


if __name__ == "__main__":
    sys.exit(main())
