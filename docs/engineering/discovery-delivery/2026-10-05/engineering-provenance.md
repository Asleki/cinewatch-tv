# CineWatch governed multi-system engineering provenance

This is normalized engineering evidence, not a private conversation transcript or a training lesson. The owner explicitly specified the current workflow: ChatGPT Chat → Codex → GitHub/CineWatch → Google Drive evidence. AWS/SSM is separately authorized production-command transport.

ChatGPT Chat supplies planning, architecture, authorization, review and acceptance/rejection decisions. Codex performs inspection, implementation, qualification, packaging and authorized execution. GitHub is canonical source authority; Google Drive is durable artifact/evidence authority. Git identities and provider/API observations must remain distinct from chat-reported history. Tool execution does not itself expand authorization.

Original message timestamps are unavailable here and remain unknown. The JSON companion records the exact normalization time, source/tool identities, authorization scope and evidence references. Git commit times and preserved command/CI times retain their original provenance. Full transcripts, credentials and unrelated personal material are excluded. New interpreted delivery documents remain TRAINING_REVIEW_REQUIRED. Existing upstream eligibility is preserved; central ingestion does not silently promote it.

## D003 → D004 failure and correction

D003 payload hashes passed, but apply_003.py blanket-set replacement files to mode 0644. Two tracked executables lost Git mode 100755: scripts/check_catalog_experience.py and scripts/check_refinement_regression.py. The resulting complete Git tree was 24b56a85c7a84751b558441c39b8b5c3bb97a445, not the qualified 274e466bd2fd48ba9bc10cd52d66201f66af78c5. The mandatory tree gate caught this defect and promotion stopped. Earlier content-only qualification had missed the mode difference; that verification gap is preserved.

D004 preserved all 53 D003 payload bytes and introduced required per-path git_mode/git_blob metadata, strict rejection of missing or unsupported modes, executable-mode mapping and full Git-tree preflight/post-application regression. Two independently applied clean checkouts reproduced 274e466bd2fd48ba9bc10cd52d66201f66af78c5; a fresh promotion-stage checkout reproduced it again. Existing D003 source and projection identities were reused, not rewritten.

The original stopped D003 attempt also recorded a local qualification process inadvertently starting after assertion failure because its shell sequence lacked fail-fast; it was stopped and never claimed complete. A D004 Drive readback verifier initially omitted the archive payload/ prefix, then passed after correcting that external verifier. Neither event mutated the immutable payload or predecessor ZIP.

The complete artifact lineage and actual CI/results are in delivery-closure-evidence.json and the accompanying receipts. Final closure CI is saved externally, rather than recursively adding another Chronicle/source/projection pair. No production deployment, AWS/SSM operation or live/browser/device acceptance occurs in this authorization.
