#!/usr/bin/env python3
"""Build deterministic Markdown and JSON projections from the append-only chronicle ledger."""

from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any

from chronicle_core import ledger_path, load_events, parse_timestamp, repo_root_from_script

PROGRESS_WEIGHTS = {
    "MILESTONE_STARTED": 5,
    "ARTIFACT_GENERATED": 15,
    "ARTIFACT_VERIFIED": 20,
    "ARTIFACT_EXTRACTED": 25,
    "DELIVERY_APPLIED": 35,
    "STATIC_QUALIFICATION_PASSED": 50,
    "REPOSITORY_REGRESSION_PASSED": 60,
    "BUILD_PASSED": 68,
    "RUNTIME_QUALIFICATION_PASSED": 76,
    "FILES_STAGED": 86,
    "COMMIT_CREATED": 95,
    "PUSH_COMPLETED": 98,
    "MILESTONE_QUALIFIED": 100,
}


def seconds_label(value: float | int | None) -> str:
    if value is None:
        return "not preserved"
    seconds = int(round(value))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts: list[str] = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def event_time_label(event: dict[str, Any]) -> str:
    if event["occurred_at"] is None:
        return "time not preserved"
    return event["occurred_at"]


def is_qualification_event(event: dict[str, Any]) -> bool:
    return (
        event["event_type"] == "MILESTONE_QUALIFIED"
        or event["result"] == "QUALIFIED"
    )


def is_correction_event(event: dict[str, Any]) -> bool:
    return "CORRECTION" in event["event_type"]


def milestone_progress(events: list[dict[str, Any]]) -> int:
    if any(is_qualification_event(event) for event in events):
        return 100
    progress = 0
    for event in events:
        progress = max(progress, PROGRESS_WEIGHTS.get(event["event_type"], 0))
        event_type = event["event_type"]
        if event_type.endswith("_PASSED"):
            progress = max(progress, 60)
        if event_type.endswith("_FAILED"):
            progress = max(progress, 35)
    return progress


def observed_difficulty(events: list[dict[str, Any]]) -> float:
    failures = sum(event["result"] == "FAILED" for event in events)
    blockers = sum(event["result"] == "BLOCKED" or event["event_type"] == "BLOCKER_IDENTIFIED" for event in events)
    corrections = {
        event["correction"] or event["summary"]
        for event in events
        if is_correction_event(event)
    }
    completed_cycles = sum(
        event["event_type"].endswith("_PASSED") and event["duration_seconds"] is not None for event in events
    )
    score = 1.0 + failures * 0.8 + blockers * 0.5 + len(corrections) * 0.45 + max(0, completed_cycles - 1) * 0.1
    return round(min(5.0, score), 1)


def session_metrics(events: list[dict[str, Any]]) -> dict[str, Any]:
    command_runtime = sum(float(event["duration_seconds"] or 0) for event in events)
    active_seconds = 0.0
    paused_seconds = 0.0
    break_count = 0
    active_start: datetime | None = None
    pause_start: datetime | None = None
    session_data_present = False

    for event in events:
        event_type = event["event_type"]
        occurred_at = event["occurred_at"]
        timestamp = parse_timestamp(occurred_at) if occurred_at else None

        if event_type in {"WORK_SESSION_STARTED", "WORK_RESUMED"} and timestamp:
            session_data_present = True
            if pause_start is not None:
                paused_seconds += max(0.0, (timestamp - pause_start).total_seconds())
                pause_start = None
            if active_start is None:
                active_start = timestamp
        elif event_type == "WORK_PAUSED" and timestamp:
            session_data_present = True
            break_count += 1
            if active_start is not None:
                active_seconds += max(0.0, (timestamp - active_start).total_seconds())
                active_start = None
            pause_start = timestamp
        elif event_type in {"WORK_SESSION_ENDED", "MILESTONE_QUALIFIED"} and timestamp:
            if active_start is not None:
                session_data_present = True
                active_seconds += max(0.0, (timestamp - active_start).total_seconds())
                active_start = None

    return {
        "recorded_command_runtime_seconds": round(command_runtime, 3),
        "recorded_command_runtime_label": seconds_label(command_runtime if command_runtime else None),
        "active_session_seconds": round(active_seconds, 3) if session_data_present else None,
        "active_session_label": seconds_label(active_seconds) if session_data_present else "not preserved",
        "paused_seconds": round(paused_seconds, 3) if session_data_present else None,
        "paused_label": seconds_label(paused_seconds) if session_data_present else "not preserved",
        "break_count": break_count,
        "session_data_present": session_data_present,
    }


def elapsed_metric(events: list[dict[str, Any]]) -> tuple[float | None, str]:
    started = next((event for event in events if event["event_type"] == "MILESTONE_STARTED" and event["occurred_at"]), None)
    qualified = next((event for event in reversed(events) if event["event_type"] == "MILESTONE_QUALIFIED" and event["occurred_at"]), None)
    if not started or not qualified:
        return None, "not preserved"
    delta = max(0.0, (parse_timestamp(qualified["occurred_at"]) - parse_timestamp(started["occurred_at"])).total_seconds())
    return round(delta, 3), seconds_label(delta)


def chronological_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # The append sequence is the authoritative narrative order. This preserves
    # historical unknown-time events in their verified milestone context rather
    # than inventing a timestamp-based position for them.
    return sorted(events, key=lambda event: event["sequence"])


def build_model(events: list[dict[str, Any]]) -> dict[str, Any]:
    milestone_events: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for event in events:
        milestone_events.setdefault(event["milestone"], []).append(event)

    milestones: list[dict[str, Any]] = []
    for milestone, group in milestone_events.items():
        qualified = any(is_qualification_event(event) for event in group)
        started_event = next((event for event in group if event["event_type"] == "MILESTONE_STARTED"), group[0])
        planned_complexity = started_event["details"].get("planned_complexity")
        elapsed_seconds, elapsed_label = elapsed_metric(group)
        metrics = session_metrics(group)
        failures = sum(event["result"] == "FAILED" for event in group)
        blockers = sum(event["result"] == "BLOCKED" or event["event_type"] == "BLOCKER_IDENTIFIED" for event in group)
        correction_names = sorted({
            event["correction"] or event["summary"]
            for event in group
            if is_correction_event(event)
        })
        milestones.append({
            "milestone": milestone,
            "status": "QUALIFIED" if qualified else "IN_PROGRESS",
            "progress_percent": milestone_progress(group),
            "planned_complexity": planned_complexity,
            "observed_difficulty": observed_difficulty(group),
            "failure_count": failures,
            "blocker_count": blockers,
            "correction_count": len(correction_names),
            "corrections": correction_names,
            "elapsed_seconds": elapsed_seconds,
            "elapsed_label": elapsed_label,
            **metrics,
        })

    qualified_count = sum(item["status"] == "QUALIFIED" for item in milestones)
    current = next(
        (
            item["milestone"]
            for item in reversed(milestones)
            if item["status"] != "QUALIFIED"
        ),
        None,
    )
    exact_times = [parse_timestamp(event["occurred_at"]) for event in events if event["occurred_at"]]
    as_of = max(exact_times).isoformat() if exact_times else None
    event_failures = [event for event in events if event["result"] == "FAILED"]
    artifacts = [event for event in events if event["artifact"] is not None]
    commits = [event for event in events if event["event_type"] == "COMMIT_CREATED" and event["commit"]]

    return {
        "schema_version": "1.0",
        "projection_as_of": as_of,
        "ledger": {
            "event_count": len(events),
            "head_event_id": events[-1]["event_id"] if events else None,
            "head_sha256": events[-1]["event_sha256"] if events else None,
        },
        "summary": {
            "tracked_milestones": len(milestones),
            "qualified_milestones": qualified_count,
            "tracked_completion_percent": round((qualified_count / len(milestones) * 100.0), 1) if milestones else 0.0,
            "current_milestone": current,
            "failed_events": len(event_failures),
            "passed_events": sum(event["result"] in {"PASS", "QUALIFIED"} for event in events),
            "corrections": sum(item["correction_count"] for item in milestones),
            "commits": len(commits),
            "artifacts": len(artifacts),
        },
        "milestones": milestones,
        "failures": event_failures,
        "artifacts": artifacts,
        "commits": commits,
        "events": chronological_events(events),
    }


def render_markdown(model: dict[str, Any]) -> str:
    summary = model["summary"]
    lines = [
        "# CineWatch TV Engineering Chronicle",
        "",
        "> Generated projection from `docs/progress/activity/engineering-events.jsonl`.",
        "> The JSONL ledger is the append-only source of truth; this Markdown file must not be edited by hand.",
        "",
        "## Current state",
        "",
        f"- **Current milestone:** `{summary['current_milestone'] or 'none'}`",
        f"- **Tracked milestones:** {summary['tracked_milestones']}",
        f"- **Qualified milestones:** {summary['qualified_milestones']}",
        f"- **Tracked milestone completion:** {summary['tracked_completion_percent']}%",
        f"- **Recorded failed events:** {summary['failed_events']}",
        f"- **Recorded corrections:** {summary['corrections']}",
        f"- **Commit events:** {summary['commits']}",
        f"- **Ledger head:** `{model['ledger']['head_event_id']}` / `{model['ledger']['head_sha256']}`",
        "",
        "Tracked completion intentionally excludes future milestones that have not started.",
        "",
        "## Milestones",
        "",
        "| Milestone | Status | Progress | Observed difficulty | Failures | Corrections | Elapsed | Recorded command runtime |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for item in model["milestones"]:
        lines.append(
            f"| `{item['milestone']}` | {item['status']} | {item['progress_percent']}% | {item['observed_difficulty']}/5 | "
            f"{item['failure_count']} | {item['correction_count']} | {item['elapsed_label']} | {item['recorded_command_runtime_label']} |"
        )

    lines += ["", "## Failure and correction history", ""]
    if not model["failures"]:
        lines.append("No failed events are currently recorded.")
    else:
        lines += [
            "| Milestone | Time | Component | Failure | Correction reference |",
            "|---|---|---|---|---|",
        ]
        for event in model["failures"]:
            lines.append(
                f"| `{event['milestone']}` | {event_time_label(event)} | {event['component'] or '—'} | "
                f"{event['summary']} | {event['correction'] or '—'} |"
            )

    lines += ["", "## Commit lineage", ""]
    for event in model["commits"]:
        lines.append(f"- `{event['commit']}` — {event['summary']} ({event_time_label(event)})")

    lines += ["", "## Artifacts", ""]
    if not model["artifacts"]:
        lines.append("No delivery artifacts are currently recorded.")
    else:
        for event in model["artifacts"]:
            artifact = event["artifact"]
            sha_text = f" — SHA-256 `{artifact['sha256']}`" if artifact.get("sha256") else ""
            lines.append(f"- `{artifact['name']}`{sha_text} — {event['event_type']} ({event_time_label(event)})")

    lines += ["", "## Event timeline", ""]
    for event in model["events"]:
        evidence = f" Evidence: {'; '.join(event['evidence'])}" if event["evidence"] else ""
        duration = f" Duration: {seconds_label(event['duration_seconds'])}." if event["duration_seconds"] is not None else ""
        lines.append(
            f"- **{event_time_label(event)}** · `{event['milestone']}` · `{event['event_type']}` · **{event['result']}** — "
            f"{event['summary']}{duration}{evidence}"
        )

    lines += [
        "",
        "## Integrity and timing rules",
        "",
        "- Historical events use `timestamp_precision=unknown` when an exact timestamp was not preserved.",
        "- Git commit times are recorded as `commit-derived`, not treated as proof of unrelated activity times.",
        "- Breaks are counted only when explicit pause/resume events exist; timestamp gaps are never assumed to be breaks.",
        "- Difficulty is an evidence-based score derived from recorded failures, blockers, corrections and repeated timed cycles; it is not a subjective quality grade.",
        "- Secrets, credentials, tokens and database URLs must never be written to the chronicle.",
        "",
    ]
    return "\n".join(lines)


def projection_paths(repo_root: Path) -> tuple[Path, Path]:
    return (
        repo_root / "docs/progress/CineWatch_TV_Engineering_Chronicle.md",
        repo_root / "docs/progress/dashboard/progress-data.json",
    )


def render_outputs(repo_root: Path) -> tuple[str, str]:
    events = load_events(ledger_path(repo_root))
    model = build_model(events)
    markdown = render_markdown(model)
    json_text = json.dumps(model, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    return markdown, json_text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=repo_root_from_script(__file__))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    repo_root = args.repo.resolve()
    markdown_path, json_path = projection_paths(repo_root)
    markdown, json_text = render_outputs(repo_root)

    if args.check:
        failures: list[str] = []
        if not markdown_path.exists() or markdown_path.read_text(encoding="utf-8") != markdown:
            failures.append(str(markdown_path.relative_to(repo_root)))
        if not json_path.exists() or json_path.read_text(encoding="utf-8") != json_text:
            failures.append(str(json_path.relative_to(repo_root)))
        if failures:
            print("FAIL  generated chronicle projections are stale:")
            for failure in failures:
                print(f"      {failure}")
            return 1
        print("PASS  chronicle projections match append-only ledger")
        return 0

    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown, encoding="utf-8", newline="\n")
    json_path.write_text(json_text, encoding="utf-8", newline="\n")
    print(f"PASS  wrote {markdown_path.relative_to(repo_root)}")
    print(f"PASS  wrote {json_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
