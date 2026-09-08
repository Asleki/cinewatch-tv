# CineWatch TV V1 Frontend Application Skeleton 001

**Document ID:** `CWTV-V1-FRONTEND-SKELETON-001`

**Milestone:** `CWTV.V1.2.4`

**Status:** IMPLEMENTATION CANDIDATE

**Baseline commit:** `c0324fc80fedca08a7a0fa41cb9adef7e7575869`

**Prepared:** `2026-09-07 23:29:29 CAT (UTC+02:00)`

## 1. Purpose

This milestone creates the first runnable CineWatch TV web application boundary without implementing CineWatch product experiences or the V1.3 design system.

The skeleton proves Next.js App Router, React, strict TypeScript, metadata/robots/manifest hooks, error/loading/not-found boundaries, public environment parsing, a typed system-endpoint adapter, lint/type/build gates, and a live production-server smoke path.

## 2. Framework authority

The qualified candidate pins:

- Next.js `16.3.4` (Active LTS line at preparation time);
- React and React DOM `19.2.8`;
- TypeScript `6.0.3`;
- ESLint `9.39.5` with `eslint-config-next` `16.3.4` (temporary compatibility lock);
- Node `24.18.0` and npm `12.0.2` from the existing repository toolchain authority.

TypeScript 7 is intentionally not adopted because current Next.js 16 runtime TypeScript detection still depends on the JavaScript compiler API layout removed by TypeScript 7. TypeScript 6 retains the required API shape while allowing the project to stay on a current strict compiler line.

ESLint 10 is intentionally deferred in this milestone. The current `eslint-config-next` dependency graph still includes `eslint-plugin-react` code that calls the legacy `context.getFilename()` API removed by ESLint 10, which causes the observed `react/display-name` loader failure under ESLint `10.10.0`. ESLint `9.39.5` is therefore pinned as a compatibility exception for V1.2.4. This pin is not a long-term platform preference and must be re-evaluated once the Next.js lint dependency graph is demonstrably ESLint-10 compatible.

## 3. Application boundary

The web runtime is owned by `apps/web`.

Server Components remain the default. Client Components are introduced only where the App Router requires them; the error boundaries are the only client components in this milestone.

The Next.js application does not create `src/app/api` routes. CineWatch application APIs, rights enforcement, persistence, provider policy, and future domain logic remain behind `services/api`.

## 4. Build portability

Next.js 16 defaults to Turbopack, but this milestone explicitly uses the documented `--webpack` fallback for development/build qualification. This reduces unnecessary coupling to Android-incompatible native tooling while preserving a standard supported Next.js production build path on Linux.

Native Android/Termux remains repository-control tooling, not an authoritative Next.js production-build platform. Full web lint/type/build/live qualification runs in the already established Linux userland or later Linux CI.

## 5. Public configuration

The frontend recognizes only public, non-secret values:

- `NEXT_PUBLIC_CINEWATCH_API_BASE_URL`;
- `NEXT_PUBLIC_CINEWATCH_SITE_URL`.

Both default to local loopback URLs when unset. No provider credentials are exposed to the browser.

The typed system client may call only the CineWatch FastAPI authority. It does not call TMDb, YouTube, or any other external provider directly.

## 6. Private-beta indexing policy

V1 remains private development. The frontend therefore establishes two independent no-index signals:

- root metadata sets `index=false` and `follow=false`;
- `robots.txt` disallows `/` for every user agent.

A public sitemap is intentionally not introduced in V1.2.4.

## 7. Asset locations

The following public locations are reserved now:

```text
apps/web/public/brand/
apps/web/public/icons/
apps/web/public/seo/
```

They contain only `.gitkeep` placeholders. Logos, favicons, wordmarks, final icons, social artwork, design tokens, and visual-system authority remain owned by `CWTV.V1.3 — Design System & Asset Foundation`.

The manifest is intentionally icon-free until that governed asset milestone.

## 8. Presentation restraint

The skeleton contains only structural CSS required for a usable baseline. It does not declare the CineWatch color system, typography system, component library, layout language, artwork policy, or other visual identity.

## 9. Qualification

The milestone must pass:

1. repository tree regression;
2. frontend skeleton static policy;
3. repository unittests;
4. deterministic npm lock generation under Node 24/npm 12;
5. Linux npm clean install;
6. ESLint;
7. strict TypeScript check;
8. Next.js production build using the governed webpack fallback;
9. live root route smoke;
10. live `robots.txt` policy check;
11. live manifest check;
12. `git diff --check` and clean post-commit worktree.

## 10. Explicit exclusions

This milestone does not implement Discover, Watch, Explore, My CineWatch, authentication, canonical catalogue pages, playback, cinema, provider adapters, PostgreSQL, rights/availability authority, final SEO, final brand assets, final design tokens, or NexVox.

## 11. Forward boundary

After qualification, `CWTV.V1.2.5 — PostgreSQL & Migration Foundation` owns the independent CineWatch PostgreSQL authority and migration substrate. `CWTV.V1.3` remains the first milestone allowed to establish final design-system and asset authority.
