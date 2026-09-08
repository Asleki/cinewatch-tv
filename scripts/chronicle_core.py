#!/usr/bin/env python3
"""Shared integrity and event helpers for the CineWatch engineering chronicle."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVENT_ID_RE = re.compile(r"^CWTV-EVT-(\d{6})$")
MILESTONE_RE = re.compile(r"^CWTV\.V\d+(?:\.\d+)+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
EVENT_TYPE_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
ALLOWED_PRECISION = {"exact", "commit-derived", "unknown"}
ALLOWED_RESULTS = {"PASS", "FAILED", "INFO", "BLOCKED", "QUALIFIED", "PAUSED", "RESUMED"}
SENSITIVE_KEYS = {
    "authorization",
    "credential",
    "credentials",
    "database_url",
    "password",
    "secret",
    "token",
}


def repo_root_from_script(script_file: str | Path) -> Path:
    return Path(script_file).resolve().parents[1]


def ledger_path(repo_root: Path) -> Path:
    return repo_root / "docs/progress/activity/engineering-events.jsonl"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_timestamp(value: str) -> datetime:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone offset or Z")
    return parsed


def canonical_event_payload(event: dict[str, Any]) -> bytes:
    payload = {key: value for key, value in event.items() if key != "event_sha256"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def calculate_event_sha256(event: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_event_payload(event)).hexdigest()


def _walk_sensitive_keys(value: Any, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            child_path = f"{path}.{key}" if path else str(key)
            if normalized in SENSITIVE_KEYS:
                findings.append(child_path)
            findings.extend(_walk_sensitive_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_walk_sensitive_keys(child, f"{path}[{index}]"))
    return findings


def validate_event(event: dict[str, Any], *, expected_sequence: int | None = None) -> None:
    required = {
        "schema_version",
        "event_id",
        "sequence",
        "occurred_at",
        "timestamp_precision",
        "timestamp_source",
        "milestone",
        "event_type",
        "component",
        "result",
        "summary",
        "duration_seconds",
        "artifact",
        "commit",
        "correction",
        "evidence",
        "details",
        "previous_event_sha256",
        "event_sha256",
    }
    missing = sorted(required.difference(event))
    if missing:
        raise ValueError(f"event missing required keys: {', '.join(missing)}")

    if event["schema_version"] != "1.0":
        raise ValueError("unsupported event schema_version")

    event_id_match = EVENT_ID_RE.fullmatch(str(event["event_id"]))
    if not event_id_match:
        raise ValueError(f"invalid event_id: {event['event_id']!r}")

    sequence = event["sequence"]
    if not isinstance(sequence, int) or sequence < 1:
        raise ValueError("sequence must be a positive integer")
    if int(event_id_match.group(1)) != sequence:
        raise ValueError("event_id sequence and sequence field differ")
    if expected_sequence is not None and sequence != expected_sequence:
        raise ValueError(f"expected sequence {expected_sequence}, got {sequence}")

    precision = event["timestamp_precision"]
    if precision not in ALLOWED_PRECISION:
        raise ValueError(f"invalid timestamp_precision: {precision}")
    occurred_at = event["occurred_at"]
    if precision == "unknown":
        if occurred_at is not None:
            raise ValueError("unknown timestamp precision requires occurred_at=null")
    else:
        if not isinstance(occurred_at, str):
            raise ValueError("exact/commit-derived timestamps require an ISO timestamp")
        parse_timestamp(occurred_at)

    milestone = event["milestone"]
    if not isinstance(milestone, str) or not MILESTONE_RE.fullmatch(milestone):
        raise ValueError(f"invalid milestone: {milestone!r}")

    event_type = event["event_type"]
    if not isinstance(event_type, str) or not EVENT_TYPE_RE.fullmatch(event_type):
        raise ValueError(f"invalid event_type: {event_type!r}")

    if event["result"] not in ALLOWED_RESULTS:
        raise ValueError(f"invalid result: {event['result']!r}")

    summary = event["summary"]
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("summary must be non-empty")

    duration = event["duration_seconds"]
    if duration is not None and (not isinstance(duration, (int, float)) or duration < 0):
        raise ValueError("duration_seconds must be null or non-negative")

    artifact = event["artifact"]
    if artifact is not None:
        if not isinstance(artifact, dict) or not artifact.get("name"):
            raise ValueError("artifact must contain a name")
        sha = artifact.get("sha256")
        if sha is not None and (not isinstance(sha, str) or not SHA256_RE.fullmatch(sha)):
            raise ValueError("artifact sha256 must be 64 lowercase hex characters")

    commit = event["commit"]
    if commit is not None and (not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit)):
        raise ValueError("commit must be a 7-40 character lowercase hexadecimal Git SHA")

    if not isinstance(event["evidence"], list) or not all(isinstance(item, str) for item in event["evidence"]):
        raise ValueError("evidence must be a list of strings")
    if not isinstance(event["details"], dict):
        raise ValueError("details must be an object")

    sensitive = _walk_sensitive_keys(event["details"])
    if sensitive:
        raise ValueError(f"sensitive keys are not allowed in chronicle details: {', '.join(sensitive)}")

    event_sha = event["event_sha256"]
    if not isinstance(event_sha, str) or not SHA256_RE.fullmatch(event_sha):
        raise ValueError("event_sha256 must be 64 lowercase hex characters")
    if calculate_event_sha256(event) != event_sha:
        raise ValueError(f"event hash mismatch for {event['event_id']}")


def load_events(path: Path, *, verify_chain: bool = True) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    events: list[dict[str, Any]] = []
    previous_hash: str | None = None
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            raise ValueError(f"blank line in ledger at line {line_number}")
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON at ledger line {line_number}: {exc}") from exc
        validate_event(event, expected_sequence=line_number)
        if verify_chain and event["previous_event_sha256"] != previous_hash:
            raise ValueError(f"event hash-chain mismatch at {event['event_id']}")
        previous_hash = event["event_sha256"]
        events.append(event)
    return events


def make_event(
    *,
    sequence: int,
    previous_event_sha256: str | None,
    milestone: str,
    event_type: str,
    result: str,
    summary: str,
    component: str = "",
    occurred_at: str | None = None,
    timestamp_precision: str = "exact",
    timestamp_source: str = "manual",
    duration_seconds: float | int | None = None,
    artifact_name: str | None = None,
    artifact_sha256: str | None = None,
    commit: str | None = None,
    correction: str | None = None,
    evidence: list[str] | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if occurred_at is None and timestamp_precision != "unknown":
        occurred_at = utc_now_iso()
    artifact = None
    if artifact_name is not None:
        artifact = {"name": artifact_name, "sha256": artifact_sha256}

    event: dict[str, Any] = {
        "schema_version": "1.0",
        "event_id": f"CWTV-EVT-{sequence:06d}",
        "sequence": sequence,
        "occurred_at": occurred_at,
        "timestamp_precision": timestamp_precision,
        "timestamp_source": timestamp_source,
        "milestone": milestone,
        "event_type": event_type,
        "component": component,
        "result": result,
        "summary": summary.strip(),
        "duration_seconds": duration_seconds,
        "artifact": artifact,
        "commit": commit,
        "correction": correction,
        "evidence": evidence or [],
        "details": details or {},
        "previous_event_sha256": previous_event_sha256,
    }
    event["event_sha256"] = calculate_event_sha256(event)
    validate_event(event, expected_sequence=sequence)
    return event


def append_event(path: Path, **kwargs: Any) -> dict[str, Any]:
    events = load_events(path)
    sequence = len(events) + 1
    previous_hash = events[-1]["event_sha256"] if events else None
    event = make_event(sequence=sequence, previous_event_sha256=previous_hash, **kwargs)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")
    return event
