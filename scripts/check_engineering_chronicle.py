#!/usr/bin/env python3
"""Static policy and integrity checks for CWTV.V1.2.5.1 engineering chronicle foundation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from chronicle_core import ledger_path, load_events, repo_root_from_script

REQUIRED_PATHS = [
    "docs/progress/README.md",
    "docs/progress/CineWatch_TV_Engineering_Chronicle.md",
    "docs/progress/activity/engineering-events.jsonl",
    "docs/progress/activity/EVENT_SCHEMA.md",
    "docs/progress/dashboard/index.html",
    "docs/progress/dashboard/dashboard.css",
    "docs/progress/dashboard/dashboard.js",
    "docs/progress/dashboard/progress-data.json",
    "scripts/chronicle_core.py",
    "scripts/bootstrap_engineering_chronicle.py",
    "scripts/build_progress_dashboard.py",
    "scripts/record_engineering_activity.py",
    "scripts/run_and_record.py",
    "scripts/check_progress_dashboard_runtime.sh",
    "tests/repository/test_engineering_chronicle.py",
]

BOOTSTRAP_MILESTONE_PREFIX = [
    "CWTV.V1.1",
    "CWTV.V1.2.1",
    "CWTV.V1.2.2",
    "CWTV.V1.2.3",
    "CWTV.V1.2.4",
    "CWTV.V1.2.5",
    "CWTV.V1.2.5.1",
]


def fail(message: str) -> None:
    print(f"FAIL  {message}")
    raise SystemExit(1)


def pass_line(message: str) -> None:
    print(f"PASS  {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap-gate", action="store_true", help="Require the initial CWTV.V1.2.5.1 bootstrap state exactly.")
    args = parser.parse_args()
    repo = repo_root_from_script(__file__)

    missing = [path for path in REQUIRED_PATHS if not (repo / path).exists()]
    if missing:
        fail("missing chronicle paths: " + ", ".join(missing))
    pass_line("engineering chronicle paths")

    try:
        events = load_events(ledger_path(repo), verify_chain=True)
    except ValueError as exc:
        fail(str(exc))
    if not events:
        fail("chronicle ledger is empty")
    pass_line("append-only event schema and SHA-256 hash chain")

    ids = [event["event_id"] for event in events]
    if len(ids) != len(set(ids)):
        fail("duplicate event IDs detected")
    if events[-1]["sequence"] != len(events):
        fail("ledger sequence does not match event count")
    pass_line("unique contiguous event identity")

    milestone_order: list[str] = []
    for event in events:
        if event["milestone"] not in milestone_order:
            milestone_order.append(event["milestone"])
    if milestone_order[: len(BOOTSTRAP_MILESTONE_PREFIX)] != BOOTSTRAP_MILESTONE_PREFIX:
        fail("initial milestone lineage was reordered or incompletely backfilled")
    pass_line("initial historical milestone lineage is preserved and future append is allowed")

    unknown_times = [event for event in events if event["timestamp_precision"] == "unknown"]
    if not unknown_times:
        fail("expected preserved unknown historical timestamps are missing")
    if any(event["occurred_at"] is not None for event in unknown_times):
        fail("unknown historical timestamp was silently invented")
    pass_line("unknown historical times remain explicitly unknown")

    commit_events = [event for event in events if event["event_type"] == "COMMIT_CREATED"]
    if len(commit_events) < 6:
        fail("initial commit lineage is incomplete")
    if any(event["timestamp_precision"] != "commit-derived" for event in commit_events):
        fail("commit events must be marked commit-derived")
    pass_line("initial Git commit lineage and timestamp provenance")

    if not any(event["result"] == "FAILED" for event in events):
        fail("historical failure evidence missing")
    if not any(event["event_type"] == "CORRECTION_GENERATED" for event in events):
        fail("historical correction evidence missing")
    pass_line("failure and correction history preserved instead of rewritten")

    sensitive_terms = ["postgresql+psycopg://", "bearer ", "ghp_", "github_pat_", "aws_secret_access_key"]
    ledger_text = ledger_path(repo).read_text(encoding="utf-8").lower()
    for term in sensitive_terms:
        if term.lower() in ledger_text:
            fail(f"sensitive credential-like content detected in chronicle ledger: {term}")
    pass_line("chronicle secret-exclusion policy")

    wrapper_text = (repo / "scripts/run_and_record.py").read_text(encoding="utf-8")
    started_marker = 'event_type=f"{activity}_STARTED"'
    rebuild_marker = "pre_command_build = rebuild_projections(repo)"
    command_marker = "completed = subprocess.run(command, cwd=repo, check=False)"
    result_marker = "final_build = rebuild_projections(repo)"
    started_pos = wrapper_text.find(started_marker)
    rebuild_pos = wrapper_text.find(rebuild_marker)
    command_pos = wrapper_text.find(command_marker)
    result_pos = wrapper_text.find(result_marker)
    if min(started_pos, rebuild_pos, command_pos, result_pos) < 0:
        fail("run_and_record projection synchronization contract is incomplete")
    if not (started_pos < rebuild_pos < command_pos < result_pos):
        fail("run_and_record must rebuild projections after STARTED and before the wrapped command, then rebuild after result recording")
    pass_line("self-recording command projection synchronization policy")

    builder = repo / "scripts/build_progress_dashboard.py"
    completed = subprocess.run([sys.executable, str(builder), "--repo", str(repo), "--check"], cwd=repo, check=False)
    if completed.returncode != 0:
        fail("generated Markdown/JSON projections are stale")
    pass_line("deterministic Markdown and dashboard projections")

    data = json.loads((repo / "docs/progress/dashboard/progress-data.json").read_text(encoding="utf-8"))
    if data["summary"]["qualified_milestones"] < 6:
        fail("dashboard lost qualified historical milestones")
    if data["summary"]["tracked_milestones"] < 7:
        fail("dashboard lost the initial started-milestone lineage")
    if args.bootstrap_gate:
        if data["summary"]["current_milestone"] != "CWTV.V1.2.5.1":
            fail("bootstrap current milestone must be CWTV.V1.2.5.1")
        if data["summary"]["qualified_milestones"] != 6 or data["summary"]["tracked_milestones"] != 7:
            fail("bootstrap gate requires exactly six qualified and seven tracked milestones")
    pass_line("dashboard summary derives from append-only started milestones")

    html = (repo / "docs/progress/dashboard/index.html").read_text(encoding="utf-8")
    js = (repo / "docs/progress/dashboard/dashboard.js").read_text(encoding="utf-8")
    css = (repo / "docs/progress/dashboard/dashboard.css").read_text(encoding="utf-8")
    combined = "\n".join([html, js, css])
    if "progress-data.json" not in js:
        fail("dashboard does not load generated progress-data.json")
    if "noindex,nofollow" not in html:
        fail("private V1 dashboard must remain noindex/nofollow")
    if any(marker in combined for marker in ["https://", "http://", "cdn.", "fonts.googleapis"]):
        fail("dashboard foundation must not depend on external web assets")
    pass_line("self-contained private dashboard and noindex policy")

    tracked_generated = [path for path in repo.rglob("*") if path.is_file() and ("__pycache__" in path.parts or path.suffix == ".pyc")]
    # Generated Python files may exist locally after tests, but they must never be tracked.
    tracked = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z"],
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8").split("\0")
    bad_tracked = [path for path in tracked if path and ("/__pycache__/" in f"/{path}" or path.endswith(".pyc"))]
    if bad_tracked:
        fail("tracked Python cache artifacts detected: " + ", ".join(bad_tracked))
    pass_line("no tracked __pycache__ or .pyc artifacts")

    pass_line("CWTV.V1.2.5.1 Engineering Chronicle & Progress Dashboard Foundation policy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
