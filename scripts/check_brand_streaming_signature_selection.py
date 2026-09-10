#!/usr/bin/env python3
"""Validate the CWTV.V1.3.1 A3 Signature Cinematic selection lock."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

LOCK = Path("docs/architecture/CineWatch_TV_V1_A3_Signature_Cinematic_Selection_Lock_001.md")
PARENT = Path("docs/architecture/CineWatch_TV_V1_Brand_and_Streaming_Signature_Authority_001.md")
MANIFEST = Path("docs/architecture/evidence/CineWatch_TV_V1_A3_Signature_Cinematic_Selected_Direction_001.json")
EVIDENCE = Path("docs/architecture/evidence/CineWatch_TV_V1_A3_Signature_Cinematic_Selected_Direction_001.png")

EXPECTED_EVIDENCE_SHA256 = "a0da8a1259fd72886d86af8591f32d32cf90487bc412a8fef07239ef07b0ed1c"
EXPECTED_WIDTH = 1448
EXPECTED_HEIGHT = 1086
EXPECTED_SOURCE_BASELINE = "233301bf98da58e7c871a03158518b09e7369c90"


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"PASS  {message}")


def require_file(repo: Path, rel: Path) -> Path:
    path = repo / rel
    if not path.is_file():
        fail(f"required path missing: {rel.as_posix()}")
    return path


def check_markdown_whitespace(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    if "\r" in raw:
        fail(f"Markdown must use LF line endings: {path.name}")
    for lineno, line in enumerate(raw.split("\n"), start=1):
        if line.endswith((" ", "\t")):
            fail(f"Markdown trailing whitespace: {path.name}:{lineno}")
    if not raw.endswith("\n"):
        fail(f"Markdown must end with one newline: {path.name}")


def png_dimensions(data: bytes) -> tuple[int, int]:
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        fail("selection evidence is not a PNG")
    if len(data) < 24 or data[12:16] != b"IHDR":
        fail("selection evidence PNG has invalid IHDR")
    return struct.unpack(">II", data[16:24])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo = args.repo.resolve()

    lock_path = require_file(repo, LOCK)
    parent_path = require_file(repo, PARENT)
    manifest_path = require_file(repo, MANIFEST)
    evidence_path = require_file(repo, EVIDENCE)
    ok("A3 selection authority and evidence paths")

    check_markdown_whitespace(lock_path)
    ok("selection-lock Markdown has LF endings and no trailing whitespace")

    lock = lock_path.read_text(encoding="utf-8")
    required_lock_tokens = (
        "**A3 — Signature Cinematic**",
        "**CineWatch TV**",
        "APPROVED SELECTION",
        "CWTV.V1.3.2 — CineWatch Production Brand Geometry Foundation",
        "raster pixels SHALL NOT become the geometry authority",
        "Production vector geometry remains pending CWTV.V1.3.2",
    )
    for token in required_lock_tokens:
        if token not in lock:
            fail(f"selection lock is missing required authority token: {token}")
    ok("A3 selection, casing, and production-boundary authority")

    parent = parent_path.read_text(encoding="utf-8")
    for token in ("Concept A — Aperture C", "A1", "A2", "A3", "A4", "A5", "A6"):
        if token not in parent:
            fail(f"parent streaming-signature authority missing token: {token}")
    ok("parent Aperture C refinement authority remains available")

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid selection evidence manifest: {exc}")

    if payload.get("schema_version") != 1:
        fail("selection manifest schema_version must be 1")
    if payload.get("product") != "CineWatch TV":
        fail("manifest product casing must be exactly CineWatch TV")
    if payload.get("canonical_human_facing_casing") != "CineWatch TV":
        fail("canonical human-facing casing must be exactly CineWatch TV")
    if payload.get("source_baseline_commit") != EXPECTED_SOURCE_BASELINE:
        fail("unexpected source baseline commit")

    selected = payload.get("selected_candidate", {})
    expected_selected = {"id": "A3", "name": "Signature Cinematic", "status": "SELECTED"}
    if selected != expected_selected:
        fail("manifest must select only A3 — Signature Cinematic")

    evidence = payload.get("evidence", {})
    if evidence.get("path") != EVIDENCE.as_posix():
        fail("manifest evidence path does not match governed evidence path")
    if evidence.get("classification") != "APPROVED_SELECTION_EVIDENCE":
        fail("manifest evidence classification is not approved selection evidence")
    if evidence.get("production_asset") is not False:
        fail("concept board must not be classified as a production asset")
    if evidence.get("production_geometry_authorized") is not False:
        fail("concept board must not authorize production geometry")
    ok("machine-readable A3 selection and non-production classification")

    data = evidence_path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_EVIDENCE_SHA256:
        fail(f"selection evidence SHA-256 mismatch: {digest}")
    if evidence.get("sha256") != digest:
        fail("manifest evidence SHA-256 does not match evidence bytes")

    w, h = png_dimensions(data)
    if (w, h) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        fail(f"selection evidence dimensions must be {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}")
    if evidence.get("width") != w or evidence.get("height") != h:
        fail("manifest dimensions do not match evidence PNG")
    ok("approved board SHA-256 and dimensions")

    if evidence.get("path", "").startswith("apps/web/public/"):
        fail("selection evidence must not be installed as a public production asset")
    ok("selection evidence remains outside production public-asset paths")

    print("PASS  CWTV.V1.3.1 A3 Signature Cinematic selection lock")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
