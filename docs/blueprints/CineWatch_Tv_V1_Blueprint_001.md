# CineWatch TV V1 Blueprint 001

**Document ID:** `CWTV-V1-BLUEPRINT-001`
**Product:** CineWatch TV
**Release:** V1
**Document type:** Product / Architecture / Engineering / Governance Blueprint
**Status:** APPROVED
**Revision:** 001
**Date:** 2026-09-07
**Editable authority:** this Markdown document
**Frozen human-readable copy:** generated PDF after approval
**Legacy reference repository:** `Asleki/CineWatchStream`
**V1 repository:** `Asleki/cinewatch-tv`
**Planned public domain:** `cinewatchtv.com`

---

## 1. Purpose

This blueprint establishes the initial source of truth for CineWatch TV V1 before production application code is introduced.

CineWatch TV V1 is a new private-beta implementation. It does not evolve the legacy `CineWatchStream` repository in place. The legacy repository is retained as product and styling provenance, while V1 establishes new runtime authority for backend services, PostgreSQL persistence, user identity, rights governance, playback availability, community state, cinema foundations, cinematic knowledge, and future AI readiness.

This document deliberately separates:

- product identity from implementation history;
- external metadata from CineWatch-native authority;
- content discovery from legal playback;
- provider/API permission from underlying-content rights;
- screenplays from transcripts, subtitles, captions, and quotations;
- product analytics from AI-training consent;
- AI search from AI inference from AI training;
- real-world authority from future NexiLabs simulation-realm authority.

---

## 2. Product identity

### 2.1 Name

Human-facing product name: **CineWatch TV**

Machine namespace: `cinewatch`

Repository: `Asleki/cinewatch-tv`

Planned public production domain: `cinewatchtv.com`

The product is multi-territory by design. No country is hardcoded as the identity or permanent operating territory of CineWatch TV.

### 2.2 Product definition

CineWatch TV is a **legal-first movie, television, cinema, cinematic-companion, and entertainment-knowledge platform**.

Its long-term identity is not limited to streaming. CineWatch TV connects:

- what exists;
- what a user may legally watch;
- where a user may watch it;
- the people who created it;
- the story and character graph;
- the writing and screenplay history where rights permit;
- music and sound;
- interviews;
- events;
- imagery and video;
- production craft;
- cinema/theatre availability;
- community participation;
- personal viewing state;
- future intelligent assistance.

### 2.3 Product principle

CineWatch TV SHALL NOT be designed as:

- a TMDB clone;
- a YouTube channel or wrapper;
- an unlicensed MovieBox-style catalog;
- a generic poster database with a `Watch Now` button;
- an AI-training scraper.

The intended product identity is:

**Discover it. Watch it. Explore it.**

---

## 3. Release lifecycle

### 3.1 V1 — Development

Approximate duration: **6 months**

Characteristics:

- private;
- invite-only;
- initially four authorized testers;
- no commercial activity;
- real backend and real persistence;
- real user accounts;
- real user library/community state;
- rights-governed legal playback;
- development/freemium/noncommercial provider access where permitted;
- no dependency on NexiLabs monetary-system readiness.

### 3.2 V2 — Production + Research

Approximate duration: **12 months**

Characteristics:

- production-grade deployment;
- noncommercial;
- broader user and provider qualification may occur;
- production monitoring and security posture;
- external providers must explicitly confirm whether non-revenue production use remains covered by their developer/noncommercial terms;
- NexVox-related research may begin only on data/content for which search, inference, and/or training permissions are explicitly qualified.

V2 being noncommercial SHALL NOT be interpreted as automatic permission to use every developer API in a production environment.

### 3.3 V3 — Commercial

Future commercial release.

Before commercial operation:

- API commercial terms are qualified;
- provider and network commercial permissions are qualified;
- content licenses required for CineWatch-hosted or CineWatch-displayed material are obtained;
- commercial payment authority is integrated where needed;
- public registration and moderation are production-qualified;
- trademark/brand clearance is reviewed;
- security and privacy release gates are satisfied;
- public SEO/indexing is intentionally enabled.

---

## 4. Legacy CineWatchStream authority

Legacy repository: `Asleki/CineWatchStream`

### 4.1 Preserved as product provenance

The legacy repository may remain authoritative reference material for:

- CineWatch visual identity and historical styling intent;
- layout concepts;
- navigation concepts;
- content sections and taxonomy;
- search/product behavior intent;
- movie/TV details concepts;
- cast, trailer, recommendation, and review concepts;
- playlist/watchlist product intent;
- cinema-guide and booking UI concepts;
- theme intent;
- historical API integration knowledge.

### 4.2 Explicitly not V1 runtime authority

The legacy implementation SHALL NOT be treated as authoritative for:

- V1 authentication;
- V1 PostgreSQL schema;
- V1 persistent user state;
- API credentials;
- rights decisions;
- legal playback;
- payment authority;
- backend architecture;
- deployment architecture;
- security architecture;
- V1 file naming;
- V1 module boundaries;
- V1 routing contracts.

No wholesale copy of legacy code is presumed safe. Legacy functionality is inspected, classified, and selectively reimplemented.

---

## 5. V1 objectives

V1 SHALL establish:

1. private authenticated access for the initial authorized testers;
2. a real CineWatch backend;
3. PostgreSQL as the authoritative CineWatch-native persistent store;
4. real user account/profile state;
5. movie and television discovery;
6. clear, rights-governed viewing availability;
7. legal CineWatch-hosted or authorized-embed playback where permission exists;
8. provider handoff where CineWatch does not have playback authority;
9. watchlists, playlists, favorites, history, and progress;
10. CineWatch ratings and reviews;
11. separately identified external reviews;
12. cinema/theatre discovery foundations;
13. a governed design system;
14. dark, light, and system appearance modes;
15. complete asset governance;
16. SEO-ready architecture while V1 remains non-indexed;
17. accessibility foundations;
18. observability and auditability;
19. NexVox-ready search contracts and consent-aware data capture;
20. future payment and NexiLabs integration boundaries without current dependency.

---

## 6. V1 non-goals

V1 does not require:

- unrestricted public registration;
- public commercial launch;
- real-world payment processing;
- NexiLabs monetary-system availability;
- CineWatch-owned premium Hollywood licensing;
- proprietary DRM infrastructure;
- a proprietary video CDN for third-party copyrighted works;
- native Android, iOS, or smart-TV applications;
- user photo/video uploads;
- NexVox production inference;
- NexVox model training;
- full public SEO indexing;
- globally authoritative cinema ticketing;
- a commercial screenplay redistribution library.

---

## 7. Core authority principles

### 7.1 CineWatch-native state

CineWatch PostgreSQL SHALL own CineWatch-native state, including:

- CineWatch canonical identities;
- user profiles;
- memberships and entitlements;
- watchlists;
- playlists;
- favorites;
- watch history;
- watch progress;
- CineWatch ratings;
- CineWatch reviews;
- CineWatch moderation state;
- source/provider crosswalks;
- CineWatch rights receipts;
- CineWatch provider-permission records;
- audit records.

### 7.2 External providers

External services provide governed evidence, enrichment, availability, or media delivery. They do not automatically become CineWatch identity authority.

Examples include TMDB, YouTube, TVmaze, MusicBrainz, Musixmatch, Genius, Wikimedia/Wikidata, network/studio feeds, and cinema/showtime providers.

### 7.3 Five separate facts

The following SHALL remain separate:

`metadata available`

`legally watchable`

`embeddable`

`hostable`

`AI-training permitted`

One does not imply another.

---

## 8. Primary product experiences

CineWatch TV V1 is designed around four primary experiences.

### 8.1 Discover

Discover covers the wider cinematic and television universe.

Potential contents include:

- movies;
- television series;
- seasons and episodes;
- people;
- networks;
- genres;
- trends;
- upcoming releases;
- recommendations;
- collections;
- cinema releases;
- trailers;
- reviews;
- provider availability.

A title may appear in Discover even when CineWatch has no full-title playback authority.

### 8.2 Watch

Watch contains only titles with a verified viewing path.

Canonical availability states are expected to include:

- `PLAY_ON_CINEWATCH`
- `PLAY_EMBEDDED`
- `WATCH_FREE_EXTERNAL`
- `WATCH_SUBSCRIPTION_EXTERNAL`
- `RENT_EXTERNAL`
- `BUY_EXTERNAL`
- `WATCH_IN_CINEMA`
- `TRAILER_ONLY`
- `DISCOVERY_ONLY`

The frontend SHALL NOT present an ambiguous generic `Watch Now` action when no verified viewing path exists.

### 8.3 Explore

Explore is CineWatch TV's cinematic-companion and knowledge layer.

Potential domains include:

- Story & Characters;
- Cast & Crew;
- Writing & Screenplay;
- Music & Sound;
- Behind the Scenes;
- Interviews;
- Events;
- Galleries;
- Production;
- Directing;
- Cinematography;
- Editing;
- Production Design;
- VFX / CGI;
- Practical Effects;
- Stunts;
- Sound Design;
- Costume;
- Hair & Makeup;
- Props;
- Filming Locations;
- Awards;
- Trivia;
- Related Works;
- timelines/canon where supported by reliable evidence.

Explore is a first-class product experience, not a miscellaneous attachment area.

### 8.4 My CineWatch

My CineWatch is the authenticated personal layer:

- Continue Watching;
- Watchlist;
- Playlists;
- Favorites;
- History;
- Progress;
- Ratings;
- Reviews;
- Preferences;
- future provider/service preferences;
- future followed people/titles.

---

## 9. Canonical content identity

CineWatch SHALL mint its own canonical identities.

External IDs are crosswalks, not primary identity.

Conceptually:

`CineWatch title -> TMDB / IMDb / TVmaze / Wikidata / provider IDs`

Initial entity families include:

- Movie;
- Series;
- Season;
- Episode;
- Person;
- Character;
- Network;
- Company;
- Event;
- Venue;
- Music Work / Recording / Release;
- Media Resource;
- Screenplay / Document.

Exact identifier syntax is deferred to the canonical-content milestone.

---

## 10. Cinematic knowledge graph

CineWatch TV SHALL model relationships rather than storing entertainment knowledge as isolated strings.

Examples:

- person `acted_in` title;
- person `directed` title;
- person `wrote` screenplay;
- actor `portrays` character;
- character `appears_in` episode;
- music recording `appears_in` title or episode where verified;
- interview `features` person;
- event `relates_to` title;
- gallery asset `captured_at` event;
- VFX vendor `worked_on` title;
- screenplay scene `corresponds_to` finished scene where rights and evidence permit.

The graph is intended to improve search, recommendations, Explore, future scene context, and future NexVox reasoning.

---

## 11. Screenplay Vault

Screenplays are a strategic CineWatch knowledge domain, but availability to download on the internet does not establish CineWatch republication or AI-training rights.

### 11.1 Screenplay states

Expected states include:

- `FULL_SCREENPLAY`
- `AUTHORIZED_EXTERNAL_SCREENPLAY`
- `EXCERPT_AUTHORIZED`
- `PUBLIC_DOMAIN_SCREENPLAY`
- `SCREENPLAY_KNOWN_NO_ACCESS`
- `NO_SCREENPLAY_SOURCE`

### 11.2 Distinct textual resource classes

CineWatch SHALL distinguish:

- Screenplay;
- Shooting Script;
- Production Draft;
- Transcript;
- Subtitle;
- Caption;
- Quote;
- Article;
- Production Document.

Subtitles SHALL NOT be relabeled as screenplays.

### 11.3 Rights principle

A screenplay may be known to exist while CineWatch correctly refuses to display or ingest it.

A public URL, PDF download, API response, or third-party script website is evidence of availability, not automatically evidence of permission.

### 11.4 Future structure

For rights-cleared screenplays, the model may eventually represent:

- draft/revision;
- writer;
- scene;
- slug line;
- interior/exterior;
- location;
- time of day;
- character;
- age description;
- dialogue;
- action;
- transition;
- props;
- vehicles;
- wardrobe;
- stunts;
- VFX/practical-effect references;
- production notes.

This structure may later support a future Nexa script-writing/production product, but CineWatch TV itself is not that future writing application.


---

## 12. Production Craft

CineWatch Explore SHALL treat production craft as first-class governed knowledge.

Candidate domains:

- Writing;
- Directing;
- Cinematography;
- Editing;
- Production Design;
- VFX;
- CGI;
- Practical Effects;
- Stunts;
- Sound Design;
- Score;
- Music Supervision;
- Costume;
- Hair & Makeup;
- Props;
- Locations;
- Animation;
- Color Grading;
- Virtual Production.

Data MUST come from qualified evidence and SHALL NOT be invented when unavailable.

---

## 13. Interviews, events, images, and videos

These resources SHALL be modeled as first-class entities with provenance.

### 13.1 Interviews

Potential fields:

- title;
- related title/episode/person;
- interviewer;
- publisher;
- event;
- recording date;
- publication date;
- source;
- rights mode;
- topics.

Topics may include writing, character, direction, VFX, casting, costume, music, production, and stunts.

### 13.2 Events

Candidate event types:

- premiere;
- festival;
- press junket;
- awards ceremony;
- convention;
- panel;
- reunion;
- fan event;
- studio showcase;
- special screening.

### 13.3 Galleries

Candidate image classes:

- Poster;
- Backdrop;
- Production Still;
- Episode Still;
- Behind the Scenes;
- Premiere;
- Press Event;
- Award Event;
- Portrait;
- Character;
- Costume;
- Set;
- Location;
- Concept Art;
- Storyboard;
- VFX Breakdown.

### 13.4 Video

Candidate video classes:

- Trailer;
- Teaser;
- Clip;
- Behind the Scenes;
- Featurette;
- Interview;
- Premiere;
- Panel;
- VFX Breakdown;
- Stunt Breakdown;
- Music Video;
- Table Read;
- Production Diary.

Every resource remains subject to source/provider and underlying-content rights.

---

## 14. Cast, roles, and age semantics

CineWatch SHALL distinguish:

- person's actual date of birth;
- actor age at filming;
- actor age at release;
- character age in story;
- age range specified in casting/writing material.

These are different facts and SHALL NOT be collapsed.

Where minors or age-sensitive information is involved, privacy and safety policy must be considered independently from entertainment metadata.

---

## 15. Music & Sound

Music identity should not be owned by a single streaming provider.

The intended model is:

`CineWatch music identity -> MusicBrainz crosswalk -> optional provider adapters`

Potential Explore sections:

- Original Score;
- Soundtrack Album;
- Songs Featured;
- Composer;
- Music Supervisor;
- Performers;
- Opening Theme;
- Closing Theme;
- Episode Music.

Lyrics and synchronized lyric use require separate provider/content permission and MUST NOT be assumed from track metadata availability.

---

## 16. User identity and private beta

Initial V1 access:

**four authorized testers**

Preferred model:

`Invitation/allowlist -> registration -> verification -> authentication -> CineWatch profile`

Authentication implementation is expected to use a managed identity authority such as AWS Cognito unless later evidence changes the decision.

PostgreSQL stores CineWatch profile and state linked to the external authentication subject. Authentication passwords SHALL NOT be stored as CineWatch application data.

Candidate roles:

- `FOUNDER`
- `ADMIN`
- `TESTER`

Role names and privileges are finalized during the identity milestone.

---

## 17. User library

CineWatch SHALL distinguish:

- Watchlist — intent to watch;
- Playlist — user-curated collection;
- Favorites;
- Watch History;
- Watch Progress;
- Continue Watching — derived from progress;
- Completed/Seen;
- Rating;
- Review.

Legacy localStorage state is not V1 persistence authority.

---

## 18. Reviews and community

CineWatch Community reviews and external reviews SHALL remain visibly and structurally distinct.

### 18.1 CineWatch reviews

Expected concepts:

- review;
- revision;
- rating;
- spoiler flag;
- moderation status;
- report;
- reaction.

### 18.2 External reviews

External reviews retain provider provenance.

TMDB reviews SHALL NOT be represented as CineWatch Community reviews.

### 18.3 Future review media

V1 may prepare a `review_media` contract for future:

- Image;
- Video;
- Audio.

Actual uploads are not required in V1.

---

## 19. Cinema and theatre foundation

CineWatch TV may model:

- cinema venue;
- theatre;
- screen;
- showtime;
- seat map;
- seat;
- seat hold;
- booking;
- ticket.

V1 SHALL NOT pretend that a client-side confirmation is a completed financial transaction.

Live showtime data may come from:

- approved provider APIs;
- cinema-owned feeds;
- verified manual data;
- future partnerships.

If authoritative live data is unavailable, CineWatch must say so.

---

## 20. Playback rights authority

Playback is governed separately from metadata.

### 20.1 Rights classes

- **A — HOSTED:** CineWatch has permission to serve the media.
- **B — AUTHORIZED_EMBED:** media remains with an authorized provider and CineWatch may embed it.
- **C — PROVIDER_HANDOFF:** CineWatch identifies a legal viewing provider but does not play the full title itself.
- **D — DISCOVERY_ONLY:** no verified full-title viewing authority.

### 20.2 Fail-closed rule

`No valid playback authority -> no full-title playback claim`

### 20.3 Rights receipt

A future rights receipt is expected to record:

- subject/title;
- source;
- rights class;
- license code;
- rights holder;
- territory;
- host permission;
- embed permission;
- display permission;
- commercial-use permission;
- attribution;
- evidence source;
- evidence hash/reference;
- verification date;
- validity/expiry;
- status.

---

## 21. Provider permission authority

API/service permission and underlying-content permission are separate.

### 21.1 Provider permission asks

For each provider CineWatch must determine:

- V1 development permission;
- V2 production/noncommercial permission;
- V3 commercial path;
- metadata display;
- text/content display;
- image display;
- video embedding;
- caching;
- persistent storage;
- territory restrictions;
- attribution;
- rate limits;
- SLA;
- AI search;
- AI inference;
- AI training.

### 21.2 Source permission receipt

The operational model should support a provider-level permission record separate from title/media rights receipts.

Two gates may therefore apply:

`provider permission + content rights -> CineWatch capability`

---

## 22. Current API/content-rights outreach

The first corporate/API qualification wave was sent on **2026-09-07 CAT** to:

1. TMDB;
2. The Church of Jesus Christ of Latter-day Saints — Intellectual Property Office;
3. Genius;
4. Musixmatch;
5. Warner Bros. Discovery.

No further outreach is part of this initial commit.

Future outreach is planned in batches of five, separated by approximately twelve hours when explicitly scheduled.

The live qualification state is maintained in:

`docs/governance/CineWatch_TV_V1_API_Content_Rights_Qualification_Register_001.md`

---

## 23. External-source governance

Every external source should eventually receive a governed status such as:

- `QUALIFIED`
- `DEVELOPMENT_ONLY`
- `V2_APPROVED`
- `COMMERCIAL_PENDING`
- `CONTRACT_REQUIRED`
- `RIGHTS_PENDING`
- `PROHIBITED`
- `DEFERRED`

Provider correspondence and agreements may be confidential. The Git repository should contain public terms references and normalized decisions, not private commercial contracts or secret credentials.

---

## 24. NexVox readiness

NexVox itself is not a V1 dependency.

CineWatch V1 SHALL prepare a stable search/intelligence boundary.

Conceptually:

`TEXT | future VOICE | future NEXVOX -> Search Intent -> CineWatch Search`

Normalized intent may contain:

- query;
- language;
- entities;
- filters;
- source;
- confidence;
- spoiler boundary.

This enables future voice/AI integration without rebuilding CineWatch search.

---

## 25. AI permission separation

CineWatch SHALL distinguish:

- `AI_SEARCH_ALLOWED`
- `AI_INFERENCE_ALLOWED`
- `AI_TRAINING_ALLOWED`

Unknown AI-training permission defaults to **not training-eligible**.

External API access, content display permission, or public availability SHALL NOT be interpreted as AI-training permission.

---

## 26. NexVox data foundation

Potential CineWatch-native signals include:

- search submitted;
- result clicked;
- search abandoned;
- query reformulated;
- title viewed;
- trailer started;
- playback started;
- playback paused;
- playback completed;
- watchlist change;
- playlist change;
- favorite change;
- rating created;
- review created;
- provider selected;
- availability selected.

Consent classes must be separate:

- service/operational data;
- product analytics;
- AI-training consent;
- future voice/audio retention consent.

A user opting into analytics does not automatically opt into AI training.

---

## 27. AI training provenance

Future training candidates should be able to record:

- source;
- creator;
- license;
- consent;
- timestamp;
- transformation history;
- redaction state;
- human validation;
- training eligibility;
- dataset version.

Candidate states:

- `TRAINING_ELIGIBLE`
- `TRAINING_PROHIBITED`
- `TRAINING_REVIEW_REQUIRED`

Third-party provider content SHALL NOT automatically enter NexVox training datasets.

---

## 28. Future Nexa creative-software readiness

CineWatch's screenplay and production knowledge may later inform a separate future Nexa product for screenwriting and production planning.

Possible future functions include:

- screenplay drafting;
- revision comparison;
- character continuity;
- location reports;
- cast breakdowns;
- prop/wardrobe tracking;
- VFX/stunt requirements;
- production complexity;
- scene scheduling.

CineWatch TV SHALL remain the cinematic discovery/watch/knowledge platform rather than absorbing that future product into its core scope.

---

## 29. NexiLabs simulation-realm readiness

CineWatch TV V1 does not depend on NexiLabs simulation monetary systems or simulation registries.

The architecture should remain capable of a future realm distinction such as:

- `REAL_WORLD`
- `NEXILABS_SIMULATION`

A NexiLabs transaction may be fully authoritative and auditable within the NexiLabs realm while having no real-world legal-tender effect.

Simulation-realm integration is future-ready architecture, not a V1 release blocker.

---

## 30. Monetary integration boundary

V1 does not require a working payment gateway.

CineWatch should eventually expose a provider-neutral contract conceptually capable of:

- create payment intent;
- authorize;
- verify receipt;
- query status;
- refund/reverse.

Future implementations may include NexiLabs simulation-realm payment authority during compatible development/testing or later production systems.

Until an authoritative payment system is integrated, CineWatch SHALL NOT use a fake frontend success state to represent financial settlement.


---

## 31. Backend direction

Current target:

- Python;
- FastAPI;
- PostgreSQL;
- migration tooling;
- typed request/response contracts;
- repository/service/domain boundaries.

Preferred separation:

`API -> application services -> domain -> repositories/integrations`

The browser should not orchestrate large numbers of raw provider requests as the primary architecture.

---

## 32. Frontend direction

Current target:

- TypeScript;
- a modern component framework suitable for SEO and server/client rendering;
- modular feature boundaries;
- shared UI components;
- shared design tokens;
- typed API contracts.

The exact framework choice is finalized in CWTV.V1.2.

---

## 33. Design system

Appearance modes:

- Light;
- Dark;
- System.

Design tokens should cover:

- colors;
- typography;
- spacing;
- radii;
- shadows;
- motion;
- breakpoints;
- z-index.

Components should consume semantic tokens rather than uncontrolled hardcoded colors.

---

## 34. Naming conventions

Application naming follows ecosystem conventions:

- web files and routes: `kebab-case`;
- TypeScript values/functions: `camelCase`;
- TypeScript components/types: `PascalCase`;
- Python modules/functions: `snake_case`;
- PostgreSQL objects: `snake_case`;
- CSS custom properties: `--cw-*`;
- AWS resources: `cinewatch-v1-<environment>-*` or another explicitly governed pattern.

Formal numbered governance documents may retain controlled document names such as:

`CineWatch_Tv_V1_Blueprint_001.md`

---

## 35. Asset governance

V1 should eventually validate:

- every referenced local asset exists;
- no zero-byte asset;
- canonical placeholders exist;
- no unintended duplicate hashes;
- appropriate WebP/AVIF/SVG use;
- image dimensions are supplied;
- alt text exists where required;
- external artwork retains source/provenance;
- generated assets are distinguished from provider assets.

Missing legacy placeholders and stale asset paths SHALL NOT be carried forward blindly.

---

## 36. AWS and PostgreSQL direction

Expected AWS building blocks may include:

- RDS PostgreSQL;
- Cognito;
- S3;
- CloudFront;
- ACM;
- Route 53;
- Secrets Manager;
- KMS;
- CloudWatch;
- backend compute selected after cost/operational analysis.

CineWatch TV SHALL use its own database authority and SHALL NOT reuse the NexiLabs `npp_dev` database.

AWS credentials and database credentials must remain outside Git.

---

## 37. Environments

Expected environments:

- local;
- development;
- private beta/staging;
- production.

V1 private beta should remain non-indexed.

V2 may be production-grade while still noncommercial.

V3 enables public commercial behavior only after qualification.

---

## 38. SEO

SEO architecture should exist from V1 even when indexing is disabled.

Expected capabilities:

- canonical URLs;
- OpenGraph;
- social metadata;
- sitemap generation;
- robots controls;
- structured data for eligible resources;
- consistent product/domain identity.

V1 private environments default to:

`noindex, nofollow`

Public indexing is an explicit later release action.

---

## 39. Accessibility

Target:

**WCAG 2.2 AA**

Expected foundations include:

- keyboard navigation;
- visible focus;
- sufficient contrast;
- semantic structure;
- labels;
- screen-reader support;
- reduced-motion support;
- responsive scaling;
- captions/subtitles where provided and legally available.

---

## 40. Security

Minimum principles:

- HTTPS outside local development;
- secrets outside source control;
- no private API secrets in browser bundles;
- least-privilege IAM;
- input validation;
- parameterized database access;
- secure session/token handling;
- XSS defense;
- CSRF analysis;
- content-security policy;
- audit logging;
- dependency scanning;
- backup/restore strategy;
- encryption at rest where appropriate;
- private storage by default.

---

## 41. Privacy

Data classes should distinguish:

- authentication data;
- profile data;
- behavioral/operational data;
- analytics;
- community content;
- AI-training data;
- future voice/audio data.

Retention and consent policies are finalized before collection expands beyond V1 necessity.

---

## 42. Observability and audit

V1 should eventually support:

- structured logs;
- request IDs;
- correlation IDs;
- provider latency;
- provider failure counts;
- API quota visibility;
- rights-verification failures;
- playback failures;
- authentication events;
- important mutation audit events.

Important governance mutations should record actor, action, subject, timestamp, and correlation context.

---

## 43. Testing and CI

Expected qualification layers:

- unit tests;
- contract tests;
- repository tests;
- integration tests;
- API tests;
- frontend component tests;
- end-to-end tests;
- migration checks;
- asset validation;
- security/dependency checks.

Human testing by the four V1 testers supplements but does not replace automated qualification.

---

## 44. Initial milestone sequence

### CWTV.V1.1 — Brand, Experience, Legacy, Rights & Governance Foundation

Establish product identity, release lifecycle, legacy authority, Discover/Watch/Explore/My CineWatch, rights governance, provider qualification, and initial documentation.

### CWTV.V1.2 — Repository & Engineering Foundation

Establish runnable application structure, frontend/backend choices, formatting, linting, tests, CI, contracts, and migration tooling.

### CWTV.V1.3 — Design System & Asset Foundation

Establish tokens, typography, themes, shared components, accessibility baseline, and asset qualification.

### CWTV.V1.4 — AWS & PostgreSQL Foundation

Establish CineWatch-owned AWS environments, PostgreSQL, secrets handling, connectivity, migrations, observability, and backups.

### CWTV.V1.5 — Identity & Private Membership

Implement registration/invitation, authentication, profiles, roles, tester access, membership/entitlement foundations.

### CWTV.V1.6 — Canonical Content Foundation

Create CineWatch identities and external crosswalks.

### CWTV.V1.7 — External API Gateway

Implement provider adapters, caching, quotas, provenance, and source-policy enforcement.

### CWTV.V1.8 — Rights & Availability Authority

Implement rights receipts, provider permission state, territory-aware availability, and fail-closed playback.

### CWTV.V1.9 — Discover Experience

Implement the broad metadata/discovery experience.

### CWTV.V1.10 — Watch Experience & Legal Playback

Implement verified CineWatch playback/embedding/provider handoff.

### CWTV.V1.11 — Explore & Cinematic Knowledge

Implement the first Explore knowledge domains, including production evidence and rights-governed resources.

### CWTV.V1.12 — User Library

Implement watchlists, playlists, favorites, history, progress, and Continue Watching.

### CWTV.V1.13 — Community & Reviews

Implement CineWatch ratings/reviews, external review separation, and moderation foundations.

### CWTV.V1.14 — Cinema Foundation

Implement venue/showtime/booking data architecture without pretending unavailable payment/showtime authority exists.

### CWTV.V1.15 — NexVox Data & Search Foundation

Implement consent-aware events, search-intent contract, provenance, and training-eligibility architecture.

### CWTV.V1.16 — SEO, Accessibility, Privacy & Security Qualification

Complete private-beta qualification across these cross-cutting concerns.

### CWTV.V1.17 — Private Beta Qualification

End-to-end regression, rights audit, provider quota audit, restore tests, user acceptance, and V1 freeze.

---

## 45. Governance locks

### LOCK-001 — Legacy authority

`CineWatchStream` SHALL NOT become the V1 runtime authority.

### LOCK-002 — CineWatch state

PostgreSQL SHALL own CineWatch-native persistent state.

### LOCK-003 — Playback

No full-title playback claim SHALL occur without an approved legal viewing authority.

### LOCK-004 — Experiences

Discover and Watch SHALL remain distinct experiences over shared canonical content identities.

### LOCK-005 — Explore

Cinematic source material, production evidence, interviews, events, photographs, videos, and craft knowledge SHALL be independently governed first-class resources rather than unstructured attachments.

### LOCK-006 — External identities

External provider IDs SHALL NOT silently become CineWatch primary identities.

### LOCK-007 — Provider/content rights

API permission SHALL NOT be treated as underlying-content copyright permission.

### LOCK-008 — Screenplay semantics

Screenplay, transcript, subtitle, caption, quote, and article SHALL remain semantically distinct.

### LOCK-009 — AI permissions

AI search, AI inference, and AI training SHALL remain separate permissions.

### LOCK-010 — Training

Third-party content SHALL NOT automatically become NexVox training data.

### LOCK-011 — Consent

Product analytics consent SHALL NOT automatically constitute AI-training consent.

### LOCK-012 — NexiLabs dependency

NexiLabs monetary or registry availability SHALL NOT block CineWatch TV V1.

### LOCK-013 — Realm integrity

Any future NexiLabs integration SHALL preserve realm-scoped authority and prevent silent cross-realm state.

### LOCK-014 — Styling

Frontend styling SHALL be governed by reusable semantic design tokens and shared components.

### LOCK-015 — Secrets

Secrets SHALL NOT be committed to Git or exposed in browser code.

### LOCK-016 — Private beta indexing

V1 private beta SHALL remain non-indexed until public-release qualification explicitly changes that state.

### LOCK-017 — Documentation authority

This Markdown blueprint is the editable source. An approved PDF is a frozen human-readable rendering and SHALL NOT be maintained as an independent divergent specification.

---

## 46. V1 qualification criteria

V1 is not qualified merely because pages render.

At minimum, the authorized testers must be able to:

- authenticate;
- maintain profiles;
- discover content;
- search;
- open canonical details;
- see clear legal availability;
- play only verified authorized content;
- use watchlists/playlists;
- maintain progress/history;
- rate and review;
- inspect CineWatch versus external-review provenance;
- use qualified Explore resources;
- view available cinema information.

And the system must prove:

- PostgreSQL persistence;
- backend authority;
- rights enforcement;
- provider policy enforcement;
- private-beta access controls;
- migration repeatability;
- backup/restore readiness;
- automated qualification.

---

## 47. V2/V3 readiness gates

Before V2/V3 expansion, review:

- provider terms;
- commercial/API licensing;
- public registration;
- privacy/terms;
- content licensing;
- brand/trademark clearance;
- production payment authority;
- moderation;
- security assessment;
- scale/cost;
- SEO indexing;
- AI permission status;
- territory handling.

---

## 48. Approval

**Blueprint ID:** `CWTV-V1-BLUEPRINT-001`

**Revision:** `001`

**Status:** APPROVED

**Approval statement:** I approve CWTV-V1-BLUEPRINT-001 Revision 001.

**Approved by:** Alex Malunda

**Role / authority:** Developer

**Approval recorded:** 2026-09-07 10:32:59 CAT (UTC+02:00)

**Digital Signature Code:** `DEV_SIG007353F`

**Signed date:** 2026-09-07

**Signed time:** 11:03 CAT (UTC+02:00)

**Signed PDF artifact:** `CineWatch_Tv_V1_Blueprint_001.pdf`

**Signed PDF SHA-256:** `11be70aa7519ed32128343f862e15deb969744306155b0cf92edcb131a66cdb3`

**Signature attestation:** VERIFIED

The signed PDF companion is immutable approval evidence. Its embedded post-signature fields still state `PENDING SIGNED COPY` because those fields were printed before the signature was applied. They are intentionally not edited after signing: modifying the PDF would produce a different SHA-256 and weaken the attestation chain. This Markdown approval record therefore carries the final verification hash for the signed PDF.

Sections 1-47 remain the approved substantive blueprint. Changes to those governed sections after this approval require an explicit revision or correction process rather than silent edits.
