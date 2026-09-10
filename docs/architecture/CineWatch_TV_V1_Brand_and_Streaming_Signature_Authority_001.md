# CineWatch TV V1 Brand and Streaming Signature Authority 001

**Document ID:** `CWTV-V1-BRAND-STREAMING-SIGNATURE-AUTHORITY-001`
**Product:** CineWatch TV
**Repository:** `Asleki/cinewatch-tv`
**Parent milestone:** `CWTV.V1.3 — Design System & Asset Foundation`
**Mini-milestone:** `CWTV.V1.3.1 — Design System Evidence & Competitive Intelligence`
**Status:** `CANDIDATE`
**Revision:** `001`
**Effective date:** `2026-09-10`

---

## 1. Purpose

This document defines the candidate brand and streaming-signature authority for CineWatch TV V1.

It converts the selected **Concept A — Aperture C** direction into an engineering specification that governs how the CineWatch identity must behave across:

- primary brand mark;
- wordmark and lockup;
- dark mode;
- light mode;
- monochrome use;
- favicon;
- PWA and application icons;
- SEO and social-share imagery;
- loading and motion language;
- responsive presentation;
- accessibility;
- asset provenance;
- production qualification.

This document does **not** declare the current concept-board artwork to be a production asset.

The concept board is design evidence. Production geometry must be independently refined, engineered, qualified, and versioned.

---

# 2. Selected direction

CineWatch TV selects:

**Concept A — Aperture C**

as the V1 brand identity direction.

The selected direction is intended to become more than a standalone logo.

It must become the recognizable **CineWatch Streaming Signature**: a coherent identity system spanning mark, wordmark, color, motion, focus, media framing, application icons, social presentation, and streaming interaction.

The selection does not yet lock:

- final vector geometry;
- final aperture-blade count;
- final exact proportions;
- final typography;
- final hexadecimal brand colors;
- final animation;
- final favicon construction;
- final SEO artwork;
- final production asset hashes.

Those are subject to qualification.

---

# 3. Brand character

CineWatch TV should feel:

- cinematic;
- intelligent;
- calm;
- trustworthy;
- exploratory;
- premium without becoming luxury-exclusive;
- technically precise;
- modern;
- rights-aware;
- content-first.

CineWatch TV should not feel like:

- a Netflix derivative;
- a generic play-button application;
- a gaming/neon interface;
- a generic entertainment-news portal;
- a plain metadata database;
- a provider-branded shell;
- a visual clone of any benchmark platform.

---

# 4. Signature meaning

The Aperture C signature should communicate multiple CineWatch ideas without becoming a literal illustration.

Candidate semantic interpretation:

| Signature element | Meaning |
|---|---|
| Outer `C` silhouette | CineWatch identity and cinematic frame |
| Aperture-like internal segmentation | Multiple perspectives into a title |
| Forward-facing opening | Discovery, movement, continuity |
| Central negative space | The work remains the focus |
| Circular/frame geometry | Viewing, cinema, lens, continuity |
| Controlled segmentation | Structured knowledge, not visual noise |

The visual mark should read first as a distinctive **CineWatch `C`**, and only secondarily as an aperture/lens reference.

It SHALL NOT become a stock camera-aperture icon.

---

# 5. Streaming-signature system

The CineWatch Streaming Signature is broader than the logo.

It consists of:

```text
CINEWATCH STREAMING SIGNATURE
        │
        ├── identity mark
        ├── wordmark
        ├── horizontal lockup
        ├── compact lockup
        ├── typography
        ├── color language
        ├── motion language
        ├── focus/interaction language
        ├── favicon
        ├── PWA/app icon
        ├── SEO/social identity
        ├── loading identity
        └── dark/light/monochrome behavior
```

A CineWatch screen should remain recognizably CineWatch even when the primary logo is not visible.

---

# 6. Geometry requirements

Production Aperture C geometry SHALL be engineered as vector-first artwork.

Required properties:

- recognizable `C` silhouette;
- balanced optical weight;
- stable negative space;
- strong circular/frame structure;
- no accidental play-button triangle as the dominant read;
- no fragile hairline details;
- no blade intersections that collapse at small sizes;
- no dependency on gradient to remain recognizable;
- no provider-specific visual language;
- clean rendering on dark and light backgrounds;
- viable single-color rendering.

## 6.1 Minimum-size behavior

The mark must be evaluated at:

- 16 px;
- 24 px;
- 32 px;
- 64 px;
- 128 px;
- 192 px;
- 512 px.

At 16–24 px, simplified geometry MAY be required.

A dedicated tiny-size variant may be created if the master geometry cannot survive at favicon scale without loss of identity.

## 6.2 Optical correction

Geometrically perfect circles or segments do not automatically produce optically balanced results.

Production SVG construction MAY use:

- optical overshoot;
- non-uniform segment spacing;
- adjusted blade widths;
- adjusted opening angle;
- corrected visual centering.

Any correction must remain deterministic and documented.

---

# 7. Aperture refinement families

The next visual refinement gate SHALL compare only Aperture C descendants.

Candidate refinement families:

| ID | Direction | Primary objective |
|---|---|---|
| `A1` | Signature Balanced | Best overall identity |
| `A2` | Signature Geometric | Technical precision and vector clarity |
| `A3` | Signature Cinematic | More expressive cinema character |
| `A4` | Signature Compact | Tiny-size/favicons/app icons |
| `A5` | Signature Monochrome | Strong single-color identity |
| `A6` | Signature Premium | Strong wordmark/brand lockup |

Each direction must be judged as the same identity family, not six unrelated logos.

---

# 8. Refinement scoring

Each refinement candidate should be scored using:

| Criterion | Weight |
|---|---:|
| Distinctiveness | 15 |
| CineWatch relevance | 15 |
| Tiny-size legibility | 15 |
| Dark/light compatibility | 10 |
| Monochrome strength | 10 |
| Favicon suitability | 10 |
| PWA/app-icon suitability | 10 |
| TV-distance readability | 5 |
| Wordmark compatibility | 5 |
| Longevity | 5 |

**Total: 100**

No candidate should qualify solely because it looks attractive at large size.

---

# 9. Wordmark authority

The brand wordmark should present:

**CINEWATCH TV**

or, where spatially appropriate:

**CINEWATCH**

with `TV` treated as a controlled descriptor.

The wordmark should be:

- legible;
- restrained;
- premium;
- modern;
- stable at small and large sizes;
- compatible with the mark;
- independent from provider typography.

The wordmark SHALL NOT:

- imitate Netflix letterforms;
- imitate Disney script;
- imitate HBO/Max typography;
- rely on novelty distortion;
- become unreadable at navigation scale.

A custom wordmark treatment MAY be derived from a qualified typeface, but final usage must respect licensing.

---

# 10. Lockup variants

The production identity should support, where qualified:

```text
MARK ONLY
[C]

HORIZONTAL
[C] CINEWATCH TV

COMPACT
[C]
CINEWATCH
TV

WORDMARK ONLY
CINEWATCH TV
```

Not every lockup must exist if it creates unnecessary duplication.

The smallest viable asset family should be preferred.

---

# 11. Dark mode

Dark mode is the primary cinematic brand context.

Candidate direction:

- near-black/midnight canvas;
- light primary wordmark;
- signal-aqua accent;
- restrained gold only where semantically appropriate.

The mark must remain recognizable without glow.

Glow effects MAY appear in motion/hero contexts but SHALL NOT be required for identity recognition.

---

# 12. Light mode

Light mode must be intentionally designed rather than produced through inversion.

Requirements:

- dark mark/wordmark;
- darker accessible signal color;
- clear surface separation;
- preserved brand identity;
- no weak pale-aqua text at insufficient contrast.

Dark and light variants SHALL share the same core geometry.

---

# 13. Monochrome authority

The mark must work in:

- pure white;
- pure black or near-black;
- single-color print;
- single-color UI icon use.

Monochrome qualification is mandatory.

If the mark is recognizable only through multiple colors, the geometry is not qualified.

---

# 14. Candidate color family

The initial design direction is:

```text
MIDNIGHT
    +
SIGNAL AQUA
    +
RESTRAINED CINEMA GOLD
```

Candidate dark values:

| Role | Candidate |
|---|---|
| Canvas | `#07090D` |
| Surface | `#0F141B` |
| Raised | `#171F29` |
| Primary text | `#F4F7FA` |
| Secondary text | `#A7B2BF` |
| Signal Aqua | `#23D8D5` |
| Cinema Gold | `#E9B95A` |

Candidate light values:

| Role | Candidate |
|---|---|
| Canvas | `#F7F8FA` |
| Surface | `#FFFFFF` |
| Raised | `#EFF3F6` |
| Primary text | `#11161C` |
| Secondary text | `#5C6875` |
| Signal | `#00787A` |

These values are **candidate evidence only** until component-level accessibility and brand qualification.

---

# 15. Color semantics

Signal Aqua should represent:

- CineWatch interaction;
- active focus;
- intelligent discovery;
- selected/interactive state where appropriate;
- brand recognition.

Cinema Gold should be secondary.

Possible uses:

- editorial emphasis;
- premium cinematic detail;
- awards/heritage context;
- controlled highlight.

Cinema Gold SHALL NOT become the default primary action color.

Provider brand colors must remain provider-owned and isolated from CineWatch identity.

---

# 16. Typography candidates

Candidate role model:

| Role | Candidate | Use |
|---|---|---|
| UI / navigation / metadata | Inter Variable | Primary interface |
| Editorial / Explore | Source Serif 4 | Long-form/editorial |
| Screenplay/document | Courier Prime | Screenplay semantics |

No font binary is authorized by this document.

Before adoption, each font must pass:

- license verification;
- redistribution review;
- WOFF2 suitability;
- weight/variable coverage;
- file-size review;
- fallback-stack definition;
- rendering review;
- dark/light readability review.

---

# 17. Favicon requirements

The favicon must derive from Aperture C but MAY use simplified geometry.

Required evaluations:

- 16×16;
- 32×32;
- browser tab on light chrome;
- browser tab on dark chrome;
- high-DPI rendering.

The favicon SHALL NOT contain:

- the full wordmark;
- microscopic internal detail;
- low-contrast gradients required for recognition.

---

# 18. PWA/application-icon requirements

The application icon must support:

- 192×192;
- 512×512;
- maskable 512×512;
- square social/profile crop;
- Android adaptive-safe composition where applicable.

The mark must have sufficient internal safe-area margin.

The application icon should not rely on text.

---

# 19. SEO and social-share identity

The public SEO asset family should include a qualified default CineWatch visual identity.

Candidate baseline:

- Open Graph: `1200 × 630`;
- square social/profile asset;
- light-brand fallback where useful.

The default SEO card should communicate:

- CineWatch identity;
- cinematic tone;
- product positioning;
- no false playback promise.

Future title-specific SEO cards may include title imagery only when that imagery is rights-qualified for such use.

---

# 20. SEO safe-area policy

Important text and brand content should remain within a central safe region so previews survive:

- social crop variations;
- mobile messaging previews;
- rounded thumbnail crops;
- partial metadata overlays.

Text should never be placed flush against the 1200×630 boundary.

---

# 21. Motion signature

The Aperture C may eventually support restrained motion.

Candidate motion ideas:

- aperture segments assemble into `C`;
- subtle rotational alignment;
- light signal passes through the opening;
- controlled reveal of the wordmark;
- progress/loading interpretation.

Motion SHALL NOT:

- make the mark unreadable;
- rotate continuously without purpose;
- mimic a generic buffering spinner;
- ignore `prefers-reduced-motion`;
- delay access to content.

A static mark remains the authority.

---

# 22. Loading identity

The loading system MAY reference Aperture C geometry.

It should feel like CineWatch rather than a generic spinner.

Possible state model:

```text
STATIC MARK
    ↓
SHORT SIGNAL / APERTURE MOTION
    ↓
CONTENT READY
```

For reduced motion:

```text
STATIC MARK
    ↓
SUBTLE OPACITY/PROGRESS STATE
    ↓
CONTENT READY
```

---

# 23. Focus and interaction signature

CineWatch identity should extend into interaction.

Candidate focus/selection language:

- signal-aqua focus ring;
- controlled surface elevation;
- subtle image-aware edge treatment;
- clear selected state;
- no provider-color takeover.

Focus must remain visible in both themes.

Color alone SHALL NOT be the only indicator of selection.

---

# 24. Media framing

CineWatch should develop a recognizable relationship between its mark and media geometry.

Candidate framing ideas:

- controlled corner/radius system;
- subtle aperture-inspired masks or transitions where appropriate;
- cinematic edge gradients;
- consistent poster/still aspect-ratio handling.

The UI SHALL NOT apply the Aperture C shape as a decorative mask everywhere.

Brand motifs must be restrained.

---

# 25. Production asset hierarchy

Recommended source hierarchy:

```text
MASTER VECTOR
        ↓
QUALIFIED SVG DELIVERY ASSETS
        ↓
RASTER DERIVATIVES
        ↓
PWA / FAVICON / SEO DERIVATIVES
```

The vector master is the geometry authority.

Raster assets are derivatives.

---

# 26. Candidate public asset structure

```text
apps/web/public/
├── brand/
│   ├── cinewatch-mark.svg
│   ├── cinewatch-wordmark.svg
│   ├── cinewatch-lockup.svg
│   └── cinewatch-monochrome.svg
│
├── icons/
│   ├── favicon.svg
│   ├── favicon-32.png
│   ├── apple-touch-icon.png
│   ├── icon-192.png
│   ├── icon-512.png
│   └── icon-maskable-512.png
│
└── seo/
    ├── cinewatch-default-og.webp
    ├── cinewatch-default-og-light.webp
    └── cinewatch-default-square.webp
```

Exact filenames remain candidate until implementation.

---

# 27. Asset provenance

Every production brand asset must have provenance metadata.

Minimum fields:

```yaml
asset_id:
asset_role:
source_master:
derivative_of:
created_by:
creation_method:
created_at:
license_or_ownership:
rights_status:
width:
height:
format:
bytes:
sha256:
qualified_at:
qualification_status:
notes:
```

The final asset manifest may be YAML, JSON, or another governed machine-readable format.

---

# 28. Ownership and rights

CineWatch production brand assets must have clear ownership/permission status.

Externally generated concept imagery is design evidence until:

- final geometry is intentionally selected;
- ownership/usage conditions are understood;
- the production vector is independently engineered;
- the asset is qualified and hashed.

Third-party provider logos remain third-party assets and are not part of CineWatch brand ownership.

---

# 29. Accessibility

Brand presentation must meet accessibility requirements.

Required:

- adequate logo/background contrast;
- meaningful text alternative where the logo conveys identity;
- decorative handling where surrounding text already names CineWatch;
- no critical meaning conveyed solely by color;
- reduced-motion behavior;
- visible keyboard focus where the logo is interactive;
- legibility at target sizes.

The logo itself should not be overloaded with textual information.

---

# 30. Responsive brand behavior

The identity must adapt by available space.

Candidate behavior:

| Context | Brand treatment |
|---|---|
| Small mobile | mark or compact lockup |
| Standard mobile | mark + concise wordmark |
| Tablet | horizontal lockup |
| Desktop | full lockup |
| Large screen | full lockup with distance-readable spacing |
| Favicon | simplified mark |
| PWA | mark only |
| SEO | mark + wordmark + optional product descriptor |

Responsive branding is recomposition, not arbitrary scaling.

---

# 31. Prohibited transformations

Production brand assets SHALL NOT be:

- stretched;
- skewed;
- rotated arbitrarily;
- recolored with provider colors;
- given uncontrolled gradients;
- placed over insufficient-contrast imagery;
- surrounded by random glow;
- converted into a generic play icon;
- cropped through essential mark geometry;
- redrawn independently per page;
- modified without provenance/versioning.

---

# 32. Signature distinctiveness test

Before final approval, the identity should be tested without the wordmark.

Question:

> If the word `CineWatch` is removed, does the mark still feel sufficiently distinctive to become recognizable through repeated product use?

The answer must be yes before final qualification.

---

# 33. Tiny-size qualification

The production mark should be exported at 16, 24, 32, and 64 px and viewed at native size.

Qualification should check:

- silhouette readability;
- segment separation;
- center balance;
- opening visibility;
- absence of blur-induced merging;
- dark/light rendering.

No zoomed preview may substitute for native-size qualification.

---

# 34. TV-distance qualification

The mark and wordmark should be tested at representative large-screen viewing distance.

Required concerns:

- word spacing;
- letter spacing;
- mark recognition;
- focus-state visibility;
- contrast;
- reduced fine detail.

TV-distance qualification does not imply a native TV application is part of V1.

---

# 35. Brand signature versus provider identity

CineWatch may display provider identity when needed for rights-aware actions.

Example:

```text
CineWatch identity
    ↓
Open on provider
    ↓
Provider logo / provider color
```

Provider branding must remain visually subordinate to CineWatch application identity while remaining clear enough to communicate the handoff destination.

---

# 36. Brand signature versus content artwork

Content artwork should remain the strongest visual material on many discovery/title surfaces.

CineWatch brand expression should therefore often appear through:

- spacing;
- typography;
- focus;
- surface language;
- motion;
- controls;
- transitions;
- rights-state design.

The CineWatch logo SHALL NOT be watermarked over every media image.

---

# 37. Initial production qualification matrix

Before assets are accepted:

| Test | Required |
|---|---|
| SVG validity | PASS |
| SVG deterministic formatting | PASS |
| No embedded raster in vector master | PASS |
| Dark-mode preview | PASS |
| Light-mode preview | PASS |
| Monochrome preview | PASS |
| 16 px preview | PASS |
| 24 px preview | PASS |
| 64 px preview | PASS |
| 192 px app preview | PASS |
| 512 px app preview | PASS |
| Maskable safe-area preview | PASS |
| 1200×630 SEO preview | PASS |
| Contrast review | PASS |
| Reduced-motion alternative | PASS if motion exists |
| Asset manifest entry | PASS |
| SHA-256 recorded | PASS |
| Rights/ownership state | PASS |

---

# 38. Refinement-board requirement

The next visual artifact after this authority should compare:

```text
A1 — Signature Balanced
A2 — Signature Geometric
A3 — Signature Cinematic
A4 — Signature Compact
A5 — Signature Monochrome
A6 — Signature Premium
```

Each must be shown in:

- black on white;
- white on black;
- candidate signal-aqua treatment;
- 16 px;
- 24 px;
- 64 px;
- wordmark lockup;
- favicon;
- application icon;
- maskable crop;
- SEO card;
- large-screen context.

The refinement board remains evidence until one candidate is selected.

---

# 39. Relationship to existing V1.3 authorities

`CineWatch_TV_V1_Competitive_Design_Intelligence_001.md` answers:

> What did CineWatch study?

`CineWatch_TV_V1_Design_System_and_Asset_Foundation_001.md` answers:

> What design architecture should CineWatch use?

This document answers:

> What must the CineWatch brand and streaming signature become?

Together, these documents form the candidate design-evidence and design-authority package for `CWTV.V1.3.1`.

---

# 40. Non-authorizations

This candidate authority does not yet authorize:

- production SVG geometry;
- final logo;
- final wordmark;
- final color hex values;
- font binaries;
- favicon installation;
- PWA icon installation;
- final SEO images;
- animation;
- provider logo use;
- title imagery;
- public deployment.

---

# 41. Qualification outcome required for CWTV.V1.3.1

Before `CWTV.V1.3.1` can close, the project should have:

- competitive design intelligence;
- design-system/asset authority;
- selected brand direction;
- streaming-signature authority;
- refinement evidence;
- final brand-direction selection;
- explicit implementation scope for the next V1.3 mini-milestone;
- Chronicle/dashboard evidence;
- successful repository checks.

The actual production implementation may occur in subsequent `CWTV.V1.3.x` mini-milestones.

---

## 42. Status

**Status:** `CANDIDATE`

Concept A — Aperture C is selected as the CineWatch TV V1 identity direction.

Final geometry and production assets remain pending visual refinement and qualification.
