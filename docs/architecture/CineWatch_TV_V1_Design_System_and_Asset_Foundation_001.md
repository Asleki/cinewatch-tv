# CineWatch TV V1 Design System and Asset Foundation 001

**Document ID:** `CWTV-V1-DESIGN-SYSTEM-ASSET-FOUNDATION-001`
**Product:** CineWatch TV
**Repository:** `Asleki/cinewatch-tv`
**Parent milestone:** `CWTV.V1.3 — Design System & Asset Foundation`
**Mini-milestone:** `CWTV.V1.3.1 — Design System Evidence & Competitive Intelligence`
**Status:** `CANDIDATE`
**Revision:** `001`
**Effective date:** `2026-09-10`

---

## 1. Purpose

This document defines the candidate architecture for the CineWatch TV V1 design system and governed public-asset foundation.

It converts selected findings from `CineWatch_TV_V1_Competitive_Design_Intelligence_001.md` into CineWatch-owned engineering rules.

The design system exists to ensure that CineWatch TV remains:

- visually distinctive;
- semantically correct;
- accessible;
- responsive by composition rather than simple scaling;
- rights-aware;
- provider-aware;
- maintainable;
- explainable as a software-engineering project;
- consistent across Discover, Watch, Explore and My CineWatch;
- independent from any single CSS framework.

This document is `CANDIDATE` until `CWTV.V1.3.1` qualification.

---

# 2. Authority hierarchy

CineWatch frontend presentation SHALL follow this hierarchy:

```text
Approved CineWatch product/governance authority
                    ↓
CineWatch design-system authority
                    ↓
Semantic HTML structure
                    ↓
Design tokens
                    ↓
Theme resolution
                    ↓
Native CSS / CSS Modules
                    ↓
Optional Tailwind utilities where justified
                    ↓
React / TypeScript behavior
```

A utility framework SHALL NOT become a stronger authority than CineWatch design tokens or semantic markup.

Provider styles SHALL NOT become CineWatch design authority.

Legacy CineWatchStream styles SHALL NOT become V1 design authority.

---

# 3. HTML semantics

React/Next.js TSX is the authoring format, but rendered structure SHALL use genuine semantic HTML.

Preferred elements include, where appropriate:

- `header`;
- `nav`;
- `main`;
- `section`;
- `article`;
- `aside`;
- `figure`;
- `figcaption`;
- `footer`;
- `form`;
- `label`;
- `button`;
- `dialog`;
- ordered/unordered lists;
- correctly ordered headings.

`div` and `span` remain valid when no stronger semantic element exists.

### Rule

**Componentization SHALL NOT erase document semantics.**

A React component does not justify replacing meaningful landmarks with anonymous containers.

---

# 4. CSS authority

CineWatch V1 is **CSS-first**.

Primary tools:

- CSS custom properties;
- CSS cascade;
- inheritance;
- specificity control;
- CSS Grid;
- Flexbox;
- media queries;
- container queries;
- `clamp()`;
- `min()`;
- `max()`;
- `aspect-ratio`;
- logical properties;
- `prefers-color-scheme`;
- `prefers-reduced-motion`;
- `color-mix()` where browser support and fallbacks are acceptable;
- transitions;
- animations;
- pseudo-elements;
- pseudo-classes;
- `@supports` where progressive enhancement is useful.

This is intentional engineering authority, not merely a styling preference.

---

# 5. Tailwind policy

Tailwind CSS is **permitted, not required**.

Policy shorthand:

**CSS-first, Tailwind-when-justified.**

Tailwind MAY be introduced only when a real implementation benefit exists.

Suitable examples may include:

- low-complexity internal utility surfaces;
- repetitive layout primitives;
- rapid but governed composition;
- areas where utility classes clearly reduce duplication without obscuring design intent.

Tailwind SHALL NOT:

- replace CineWatch design tokens;
- define independent color/spacing/radius values;
- override semantic HTML;
- become mandatory for every page;
- force complex cinematic pages into long utility strings;
- become a second visual system;
- cause the same styling responsibility to be owned simultaneously by CSS Modules and arbitrary utility classes.

## 5.1 CSS-exclusive surfaces

A page or component MAY be designated **CSS-exclusive**.

Likely candidates include:

- cinematic title-detail heroes;
- screenplay/document readers;
- Explore editorial features;
- image/video galleries;
- complex knowledge surfaces;
- advanced responsive compositions;
- remote/keyboard-focused large-screen layouts;
- animation-heavy surfaces;
- accessibility-sensitive controls requiring precise selectors/state.

The reason for CSS exclusivity should be architectural clarity, not ideology.

---

# 6. Proposed stylesheet architecture

Candidate source structure:

```text
apps/web/src/
├── app/
│   └── globals.css
├── styles/
│   ├── reset.css
│   ├── tokens.css
│   ├── themes.css
│   ├── typography.css
│   ├── motion.css
│   └── utilities.css
└── components/
    └── <component>/
        ├── <component>.tsx
        └── <component>.module.css
```

Responsibilities:

| File | Authority |
|---|---|
| `globals.css` | global assembly and root behavior |
| `reset.css` | safe normalization |
| `tokens.css` | design variables |
| `themes.css` | dark/light/system semantic mapping |
| `typography.css` | global type roles and rhythm |
| `motion.css` | motion tokens and reduced-motion policy |
| `utilities.css` | small universal primitives only |
| `*.module.css` | component-level visual ownership |

`globals.css` SHALL NOT become a monolithic repository for component styling.

---

# 7. Design-token architecture

Tokens should be semantic enough to survive visual redesign.

Candidate namespaces:

```css
--cw-color-*
--cw-font-*
--cw-size-*
--cw-space-*
--cw-radius-*
--cw-border-*
--cw-shadow-*
--cw-motion-*
--cw-layer-*
--cw-content-*
--cw-media-*
--cw-rights-*
```

Exact names remain subject to implementation qualification.

## 7.1 Token levels

The system should distinguish:

```text
PRIMITIVE
raw value

    ↓

SEMANTIC
meaning within CineWatch

    ↓

COMPONENT
optional local interpretation
```

Example:

```text
neutral-950
    ↓
surface-cinema
    ↓
title-hero-background
```

Components should prefer semantic tokens rather than raw literals.

---

# 8. Color-system direction

The legacy Netflix-like red SHALL NOT automatically remain the CineWatch V1 defining accent.

Candidate visual family:

- midnight/carbon cinematic base;
- neutral raised surfaces;
- luminous aqua/teal primary signal;
- restrained cinematic gold/amber secondary signal;
- accessible semantic success/warning/error states;
- dedicated rights-state semantics.

Exact color values are deferred until contrast/component qualification.

## 8.1 Provider colors

Provider brand colors MAY appear only when representing that provider.

Provider colors SHALL NOT:

- recolor CineWatch navigation;
- define CineWatch buttons globally;
- replace CineWatch accent colors;
- visually imply provider ownership of CineWatch.

---

# 9. Themes

V1 SHALL support:

- dark;
- light;
- system.

System mode should resolve through the operating-system/browser preference.

Theme logic SHALL be centralized.

Pages SHALL NOT implement their own independent theme switches.

## 9.1 Dark mode

Dark mode is the primary cinematic canvas, but not the only supported mode.

## 9.2 Light mode

Light mode must be designed intentionally rather than implemented as a naive inversion.

## 9.3 Theme persistence

Theme preference should eventually be stored through the appropriate user/client preference mechanism without exposing private authority to browser code.

---

# 10. Typography

CineWatch should use typography by semantic role.

Candidate roles:

| Role | Purpose |
|---|---|
| UI sans | navigation, controls, metadata, system text |
| Editorial serif | long-form Explore/editorial presentation |
| Screenplay mono/typewriter | script/document semantics only |

Inter Variable is a strong UI candidate because of continuity with the legacy design and strong interface readability, but it is not authorized until license and delivery qualification are complete.

Typography SHALL define:

- family;
- weight;
- optical/variable behavior if used;
- line height;
- letter spacing;
- fluid size rules;
- heading hierarchy;
- metadata hierarchy;
- long-form reading width.

No font binary may be added without license/provenance review.

---

# 11. Spacing

Spacing SHALL use a governed scale.

Raw one-off margins and paddings should be exceptional.

The final scale should support:

- dense metadata;
- ordinary interface composition;
- editorial reading;
- cinematic whitespace;
- large-screen distance readability.

Spacing tokens should be used through semantic/component CSS rather than invented independently per page.

---

# 12. Radius and borders

CineWatch should use a small governed radius family.

Likely roles:

- small control radius;
- standard card radius;
- elevated panel radius;
- pill/badge radius;
- circular control radius.

Border use should primarily express:

- separation;
- focus;
- interaction state;
- rights/provider status where appropriate.

Borders SHALL NOT substitute for hierarchy everywhere.

---

# 13. Elevation and surfaces

CineWatch should prefer layered surfaces and image-aware gradients over exaggerated shadow-heavy cards.

Candidate surface roles:

- canvas;
- cinema;
- raised;
- floating;
- overlay;
- glass/translucent surface where justified;
- document surface;
- editorial surface.

Elevation must remain legible in both dark and light themes.

---

# 14. Motion

Motion is functional first.

Candidate motion roles:

- fast feedback;
- standard transition;
- deliberate cinematic transition;
- loading/progress;
- spatial navigation.

Motion SHALL NOT:

- block interaction;
- hide important state;
- cause excessive movement;
- ignore `prefers-reduced-motion`;
- make hover the only discoverable interaction state.

Reduced-motion behavior must be defined alongside default motion.

---

# 15. Responsive architecture

CineWatch SHALL use:

**Recompose, do not merely resize.**

## Mobile

- focused dominant task;
- thumb-accessible controls;
- limited simultaneous information;
- bottom navigation only where it clearly improves primary navigation.

## Tablet

- parallel context;
- split panes where useful;
- portrait/landscape recomposition;
- richer media + metadata coexistence.

## Desktop

- richer navigation;
- more simultaneous context;
- multi-column Explore surfaces;
- more persistent secondary information.

## Large-screen / TV-like web

- distance readability;
- larger focus targets;
- strong selected/focus state;
- keyboard/remote-friendly interaction;
- reduced dependence on pointer hover.

Breakpoints should emerge from layout failure/content needs rather than named device brands.

Container queries are encouraged for reusable components whose behavior depends on available component width.

---

# 16. Media geometry

CineWatch SHALL NOT use one card geometry for every entity.

| Entity/domain | Preferred geometry |
|---|---|
| Movie / series | 2:3 poster |
| Person | 4:5 portrait |
| Episode | 16:9 still |
| Film still | 16:9 / 3:2 |
| Music release | 1:1 artwork |
| Editorial feature | flexible editorial crop |
| Screenplay | page/document |
| Provider | identity badge |
| Cinema/showtime | schedule/location card |

Components must preserve source aspect ratio or use approved crops.

---

# 17. Core product worlds

The design system must support four distinct but coherent worlds.

## Discover

Discovery, recommendations, trending, genres, collections and editorial entry points.

## Watch

Playback authority, provider availability, handoff, episodes/seasons, cinema/showtime where applicable.

## Explore

Knowledge and craft:

- overview;
- people;
- characters;
- writing;
- music and sound;
- production;
- locations;
- costumes;
- VFX;
- galleries;
- interviews;
- events;
- news;
- reviews.

## My CineWatch

Private user state:

- history;
- progress;
- watchlist;
- playlists;
- favorites;
- ratings;
- reviews;
- recommendations.

These worlds may use different compositions while sharing the same tokens, typography and interaction language.

---

# 18. Rights-aware UI

Visual design SHALL reflect actual backend rights authority.

Candidate states:

| State | UI principle |
|---|---|
| `HOSTED` | CineWatch playback only when permitted |
| `AUTHORIZED_EMBED` | clearly attributed authorized embedded playback |
| `PROVIDER_HANDOFF` | clear external provider action |
| `DISCOVERY_ONLY` | no fake playback action |
| `UNAVAILABLE` | explicit unavailable state |
| `RIGHTS_UNKNOWN` | fail closed |

A provider link SHALL NOT visually masquerade as CineWatch-hosted playback.

Unknown authority SHALL NOT produce a generic `Play` button.

Rights state should remain understandable without relying on color alone.

---

# 19. Navigation

Navigation must emphasize the four primary worlds without becoming crowded.

Research direction:

```text
Discover
Watch
Explore
My CineWatch
Search
Profile / account
```

Movies, TV shows, people, genres, providers and other taxonomies may appear as subnavigation, search scopes, hubs, filters or context-specific routes rather than all competing for primary navigation.

Search should remain a first-class action.

---

# 20. Search

Search should eventually support structured discovery across:

- movies;
- television;
- people;
- cast/crew;
- characters;
- genres;
- providers;
- music;
- editorial knowledge where indexed;
- cinema/showtimes where supported.

Search suggestions must distinguish entity types.

Search results must not imply playback authority merely because a title exists.

---

# 21. Component families

The design system should build domain-specific component families instead of one generic card.

Candidate families:

- navigation;
- search;
- poster card;
- episode card;
- person card;
- soundtrack/release card;
- editorial story card;
- provider badge/action;
- rights status;
- hero;
- metadata strip;
- season/episode selector;
- progress indicator;
- rating/review surface;
- gallery;
- document/screenplay reader;
- empty/loading/error state;
- dialog;
- toast/notice;
- tabs/segmented navigation where semantically justified.

Component APIs should expose meaningful state rather than raw styling knobs.

---

# 22. Accessibility authority

Accessibility is architecture.

Required baseline:

- semantic landmarks;
- keyboard operability;
- visible focus;
- logical focus order;
- semantic controls;
- screen-reader names;
- labels and instructions;
- proper heading hierarchy;
- sufficient contrast;
- non-color-only state;
- reduced-motion handling;
- accessible dialogs;
- accessible validation;
- appropriate live regions;
- minimum comfortable target sizing;
- captions/subtitles/transcripts where legally and technically applicable;
- no keyboard traps;
- no hover-only essential actions.

Existing V1 loading/error semantics should be preserved during visual redesign.

---

# 23. Loading, empty, error and unavailable states

These states are part of the design system, not afterthoughts.

Distinct system states should include:

- initial loading;
- incremental loading;
- empty list;
- no search result;
- provider unavailable;
- rights unknown;
- title unavailable;
- network/API failure;
- route not found;
- global application failure.

Each state should communicate:

- what happened;
- whether user action is possible;
- whether retry is appropriate;
- whether content is unavailable by design rather than error.

---

# 24. Public asset foundation

Governed public assets are reserved under:

```text
apps/web/public/
├── brand/
├── icons/
└── seo/
```

V1.3 SHALL define contents rather than filling these folders ad hoc.

## 24.1 Brand

Candidate contents:

- primary CineWatch wordmark;
- symbol/mark;
- monochrome variants;
- light/dark variants where needed;
- safe-area specifications;
- source/master format;
- optimized delivery formats.

## 24.2 Icons

Candidate contents:

- favicon;
- browser icons;
- PWA icons;
- maskable icon;
- Apple-touch icon where needed;
- application icon variants.

## 24.3 SEO/social

Candidate contents:

- default Open Graph image;
- social share fallback;
- title-specific generated/qualified imagery later where permitted.

---

# 25. Asset governance record

Every governed production asset should be traceable by metadata such as:

```yaml
asset_id:
path:
role:
source:
source_type:
creator_or_owner:
license_or_permission:
rights_status:
created_at:
qualified_at:
sha256:
width:
height:
format:
bytes:
alt_text_policy:
notes:
```

The exact schema may later move into machine-readable YAML/JSON/CSV authority.

No asset is production-approved solely because it exists in the repository.

---

# 26. Image formats

Candidate policy:

- SVG for suitable vector brand/icon assets;
- WebP/AVIF for optimized photographic/raster delivery where browser/platform support and source quality justify it;
- PNG only when its characteristics are required;
- JPEG only when justified by source/workflow compatibility.

Image optimization must not erase provenance or destroy source masters.

Source/master assets may need preservation separately from delivery derivatives.

---

# 27. Icon strategy

CineWatch should prefer a small coherent icon system.

Rules:

- icons supplement, not replace, essential text where ambiguity exists;
- accessible names belong on icon-only controls;
- provider logos are provider identity, not generic UI icons;
- random mixed icon families are prohibited;
- icon stroke/fill style should remain consistent.

An external icon package may be adopted only after bundle-size, license and visual-fit review.

---

# 28. Brand identity direction

CineWatch V1 should be recognizable without its logo.

Identity should emerge from:

- surface palette;
- typography;
- content geometry;
- spacing rhythm;
- motion;
- focus/interaction style;
- rights-aware actions;
- Explore depth;
- consistent responsive behavior.

CineWatch SHALL NOT depend on a copied streaming-service color pattern to feel cinematic.

---

# 29. Information-density rule

CineWatch must support both:

- low-density cinematic presentation;
- high-density knowledge/editorial presentation.

The design system should not force both into one layout.

Examples:

```text
TITLE HERO
low density
visual atmosphere
primary actions

EXPLORE / CREDITS / WRITING
higher density
structured reading
relationships
navigation
```

Both must still feel like CineWatch.

---

# 30. Design-quality target

Internal target:

| Dimension | Target |
|---|---:|
| Brand distinction | 9.5+/10 |
| Cinematic presentation | 9.5+/10 |
| Navigation clarity | 9.5+/10 |
| Discovery | 9.5+/10 |
| Information hierarchy | 9.5+/10 |
| Responsive recomposition | 9.5+/10 |
| Accessibility | 9.5+/10 |
| Editorial/knowledge depth | 10/10 |
| Provider clarity | 10/10 |
| Rights clarity | 10/10 |
| Cross-domain integration | 10/10 |

These are engineering ambition targets, not third-party certification.

---

# 31. Initial implementation sequence

Following qualification of this authority, implementation should proceed in small governed mini-milestones rather than attempting the entire UI at once.

Recommended sequence:

```text
tokens / reset / themes
        ↓
typography / motion
        ↓
brand + icon asset qualification
        ↓
global shell / navigation
        ↓
loading / error / empty-state family
        ↓
core card geometries
        ↓
hero / title identity
        ↓
responsive recomposition
        ↓
Discover
        ↓
Watch / rights-aware actions
        ↓
Explore
        ↓
My CineWatch
```

Exact mini-milestone numbering remains subject to repository governance.

---

# 32. Qualification requirements

Before this document can become locked/qualified, V1.3.1 should demonstrate:

- competitive evidence recorded;
- legacy evidence classified;
- CSS-first policy recorded;
- Tailwind selective-use policy recorded;
- CSS-exclusive surfaces permitted;
- semantic HTML authority recorded;
- responsive recomposition rule recorded;
- theme requirements recorded;
- typography roles recorded;
- asset governance direction recorded;
- accessibility baseline recorded;
- rights-aware UI principle recorded;
- no production asset or dependency added prematurely;
- Markdown/document checks pass;
- engineering chronicle and dashboard are updated according to project workflow.

---

# 33. Explicit non-authorizations

This candidate document does **not** yet authorize:

- a specific Tailwind installation;
- a specific component library;
- final brand hex colors;
- final font binaries;
- final logo replacement;
- copying legacy assets into V1;
- full homepage implementation;
- playback implementation;
- provider runtime integration;
- screenplay redistribution;
- unqualified copyrighted images;
- commercial media use.

---

# 34. Relationship to competitive intelligence

`CineWatch_TV_V1_Competitive_Design_Intelligence_001.md` answers:

> What did CineWatch study and learn?

This document answers:

> What architecture should CineWatch use as a result?

Competitive evidence may change over time.

CineWatch product authority changes only through governed revision.

---

# 35. Status note

This document remains `CANDIDATE`.

It should be qualified only after review, repository validation, chronicle recording and any required architecture/governance checks.

Until then, implementation should treat these rules as the candidate V1.3 direction, not an already locked historical fact.
