#!/usr/bin/env python3
"""Validate CWTV.V1.3.2.1 A3 master geometry parameterization."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

AUTH = Path("docs/architecture/CineWatch_TV_V1_A3_Master_Geometry_Parameterization_001.md")
PARAMS = Path("docs/architecture/geometry/CineWatch_TV_V1_A3_Master_Geometry_Parameters_001.json")
SELECTION = Path("docs/architecture/CineWatch_TV_V1_A3_Signature_Cinematic_Selection_Lock_001.md")

EXPECTED_BASELINE = "eed31123509a5a7410f45d95a815164451055a47"
EXPECTED_PARAM_SHA256 = "a0d5768be2fec9b674ffbb55cdf680c878ca78673673b3b27eacac3a40a70e90"


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"PASS  {message}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON {path}: {exc}")


def check_md_whitespace(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    if "\r" in raw:
        fail(f"Markdown must use LF line endings: {path}")
    if not raw.endswith("\n"):
        fail(f"Markdown must end with newline: {path}")
    for lineno, line in enumerate(raw.split("\n"), start=1):
        if line.endswith((" ", "\t")):
            fail(f"Markdown trailing whitespace: {path}:{lineno}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo = args.repo.resolve()

    for rel in (AUTH, PARAMS, SELECTION):
        if not (repo / rel).is_file():
            fail(f"required path missing: {rel.as_posix()}")
    ok("A3 parameterization authority paths")

    check_md_whitespace(repo / AUTH)
    ok("A3 parameterization Markdown whitespace")

    selection = (repo / SELECTION).read_text(encoding="utf-8")
    for token in (
        "A3 — Signature Cinematic",
        "CineWatch TV",
        "Production vector geometry remains pending CWTV.V1.3.2",
    ):
        if token not in selection:
            fail(f"selection lock missing required token: {token}")
    ok("A3 selection and canonical casing remain locked")

    data = (repo / PARAMS).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_PARAM_SHA256:
        fail(f"parameter JSON SHA-256 mismatch: {digest}")
    payload = load_json(repo / PARAMS)
    ok("parameter JSON integrity")

    if payload.get("schema_version") != 1:
        fail("schema_version must be 1")
    if payload.get("algorithm_id") != "cinewatch-a3-annular-aperture-c/v1":
        fail("unexpected A3 geometry algorithm")
    if payload.get("status") != "CANDIDATE_PARAMETER_BASELINE":
        fail("parameter status must remain CANDIDATE_PARAMETER_BASELINE")
    if payload.get("production_asset_authorized") is not False:
        fail("parameterization must not authorize production assets")

    sel = payload.get("selection", {})
    if sel.get("candidate_id") != "A3":
        fail("only A3 may be parameterized")
    if sel.get("candidate_name") != "Signature Cinematic":
        fail("unexpected selected candidate name")
    if sel.get("canonical_human_facing_brand") != "CineWatch TV":
        fail("human-facing brand casing must be exactly CineWatch TV")
    ok("A3 parameter identity and casing")

    cs = payload.get("coordinate_system", {})
    if cs.get("view_box") != [0, 0, 1024, 1024]:
        fail("master viewBox must be 0 0 1024 1024")
    if cs.get("angle_unit") != "millidegree":
        fail("angles must use integer millidegrees")
    if cs.get("angle_positive_direction") != "clockwise":
        fail("angle direction must be clockwise")
    if cs.get("coordinate_quantum_milliunit") != 1:
        fail("coordinate quantum must be 0.001 design unit")
    if cs.get("rounding_mode") != "half_even":
        fail("rounding mode must be half_even")
    ok("deterministic coordinate-system contract")

    optical = payload.get("optical_frame", {})
    expected_optical = {
        "geometric_frame_center": [512, 512],
        "mark_center": [524, 512],
        "optical_offset": [12, 0],
        "outer_radius": 420,
        "inner_radius": 228,
        "ring_thickness": 192,
        "minimum_viewbox_margin": 80,
    }
    if optical != expected_optical:
        fail("optical-frame parameters differ from Revision 001 authority")

    outer_r = optical["outer_radius"]
    inner_r = optical["inner_radius"]
    if outer_r - inner_r != optical["ring_thickness"]:
        fail("ring thickness is inconsistent with radii")

    cx, cy = optical["mark_center"]
    margins = [
        cx - outer_r,
        cy - outer_r,
        1024 - (cx + outer_r),
        1024 - (cy + outer_r),
    ]
    if min(margins) < optical["minimum_viewbox_margin"]:
        fail(f"outer geometry violates minimum viewBox margin: {margins}")
    ok("optical frame, radii, and viewBox containment")

    opening = payload.get("opening", {})
    outer = opening.get("outer", {})
    inner = opening.get("inner", {})

    expected_outer = {
        "center_mdeg": 0,
        "width_mdeg": 80000,
        "lower_edge_mdeg": 40000,
        "upper_edge_mdeg": 320000,
        "occupied_arc_mdeg": 280000,
    }
    expected_inner = {
        "center_mdeg": 12000,
        "width_mdeg": 92000,
        "lower_edge_mdeg": 58000,
        "upper_edge_mdeg": 326000,
        "occupied_arc_mdeg": 268000,
    }
    if outer != expected_outer:
        fail("outer opening parameters differ from Revision 001")
    if inner != expected_inner:
        fail("inner opening parameters differ from Revision 001")
    ok("forward-opening authority")

    seg = payload.get("segmentation", {})
    for key in (
        "count",
        "outer_gap_mdeg",
        "inner_gap_mdeg",
        "outer_segment_span_mdeg",
        "inner_segment_span_mdeg",
        "outer_control_length_milli_thickness",
        "inner_control_length_milli_thickness",
    ):
        if not isinstance(seg.get(key), int):
            fail(f"segmentation field must be integer-backed: {key}")

    if seg["count"] != 6:
        fail("A3 parameter baseline must use six segments")
    if seg["connector_model"] != "cubic-tangent-bridge":
        fail("unexpected connector model")

    count = seg["count"]
    derived_outer_span = (
        outer["occupied_arc_mdeg"] - (count - 1) * seg["outer_gap_mdeg"]
    )
    derived_inner_span = (
        inner["occupied_arc_mdeg"] - (count - 1) * seg["inner_gap_mdeg"]
    )
    if derived_outer_span % count:
        fail("outer segment span is not exactly divisible in millidegrees")
    if derived_inner_span % count:
        fail("inner segment span is not exactly divisible in millidegrees")
    if derived_outer_span // count != seg["outer_segment_span_mdeg"]:
        fail("outer segment span does not derive from opening/gap parameters")
    if derived_inner_span // count != seg["inner_segment_span_mdeg"]:
        fail("inner segment span does not derive from opening/gap parameters")

    outer_starts = [
        outer["lower_edge_mdeg"]
        + i * (seg["outer_segment_span_mdeg"] + seg["outer_gap_mdeg"])
        for i in range(count)
    ]
    outer_ends = [x + seg["outer_segment_span_mdeg"] for x in outer_starts]
    inner_starts = [
        inner["lower_edge_mdeg"]
        + i * (seg["inner_segment_span_mdeg"] + seg["inner_gap_mdeg"])
        for i in range(count)
    ]
    inner_ends = [x + seg["inner_segment_span_mdeg"] for x in inner_starts]

    if outer_starts != [40000, 87600, 135200, 182800, 230400, 278000] or outer_ends != [82000, 129600, 177200, 224800, 272400, 320000]:
        fail("derived outer segment table changed")
    if inner_starts != [58000, 103600, 149200, 194800, 240400, 286000] or inner_ends != [98000, 143600, 189200, 234800, 280400, 326000]:
        fail("derived inner segment table changed")
    if outer_ends[-1] != outer["upper_edge_mdeg"]:
        fail("outer segmentation does not terminate at opening edge")
    if inner_ends[-1] != inner["upper_edge_mdeg"]:
        fail("inner segmentation does not terminate at opening edge")
    ok("exact six-segment millidegree derivation")

    render = payload.get("rendering_contract", {})
    if render.get("vector_first") is not True:
        fail("geometry must remain vector-first")
    if render.get("monochrome_geometry_authoritative") is not True:
        fail("monochrome geometry must remain authoritative")
    if render.get("gradient_authoritative") is not False:
        fail("gradient must remain non-authoritative")
    if render.get("embedded_raster_allowed") is not False:
        fail("embedded raster must remain prohibited")
    if render.get("stroke") != "none":
        fail("master geometry must not depend on strokes")
    ok("monochrome-first vector rendering contract")

    q = payload.get("qualification_contract", {})
    if q.get("master_direct_use_min_px") != 64:
        fail("master direct-use minimum must remain 64 px pending visual qualification")
    if q.get("tiny_variant_review_sizes_px") != [16, 24, 32]:
        fail("tiny-size review set changed")
    if q.get("tiny_variant_status") != "NOT_YET_DEFINED":
        fail("tiny variant must remain undefined in CWTV.V1.3.2.1")

    gap64 = inner_r * math.radians(seg["inner_gap_mdeg"] / 1000) * (64 / 1024)
    if gap64 < q.get("minimum_projected_inner_gap_at_64_px", 0):
        fail(f"projected inner gap at 64 px is too small: {gap64:.6f} px")
    ok(f"64 px projected inner-gap floor ({gap64:.3f} px)")

    forbidden_public = (
        repo / "apps/web/public/brand/cinewatch-mark.svg",
        repo / "apps/web/public/icons/favicon.svg",
    )
    introduced = [str(p.relative_to(repo)) for p in forbidden_public if p.exists()]
    if introduced:
        fail("CWTV.V1.3.2.1 may not introduce production geometry: " + ", ".join(introduced))
    ok("no final production SVG introduced by parameterization gate")

    next_gate = payload.get("next_gate", {})
    if next_gate.get("milestone") != "CWTV.V1.3.2.2":
        fail("next gate must be CWTV.V1.3.2.2")

    print("PASS  CWTV.V1.3.2.1 A3 Master Geometry Parameterization")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
