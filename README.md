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

- **V1 — Development:** approximately 6 months; private, invite-only development and testing; initially four authorized testers; no commercial activity.
- **V2 — Production + Research:** approximately 12 months; production-grade deployment, still noncommercial; AI/ML research only where the applicable data/content rights explicitly permit it.
- **V3 — Commercial:** future commercial release after required provider, API, content, distribution, and other commercial rights are qualified.

## Legacy repository

`Asleki/CineWatchStream` is retained as the **Legacy Product Source of Truth** for styling intent, page concepts, content taxonomy, interaction history, and prior integration evidence.

It is **not** the runtime authority for V1 authentication, backend architecture, persistent state, legal playback decisions, secrets, payments, deployment, or security.

## Architecture authority

The approved V1 blueprint source is:

`docs/blueprints/CineWatch_Tv_V1_Blueprint_001.md`

Its signed human-readable approval companion is:

`docs/blueprints/CineWatch_Tv_V1_Blueprint_001.pdf`

The current API/content-rights qualification register is:

`docs/governance/CineWatch_TV_V1_API_Content_Rights_Qualification_Register_001.md`

## Initial engineering direction

The blueprint currently targets:

- AWS-hosted services;
- PostgreSQL as the authoritative CineWatch data store;
- a CineWatch-owned backend/API boundary;
- a modular frontend with a governed design system;
- real authentication and user state;
- provider-neutral rights and availability contracts;
- future NexVox search/inference integration without making AI a V1 blocker;
- future NexiLabs simulation-realm integration without making NexiLabs monetary systems a V1 dependency.

The exact application stack and deployable repository tree are established in the next engineering milestone after Blueprint 001 is reviewed and approved.

## Security

Never commit:

- passwords;
- API keys;
- OAuth client secrets;
- AWS credentials;
- database credentials;
- private certificates or signing keys;
- private contracts or confidential provider correspondence;
- personal access tokens.

Use environment variables, AWS Secrets Manager, or another approved secret store when the relevant infrastructure milestone begins.

## Licensing

No open-source license has been selected for this repository. Until an explicit licensing decision is made, do not assume that repository visibility or access grants permission to reuse, redistribute, or commercially exploit the source code.

## Current milestone

**CWTV.V1.1 — Brand, Experience, Legacy, Rights & Governance Foundation**

The repository begins with documentation and governance authority before production application code is introduced.
