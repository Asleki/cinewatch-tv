#!/usr/bin/env python3
"""Append one timestamped event to the CineWatch engineering chronicle."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from chronicle_core import append_event, ledger_path, parse_timestamp, repo_root_from_script, utc_now_iso


def parse_details(values: list[str]) -> dict[str, Any]:
    details: dict[str, Any] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"detail must use KEY=VALUE form: {value!r}")
        key, raw = value.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("detail key may not be empty")
        details[key] = raw
    return details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=repo_root_from_script(__file__))
    parser.add_argument("--milestone", required=True)
    parser.add_argument("--event-type", required=True)
    parser.add_argument("--component", default="")
    parser.add_argument("--result", default="INFO", choices=["PASS", "FAILED", "INFO", "BLOCKED", "QUALIFIED", "PAUSED", "RESUMED"])
    parser.add_argument("--summary", required=True)
    parser.add_argument("--occurred-at", help="Offset-aware ISO-8601 timestamp; defaults to current UTC time.")
    parser.add_argument("--timestamp-precision", default="exact", choices=["exact", "commit-derived", "unknown"])
    parser.add_argument("--timestamp-source", default="manual")
    parser.add_argument("--duration-seconds", type=float)
    parser.add_argument("--artifact-name")
    parser.add_argument("--artifact-sha256")
    parser.add_argument("--commit")
    parser.add_argument("--correction")
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--detail", action="append", default=[])
    parser.add_argument("--no-build", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo.resolve()
    occurred_at = args.occurred_at
    if args.timestamp_precision == "unknown":
        occurred_at = None
    elif occurred_at is None:
        occurred_at = utc_now_iso()
    else:
        parse_timestamp(occurred_at)

    try:
        details = parse_details(args.detail)
        event = append_event(
            ledger_path(repo_root),
            milestone=args.milestone,
            event_type=args.event_type,
            component=args.component,
            result=args.result,
            summary=args.summary,
            occurred_at=occurred_at,
            timestamp_precision=args.timestamp_precision,
            timestamp_source=args.timestamp_source,
            duration_seconds=args.duration_seconds,
            artifact_name=args.artifact_name,
            artifact_sha256=args.artifact_sha256,
            commit=args.commit,
            correction=args.correction,
            evidence=args.evidence,
            details=details,
        )
    except (ValueError, OSError) as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1

    print(f"PASS  appended {event['event_id']} {event['event_type']} ({event['milestone']})")

    if not args.no_build:
        build_script = repo_root / "scripts/build_progress_dashboard.py"
        completed = subprocess.run([sys.executable, str(build_script), "--repo", str(repo_root)], check=False)
        if completed.returncode != 0:
            print("FAIL  event appended but chronicle projection rebuild failed", file=sys.stderr)
            return completed.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
