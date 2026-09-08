# CWTV ADR 0003 — Frontend Runtime and Build Portability

**Status:** ACCEPTED FOR CWTV.V1.2.4 CANDIDATE

**Baseline:** `c0324fc80fedca08a7a0fa41cb9adef7e7575869`

**Prepared:** `2026-09-07 23:29:29 CAT (UTC+02:00)`

## Decision

CineWatch TV V1 uses Next.js 16.3.4 App Router with React 19.2.8 and TypeScript 6.0.3 under the existing Node 24/npm 12 toolchain authority.

`next dev --webpack` and `next build --webpack` are the initial governed web commands. Native Android/Termux is not a production-build gate. Full Next.js runtime qualification runs in Linux userland and later Linux CI.

## Reasons

- Next.js 16 is the active supported major line at preparation time.
- Next.js officially supports Linux, macOS, and Windows rather than Android as a native target.
- TypeScript 7's native compiler package layout is not yet compatible with Next.js 16's TypeScript dependency detection; TypeScript 6 remains compatible with the JavaScript compiler API expected by Next.js.
- The webpack fallback is explicitly supported by Next.js 16 and avoids making Turbopack-specific native behavior a V1.2.4 requirement.
- CineWatch's approved architecture already states that Linux CI is authoritative for frontend production builds.

## Consequences

- Termux may still manage npm metadata and repository files, but a failed native Android Next.js build is not a release failure.
- The existing `cwtv-linux` PRoot environment can host a Node 24 Linux ARM64 runtime for local full-build proof.
- A later governed update may move the build to Turbopack after CI/platform qualification without changing the App Router product architecture.
