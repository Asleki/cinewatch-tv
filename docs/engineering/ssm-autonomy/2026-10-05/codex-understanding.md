# Codex Understanding — CineWatch SSM autonomy

Recorded at: 2026-10-05T10:44:48Z / 12:44:48 CAT. Record type: Codex technical synthesis. Training eligibility: TRAINING_REVIEW_REQUIRED. This is interpretation linked to evidence, not a lesson, model response dataset or verified deployment event.

## Authority and current understanding

Git governs CineWatch source/file history. The canonical engineering activity ledger is docs/progress/activity/engineering-events.jsonl; Chronicle Markdown and dashboard JSON are generated projections. CineWatch's nexvox/engineering corpus is an application-local engineering projection, not a production runtime dependency. The private nexvox-praxis-corpus receives separately qualified, timestamped engineering snapshots/batches. NexVox AI performs any later approved training transformation. These authorities remain separate.

The prior read-only audit correctly described an earlier host without an instance profile or managed SSM registration. Newer owner-maintained Investigation/Findings/Handoff evidence reports deliberate attachment of cinewatch-ssm-instance-role, amazon-ssm-agent 3.3.4793.0 running, managed-node status Online and successful console Run Command 4aed2bdc-e5cf-4c96-b690-a5fec1fc28c7. These newer reports supersede the earlier absent-SSM state as human-provided operational evidence. This session has not independently reverified those facts against AWS because the connector did not execute API calls.

The current console-reported host is CineWatch instance i-00547a7236a653a6b in eu-north-1, hostname ip-172-31-19-213, auto-assigned public IPv4 13.61.187.17, deployed SHA 304bc33e30130229f4be401528ddfda744815b57 and Next.js BUILD_ID PbPahqCFKtoWdGjsja0IP. The newer phone evidence reports SSH restricted to 217.74.224.187/32, not the earlier 217.74.224.165/32. Reserved EIP 13.50.147.240 / eipalloc-04a58b382c29a5733 remains reported unassociated. Conflicting older IDs/IPs are history, not current authority. These values require fresh AWS/host attestation before deployment.

## Console failure and correction lineage

The Findings Register reports that an initial SSM script reached the host but Git emitted dubious-ownership errors because the repository is owned by ubuntu while Run Command executes as root. A later successful command masked that earlier error in a non-fail-fast script. A second command, 63144374-4dea-4b4a-9525-f1a5175a4204, failed. Its unsupported pipefail under the default shell is a documented working diagnosis, not a verified root cause: stderr was not available in the source evidence. The corrected successful console proof is 4aed2bdc-e5cf-4c96-b690-a5fec1fc28c7. Do not convert console overall Success into proof that every earlier subcommand succeeded.

Run repository commands as sudo -u ubuntu -H, use the exact authorized POSIX-safe set -eu body, and do not add a global root safe.directory exception. Preserve the failed attempts and correction relationships. The supplied Findings Register reuses some finding identifiers; disambiguate by document identity and section/order, not by claiming those reused IDs are unique event keys. No retroactive historical ledger events are manufactured.

## This session's observed blocker

Two AWS connector calls returned the identical instruction that authentication had been requested and accepted and that the tool should be retried. Neither returned api_calls, AWS identity, managed-node data or command output. The owner also stated they had reconnected AWS. The repeated prompt is a connector authentication loop, not an observed IAM denial, SSM delivery failure or host outage. No SendCommand was issued and no new Command ID exists. Retries stopped rather than repeatedly requesting reconnection or changing permissions.

Current caller/account cannot be independently reconfirmed from this session. Earlier authenticated account 043826525255 / alex-admin remains historical evidence. This session has no configured CLI/provider identity selector, AWS CLI or boto3 fallback; do not substitute unrelated credentials or ask for secret keys.

## Bounded deployment understanding

The expected future command path is Codex connected AWS identity → SSM → CineWatch EC2. Termux/SSH remains reported recovery/admin access. That becomes a qualified normal Cloud path only after Codex independently submits and retrieves the authorized read-only probe successfully. A successful console command is not that independent proof.

The public target remains https://www.cinewatchtv.com/. Reported existing Nginx/Next.js/FastAPI topology and server-only configuration should be preserved. No DNS, TLS or Nginx redesign is indicated. No new database architecture audit or database credential request is authorized. NexiLabs/NPP resources remain separate from CineWatch.

Corrected 002 remains an immutable 53-file source delivery, SHA-256 cc4b039543e05aa49545a89af0cd7806d5f9f4980440a1039706e9df3c1895fb, requiring historical base 304bc33e30130229f4be401528ddfda744815b57. It has not been applied or deployed in this task. Evidence-only commits may advance GitHub Main; any later 002 application must reconcile the newer documentation/governance-only history with that required base instead of silently overriding the package's base check.

Future release order remains governed source qualification → ordinary source commit → exact-SHA NexVox corpus and local-only PDF → separate projection commit → qualified publication → exact-SHA CI → real Chronicle closure and its own source/projection pair → separately authorized exact-SHA deployment with rollback evidence → provider/live/visual verification → Android acceptance. Passing this read-only probe would not authorize that release.

The current private Praxis layout already separates cinewatch-tv, nexilabs and nexvox-ai; nexvox-ai is the existing equivalent of the requested NexVox source area and remains RESERVED/EMPTY. Preserve that valid layout. Complete Q&A exclusion from Praxis remains the owner's stricter standing instruction, including historical Q&A-derived records. Do not infer training approval from an integrity pass.

## Deliberate non-actions and next action

No 002 application, server source mutation, deployment, service restart/reload, EC2 stop/start/reboot, IAM/security-group/DNS/EIP/Namecheap/database change, secret read or private-key distribution occurred. Current authorized repository work is evidence preservation and governed projection/ingestion only. The next operational action is the exact read-only SSM probe once the connected AWS tool actually executes; no infrastructure changes are required by this authentication-loop observation.

## Independent Codex proof — superseding update

At 2026-10-05T10:59:43.428472Z the authorized reset retry executed STS and region reads successfully: account 043826525255, caller arn:aws:iam::043826525255:user/alex-admin, region eu-north-1. The targeted node read returned Online, agent 3.3.4793.0. Codex submitted the exact authorized read-only body to only i-00547a7236a653a6b as AWS-RunShellScript command cf8d1e3c-46dc-497d-ad06-cd9fc39f9a32 at 2026-10-05T11:00:24.651Z. Retrieved at 2026-10-05T11:00:54.617377Z, overall/invocation status Success, response code 0, one target/completion, zero errors/timeouts and empty stderr.

Actual stdout confirms hostname ip-172-31-19-213, SSM user root, repository owner ubuntu:ubuntu, Git as ubuntu at 304bc33e30130229f4be401528ddfda744815b57, clean detached HEAD, BUILD_ID PbPahqCFKtoWdGjsja0IP and cinewatch-web/cinewatch-api/nginx active. The earlier blocked-before-execution record remains true for its observation time and is superseded by this successful independent proof. The attached raw API evidence preserves actual command output and timestamps.

Verdict: Codex OS command execution through SSM is GREEN. Termux is not required as the normal host-command hop and remains recovery/admin access. This proves read-only command execution and identity/service/build reads, not production build success, rollback readiness, a deployed 002 release or blanket permission for future commands. Git publication transport and live visual acceptance retain their previously documented qualifications. The separately authorized release/deployment gate remains closed.
