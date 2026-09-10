# CineWatch TV V1 Competitive Design Intelligence 001

**Document ID:** `CWTV-V1-COMPETITIVE-DESIGN-INTELLIGENCE-001`
**Product:** CineWatch TV
**Repository:** `Asleki/cinewatch-tv`
**Parent milestone:** `CWTV.V1.3 — Design System & Asset Foundation`
**Mini-milestone:** `CWTV.V1.3.1 — Design System Evidence & Competitive Intelligence`
**Status:** `CANDIDATE`
**Revision:** `001`
**Effective date:** `2026-09-10`

---

## 1. Purpose

This document preserves the design evidence used to shape CineWatch TV V1.

It records:

- the current CineWatch TV V1 frontend baseline;
- legacy CineWatchStream visual and interaction evidence;
- competitive intelligence from streaming platforms;
- competitive intelligence from music platforms;
- competitive intelligence from screenplay and production tools;
- competitive intelligence from television and entertainment editorial products;
- cross-category lessons;
- patterns to preserve, rebuild, adapt, or reject.

This document is **research evidence, not final CineWatch product authority**.

A competitor, legacy artifact, article, screenshot, design pattern, or external service does not become CineWatch architecture merely because it appears here. Final CineWatch rules are established separately by the CineWatch design-system authority.

---

## 2. Research rule: benchmark, synthesize, do not clone

CineWatch TV SHALL study product problems and interaction principles rather than reproduce another product's brand identity.

Research MAY extract lessons about:

- information hierarchy;
- discovery;
- navigation;
- personalization;
- responsive recomposition;
- content geometry;
- editorial structure;
- typography roles;
- motion;
- accessibility;
- media presentation;
- provider handoff;
- TV lifecycle state;
- screenplay and production relationships;
- music and credit relationships.

Research SHALL NOT authorize:

- copying another product's exact page composition;
- copying another service's distinctive brand identity;
- using another provider's signature color as CineWatch's defining identity;
- reproducing proprietary illustrations or screenshots as CineWatch assets;
- treating API availability as content rights;
- presenting provider availability as CineWatch playback authority;
- inferring copyright permission from public product behavior.

---

## 3. Current CineWatch TV V1 baseline

At the start of `CWTV.V1.3.1`, the V1 web application is intentionally skeletal.

Confirmed baseline:

- Next.js 16.3.4;
- React 19.2.8;
- TypeScript 6.0.3;
- native CSS only;
- no Tailwind dependency;
- no Bootstrap dependency;
- no component library;
- no icon package;
- no font package;
- `apps/web/public/brand` reserved but not yet populated;
- `apps/web/public/icons` reserved but not yet populated;
- `apps/web/public/seo` reserved but not yet populated;
- a minimal `globals.css`;
- semantic loading state;
- semantic local error state;
- semantic global error state;
- semantic not-found state;
- no final Discover implementation;
- no final Watch implementation;
- no final Explore implementation;
- no final My CineWatch implementation;
- no final catalogue experience;
- no final playback experience;
- no final design system.

### Baseline conclusion

CineWatch V1.3 begins from a **clean engineering canvas**.

The design-system milestone does not need to dismantle a pre-existing frontend framework or rescue a partially locked visual system.

---

## 4. Legacy CineWatchStream evidence

The legacy repository `Asleki/CineWatchStream` is design provenance only.

Its code and assets SHALL NOT become V1 runtime authority by default.

### 4.1 Useful legacy evidence

Observed legacy areas include:

- `css/colors.css`
  - centralized CSS-variable intent;
  - dark and light palette intent;
  - semantic colors;
  - card, button, badge and rating concepts.
- `css/main.css`
  - Inter typography;
  - cinematic hero composition;
  - horizontal media rails;
  - poster-card geometry;
  - responsive breakpoints.
- `css/header.css`
  - sticky header;
  - navigation;
  - search;
  - account controls;
  - theme toggle;
  - mobile navigation;
  - voice-search experiment.
- `css/details.css`
  - cinematic backdrop;
  - poster/detail composition;
  - title metadata grouping;
  - gradient overlays.
- `css/cinemaguide.css`
  - cinema-specific hero;
  - filtering;
  - venue/movie layout;
  - ticket-oriented calls to action.
- `partials/header.html`
  - semantic navigation foundation.
- `partials/footer.html`
  - corporate, support, Explore and social groupings.
- `images/`
  - logo;
  - hero imagery;
  - placeholders;
  - profile image;
  - policy imagery.

### 4.2 Legacy classification

Legacy evidence follows:

```text
INSPECT
   ↓
CLASSIFY
   ↓
SELECT
   ↓
REIMPLEMENT
```

It does **not** follow:

```text
COPY
   ↓
IMPORT
   ↓
DECLARE AUTHORITATIVE
```

---

## 5. Legacy design score

| Dimension | Score |
|---|---:|
| Initial visual identity | 6.8/10 |
| Dark entertainment atmosphere | 8.0/10 |
| Typography direction | 7.7/10 |
| CSS-token concept | 8.1/10 |
| Information architecture | 7.1/10 |
| Responsive design | 6.7/10 |
| Component consistency | 5.8/10 |
| Accessibility | 6.6/10 |
| Asset governance | 4.9/10 |
| Rights-aware interaction | 2.0/10 |

**Overall reference value:** `6.4/10`

### Preserve as principles

- dark cinematic baseline;
- semantic HTML intent;
- CSS custom-property concept;
- poster geometry;
- cinematic hero/backdrop composition;
- search as a major action;
- dark/light theme intent;
- title-detail depth;
- cinema-specific presentation;
- responsive intent.

### Rebuild

- token naming;
- theme architecture;
- component ownership;
- accessibility guarantees;
- responsive architecture;
- spacing;
- motion;
- icon governance;
- asset governance;
- error/loading presentation;
- navigation architecture;
- search architecture.

### Reject

- Netflix-like red as the defining CineWatch identity;
- duplicated or conflicting CSS rules;
- generic `Watch Now` actions without rights authority;
- identical poster rails as the answer to every content type;
- page-by-page visual drift;
- uncontrolled external visual dependencies;
- provider availability presented as legal playback authority.

---

## 6. Competitive scoring methodology

Each benchmark is scored out of 10 for **usefulness to CineWatch design engineering**.

This is not a subscriber ranking, company ranking, or content-quality ranking.

Weighted dimensions:

| Dimension | Weight |
|---|---:|
| Information hierarchy | 20% |
| Discovery and navigation | 20% |
| Responsive/device adaptation | 15% |
| Domain-specific information architecture | 15% |
| Accessibility and interaction clarity | 10% |
| Visual distinctiveness | 10% |
| Relevance to CineWatch architecture | 10% |

---

# 7. Streaming benchmark

| Rank | Product | Score | Primary CineWatch lesson |
|---:|---|---:|---|
| 1 | Apple TV | 9.6 | Cinematic restraint and large-screen composition |
| 2 | Netflix | 9.5 | Discovery intelligence and rapid decision support |
| 3 | MUBI | 9.3 | Cinema culture and editorial curation |
| 4 | Disney+ | 9.0 | Cross-device navigation and content worlds |
| 5 | HBO Max | 8.9 | Prestige imagery and title presentation |
| 6 | Crunchyroll | 8.7 | Series/season/episode and fandom structure |
| 7 | Hulu | 8.6 | Live/on-demand/library coexistence |
| 8 | Peacock | 8.4 | Time-sensitive and mobile discovery |
| 9 | Prime Video | 8.1 | Large-catalogue/provider complexity lessons |
| 10 | Roku | 8.0 | Provider handoff and search utility |

## 7.1 Apple TV

Primary lessons:

- content should remain visually dominant;
- restraint can feel more premium than UI density;
- large-screen experiences deserve their own composition;
- profile state and personalized recommendations should be easy to understand;
- poster art can carry hierarchy without excessive chrome.

Research reference:

`https://www.apple.com/uk/newsroom/2025/06/apple-tv-brings-a-beautiful-redesign-and-enhanced-home-entertainment-experience/`

## 7.2 Netflix

Primary lessons:

- decision-relevant title information should be surfaced early;
- Search and personal-library actions should remain easy to reach;
- discovery should reduce decision time;
- mobile and TV discovery do not need identical interaction models;
- recommendations are part of the product interface, not merely backend output.

Research reference:

`https://about.netflix.com/en/news/unveiling-our-innovative-new-tv-experience`

## 7.3 MUBI

Primary lessons:

- cinema can be presented as culture, curation and editorial knowledge;
- a streaming/discovery product can support long-form interpretation without feeling like a generic news site;
- human editorial framing remains valuable alongside algorithmic discovery.

Research reference:

`https://mubi.com/en/notebook`

## 7.4 Disney+

Primary lessons:

- navigation may move according to context;
- mobile, browser and large-screen layouts should be recomposed;
- content hubs and personalized surfaces can coexist;
- title state can be communicated visually without overwhelming artwork.

Research references:

- `https://www.disneyplus.com/explore/articles/disney-plus-app-redesign-new-features`
- `https://help.disneyplus.com/en-GB/article/disneyplus-en-gy-navigate-app`
- `https://www.disneyplus.com/explore/articles/disney-plus-verts`

## 7.5 HBO Max

Primary lessons:

- premium content benefits from strong full-bleed imagery;
- dramatic imagery must not reduce orientation;
- prestige presentation is not a substitute for usable navigation.

## 7.6 Crunchyroll

Primary lessons:

- episodic media requires series/season/episode hierarchy;
- localization and language matter;
- fandom-oriented discovery can differ from movie discovery.

## 7.7 Hulu

Primary lessons:

- continuation, recency, live content and library state are different user tasks;
- content state deserves first-class UI treatment.

## 7.8 Peacock

Primary lessons:

- live and time-sensitive media need a distinct visual treatment;
- mobile discovery can be more active than desktop discovery.

## 7.9 Prime Video

Primary lessons:

- a large multi-provider ecosystem can create visual and commercial complexity;
- CineWatch should make provider and rights state clearer than the underlying market complexity.

## 7.10 Roku

Primary lessons:

- provider handoff is a valid user outcome;
- search does not require CineWatch to own playback;
- availability and playback location should be made explicit.

Research reference:

`https://support.roku.com/article/discover-more-with-roku-search`

---

# 8. Music benchmark

| Rank | Product | Score | Primary CineWatch lesson |
|---:|---|---:|---|
| 1 | Spotify | 9.7 | Adaptive identity and personalization |
| 2 | Apple Music | 9.4 | Artwork-first premium presentation |
| 3 | Qobuz | 9.2 | Music, credits and editorial context |
| 4 | TIDAL | 9.0 | Serious music identity and credit depth |
| 5 | SoundCloud | 8.8 | Creator/fan discovery |
| 6 | YouTube Music | 8.7 | Audio/video continuity |
| 7 | Bandcamp | 8.5 | Artist/release context |
| 8 | Deezer | 8.2 | Accessible personalized flow |
| 9 | Amazon Music | 7.9 | Ecosystem integration and complexity caution |
| 10 | Pandora | 7.7 | Lean-back recommendation |

## 8.1 Spotify

Primary lessons:

- one product identity can adapt to multiple contexts;
- tablet should recompose rather than enlarge phone UI;
- playback can remain persistent while browsing continues;
- personalization can become part of visual storytelling.

Research references:

- `https://newsroom.spotify.com/2026-04-23/spotify-design-history/`
- `https://newsroom.spotify.com/2026-04-16/new-tablet-app-experience/`

## 8.2 Apple Music

Primary lessons:

- artwork should often be stronger than UI chrome;
- music discovery, playback, library and editorial content should remain conceptually distinct.

## 8.3 Qobuz

Primary lessons:

- playback can connect to credits, related works and editorial context;
- music should not become an isolated feature silo;
- contextual information can coexist with a persistent player.

Research reference:

`https://www.qobuz.com/us-en/magazine/story/2026/07/23/qobuz-unveils-a-new-player-and-real-time-lyrics/`

## 8.4 TIDAL

Primary lessons:

- artist and album identity should feel serious and premium;
- credits can be first-class content.

## 8.5 SoundCloud

Primary lessons:

- creator identity and community behavior can influence discovery.

## 8.6 YouTube Music

Primary lessons:

- audio and video can be related without being flattened into the same content type.

## 8.7 Bandcamp

Primary lessons:

- artist/release pages can behave like rich liner notes.

## 8.8 Deezer

Primary lessons:

- personalized flow should remain understandable.

## 8.9 Amazon Music

Primary lessons:

- broad ecosystem integration is useful;
- overloaded navigation is not.

## 8.10 Pandora

Primary lessons:

- lean-back discovery can be continuous rather than search-driven.

---

# 9. Screenwriting and production benchmark

| Rank | Product | Score | Primary CineWatch lesson |
|---:|---|---:|---|
| 1 | StudioBinder | 9.6 | Story → scene → people/object/production relationships |
| 2 | Arc Studio | 9.3 | Focused document hierarchy |
| 3 | WriterDuet | 9.1 | Collaboration and revision state |
| 4 | Final Draft | 8.9 | Professional document semantics |
| 5 | Fade In | 8.8 | Structured screenplay navigation |
| 6 | Scriptation | 8.8 | Script reading, annotation and production tagging |
| 7 | Highland | 8.6 | Minimal document environment |
| 8 | Celtx | 8.5 | Script-to-production connected workflow |
| 9 | Slugline | 8.3 | Plain-text semantics and minimalism |
| 10 | Trelby | 7.7 | Open structured screenplay representation |

## 9.1 StudioBinder

Strongest lesson:

```text
TITLE
  ↓
SCREENPLAY
  ↓
SCENE
  ↓
CHARACTER / CAST
PROP
COSTUME
LOCATION
MUSIC
VFX
PRODUCTION EVIDENCE
```

CineWatch Explore should eventually benefit from relationships rather than disconnected pages.

Research references:

- `https://www.studiobinder.com/tutorials/breakdown/intro-to-script-breakdowns/`
- `https://www.studiobinder.com/script-breakdown-software/`

## 9.2 Arc Studio

Primary lesson:

Document-heavy experiences should optimize focus and reading rather than inherit poster-grid entertainment layouts.

## 9.3 WriterDuet

Primary lesson:

Read, review, comment and edit authority should remain distinct if future CineWatch research/collaboration capabilities are introduced.

Research reference:

`https://www.writerduet.com/article/149-invite-collaborators-to-a-project`

## 9.4 Final Draft

Primary lesson:

Story structure deserves specialist navigation: beats, outlines, scenes, characters and focus modes.

Research references:

- `https://www.finaldraft.com/products/features/`
- `https://www.finaldraft.com/learn/final-draft-quick-start/`

## 9.5 Fade In

Primary lesson:

Document semantics, revisions and navigation should remain explicit.

Research reference:

`https://www.fadeinpro.com/page.pl?content=features`

## 9.6 Scriptation

Primary lesson:

CineWatch is more likely to require governed screenplay reading/exploration than a full screenplay authoring environment.

Research references:

- `https://help.scriptation.com/en/article/what-is-scriptation-fuj75j/`
- `https://scriptation.com/features/annotations/`

## 9.7 Highland

Primary lesson:

Minimalism is valuable on long-reading surfaces.

## 9.8 Celtx

Primary lesson:

Connected production data is stronger than duplicating the same facts independently across pages.

Research references:

- `https://www.celtx.com/product/writing/`
- `https://www.celtx.com/product/pre-production/breakdown/`

## 9.9 Slugline

Primary lesson:

Plain-text semantics can support derived structure such as outline/timeline views.

Research references:

- `https://www.slugline.co/faqs/features`
- `https://www.slugline.co/underthehood`

## 9.10 Trelby

Primary lesson:

Structured semantic data can serve human reading, reports, comparison and machine-readable exchange.

Research reference:

`https://trelby.org/`

---

# 10. Television and entertainment editorial benchmark

| Rank | Product | Score | Primary CineWatch lesson |
|---:|---|---:|---|
| 1 | TVLine | 9.4 | TV state, return dates, renewal/cancellation utility |
| 2 | Variety | 9.2 | Professional information hierarchy |
| 3 | The Hollywood Reporter | 9.2 | Premium imagery and long-form pacing |
| 4 | Vulture | 9.1 | Cultural context and editorial personality |
| 5 | IndieWire | 8.9 | Film/TV criticism and cinephile depth |
| 6 | Deadline | 8.7 | Fast production/industry information |
| 7 | Entertainment Weekly | 8.6 | Accessible entertainment storytelling |
| 8 | TheWrap | 8.5 | Streaming/business/analysis separation |
| 9 | Collider | 8.1 | Visual genre/pop-culture discovery |
| 10 | ScreenRant | 7.5 | Discoverability with density caution |

## 10.1 TVLine

Primary lesson:

A TV title needs state beyond poster, title and synopsis.

Useful states include:

- renewed;
- cancelled;
- final season;
- pending;
- returning;
- premiere date;
- return date;
- platform/network.

Research reference:

`https://www.tvline.com/2196897/canceled-renewed-tv-shows-scorecard-premiere-dates/`

## 10.2 Variety

Primary lesson:

High information density can remain readable when hierarchy is strong.

## 10.3 The Hollywood Reporter

Primary lesson:

Premium photography and long-form editorial pacing can coexist.

## 10.4 Vulture

Primary lesson:

Entertainment discovery can include criticism, recaps and cultural context.

## 10.5 IndieWire

Primary lesson:

Cinephile depth deserves dedicated editorial architecture.

## 10.6 Deadline

Primary lesson:

Time-sensitive casting, production and industry information needs fast hierarchy.

## 10.7 Entertainment Weekly

Primary lesson:

Editorial content can remain visually accessible to a broad audience.

## 10.8 TheWrap

Primary lesson:

Streaming, television, business and analysis are related but not interchangeable contexts.

## 10.9 Collider

Primary lesson:

Genre and franchise discovery benefits from strong imagery.

## 10.10 ScreenRant

Primary lesson:

Discoverability matters, but CineWatch Explore should not become a dense SEO-style article wall.

---

# 11. Cross-category synthesis

The strongest synthesis is:

**Apple TV restraint
+ Netflix discovery intelligence
+ MUBI cinematic/editorial culture
+ Spotify adaptive personalization
+ Qobuz music/credit context
+ TVLine television-state intelligence
+ StudioBinder relationship modeling
+ Scriptation document exploration
+ Roku provider handoff
+ CineWatch rights authority**

This synthesis identifies problems to solve.

It does **not** authorize copying any of those products.

---

# 12. CineWatch product-world model

CineWatch should not optimize only for "find a title and press Play."

Candidate primary worlds:

## Discover

What exists and what is worth discovering.

## Watch

What can legally be watched, where, and under which authority.

## Explore

People, characters, writing, music, production, locations, costumes, VFX, interviews, galleries, events, news and craft.

## My CineWatch

History, progress, watchlist, playlists, favorites, ratings, reviews and recommendations.

---

# 13. Domain geometry

A universal poster card SHALL NOT represent every domain.

| Domain | Preferred geometry |
|---|---|
| Movie / series poster | 2:3 |
| Person / cast portrait | 4:5 |
| Music artwork | 1:1 |
| Film still / editorial hero | 16:9 or 3:2 |
| Episode still | 16:9 |
| Script / screenplay | document/page surface |
| News/article | editorial surface |
| Provider | badge/identity surface |
| Cinema/showtime | schedule/location/action surface |

---

# 14. Rights-aware interaction

Candidate rights states:

| Authority state | Interaction principle |
|---|---|
| `HOSTED` | Play in CineWatch only with legal authority |
| `AUTHORIZED_EMBED` | Watch through approved embedded provider path |
| `PROVIDER_HANDOFF` | Open the approved provider |
| `DISCOVERY_ONLY` | Present information without false playback |
| `UNAVAILABLE` | State unavailability clearly |
| `RIGHTS_UNKNOWN` | Fail closed |

**API availability is not playback authority.**

**Provider availability is not copyright permission.**

**Unknown permission is not permission.**

---

# 15. Responsive research conclusion

CineWatch SHALL follow:

**Recompose, do not merely resize.**

| Context | Principle |
|---|---|
| Mobile | thumb-first, focused dominant task |
| Tablet | split context and parallel exploration |
| Desktop | richer navigation and multi-column knowledge |
| Large screen / TV-like web | distance readability, focus-first interaction, large targets |

Breakpoints should follow content behavior rather than device-brand widths.

---

# 16. HTML/CSS research conclusion

Primary direction:

```text
Semantic HTML through React/Next.js TSX
        ↓
CineWatch design tokens
        ↓
Native CSS
        ↓
CSS Modules / page-specific CSS
        ↓
React + TypeScript behavior
```

Tailwind remains **permitted but optional**.

Research policy:

**CSS-first, Tailwind-when-justified.**

Certain experiences may be deliberately designated **CSS-exclusive** when custom cinematic, editorial, screenplay, gallery, animation, responsive, or accessibility behavior makes direct CSS the clearer engineering authority.

---

# 17. Candidate visual direction

The legacy Netflix-like red should not define CineWatch V1.

Research direction:

- deep midnight/carbon surfaces;
- luminous cool primary signal such as aqua/teal;
- restrained warm cinematic secondary signal such as gold/amber;
- strong neutral surface and text ramps;
- provider colors limited to provider-owned identity;
- semantic colors for rights, success, warning and error.

No exact hexadecimal values are authorized by this research document.

---

# 18. Typography direction

Legacy use of Inter is a strong continuity candidate.

Candidate role model:

| Role | Direction |
|---|---|
| UI/navigation/metadata | highly legible modern sans; Inter Variable candidate |
| Editorial/Explore long-form | restrained editorial serif |
| Screenplay/document surfaces | screenplay-appropriate mono/typewriter family |

Any font must pass license, redistribution, format, weight, file-size, fallback and loading review.

No font binary is authorized here.

---

# 19. Accessibility research conclusion

V1.3 should preserve and expand:

- semantic landmarks;
- real links and buttons;
- visible keyboard focus;
- logical heading order;
- accessible dialogs;
- sufficient contrast;
- non-color-only status communication;
- reduced-motion support;
- adequate target sizes;
- keyboard navigation;
- loading/error announcements;
- captions/media alternatives where applicable.

Visual richness must never remove semantic correctness.

---

# 20. Asset research conclusion

V1.3 should govern:

- master brand assets;
- favicons;
- application icons;
- PWA icons;
- maskable icons;
- SEO/social images;
- placeholders;
- poster/backdrop fallbacks;
- illustrations;
- aspect ratios;
- WebP/AVIF strategy;
- raster/SVG rules;
- provenance;
- copyright/license;
- optimization;
- naming;
- alternative text;
- decorative-image behavior.

No legacy asset should enter V1 merely because it already exists.

---

# 21. Anti-pattern register

The final design authority should prevent:

1. endless identical rails;
2. poster cards for every domain;
3. false `Play` or `Watch Now` actions;
4. provider branding becoming CineWatch identity;
5. Netflix-derived primary branding;
6. random per-page color values;
7. arbitrary spacing or radii;
8. duplicate theme logic;
9. giant monolithic `globals.css`;
10. inaccessible custom controls;
11. simple shrinking as "responsive design";
12. critical hover-only interactions;
13. decorative motion without reduced-motion support;
14. Tailwind becoming an unmanaged second design system;
15. direct provider credentials in browser code;
16. unqualified assets;
17. SEO-style editorial walls;
18. screenplay pages built as poster grids;
19. visual rights claims not backed by authority.

---

# 22. Candidate design-system architecture

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

This remains a research recommendation until accepted by the CineWatch design-system authority.

---

# 23. Quality target

| Dimension | V1.3 target |
|---|---:|
| Brand distinction | 9.5+/10 |
| Cinematic presentation | 9.5+/10 |
| Navigation clarity | 9.5+/10 |
| Discovery | 9.5+/10 |
| Information hierarchy | 9.5+/10 |
| Responsive recomposition | 9.5+/10 |
| Accessibility | 9.5+/10 |
| Editorial / knowledge depth | 10/10 |
| Provider clarity | 10/10 |
| Rights clarity | 10/10 |
| Cross-domain integration | 10/10 |

These are internal engineering targets, not claims of independent certification.

---

# 24. Research outcome

The evidence supports a CineWatch V1 direction that:

- preserves the cinematic intent of the legacy product;
- creates a new governed token/theme architecture;
- uses semantic HTML and native CSS as primary design authority;
- allows Tailwind selectively;
- permits CSS-exclusive pages when justified;
- differentiates domains by geometry and information needs;
- models relationships instead of isolated pages;
- exposes TV lifecycle state;
- exposes provider handoff clearly;
- exposes rights state clearly;
- creates a distinct CineWatch identity;
- qualifies assets before use;
- treats accessibility as architecture.

The companion authority document converts selected findings into CineWatch-owned rules.

---

## 25. Status note

This document remains `CANDIDATE` until `CWTV.V1.3.1` verification and qualification.

No design token, exact color value, font binary, production asset, Tailwind dependency, or user-facing component becomes authorized merely because it appears in this research record.
