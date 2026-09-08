# CineWatch Engineering Event Schema 1.0

Each line in `engineering-events.jsonl` is one complete JSON object.

Required fields:

| Field | Meaning |
|---|---|
| `schema_version` | Event schema version (`1.0`). |
| `event_id` | Stable contiguous ID such as `CWTV-EVT-000043`. |
| `sequence` | Append order. |
| `occurred_at` | Offset-aware ISO-8601 timestamp or `null` when not preserved. |
| `timestamp_precision` | `exact`, `commit-derived`, or `unknown`. |
| `timestamp_source` | Provenance of the timestamp. |
| `milestone` | Milestone that owns the event. |
| `event_type` | Uppercase semantic event type. |
| `component` | Affected engineering component. |
| `result` | `PASS`, `FAILED`, `INFO`, `BLOCKED`, `QUALIFIED`, `PAUSED`, or `RESUMED`. |
| `summary` | Human-readable factual summary. |
| `duration_seconds` | Timed activity duration when measured. |
| `artifact` | Optional artifact name and SHA-256. |
| `commit` | Optional Git commit SHA. |
| `correction` | Optional correction/revision identifier. |
| `evidence` | Zero or more concise evidence strings. |
| `details` | Non-secret structured details. |
| `previous_event_sha256` | Hash of the previous event, or `null` for the first event. |
| `event_sha256` | SHA-256 over the canonical event payload excluding this field. |

## Timing rule

Unknown historic timestamps remain `null`. A Git commit timestamp may be used only for the commit event itself and for a qualification event explicitly anchored to that commit; its precision is `commit-derived`.

## Event naming

The ledger permits new uppercase event types as engineering evolves. Recommended families include:

- `MILESTONE_STARTED`
- `ARTIFACT_GENERATED`
- `ARTIFACT_VERIFIED`
- `ARTIFACT_EXTRACTED`
- `DELIVERY_APPLIED`
- `COMPILE_STARTED` / `COMPILE_PASSED` / `COMPILE_FAILED`
- `TEST_STARTED` / `TEST_PASSED` / `TEST_FAILED`
- `BUILD_STARTED` / `BUILD_PASSED` / `BUILD_FAILED`
- `ROOT_CAUSE_IDENTIFIED`
- `BLOCKER_IDENTIFIED`
- `CORRECTION_GENERATED`
- `CORRECTION_APPLIED`
- `WORK_SESSION_STARTED`
- `WORK_PAUSED`
- `WORK_RESUMED`
- `WORK_SESSION_ENDED`
- `FILES_STAGED`
- `COMMIT_CREATED`
- `PUSH_COMPLETED`
- `MILESTONE_QUALIFIED`

## Secret rule

Do not record credentials, access tokens, passwords, Authorization headers, database URLs, private keys, cookies, or cloud secrets. Evidence must be redacted before it enters the ledger.
