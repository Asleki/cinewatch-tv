# CineWatch TV V1 Production Brand Asset Browser Qualification 001

**Document ID:** `CWTV-V1-PRODUCTION-BRAND-ASSET-BROWSER-QUALIFICATION-001`
**Milestone:** `CWTV.V1.3.2.3 — Production Brand Asset Build & Browser Qualification`
**Revision:** `R2`
**Status:** `PRODUCTION_BROWSER_QUALIFIED`
**Baseline commit:** `6f140affbeacb646bfd90089b0e9b008e88be955`
**Canonical brand casing:** `CineWatch TV`
**Human browser approval:** `APPROVED`
**Approved at:** `2026-09-11T01:18:00+02:00`

## Purpose

This milestone establishes the production-authorized CineWatch TV brand asset family after direct human inspection of the real files in the running Next.js application.

The approval sequence completed as:

`generated/exported files → repository tests → browser runtime proof → human approval → production authority`

The browser, not a static board, was the final human approval surface.

## Qualified identity system

The approved production system is:

- A3 — Signature Cinematic as the selected identity direction.
- R1A — Clear Chord as the master geometry for `64 px` and above.
- M1 — Six-Blade Wide Gap as the micro geometry for `16 / 24 / 32 px`.
- `CineWatch` remains one consistent text color within each background context.
- `TV` carries the aqua accent.
- The aperture-C carries the approved teal/aqua cinematic treatment.
- The canonical human-facing casing is exactly `CineWatch TV`.

## Browser proof

The real Next.js qualification route was:

`/brand-qualification`

The route loaded production files directly from:

- `apps/web/public/brand/`
- `apps/web/public/icons/`
- `apps/web/public/seo/`

The human reviewer inspected the real browser rendering and accepted:

- complete light and dark R1A lockups;
- full-color, black, and white/reversed marks;
- outlined light and dark wordmarks;
- direct M1 source-vector proof;
- native M1 `16 / 24 / 32 px` outputs;
- browser favicon presentation;
- application icons;
- maskable safe area;
- Open Graph export;
- square social export;
- responsive browser containment.

## 16 px decision

The native `16 × 16` M1 result is explicitly accepted for this milestone.

The reviewer acknowledged that 16 physical pixels necessarily provide less detail than 24 or 32 pixels and approved the current M1 result as sufficiently recognizable for the CineWatch aperture-C identity.

This decision does not prevent a later 16 px-only optical refinement.

A future 16 px refinement may be introduced without reopening:

- the approved `24 px` M1 result;
- the approved `32 px` M1 result;
- the approved R1A `64 px+` master regime.

## Favicon proof

Chrome visibly displayed the CineWatch aperture-C favicon in the Brand Qualification browsing surface.

The favicon presentation is therefore human-verified.

The exact file Chrome chooses from the supplied favicon sizes remains browser-controlled and is not treated as a deterministic source-size claim.

## Production authority

The machine-readable geometry system and asset manifest now record:

`PRODUCTION_BROWSER_QUALIFIED`

and:

`production_asset_authorized = true`

The production files may proceed to ordinary repository source commit qualification.

## Remaining engineering sequence

After applying this approval lock:

1. record `PRODUCTION_BRAND_ASSETS_APPROVED`;
2. run focused and full repository regression;
3. inspect the exact source scope;
4. commit the ordinary source changes;
5. regenerate the NexVox engineering corpus from that exact source commit;
6. build the required local-only NexVox PDF;
7. qualify the NexVox projection boundary;
8. commit the projection;
9. push the source/projection pair.

## Status

**PRODUCTION BROWSER QUALIFIED — HUMAN APPROVED**
