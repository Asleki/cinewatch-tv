#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANIFEST = ROOT / "apps/web/public/brand/asset-manifest.json"
SYSTEM = ROOT / "docs/architecture/geometry/CineWatch_TV_V1_A3_Production_Geometry_System_001.json"
ROUTE = ROOT / "apps/web/src/app/brand-qualification/page.tsx"

REQUIRED_BRAND = {
    "cinewatch-mark-r1a-full.svg",
    "cinewatch-mark-r1a-black.svg",
    "cinewatch-mark-r1a-white.svg",
    "cinewatch-mark-m1-full.svg",
    "cinewatch-wordmark-on-light.svg",
    "cinewatch-wordmark-on-dark.svg",
    "cinewatch-lockup-on-light.svg",
    "cinewatch-lockup-on-dark.svg",
    "asset-manifest.json",
}
REQUIRED_ICONS = {
    "cinewatch-micro-16.png": (16, 16),
    "cinewatch-micro-24.png": (24, 24),
    "cinewatch-micro-32.png": (32, 32),
    "cinewatch-favicon-16.png": (16, 16),
    "cinewatch-favicon-32.png": (32, 32),
    "cinewatch-favicon-48.png": (48, 48),
    "cinewatch-app-icon-180.png": (180, 180),
    "cinewatch-app-icon-192.png": (192, 192),
    "cinewatch-app-icon-512.png": (512, 512),
    "cinewatch-app-icon-light-512.png": (512, 512),
    "cinewatch-maskable-icon-512.png": (512, 512),
}
REQUIRED_SEO = {
    "cinewatch-og-1200x630.png": (1200, 630),
    "cinewatch-social-1080x1080.png": (1080, 1080),
}


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        fail(f"not PNG: {path.relative_to(ROOT)}")
    return struct.unpack(">II", data[16:24])


def check_svg(path: Path, expected_paths: int | None = None) -> None:
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        fail(f"invalid SVG {path.relative_to(ROOT)}: {exc}")
    root = tree.getroot()
    text = path.read_text(encoding="utf-8")
    if "<image" in text:
        fail(f"embedded raster forbidden in SVG: {path.relative_to(ROOT)}")
    if "stroke=" in text:
        fail(f"stroke dependency forbidden in SVG: {path.relative_to(ROOT)}")
    paths = [e for e in root.iter() if e.tag.endswith("path")]
    if expected_paths is not None and len(paths) != expected_paths:
        fail(f"{path.relative_to(ROOT)} expected {expected_paths} paths, found {len(paths)}")


def main() -> int:
    for path in (MANIFEST, SYSTEM, ROUTE):
        if not path.is_file():
            fail(f"required authority path missing: {path.relative_to(ROOT)}")

    system = json.loads(SYSTEM.read_text(encoding="utf-8"))
    if system.get("status") != "PRODUCTION_BROWSER_QUALIFIED":
        fail("production geometry system must be PRODUCTION_BROWSER_QUALIFIED after human browser approval")
    if system.get("production_asset_authorized") is not True:
        fail("production assets must be authorized after browser approval")
    if system.get("brand_name") != "CineWatch TV":
        fail("canonical brand name must be CineWatch TV")

    master = system.get("master", {})
    if master.get("id") != "R1A" or master.get("connector_model") != "straight-chord":
        fail("master geometry must be approved R1A Clear Chord")
    if master.get("use_min_px") != 64:
        fail("R1A master minimum use must remain 64 px")

    micro = system.get("micro", {})
    if micro.get("id") != "M1":
        fail("micro geometry must be approved M1")
    if micro.get("native_sizes_px") != [16, 24, 32]:
        fail("M1 native size regime must be exactly 16/24/32")
    if micro.get("segment_count") != 6 or micro.get("outer_gap_mdeg") != 11600:
        fail("M1 six-blade wide-gap geometry changed")

    brand_dir = ROOT / "apps/web/public/brand"
    icon_dir = ROOT / "apps/web/public/icons"
    seo_dir = ROOT / "apps/web/public/seo"

    actual_brand = {p.name for p in brand_dir.iterdir()}
    if actual_brand != REQUIRED_BRAND:
        fail(f"unexpected brand asset set: {sorted(actual_brand)}")

    actual_icons = {p.name for p in icon_dir.iterdir()}
    if actual_icons != set(REQUIRED_ICONS):
        fail(f"unexpected icon asset set: {sorted(actual_icons)}")

    actual_seo = {p.name for p in seo_dir.iterdir()}
    if actual_seo != set(REQUIRED_SEO):
        fail(f"unexpected SEO asset set: {sorted(actual_seo)}")

    for name in REQUIRED_BRAND - {"asset-manifest.json"}:
        path = brand_dir / name
        if name.startswith("cinewatch-mark-r1a-") or name == "cinewatch-mark-m1-full.svg":
            check_svg(path, expected_paths=6)
        else:
            check_svg(path)

    for name, expected in REQUIRED_ICONS.items():
        if png_size(icon_dir / name) != expected:
            fail(f"PNG dimensions mismatch for {name}")

    for name, expected in REQUIRED_SEO.items():
        if png_size(seo_dir / name) != expected:
            fail(f"PNG dimensions mismatch for {name}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("status") != "PRODUCTION_BROWSER_QUALIFIED":
        fail("asset manifest must be production-browser qualified")
    if manifest.get("production_asset_authorized") is not True:
        fail("asset manifest must record production asset authorization")
    entries = manifest.get("assets", [])
    by_path = {e["path"]: e for e in entries}

    expected_files = []
    for directory in (brand_dir, icon_dir, seo_dir):
        for path in directory.iterdir():
            if path == MANIFEST:
                continue
            expected_files.append(path)

    for path in expected_files:
        rel = path.relative_to(ROOT).as_posix()
        entry = by_path.get(rel)
        if entry is None:
            fail(f"manifest missing asset: {rel}")
        if entry.get("sha256") != sha256(path):
            fail(f"manifest SHA-256 mismatch: {rel}")

    route = ROUTE.read_text(encoding="utf-8")
    if 'process.env.NODE_ENV === "production"' not in route or "notFound()" not in route:
        fail("browser qualification route is not development-only")
    for token in (
        "/brand/cinewatch-lockup-on-light.svg",
        "/brand/cinewatch-lockup-on-dark.svg",
        "/brand/cinewatch-mark-r1a-full.svg",
        "/brand/cinewatch-mark-m1-full.svg",
        "/icons/cinewatch-micro-${size}.png",
        "/icons/cinewatch-app-icon-180.png",
        "/icons/cinewatch-maskable-icon-512.png",
        "/seo/cinewatch-og-1200x630.png",
    ):
        if token not in route:
            fail(f"browser route missing actual asset reference: {token}")

    print("PASS  R1A master and M1 micro size-regime authority")
    print("PASS  exact production-candidate brand asset inventory")
    print("PASS  SVG structure and no embedded-raster/stroke dependency")
    print("PASS  native PNG dimensions for micro, favicon, app, maskable, and SEO assets")
    print("PASS  asset manifest SHA-256 integrity")
    print("PASS  development-only browser route loads real public asset files")
    print("PASS  production authorization records completed human browser approval")
    lockup_light = (brand_dir / "cinewatch-lockup-on-light.svg").read_text(encoding="utf-8")
    if 'viewBox="0 0 3200 820"' not in lockup_light:
        fail("R1A light lockup framing must preserve the complete wordmark")

    css = (ROOT / "apps/web/src/app/brand-qualification/brand-qualification.module.css").read_text(encoding="utf-8")
    if "figure figcaption {" in css and ".card figure figcaption {" not in css:
        fail("CSS Module must not contain an unscoped figure figcaption selector")
    for token in (
        "object-fit: contain",
        "grid-template-columns: minmax(0, 1fr)",
        "aspect-ratio: 1200 / 630",
    ):
        if token not in css:
            fail(f"responsive browser qualification guard missing: {token}")

    print("PASS  complete lockup framing guard")
    print("PASS  CSS Module local-selector and responsive containment guards")
    approval = system.get("browser_gate", {}).get("human_approval", {})
    if approval.get("status") != "APPROVED":
        fail("human browser approval record missing")
    if approval.get("micro_16_px") != "ACCEPTED":
        fail("16 px M1 human acceptance missing")
    if approval.get("favicon_visual_proof") != "PASS":
        fail("browser favicon visual proof missing")
    print("PASS  human browser approval record including 16 px M1 and favicon proof")
    print("PASS  CWTV.V1.3.2.3-R2 production brand browser approval lock")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
