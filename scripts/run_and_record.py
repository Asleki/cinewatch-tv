#!/usr/bin/env python3
"""Run a command and append start/result events with exact timestamps and duration."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
import time
from pathlib import Path

from chronicle_core import append_event, ledger_path, repo_root_from_script, utc_now_iso


def rebuild_projections(repo: Path) -> int:
    """Rebuild generated Chronicle projections from the current ledger head."""
    completed = subprocess.run(
        [sys.executable, str(repo / "scripts/build_progress_dashboard.py"), "--repo", str(repo)],
        cwd=repo,
        check=False,
    )
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=repo_root_from_script(__file__))
    parser.add_argument("--milestone", required=True)
    parser.add_argument("--activity", required=True, help="Uppercase activity prefix, e.g. STATIC_QUALIFICATION")
    parser.add_argument("--component", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("FAIL  command is required after --", file=sys.stderr)
        return 2

    activity = args.activity.upper()
    repo = args.repo.resolve()
    ledger = ledger_path(repo)
    command_text = shlex.join(command)

    append_event(
        ledger,
        milestone=args.milestone,
        event_type=f"{activity}_STARTED",
        component=args.component,
        result="INFO",
        summary=f"{args.summary} started.",
        occurred_at=utc_now_iso(),
        timestamp_precision="exact",
        timestamp_source="run_and_record",
        details={"command": command_text},
    )

    # The STARTED event changes the ledger head. Rebuild before the wrapped
    # command executes so commands that validate projection freshness observe
    # a projection that already includes their own STARTED event.
    pre_command_build = rebuild_projections(repo)
    if pre_command_build != 0:
        append_event(
            ledger,
            milestone=args.milestone,
            event_type=f"{activity}_RECORDING_FAILED",
            component=args.component,
            result="FAILED",
            summary=f"{args.summary} was not started because the pre-command Chronicle projection rebuild failed.",
            occurred_at=utc_now_iso(),
            timestamp_precision="exact",
            timestamp_source="run_and_record",
            evidence=[f"projection_exit_code={pre_command_build}"],
            details={"command": command_text, "phase": "pre-command-projection-rebuild"},
        )
        rebuild_projections(repo)
        print("FAIL  STARTED event was recorded but pre-command dashboard rebuild failed", file=sys.stderr)
        return pre_command_build

    start_monotonic = time.monotonic()
    completed = subprocess.run(command, cwd=repo, check=False)
    duration = round(time.monotonic() - start_monotonic, 3)
    result_event = f"{activity}_{'PASSED' if completed.returncode == 0 else 'FAILED'}"
    result_value = "PASS" if completed.returncode == 0 else "FAILED"

    append_event(
        ledger,
        milestone=args.milestone,
        event_type=result_event,
        component=args.component,
        result=result_value,
        summary=f"{args.summary} {'passed' if completed.returncode == 0 else 'failed'}.",
        occurred_at=utc_now_iso(),
        timestamp_precision="exact",
        timestamp_source="run_and_record",
        duration_seconds=duration,
        evidence=[f"exit_code={completed.returncode}"],
        details={"command": command_text, "exit_code": str(completed.returncode)},
    )

    final_build = rebuild_projections(repo)
    if final_build != 0:
        print("FAIL  command result was recorded but final dashboard rebuild failed", file=sys.stderr)
        return final_build

    print(f"PASS  recorded {result_event} duration={duration:.3f}s")
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
