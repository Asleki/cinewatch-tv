# CineWatch TV V1.3.3.2.2 Homepage Board Reference & Runtime Qualification Evidence

**Milestone:** `CWTV.V1.3.3.2.2`
**Evidence status:** Visual reference locked; runtime browser evidence pending
**Date:** 2026-09-12

## Approved visual reference

The approved homepage reference board is:

`CineWatch_TV_Homepage_Board_3Screens_Footer_Exact_Repo_Logo_FINAL.png`

Measured reference properties:

- dimensions: `1536 × 1229` pixels;
- SHA-256: `166a8da7fe6c2e2793d5f2083091d000d3f3057953cecde42bfad8f5101e1515`;
- three intended responsive views: desktop `1440 × 900`, tablet `834 × 1112`, mobile `390 × 844`;
- brand source: existing qualified CineWatch TV repository assets, not regenerated artwork.

The board is a visual target, not a requirement to hard-code the sample entertainment titles visible in the board. Live homepage content comes from the qualified CineWatch API contracts.

## User-approved semantic corrections after the board

The runtime implementation must apply these corrections even when the board visually shows sample titles:

- Stream Now means content CineWatch is authorized to play inside CineWatch;
- provider metadata or Kenyan identity alone never makes a title Stream Now content;
- Stream Now is represented by five inert placeholders until real playback rights are modeled;
- homepage media cards remain inert in this milestone while preserving future destination identity;
- footer destinations that do not exist remain non-clickable;
- people are removed as a rendered homepage rail;
- trailer playback is live when a qualifying trailer exists;
- genres, search, cultural/editorial discovery, and lazy rails can be live while staying on Home.

## Browser qualification still required

No static board can qualify the production homepage by itself.

After placement and automated gates, human browser review must verify the real Next.js runtime against real CineWatch API data at approximately desktop, tablet, and mobile widths.

Review must cover:

- exact CineWatch repository lockup use;
- hero visual balance and readability;
- ratings and synopsis behavior;
- season-aware Watch Trailer availability and in-page playback;
- Stream Now rights-safe placeholders;
- horizontal rails and lazy loading;
- dynamic Genres;
- search suggestions for titles, people, genres, editorial labels, and country/culture identities;
- theme switching;
- desktop/tablet/mobile navigation behavior;
- responsive footer anatomy;
- no accidental navigation to unimplemented pages.

Runtime screenshots, any correction identity, and final human approval belong in the Chronicle only after the implementation is running in the live repository.
