# CineWatch TV Web Application

`apps/web` is the governed Next.js App Router boundary for CineWatch TV V1.

CWTV.V1.2.4 established the runnable application skeleton. CWTV.V1.2.6 replaces hand-maintained system API response interfaces with type-only imports from `@cinewatch/contracts`, whose declarations are generated from the canonical FastAPI OpenAPI document.

It still does not implement Discover, Watch, Explore, My CineWatch, authentication, catalogue pages, playback, cinema, provider integrations, or the final design system.

## Commands

From the repository root:

```text
npm run dev:web
npm run lint:web
npm run typecheck:web
npm run build:web
npm run contracts:check
```

The full Next.js production build is qualified in Linux. Native Android/Termux remains a repository-control environment and is not a release build target.

## Authority boundary

CineWatch application APIs remain behind `services/api`. Do not add provider credentials or direct provider authority to browser code. API response types already represented in OpenAPI must come from `@cinewatch/contracts`, not duplicate frontend interfaces.

Public asset locations are reserved under `public/brand`, `public/icons`, and `public/seo`. Their actual governed contents begin in CWTV.V1.3.
