# CineWatch TV

**Status:** V1 Private Beta Development
**Repository:** `Asleki/cinewatch-tv`
**Product:** CineWatch TV
**Current release authority:** V1
**Planned public domain:** `cinewatchtv.com`

CineWatch TV is a legal-first movie, television, cinema, cinematic-companion, and media-knowledge platform. V1 is a new implementation and does not evolve the legacy `Asleki/CineWatchStream` codebase in place.

## Product direction

CineWatch TV is designed around four primary experiences:

- **Discover** — the wider movie, television, people, cinema, and entertainment metadata universe.
- **Watch** — titles with a verified legal viewing path, including CineWatch-authorized playback, authorized embeds, provider handoff, rental/purchase availability, and cinema availability.
- **Explore** — the cinematic companion and knowledge layer: story, characters, cast and crew, writing, screenplays where rights permit, music, interviews, events, galleries, production craft, VFX/CGI, locations, awards, and related production evidence.
- **My CineWatch** — authenticated user state: watchlists, playlists, favorites, history, progress, ratings, reviews, preferences, and future personalization.

CineWatch TV is not intended to be a TMDB clone, a YouTube channel, or an unlicensed streaming index. External APIs and providers supply governed evidence, enrichment, availability, or media access. CineWatch TV owns its own application state and canonical relationships.

## Release lifecycle

- **V1 — Development:** private, invite-only development and testing; initially four authorized testers; no commercial activity.
- **V2 — Production + Research:** production-grade deployment, still noncommercial; AI/ML research only where applicable data/content rights explicitly permit it.
- **V3 — Commercial:** future commercial release after required provider, API, content, distribution, and other commercial rights are qualified.

## Legacy repository

`Asleki/CineWatchStream` is retained as the **Legacy Product Source of Truth** for styling intent, page concepts, content taxonomy, interaction history, and prior integration evidence.

It is **not** runtime authority for V1 authentication, backend architecture, persistent state, legal playback decisions, secrets, payments, deployment, or security.

## Governance and architecture authority

The approved V1 blueprint source is:

`docs/blueprints/CineWatch_Tv_V1_Blueprint_001.md`

Its signed human-readable approval companion is:

`docs/blueprints/CineWatch_Tv_V1_Blueprint_001.pdf`

The approved engineering architecture is:

`docs/architecture/CineWatch_TV_V1_Engineering_Architecture_Selection_001.md`

The current API/content-rights qualification register is:

`docs/governance/CineWatch_TV_V1_API_Content_Rights_Qualification_Register_001.md`

## Engineering foundation

The initial V1 engineering direction is:

- Next.js + TypeScript web boundary under `apps/web`;
- FastAPI + Python backend boundary under `services/api`;
- PostgreSQL 17 server target with an independent `cinewatch_dev` database authority;
- npm workspaces with one root `package-lock.json`;
- Node 24 and npm 12 toolchain lines;
- Python 3.14 toolchain line;
- FastAPI OpenAPI as future runtime API-schema authority;
- Termux-supported local engineering with Linux CI authoritative for platform-specific production builds;
- AWS development followed by a governed AWS-to-Azure migration during V1;
- NPP integration, when needed, through governed provider/service contracts rather than shared application tables.

## Repository boundaries

```text
apps/web            CineWatch web application boundary
services/api        CineWatch backend service boundary
packages/contracts  Shared/generated API-contract boundary
scripts             Repository engineering and qualification scripts
tests               Cross-cutting repository qualification
docs                Blueprint, governance, architecture, and decisions
```

Product-feature implementation is introduced only by its owning milestone.

## Security

Never commit:

- passwords;
- API keys;
- OAuth client secrets;
- AWS or Azure credentials;
- database credentials;
- private certificates or signing keys;
- private contracts or confidential provider correspondence;
- personal access tokens.

Use environment variables and approved secret stores when the relevant infrastructure milestone begins.

## Licensing

No open-source license has been selected for this repository. Until an explicit licensing decision is made, do not assume that repository visibility or access grants permission to reuse, redistribute, or commercially exploit the source code.

## Current milestone

**CWTV.V1.2.4 — Frontend Application Skeleton**

The repository now contains qualified repository/toolchain and FastAPI backend foundations. CWTV.V1.2.4 introduces the first Next.js App Router runtime boundary while keeping Discover, Watch, Explore, My CineWatch, authentication, database schemas, provider integrations, rights enforcement, playback, and final design assets out of scope.
