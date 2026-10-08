# Stream Now V2 — dormant Player integration

Milestone: CWTV.V1.3.3.2.7. Owner-corrected implementation authority: [V2 work order](https://docs.google.com/document/d/1vmaYVdRgRGRwBnwiu3RAu0Jy-FbdMiD5H2KAkYaDe9M/edit), observed 8 October 2026. Its animation-only experience supersedes earlier empty-library/category proposals.

## Source authority

Player donor: `Asleki/cinewatch-player-lab`, commit `be46e3a83cfa157f0bdb91b776ad5216a08cc197`, Player Lab CI `35520671181` succeeded. Donor repository remains unchanged. CineWatch baseline: `094675a9f53daca7fa7bbce03b2be4672c17bb81`.

The component preserves the donor control, gesture, seek, caption, fullscreen, Picture-in-Picture, Remote Playback boundary and network/recovery implementation. Adaptations: add a player-scoped stylesheet import and remove the lab qualification diagnostics panel. Retain manifest types; strengthen runtime shape/URL validation. Extract only player styles with a player-shell scope; exclude lab/CinePlay/global styles, retain existing CineWatch theme/font and visible focus.

No lab media routes, file scanners, subtitles acquisition endpoints, private fixtures, movie files, provider secrets or donor dependencies enter production. Source inspection and local fixture playback do not establish a film's rights or public streaming permission. External Cast receiver delivery, DRM/HLS and subtitle-provider integration remain outside this milestone.

## Production composition and boundary

`/stream-now` resolves its manifest through a `server-only` module, then renders the real reusable engine only when a server-authorized manifest exists. The production resolver deliberately returns null for every identity. No query string, TMDb identity, browser storage, client-supplied manifest or environment URL can issue permission or create a playable source. There is no new public playback API, migration or storage provisioning.

The current default is solely a CineWatch mark on a silent CSS composition: three slowly flowing navy/aqua/teal gradient layers, one complete 30-second transform cycle, infinite seamless looping and a static reduced-motion composition. Global navigation remains usable; no catalogue, disabled player, fake film or project-state copy appears. `/under-development/stream-now` permanently redirects. All product Stream Now links use the real destination; title metadata carries no playback selection. YouTube trailers and external Where to Watch retain their separate routes.

Future authorized media onboarding must implement and qualify rights/agreement authority, authentication/entitlement, availability/territory, protected delivery/ranges and scoped manifest issuance on the server before changing the zero-source resolver. Shape validation alone is never authorization. No owner agreement, private origin or credential should be serialized to the public browser.

## Qualification and provenance

Repository regressions execute real manifest validation and denied identities. Private browser qualification bundles the actual engine outside the repository and uses generated synthetic WebM/VTT served only on loopback with byte ranges; it never ships test media or test routes. Built Next/browser and live acceptance independently check route links, no public media/engineering UI, 30-second cycle, reduced motion, light/dark/mobile and existing discovery/trailer journeys.

Chronicle preserves expected missing-feature red tests and tooling/harness failures separately from application defects, including the initial synthetic HTTP server's absent byte-range support. Append-only events, current milestone/progress and correction metrics remain canonical; generated dashboard/Markdown and CineWatch-local NexVox/PDF precede the filtered Praxis successor. ChatGPT Chat provides planning/review/owner authorization, Codex executes/qualifies, GitHub holds source authority, Drive holds durable evidence, and SSM transports the separately authorized exact-SHA production deployment.
