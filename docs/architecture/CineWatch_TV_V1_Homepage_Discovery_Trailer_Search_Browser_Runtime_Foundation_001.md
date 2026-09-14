# CineWatch TV V1 Homepage Discovery, Trailer, Search & Browser Runtime Foundation

**Milestone:** `CWTV.V1.3.3.2.2`
**Status:** Implementation candidate — browser qualification required
**Parent:** `CWTV.V1.3.3.2`
**Builds on:** `CWTV.V1.3.3.2.1` Homepage Data Contract & TMDb Aggregation Authority

## Purpose

This milestone turns the qualified homepage data contract into the first real CineWatch TV homepage experience. It intentionally aims for a polished V1 product surface without pretending every future CineWatch page, data source, or rightsholder workflow is complete.

The homepage remains the only product page implemented by this slice. Details, cast, genre, network, country, news, archive, account, playlist, and playback destinations are future surfaces.

## Locked product language

CineWatch uses two distinct top-level labels:

- **Stream Now** — content CineWatch TV is authorized to play inside CineWatch. Geography does not determine eligibility. Until rights-cleared titles exist in the runtime, five inert visual placeholders are shown and no provider title is misrepresented as streamable.
- **Discover** — the broader entertainment-information world. It can present provider-sourced metadata and preserve future destinations even when navigation to those destinations is not implemented yet.

`Hosted` is not a user-facing content label.

## Unified site frame

The Next.js root layout owns a shared CineWatch site frame for product pages:

- exact qualified CineWatch TV repository lockups;
- Home, Stream Now, and Discover navigation labels;
- unified search input;
- browser voice-search affordance when the browser exposes speech recognition;
- dark/light mode switching;
- account placeholder;
- responsive footer groups;
- mobile bottom navigation.

The development-only brand-qualification route remains outside this product frame so its already-qualified visual evidence is not reinterpreted by homepage styling.

## Homepage data loading

The first viewport continues to use the bounded `GET /api/v1/home` contract from `.2.1`.

The initial response owns:

- one hero;
- Trending Now;
- Popular Movies;
- Popular TV Shows.

The existing `trending_people` provider surface remains available to the backend contract but is intentionally not rendered as a homepage rail. People remain discoverable through search and future cast/person destinations.

## Lightweight future identity

Homepage cards are intentionally inert in this milestone, but each card preserves enough identity for later navigation without preloading a details page:

- provider identity;
- media type;
- title;
- poster/backdrop already needed for presentation;
- date;
- homepage rating;
- genre identities;
- synopsis already present in the bounded homepage contract;
- deterministic future CineWatch path.

Movie and television cards preserve `/title/{media_type}/{provider_id}`. Person search suggestions preserve `/person/{provider_id}`. Genre and editorial suggestions preserve their future CineWatch paths.

The homepage does not preload casts, reviews, episodes, complete video catalogs, or other details-page payloads for every card.

## Hero enrichment

Only the single hero receives lazy high-value enrichment.

The hero enrichment service may add:

- writers or creators from TMDb credits/creator metadata;
- IMDb, Rotten Tomatoes, and Metacritic display values when OMDb can enrich a valid IMDb identity;
- one deterministically selected YouTube trailer or teaser;
- a quote only when an authoritative future source supplies one.

No quote is fabricated. CineWatch Rating is not displayed until CineWatch owns a real rating/review source for it.

OMDb enrichment is optional. OMDb failure does not take down the TMDb-powered homepage.

## Trailer authority

`Watch Trailer` exists only when the hero enrichment contract returns a qualifying trailer.

For movies, CineWatch ranks TMDb video candidates by:

1. YouTube site;
2. Trailer before Teaser;
3. official flag;
4. official wording as a secondary signal;
5. newest publication date.

For television, CineWatch first resolves the latest regular aired season and asks for that season's videos. If that yields no qualifying trailer, series-level videos are filtered so an explicitly different season is rejected and obviously stale videos before the current-season window are excluded.

The homepage trailer modal embeds the selected video with the privacy-enhanced YouTube domain and keeps the user inside CineWatch.

The Teasers & Trailers rail is lazy and bounded. Its candidate count is deliberately small to avoid an unbounded fan-out of provider requests.

## Dynamic discovery

Lazy discovery rails are available for:

- Upcoming;
- K-Drama;
- Kenyan Stories;
- Bollywood;
- Nollywood;
- Chinese;
- Hollywood;
- Documentaries;
- Reality;
- Tyler Perry.

These are CineWatch discovery labels, not claims that TMDb natively defines those categories. Current heuristics are a V1 foundation and may be refined later without changing the meaning of Stream Now.

The first Kenyan Stories heuristic combines Kenyan-origin movie/TV discovery with Swahili-language TV discovery, then deduplicates and ranks the bounded result. It does not yet perform expensive per-title cast-nationality analysis on the homepage.

Genres are fetched dynamically from TMDb movie and television genre authorities, merged into CineWatch genre identities, and presented without opening a genre page yet.

## Search

The unified search surface combines:

- live movie/TV/person suggestions from the CineWatch API;
- dynamic genre matches;
- CineWatch editorial discovery labels;
- selected country/culture identities.

Selecting a suggestion stays on Home in this milestone. The selected suggestion already carries a future route identity for the later page implementation.

## Transport boundary

FastAPI remains the sole application API authority.

Next.js does not implement an application API route. A narrow Next.js rewrite maps the browser's same-origin `/api/cinewatch/*` transport path to the configured FastAPI `/api/v1/*` authority. This avoids browser CORS coupling during local development while preserving the existing rule that provider credentials and provider policy remain server-only in FastAPI.

The rewrite contains no provider credentials and no product business logic.

## Responsive visual target

The approved three-screen homepage board is the visual reference rather than a pixel-perfect screenshot contract. Browser qualification evaluates the real implementation at desktop, tablet, and mobile widths and may accept small implementation differences when the product remains coherent, readable, responsive, and faithful to the approved CineWatch identity.

The implementation must reuse repository production brand assets; it must not regenerate the A3 mark or lockup.

## Deferred by design

This milestone does not make the following live:

- CineWatch-owned playback titles;
- details pages;
- genre pages or Load More pages;
- network pages;
- person/cast pages;
- country pages;
- CineWatch reviews/ratings;
- quote automation;
- My List persistence;
- Archives pages;
- News pages;
- other footer destinations.

Their labels or future identities may be visible, but they must not pretend the corresponding product surface already exists.

## Qualification

The implementation candidate becomes qualified only after:

1. focused homepage experience unit tests pass;
2. endpoint tests pass;
3. canonical OpenAPI and generated TypeScript contracts are regenerated and checked;
4. the existing `.2.1` homepage foundation checker remains green;
5. the frontend skeleton checker remains green without weakening the FastAPI API boundary;
6. the `.2.2` homepage experience checker passes;
7. frontend lint, typecheck, and production build pass in the qualified Linux runtime;
8. backend and repository regressions pass;
9. `git diff --check` and Markdown/text whitespace gates pass;
10. the live FastAPI runtime proves the new endpoints with real configured provider credentials;
11. the live Next.js homepage is human-reviewed in the browser at desktop/tablet/mobile widths;
12. trailer availability, trailer modal behavior, search, mode switching, lazy rails, Stream Now placeholders, and footer behavior are visually accepted;
13. Chronicle evidence is recorded before source commit;
14. NexVox is regenerated from the exact qualified source commit only after source qualification.

The visual objective is high quality, not artificial perfection. Browser review may produce a bounded correction before qualification.
