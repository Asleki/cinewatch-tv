# CineWatch NexVox Engineering Knowledge

**Dataset ID:** `CWTV-NEXVOX-ENGINEERING-001`
**Status:** `CANDIDATE`

This directory contains the governed engineering-knowledge projection used to teach NexVox how CineWatch TV was designed, implemented, tested, corrected, qualified, and evolved.

It is separate from future CineWatch user, search, recommendation, analytics, and behavioral AI datasets.

## Authority model

- Git is the canonical commit and file-history authority.
- `docs/progress/activity/engineering-events.jsonl` is the canonical engineering-activity ledger.
- approved blueprints, architecture authorities, ADRs, governance documents, source code, tests, and scripts retain their own domain authority.
- generated Chronicle, dashboard, OpenAPI/type projections, and NexVox outputs are indexed as provenance but deduplicated from training text where appropriate.
- inspection does not imply training permission.

## Build

```bash
python scripts/build_nexvox_engineering_corpus.py --source-commit HEAD
```

## Check

```bash
python scripts/check_nexvox_engineering_corpus.py
```

## Local-only PDF

```bash
python scripts/build_nexvox_engineering_pdf.py
```

The PDF is a human-preservation projection, must remain outside Git, and is regenerated after every ordinary non-projection source commit once the corpus is rebuilt for that exact source commit.

## Projection commit rule

A normal engineering commit is followed by one NexVox projection commit containing trailers:

```text
NexVox-Source-Commit: <40-char SHA>
NexVox-Projection: true
```

Projection commits do not recursively trigger another NexVox projection.
