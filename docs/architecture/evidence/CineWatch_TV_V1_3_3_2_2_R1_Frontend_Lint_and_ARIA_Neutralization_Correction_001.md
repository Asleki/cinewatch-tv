# CineWatch TV V1.3.3.2.2-R1 Frontend Lint and ARIA Neutralization Correction Evidence 001

**Milestone:** CWTV.V1.3.3.2.2-R1
**Status:** Correction candidate
**Date:** 2026-09-12

## Trigger

The first frontend qualification gate for CWTV.V1.3.3.2.2 produced a successful Next.js production build but failed the dedicated web lint gate with two errors and four warnings.

The blocking errors were both `react-hooks/set-state-in-effect` findings in `SiteFrame.tsx`. The warnings covered an unused React import, an effect dependency shape, unsupported `aria-disabled` on an `article`, and a listbox option without `aria-selected`.

Because browser qualification is downstream of source quality qualification, the milestone must remain unqualified until the frontend lint gate is clean.

## Correction boundary

This correction changes only the two new homepage runtime components introduced by CWTV.V1.3.3.2.2:

- `apps/web/src/components/site/SiteFrame.tsx`
- `apps/web/src/components/home/HomepageExperience.tsx`

It does not modify API aggregation, provider credentials, OpenAPI contracts, generated contract outputs, PostgreSQL, AWS, NexVox, Chronicle projections, or unrelated frontend files.

## Neutralization

`SiteFrame.tsx` now initializes persisted/system theme state through a browser animation-frame callback rather than synchronously setting React state in the effect body. Short search queries are cleared from API suggestion state in user-event handlers instead of synchronously in the query effect. Search listbox options now expose `aria-selected`.

`HomepageExperience.tsx` removes the unused `useMemo` import, makes hero-effect dependencies primitive and explicit, and removes unsupported `aria-disabled` from the inert Stream Now placeholder article.

## Acceptance

R1 is accepted only if all of the following pass after placement:

- `npm run typecheck -w @cinewatch/web`
- `npm run lint -w @cinewatch/web`
- `npm run build -w @cinewatch/web`
- `python scripts/check_homepage_experience.py`
- repository regression
- `git diff --check`

Browser qualification remains a separate human gate after these source gates pass.
