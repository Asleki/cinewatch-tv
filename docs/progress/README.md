# CineWatch TV Engineering Chronicle & Progress Dashboard

**Milestone:** `CWTV.V1.2.5.1`
**Status at bootstrap:** in progress
**Source of truth:** `docs/progress/activity/engineering-events.jsonl`

This foundation records CineWatch engineering work as an append-only event ledger and derives two human-readable projections:

- `docs/progress/CineWatch_TV_Engineering_Chronicle.md`
- `docs/progress/dashboard/progress-data.json`

The HTML dashboard reads `progress-data.json`; neither generated projection is an independent authority.

## Integrity model

Each JSONL event has:

- a contiguous `CWTV-EVT-######` identity;
- an append sequence;
- offset-aware event time when the time is known;
- `timestamp_precision` of `exact`, `commit-derived`, or `unknown`;
- provenance in `timestamp_source`;
- milestone, component, event type, result and summary;
- optional duration, artifact SHA-256, Git commit, correction reference and evidence;
- `previous_event_sha256` and `event_sha256` fields forming a SHA-256 hash chain.

The hash chain protects against accidental edits to older event lines. It is an integrity aid, not a digital-signature or external notarization system.

## Historical backfill rule

The bootstrap contains only work that actually began through `CWTV.V1.2.5.1`.

It intentionally does **not** pre-populate later V1 milestones.

Historical timing rules are strict:

- exact preserved times remain exact;
- Git commit timestamps are marked `commit-derived`;
- missing event times remain `null` with `timestamp_precision=unknown`;
- time gaps are never interpreted as breaks;
- failures remain in the ledger after correction rather than being rewritten away.

## Recording a single event

```bash
python scripts/record_engineering_activity.py \
  --milestone CWTV.V1.2.5.1 \
  --event-type WORK_SESSION_STARTED \
  --component engineering-chronicle \
  --result INFO \
  --summary "Chronicle qualification session started."
```

The command appends the event and rebuilds the Markdown and JSON projections.

### Pause / resume

```bash
python scripts/record_engineering_activity.py \
  --milestone CWTV.V1.2.5.1 \
  --event-type WORK_PAUSED \
  --component engineering-chronicle \
  --result PAUSED \
  --summary "Work paused for a break."
```

```bash
python scripts/record_engineering_activity.py \
  --milestone CWTV.V1.2.5.1 \
  --event-type WORK_RESUMED \
  --component engineering-chronicle \
  --result RESUMED \
  --summary "Work resumed."
```

A timestamp gap without these events is never counted as a break.

## Running and timing a command

Use `run_and_record.py` when an activity should record exact start/end times, exit status and runtime automatically:

```bash
python scripts/run_and_record.py \
  --milestone CWTV.V1.2.5.1 \
  --activity STATIC_QUALIFICATION \
  --component engineering-chronicle \
  --summary "Chronicle static qualification" \
  -- python scripts/check_engineering_chronicle.py
```

It records and synchronizes in this order:

1. `STATIC_QUALIFICATION_STARTED`;
2. immediately rebuilds the Markdown/JSON projections so the new ledger head is visible to the wrapped command;
3. runs the command and preserves its output unchanged;
4. records `STATIC_QUALIFICATION_PASSED` or `STATIC_QUALIFICATION_FAILED`;
5. records exact duration and exit code;
6. rebuilds the progress projections again from the final ledger head.

The pre-command rebuild is required because Chronicle qualification commands themselves check that generated projections match the append-only ledger. Without it, the wrapper's own `*_STARTED` event would make those projections stale before the wrapped checker begins.

## Rebuilding projections

```bash
python scripts/build_progress_dashboard.py
```

Check for projection drift without modifying files:

```bash
python scripts/build_progress_dashboard.py --check
```

## Static qualification

```bash
python scripts/check_engineering_chronicle.py
```

## Dashboard runtime smoke

```bash
bash scripts/check_progress_dashboard_runtime.sh
```

## Viewing the dashboard locally

Serve the dashboard over HTTP because browsers commonly block JSON `fetch()` from `file://` pages:

```bash
python -m http.server 8090 -d docs/progress/dashboard
```

Then open:

```text
http://127.0.0.1:8090/
```

The page is GitHub-Pages-ready but this milestone does not enable or deploy GitHub Pages.

## Difficulty graph

Observed difficulty is derived from recorded evidence. The initial score uses:

- failed events;
- blockers;
- distinct corrections;
- repeated timed successful cycles.

The graph is deliberately labeled **observed difficulty** rather than quality or success. Historic scores can be incomplete because historic event detail was not always timestamped or recorded before this foundation existed.

## Timing metrics

The dashboard distinguishes:

- elapsed time, only when exact milestone start and qualification times exist;
- recorded command runtime from timed wrapper events;
- active session time from explicit session start/resume/pause/end events;
- paused time from explicit pause → resume intervals;
- unknown time when evidence was not preserved.

## Secret exclusion

Never write any of the following into the chronicle:

- passwords;
- tokens;
- Authorization headers;
- database connection URLs;
- AWS/Azure credentials;
- private keys;
- cookies or session secrets.

The chronicle stores evidence summaries, hashes and non-secret identifiers only.

## Responsive visual qualification contract

The dashboard must remain fully usable without page-level horizontal scrolling on mobile, tablet, or desktop viewports. Long artifact names, SHA-256 values, event types, summaries, commit metadata, and failure details must wrap within their owning card or panel.

The responsive projection uses:

- a colored but accessible dark engineering palette;
- distinct semantic accents for progress, qualification, failures, corrections and evidence;
- a responsive difficulty chart that sizes to its container instead of imposing a fixed minimum width;
- a desktop failure table that wraps safely and a mobile card-style representation with no horizontal table scroll;
- responsive timeline, artifact and commit layouts;
- progressive card/reveal and progress-bar animation;
- `prefers-reduced-motion` support so animation is never mandatory;
- no external fonts, CDN assets or web dependencies.

Visual styling remains a projection concern only. It does not modify the append-only engineering ledger or change milestone facts.
