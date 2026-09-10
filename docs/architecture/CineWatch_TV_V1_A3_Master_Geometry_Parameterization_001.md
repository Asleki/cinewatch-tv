# CineWatch TV V1 A3 Master Geometry Parameterization 001

**Document ID:** `CWTV-V1-A3-MASTER-GEOMETRY-PARAMETERIZATION-001`
**Product:** CineWatch TV
**Repository:** `Asleki/cinewatch-tv`
**Parent milestone:** `CWTV.V1.3.2 — CineWatch Production Brand Geometry Foundation`
**Mini-milestone:** `CWTV.V1.3.2.1 — A3 Master Geometry Parameterization`
**Status:** `CANDIDATE_PARAMETER_BASELINE`
**Revision:** `001`
**Effective date:** `2026-09-10`
**Source baseline commit:** `eed31123509a5a7410f45d95a815164451055a47`
**Selected direction:** `A3 — Signature Cinematic`
**Canonical human-facing brand casing:** `CineWatch TV`

---

## 1. Purpose

This authority defines the first deterministic geometry parameter model for the selected A3 — Signature Cinematic CineWatch TV mark.

It does not create or approve a final production SVG.

Its purpose is to replace subjective raster tracing and unconstrained manual Bézier editing with a reproducible mathematical contract that can be rendered, inspected, corrected, and qualified in the next gate.

The approved A3 concept board remains directional evidence only.

---

## 2. Governing selection

The governing selection remains:

**Concept A — Aperture C → A3 — Signature Cinematic**

The canonical human-facing brand casing remains:

**CineWatch TV**

This mini-milestone does not reopen A1, A2, A4, A5, or A6 as alternative brand directions.

---

## 3. Parameter source of truth

The machine-readable parameter authority is:

`docs/architecture/geometry/CineWatch_TV_V1_A3_Master_Geometry_Parameters_001.json`

SHA-256:

`a0d5768be2fec9b674ffbb55cdf680c878ca78673673b3b27eacac3a40a70e90`

The JSON file is the source of truth for numeric geometry values in this revision.

Narrative values in this Markdown document explain the contract but SHALL NOT silently diverge from the JSON authority.

---

## 4. Geometry model

The A3 master candidate is modeled as a six-segment annular Aperture C.

The future deterministic renderer SHALL construct each segment from:

1. an outer circular arc;
2. a cubic tangent bridge from outer radius to inner radius;
3. an inner circular arc in the opposite path direction;
4. a cubic tangent bridge returning to the outer radius;
5. a closed fill-only path.

The model intentionally separates:

- identity geometry;
- color treatment;
- wordmark typography;
- raster derivatives.

Only identity geometry is parameterized here.

---

## 5. Coordinate system

The master design coordinate space is:

```text
viewBox: 0 0 1024 1024
origin: top-left
+x: right
+y: down
0 degrees: +x / east
positive angle: clockwise
angle storage: integer millidegrees
coordinate output quantum: 0.001 design unit
rounding: half-even
```

Integer millidegrees are used so the parameter source does not depend on binary floating-point serialization.

The renderer may use floating-point arithmetic internally, but serialized path coordinates SHALL be quantized deterministically.

---

## 6. Optical frame

The geometric frame center is:

```text
(512, 512)
```

The candidate mark center is:

```text
(524, 512)
```

This applies a deterministic `+12` design-unit horizontal optical correction.

The correction compensates for the visual mass lost through the forward-facing C opening.

Core radii:

```text
outer radius: 420
inner radius: 228
ring thickness: 192
inner/outer ratio: 0.542857
```

The outer-circle bounding box is:

```text
x: 104 .. 944
y: 92 .. 932
```

ViewBox margins are:

```text
left:   104
top:    92
right:  80
bottom: 92
```

The minimum margin is `80` design units.

---

## 7. Forward opening

The outer opening is centered on the positive x-axis:

```text
center: 0 degrees
width: 80 degrees
occupied C arc: 280 degrees
```

The inner opening is deliberately wider and phase-shifted:

```text
center: 12 degrees clockwise
width: 92 degrees
occupied C arc: 268 degrees
```

This asymmetry creates the A3 cinematic forward sweep without using raster-derived coordinates.

The inner opening SHALL NOT be interpreted as a separate symbol or play button.

---

## 8. Aperture segmentation

The parameter baseline uses six segments.

Outer contour:

```text
segment span: 42 degrees
inter-segment gap: 5.6 degrees
```

Inner contour:

```text
segment span: 40 degrees
inter-segment gap: 5.6 degrees
```

Derived outer segment ranges, in degrees:

```text
1:  40.0 ..  82.0
2:  87.6 .. 129.6
3: 135.2 .. 177.2
4: 182.8 .. 224.8
5: 230.4 .. 272.4
6: 278.0 .. 320.0
```

Derived inner segment ranges, in degrees:

```text
1:  58.0 ..  98.0
2: 103.6 .. 143.6
3: 149.2 .. 189.2
4: 194.8 .. 234.8
5: 240.4 .. 280.4
6: 286.0 .. 326.0
```

The differing outer and inner phase positions create the aperture sweep.

The segment boundaries remain deterministic and are not manually adjustable in downstream artwork.

---

## 9. Connector model

Each radial transition uses a cubic tangent bridge.

Control lengths are expressed as thousandths of ring thickness:

```text
outer control length: 340 / 1000 × ring thickness
inner control length: 300 / 1000 × ring thickness
```

For the current ring thickness:

```text
outer control length: 65.280
inner control length: 57.600
```

These values parameterize curvature behavior without hard-coding arbitrary Bézier control points.

The next renderer must derive control points from local circle tangents and these control-length ratios.

---

## 10. Monochrome-first authority

Geometry qualification begins in monochrome.

The mark SHALL remain recognizable when:

- every segment uses one solid color;
- no gradient is present;
- no glow is present;
- no shadow is present;
- no texture is present.

Gradient is presentation treatment, not identity structure.

A geometry that requires color separation to remain readable does not qualify.

---

## 11. Tiny-size implication

At the current `5.6°` gap:

```text
projected outer-gap arc at 64 px: 2.566 px
projected inner-gap arc at 64 px: 1.393 px
```

The current master candidate therefore sets direct master use at `64 px` and above pending visual qualification.

The sizes `16 px`, `24 px`, and `32 px` remain mandatory review sizes but are explicitly routed to a tiny-geometry decision gate.

This parameterization does not yet define the tiny variant.

---

## 12. Structural invariants

A deterministic renderer based on this parameter file SHALL preserve:

- a readable capital-C silhouette;
- forward opening to the right;
- stable central negative space;
- six distinct aperture segments;
- clockwise cinematic sweep;
- no accidental dominant play-triangle read;
- no strokes or hairline dependency;
- no embedded raster;
- no provider colors;
- viable monochrome rendering;
- deterministic coordinate quantization.

Any change to a governed parameter requires a new revision or explicit correction.

---

## 13. Prohibited derivation methods

Production geometry SHALL NOT be created by:

- tracing the approved PNG board;
- vectorizing raster edges automatically;
- copying generated image pixels into an SVG;
- manually nudging unrecorded Bézier points;
- using hidden editor transforms that cannot be reconstructed from parameters;
- importing a stock aperture or camera icon;
- depending on a proprietary design-file binary as the sole source of truth.

Visual comparison to the approved A3 evidence is allowed.

Coordinate extraction from the raster is not.

---

## 14. Parameterization versus production geometry

This mini-milestone authorizes a **candidate parameter baseline**, not a final brand asset.

It does not authorize:

- `apps/web/public/brand/cinewatch-mark.svg`;
- final wordmark outlines;
- favicon or PWA installation;
- SEO derivatives;
- final colors or gradients;
- motion;
- public deployment.

A future master vector must be generated from the governed parameter model and separately qualified.

---

## 15. Acceptance criteria for CWTV.V1.3.2.1

The parameterization gate qualifies when:

- the A3 selection lock remains present;
- the parameter JSON is valid;
- all governed numeric fields are integer-backed where specified;
- the six segment ranges derive exactly from the opening and gap parameters;
- the mark bounding circle remains within the 1024-unit viewBox;
- minimum viewBox margin is at least 80 units;
- ring thickness equals 192 units;
- monochrome-first authority is explicit;
- gradients remain non-authoritative;
- no production SVG is introduced by this delivery;
- the checker and repository regression pass;
- Markdown whitespace checks pass;
- Chronicle/dashboard evidence is recorded;
- NexVox is regenerated from the exact source commit.

---

## 16. Next gate

The next gate is:

**CWTV.V1.3.2.2 — A3 Deterministic Master Vector Construction & Visual Qualification**

That gate should implement a deterministic renderer from this parameter source, produce non-installed qualification artifacts, and compare the rendered mark against the approved A3 direction.

Human review remains required before any final production mark is installed.

---

## 17. Status

**CANDIDATE PARAMETER BASELINE**

The A3 master geometry now has a deterministic mathematical starting point.

No final SVG or public brand asset is authorized by this document.
