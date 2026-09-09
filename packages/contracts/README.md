# CineWatch TV API Contracts

`@cinewatch/contracts` is the governed TypeScript projection of the CineWatch FastAPI OpenAPI authority.

CWTV.V1.2.6 establishes this one-way contract chain:

```text
FastAPI route + Pydantic response authority
        ↓
canonical OpenAPI 3.1 JSON
        ↓
openapi-typescript 7.13.0
        ↓
@cinewatch/contracts generated declarations
        ↓
Next.js consumers
```

The checked-in canonical document is `openapi/cinewatch-v1.openapi.json`. The generated declaration is `src/generated/openapi.d.ts`. Neither file is hand-edited. `src/index.d.ts` is the small governed public type surface used by application code.

Run from the repository root:

```text
npm run contracts:update
npm run contracts:check
```

The backend owns API truth. Browser code must not independently redefine response interfaces that are already represented by the canonical OpenAPI contract.

This milestone contains only the system skeleton endpoints. Discover, Watch, Explore, My CineWatch, authentication, providers, rights, cinema and NexVox contracts are deliberately out of scope.
