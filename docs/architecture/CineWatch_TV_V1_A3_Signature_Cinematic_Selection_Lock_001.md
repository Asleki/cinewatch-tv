# CineWatch TV V1 A3 Signature Cinematic Selection Lock 001

**Document ID:** `CWTV-V1-A3-SIGNATURE-CINEMATIC-SELECTION-LOCK-001`
**Product:** CineWatch TV
**Repository:** `Asleki/cinewatch-tv`
**Parent milestone:** `CWTV.V1.3 — Design System & Asset Foundation`
**Mini-milestone:** `CWTV.V1.3.1 — Design System Evidence & Competitive Intelligence`
**Decision:** `CWTV.V1.3.1-A3-SELECTION`
**Status:** `APPROVED`
**Revision:** `001`
**Effective date:** `2026-09-10`
**Source baseline commit:** `233301bf98da58e7c871a03158518b09e7369c90`

---

## 1. Purpose

This document records the human-approved CineWatch TV streaming-signature refinement decision.

It converts the Aperture C comparison exercise into an explicit engineering selection lock without promoting concept-board pixels into production geometry.

The approval scope is the **brand direction** only.

---

## 2. Locked selection

The parent identity family remains:

**Concept A — Aperture C**

The selected descendant is:

**A3 — Signature Cinematic**

A3 is the only Aperture C refinement authorized to continue into production-geometry engineering.

The other comparison descendants remain historical design evidence:

- A1 — Signature Balanced;
- A2 — Signature Geometric;
- A4 — Signature Compact;
- A5 — Signature Monochrome;
- A6 — Signature Premium.

They are not independent production alternatives unless a later governed correction explicitly reopens the selection.

---

## 3. Canonical human-facing casing

The canonical human-facing product and wordmark casing is:

**CineWatch TV**

Primary brand lockups SHALL preserve that casing.

The primary wordmark SHALL NOT be normalized to all-uppercase presentation.

Machine identifiers, filenames, environment variables, protocol fields, data keys, headings, or utility labels MAY use other case conventions where technically appropriate, but they SHALL NOT redefine the human-facing brand name.

---

## 4. A3 identity invariants

The production descendant of A3 SHALL preserve these identity invariants:

- the mark reads first as a distinctive `C`;
- the aperture/lens interpretation remains secondary;
- the forward-facing opening remains visually clear;
- the central negative space remains stable;
- the silhouette remains recognizable without a gradient;
- internal segmentation supports cinematic movement without becoming visual noise;
- no segment may make a generic play-button triangle the dominant read;
- geometry must remain viable in dark, light, and monochrome contexts;
- any optical correction must be deterministic and documented.

The selected board is directional evidence for these qualities. It is not a coordinate source for production vector geometry.

---

## 5. Approved selection evidence

The approved selected-direction board is tracked as:

`docs/architecture/evidence/CineWatch_TV_V1_A3_Signature_Cinematic_Selected_Direction_001.png`

Evidence SHA-256:

`a0da8a1259fd72886d86af8591f32d32cf90487bc412a8fef07239ef07b0ed1c`

Evidence dimensions:

`1448 × 1086`

Evidence format:

`PNG`

The board records the chosen A3 direction across illustrative lockups, appearance treatments, small-size views, icons, social presentation, and large-screen context.

The board is **design evidence only**.

Its raster pixels SHALL NOT become the geometry authority.

---

## 6. Evidence interpretation boundaries

The following board characteristics are illustrative until separately engineered and qualified:

- exact aperture segment boundaries;
- exact curve control points;
- exact opening angle;
- exact segment count;
- exact optical centering;
- gradients and highlight placement;
- typeface and letterform construction;
- precise color values;
- favicon geometry;
- application-icon geometry;
- maskable safe area;
- social-card imagery;
- large-screen mock interface;
- motion behavior.

The board may guide production work, but production geometry must be independently constructed as deterministic vector artwork.

---

## 7. Production non-authorizations

This selection lock does not authorize:

- a final SVG master;
- raster extraction of the mark from the board;
- final wordmark vector outlines;
- final typography;
- final hexadecimal brand colors;
- production gradients;
- animation;
- installed favicon assets;
- installed PWA/application icons;
- installed SEO assets;
- title artwork;
- provider artwork;
- public deployment.

Those belong to later qualification gates.

---

## 8. Relationship to Brand and Streaming Signature Authority 001

`docs/architecture/CineWatch_TV_V1_Brand_and_Streaming_Signature_Authority_001.md` remains the general candidate streaming-signature authority.

This selection lock resolves the previously open refinement decision within that authority:

- the Aperture C family remains selected;
- the A1–A6 comparison gate is complete;
- A3 — Signature Cinematic is selected;
- the canonical human-facing casing is now explicitly `CineWatch TV`;
- the refinement board requirement is satisfied as design evidence;
- production geometry and production assets remain pending.

Where the earlier candidate document uses an all-uppercase illustrative wordmark, this selection lock governs the human-facing casing.

---

## 9. Next implementation scope

The next mini-milestone should be:

**CWTV.V1.3.2 — CineWatch Production Brand Geometry Foundation**

Its scope should independently engineer and qualify the selected A3 descendant, including:

- deterministic master-vector construction;
- documented geometry parameters;
- stable `C` silhouette and negative space;
- monochrome-first structural qualification;
- dark and light rendering;
- native-size 16 px, 24 px, 32 px, and 64 px review;
- 192 px and 512 px application-icon review;
- maskable safe-area review;
- wordmark relationship and spacing;
- provenance and SHA-256 recording;
- reproducible raster derivatives only after the vector authority is qualified.

No production asset should be inferred directly from concept-board pixels.

---

## 10. Repository acceptance gate

This decision is accepted into repository history only after:

- this selection-lock document is present;
- the approved evidence PNG is present;
- its machine-readable evidence manifest is present;
- the evidence checksum and dimensions verify;
- the selection-policy checker passes;
- repository regression passes;
- Markdown trailing-whitespace validation passes;
- `git diff --check` passes;
- the Engineering Chronicle records the selection;
- the source decision commit is created before NexVox regeneration;
- the NexVox projection is regenerated from that exact source commit and committed separately.

---

## 11. Status

**APPROVED SELECTION**

A3 — Signature Cinematic is the selected CineWatch TV Aperture C descendant.

Production vector geometry remains pending CWTV.V1.3.2.
