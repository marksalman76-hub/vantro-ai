# Production Completion Master Plan

Date: 2026-06-17

Scope: owner-facing production completion plan plus AWS-20 SQS-focused live rehearsal proof. This document does not approve public launch, AWS cutover, provider calls, media generation, worker loops, Stripe calls, billing or credit mutations, customer traffic, or AWS-21+ work.

## 1. Executive Owner Summary

Current launch recommendation: no full paid public launch. The platform should remain internal-only until AWS-20 live infrastructure proof is closed, then move to a controlled private paid pilot only after durable job lifecycle, billing/credit governance, status UX, support recovery, and observability proof exist.

Current AWS migration readiness: 93%.

Current full SaaS production readiness: 74%.

Biggest blocker: AWS-20 live infrastructure proof is still not formally closed. SQS-focused live send and S3-focused marker write/read/delete have passed, but final consolidated RDS/SQS/S3 proof is not recorded.

Biggest cost/control risk: paid provider execution and long-form media jobs still require live proof that credits, package approval, provider-cost caps, retries, and failure recovery stay synchronized across real job execution.

Biggest customer-trust risk: a customer could see unclear status, delayed results, failed media, or missing downloadable assets if the durable job, worker, asset, and portal status loops are not proven end to end.

Biggest operational/support risk: support and incident handling are currently backed by strong boundaries and diagnostics, but live recovery from a failed durable job, SQS/DLQ event, billing mismatch, or asset failure has not been rehearsed.

One-sentence truth statement: the platform has serious safety architecture, but it is not public paid-launch ready until live infrastructure, durable worker execution, billing reconciliation, and support recovery are proven with synthetic and controlled pilot evidence.

## 2. Current Proven Foundation

| Area | Evidence | What is proven | Limits |
| --- | --- | --- | --- |
| Production finish audit | Commit `3cbc50f Add production finish audit and gap plan`; `PRODUCTION_FINISH_AUDIT_AND_GAP_PLAN.md` | Owner-facing gap plan exists and launch recommendation is conservative. | The audit is planning proof, not live execution proof. |
| AWS-20 safe-default rehearsal boundary | Commit `75d7895 Add AWS live rehearsal boundary`; `backend/app/runtime/aws_option_a_live_rehearsal.py`; `verify_aws_option_a_live_rehearsal.py` | Rehearsal is disabled by default, requires owner approval and per-resource flags, uses synthetic non-customer markers, and avoids providers, Stripe, billing, credits, workers, and cutover. | Full live RDS/SQS/S3 success is not proven. |
| AWS-20 SQS-focused live rehearsal | Sanitized AWS-20 SQS proof recorded from the owner-approved 2026-06-17 SQS-focused run. | `sqs_attempted=true`, `sqs_send_attempted=true`, `sqs_passed=true`, `sqs_message_non_customer=true`, `sqs_message_non_executable=true`, and `sqs_message_id_hash_prefix=5e86bff755a4`. No provider calls, media workers, Stripe calls, billing mutations, credit mutations, customer traffic, or public cutover occurred. | Proves SQS send only; does not prove S3, worker consumption, DLQ handling, final asset delivery, or the full media lifecycle. |
| AWS-20 S3-focused live rehearsal | Sanitized AWS-20 S3 proof recorded from the owner-approved 2026-06-17 S3-focused run. | `s3_upload_attempted=true`, `read_back_passed=true`, `s3_delete_attempted=true`, `cleanup_performed=true`, `object_key_hash=9d04e4154bf1`, and `bucket_reference.sha256_12=88eb3f25047d`. No RDS write, SQS send, provider calls, media workers, Stripe calls, billing mutations, credit mutations, customer traffic, or public cutover occurred. | Proves tiny synthetic S3 marker write/read/delete only; does not prove final asset lifecycle, signed delivery, worker output persistence, customer assets, or full RDS/SQS/S3 AWS-20 closure. |
| AWS route gates | `backend/app/runtime/aws_option_a_route_integration.py`; `verify_aws_option_a_route_cutover_boundary.py`; `verify_aws_option_a_route_integration.py` | AWS route behavior stays behind explicit route, validation, and operation flags; default path remains compatibility runtime. | Live durable route cutover is not enabled or proven. |
| Dry-run durable enqueue | Commit `45c61bf Add AWS durable enqueue dry-run boundary`; `verify_aws_option_a_durable_enqueue_dry_run.py` | Durable repository and queue packets are prepared in dry-run mode without RDS write or SQS send. | Live write/send remains unproven. |
| Rollback controls | Commit `8eb71c9 Add AWS rollback control boundary`; `backend/app/runtime/aws_option_a_rollback_controls.py`; `verify_aws_option_a_rollback_controls.py` | Kill switch and forced compatibility fallback can block route execution and report sanitized admin/client states. | Live incident rollback drill is not proven. |
| Observability diagnostics | Commit `0b943fb Add AWS observability diagnostics boundary`; `backend/app/runtime/aws_option_a_observability.py`; `verify_aws_option_a_observability.py` | Redacted diagnostic bundle and incident event shapes exist without CloudWatch/external logging side effects. | Live CloudWatch/alerting/dashboard proof is not present. |
| AWS migration matrix through AWS-20 | `AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md` | AWS-01 through AWS-20 boundaries are documented without AWS-21+ expansion. | Matrix does not prove live resource success. |
| Frontend build baseline | Production audit records `cd frontend && npm.cmd run build` passed. | Current frontend compiles. | Build success does not prove live user workflow quality. |
| Media cost and preflight guardrails | `backend/app/runtime/direct_media_provider_execution_runtime.py`; `verify_media_provider_preflight_safety.py`; `verify_duration_aware_media_segments.py`; `verify_complete_media_portal_renderer.py` | Complete media has preflight, duration-aware segments, credit-risk confirmation, and safer portal rendering. | Live provider reliability and final asset delivery under production conditions remain unproven. |
| Final 27-agent catalogue | Commit `2e1ea9f Lock final 27 agent catalogue visibility`; `verify_final_27_agent_catalogue_visibility.py` | Client-visible catalogue count is 27 and system agents are internal layers. | Agent quality across all workflows still needs sampled production QA. |

## 3. Current Unproven Areas

- Full AWS live RDS/SQS/S3 proof: RDS rollback path progressed, SQS-focused live send passed, S3-focused marker write/read/delete passed with cleanup, and consolidated AWS-20 proof is not yet recorded.
- Durable worker lifecycle: worker claim, idempotency, retries, terminal status, and DLQ handling are not live-proven.
- S3 final asset lifecycle: upload, signed/open/download path, retention, cleanup, and client/admin views are not proven live.
- Live provider orchestration under cost caps: Runway/ElevenLabs and fallbacks have guardrails, but provider execution under durable job, cost cap, credit, and status governance is not fully proven.
- Client popup job status/result UX under real jobs: the portal renderer is structurally improved, but async live status and final asset behavior need evidence.
- Billing/credit reconciliation under execution: entitlement and ledger boundaries exist, but Stripe, credit reservation, finalization, reversal, refunds, and provider actual cost reconciliation need proof.
- Support recovery and DLQ handling: admin diagnostics exist, but operator recovery from stuck, failed, or DLQ jobs is not rehearsed.
- Load/scale readiness: queue backpressure, concurrent job acceptance, status polling, and provider throttling behavior are not measured.
- Security/privacy/likeness handling proof: secret redaction exists, but tenant isolation, avatar/likeness consent, retention, and deletion workflows need audit evidence.
- Production deployment and rollback drill: local/verifier safety exists, but release rollback across frontend, backend, worker, AWS flags, and provider flags is not rehearsed.

## 4. Launch Gates

| Gate | Objective | Why it matters | Required work | Files likely touched | Commands/verifiers | Live spend involved? | Owner approval required? | Exact done criteria | Stop condition | Expected commit message |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gate 0: Repo clean and audit baseline | Keep a trustworthy baseline before live proof. | Prevents accidental launch changes while investigating infrastructure. | Confirm clean status, audit exists, matrix stays through AWS-20. | Docs only if baseline notes change. | `git status --short`; `git diff --check`; safe build/compile as needed. | No | No | Clean worktree except intentional docs/code changes; no AWS-21+ rows. | Dirty unrelated files or matrix expansion. | `Record production baseline evidence` |
| Gate 1: AWS live infrastructure proof | Prove bounded RDS, SQS, and S3 rehearsal resources. | AWS cutover cannot proceed until the foundation actually works. | SQS-focused rehearsal and S3-focused marker write/read/delete have passed. Remaining work: confirm and record RDS rollback evidence, then record final RDS/SQS/S3 proof. | `aws_option_a_live_rehearsal.py`; `verify_aws_option_a_live_rehearsal.py`; proof docs. | AWS-20 verifier, route/rollback/observability regressions. | Low AWS test-resource usage | Yes for live runs; no for docs-only recording | RDS rollback, SQS non-customer non-executable send, S3 marker write/read/delete all pass with sanitized output and consolidated proof is recorded. | Any secret exposure, customer data, executable queue message, failed cleanup, or broad AWS call. | `Record AWS live rehearsal proof` |
| Gate 2: Durable job lifecycle proof | Prove accepted jobs persist, queue, process, retry, and finish safely. | Paid workflows need durable state and recoverable status. | Wire or prove guarded live repository/queue path and worker lifecycle with synthetic jobs. | Route integration, repository, queue, worker, status adapters, verifiers. | Durable enqueue verifier; worker lifecycle verifier; status adapter verifier. | Possible AWS SQS/RDS test usage | Yes | Synthetic job accepted, persisted, queued, claimed once, status-updated, retried/failed/completed with no providers. | Duplicate processing, missing terminal state, unsafe retry, or unredacted diagnostics. | `Prove durable worker lifecycle` |
| Gate 3: Admin/client UX proof | Prove users and operators see useful status and recovery actions. | Trust fails when jobs are technically running but UX is confusing. | QA queued/running/failed/retry/completed/final asset states. | Admin/client portal components, status routes, support routes, verifiers. | Frontend build; portal renderer verifier; route fixtures; screenshot QA if available. | No, unless using live AWS/provider fixtures | Sometimes | Client-safe views hide internals; admin sees actionable diagnostics; final outputs open/download. | Raw packet/secrets in client view, stale status, or unclear failure messaging. | `Close launch status and support UX proof` |
| Gate 4: Billing/credits/spend governance proof | Prove paid work cannot escape package, credit, and approval controls. | This protects customer fairness and owner cost. | Stripe test-mode flow, credit reserve/finalize/reverse, provider cost estimate/actual audit, admin overrides. | Billing, credit, entitlement, Stripe runtimes and verifiers. | Billing ledger verifier; entitlement verifier; Stripe webhook tests; backend compile. | Stripe test/live depending mode | Yes for live or charge-affecting work | Provider execution blocked without entitlement/credit or explicit audited owner override. | Charge without entitlement, credit mismatch, un-audited override, or secret leak. | `Prove billing credit spend governance` |
| Gate 5: Observability/support/rollback proof | Prove incidents are detected, diagnosed, and reversible. | Paid SaaS needs operations, not just code. | Redacted logs/metrics/alerts, runbooks, rollback drill, support recovery fixtures. | Observability, admin diagnostics, runbook docs, support routes. | Observability verifier; rollback verifier; incident drill; optional CloudWatch test. | Possible AWS logging usage | Yes for live AWS logging | Owner can identify stuck/failed jobs, rollback, and recover without secret exposure. | No alert path, no runbook, rollback cannot stop execution, or secrets in logs. | `Wire launch observability evidence` |
| Gate 6: Controlled private paid pilot | Validate a narrow paid workflow with known users and cost caps. | Real customers reveal workflow gaps, but blast radius must be tiny. | Pilot package, spend cap, support rota, refund path, daily review. | Pilot docs, billing config, provider caps, support docs. | Full gate verifier set; pilot checklist; manual owner signoff. | Yes, bounded | Yes | Several controlled paid workflows complete or recover cleanly with reconciled billing and assets. | Any uncontrolled spend, unresolved customer failure, or billing inconsistency. | `Add private paid pilot launch runbook` |
| Gate 7: Full paid public launch | Open beyond private pilot only after operational proof. | Public launch magnifies every unproven edge case. | Final launch checklist, load/security proof, backup/restore, support staffing. | Launch docs, deployment configs, runbooks, tests. | Full regression, load smoke, security/privacy audit, backup/restore drill. | Yes | Yes | Owner signs full launch after all P0/P1 launch blockers are closed. | Any unresolved P0, missing rollback, missing billing reconciliation, or unreliable media flow. | `Approve full paid public launch readiness` |

## 5. Prioritized Production Backlog

| Rank | Priority | Work item | Domain | Why it matters | Current evidence | Required implementation | Required verification | Owner approval needed? | Can be done without live spend? | Readiness gain if completed | Dependencies |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | P0 | Record S3 live rehearsal proof | AWS/docs | S3 marker write/read/delete is now proven and the production plan must show the current AWS-20 blocker accurately. | Sanitized proof: `s3_upload_attempted=true`, `read_back_passed=true`, `s3_delete_attempted=true`, `cleanup_performed=true`, hash-only bucket/object references. | Record proof in production docs without exposing raw bucket, object key, account ID, credentials, or infrastructure identifiers. | `git diff --check`; `git status --short`; docs-only commit. | No | Yes | +2% AWS | SQS proof recorded |
| 2 | P0 | Final RDS/SQS/S3 AWS-20 proof record | AWS | Closes infrastructure rehearsal evidence. | RDS rollback path progressed, SQS live send passed, S3 live marker write/read/delete passed with cleanup. | Confirm/record RDS rollback evidence, include SQS and S3 proof, and explicitly state AWS-20 status. | Docs plus all AWS-20 regressions. | Yes for any new live proof, no for docs | Partly | +2% AWS, +2% SaaS | Item 1 |
| 3 | P0 | Maintain SQS and S3 rehearsal diagnostics coverage | AWS | Diagnostics are no longer the primary blocker, but they should remain available for regressions. | AWS-20 SQS diagnostics, SQS-only mode, and S3 sanitized output exist. | Keep source/verifier coverage for sanitized failure categories and redacted resource references. | AWS-20 safe-default verifier and source-level checks. | No | Yes | +0% current readiness | Items 1-2 |
| 4 | P0 | Prepare durable queue/storage cutover proof plan | AWS/backend | Infrastructure resources have individual proof, but durable route cutover remains disabled. | Route gates and dry-run durable enqueue exist. | Plan the next owner-approved synthetic durable write/send/status proof without providers or workers. | Route integration and durable enqueue verifier. | Yes for live AWS | Partly | +2% SaaS | Item 2 |
| 5 | P0 | Durable worker lifecycle proof | Backend/jobs | Paid work needs reliable async execution. | Dry-run durable enqueue exists. | Synthetic worker claim, retry, terminal status, idempotency. | Worker lifecycle verifier and status verifier. | Yes if AWS-backed | Partly | +5% SaaS | Gate 1 |
| 6 | P0 | SQS DLQ/failed job recovery proof | Backend/ops | Failed jobs must be recoverable and supportable. | Queue/DLQ boundaries exist. | DLQ fixture, failed-job status, admin recovery path. | DLQ/failure verifier. | Yes if live AWS | Partly | +3% ops | Item 5 |
| 7 | P0 | Media job status/result visibility inside Create Media popup | Frontend/media | Customers and admins need accurate job state. | Portal renderer guard exists. | Live/durable status mapping for queued, running, failed, retry, complete. | Frontend build, renderer verifier, route fixture tests. | No for fixtures | Yes | +3% client UX | Item 5 |
| 8 | P0 | Final asset storage/retrieval/open/download proof | Assets/media | A paid deliverable must be accessible. | S3/local asset boundaries exist. | Synthetic and media output asset delivery proof. | Asset delivery verifier, portal open/download fixture. | Yes for live S3 | Partly | +4% SaaS | Items 3, 5 |
| 9 | P0 | Client-safe status/errors | Client UX/security | Clients must not see internals or secrets. | Client-safe views exist in several boundaries. | End-to-end client error/status filtering. | Client route snapshots and redaction verifier. | No | Yes | +2% client UX | Items 7-8 |
| 10 | P0 | Admin full diagnostics/support view | Admin ops | Owner needs recovery detail without secrets. | Admin diagnostics exist in AWS/media paths. | Consolidate job, provider, queue, billing, asset, support evidence. | Admin fixture verifier. | No | Yes | +3% admin ops | Items 5-8 |
| 11 | P0 | Package/credit/approval enforcement under execution | Billing/spend | Paid provider work must be authorized. | Entitlement/credit boundaries exist. | Reserve, confirm, finalize, reverse credits around execution. | Billing/credit execution verifier. | Yes for live | Partly | +5% billing | Items 5, 7 |
| 12 | P0 | Stripe/billing reconciliation proof | Billing | Revenue state must match platform access. | Stripe routes and readiness exist. | Test-mode checkout, webhook, refund, subscription state reconciliation. | Stripe test verifier and ledger proof. | Yes for Stripe mode | Test mode may spend no money | +5% billing | Item 11 |
| 13 | P0 | Provider execution cost cap and owner approval proof | Media/spend | Prevents credit burn on failed or long jobs. | Preflight/high-risk confirmation exists. | Tie provider attempts to credit/cost cap and durable job evidence. | Media preflight, duration, provider attempt verifier, pilot smoke. | Yes for live providers | Fixtures yes | +4% media | Items 5, 11 |
| 14 | P1 | Media output quality proof under broad use cases | Media quality | Commercial output must be client-ready. | Media script quality verifier exists. | Sample multiple industries, durations, platforms, avatar/no-avatar modes. | Fixture QA and owner review set. | No unless live generation | Yes | +3% media | Item 13 |
| 15 | P1 | Human/avatar likeness consent and quality proof | Privacy/media | Likeness misuse is high trust/legal risk. | Human/avatar modes exist. | Consent record, asset linkage, client-safe messaging, no-human compliance. | Consent/privacy verifier and media fixtures. | Yes for policy | Yes | +3% security | Items 7, 14 |
| 16 | P1 | Observability/logging/runbook proof | Ops | Incidents need detection and response. | AWS-19 diagnostics exist. | Redacted logs, alerts, dashboards, incident runbooks. | Observability verifier plus incident drill. | Yes for live AWS logging | Partly | +4% ops | Items 5-6 |
| 17 | P1 | Load/scale smoke proof | Scale | Avoid first-pilot queue/status overload. | No load evidence. | Synthetic concurrent acceptance/status/queue test. | Load report with p95/p99 and no provider spend. | Yes if AWS resources used | Partly | +3% SaaS | Items 5, 16 |
| 18 | P1 | Security/privacy audit proof | Security | Tenant/privacy errors can kill trust. | Redaction helpers and client/admin separation exist. | Tenant isolation, secret redaction, session, retention, deletion checks. | Security/privacy verifier and dependency scan. | Yes for policy | Yes | +4% SaaS | Items 9, 15 |
| 19 | P1 | Private paid pilot plan | Launch | Pilot needs explicit caps and support. | Audit recommends limited private pilot only. | Pilot runbook, spend caps, rollback/refund/support process. | Owner-approved checklist. | Yes | Yes until pilot starts | +2% launch | Items 1-18 P0 |
| 20 | P1 | Full launch checklist | Launch | Full public launch needs gate discipline. | Production audit and this plan. | Final checklist with P0/P1 proof links and owner signoff. | Full launch review. | Yes | Yes | +2% launch | Private pilot success |

## 6. The Next 10 Codex Tasks

1. Task name: Record AWS-20 S3 live rehearsal proof.
   Goal: update the owner-facing production plan to reflect that S3-focused marker write/read/delete passed with sanitized proof and cleanup.
   Why now: S3 is no longer the current AWS-20 blocker, and the launch plan must not keep stale unproven-S3 wording.
   Files to inspect: `aws_option_a_live_rehearsal.py`, `verify_aws_option_a_live_rehearsal.py`, AWS matrix, production audit.
   Files likely changed: `PRODUCTION_COMPLETION_MASTER_PLAN.md`.
   Commands/verifiers: `git diff --check`, `git status --short`.
   Live spend: none.
   Owner approval needed: no for docs-only proof recording.
   Expected commit message: `Record AWS S3 rehearsal proof`.
   Done criteria: plan records S3 proof, AWS readiness is 93%, full SaaS readiness remains 74%, and no runtime files change.
   Do not do list: no AWS tests, providers, workers, media, Stripe, billing, credits, cutover, AWS-21.

2. Task name: Record final AWS-20 RDS/SQS/S3 proof.
   Goal: close AWS-20 live rehearsal evidence without creating AWS-21.
   Why now: AWS migration cannot advance responsibly without final infrastructure proof.
   Files to inspect: production audit, AWS matrix, AWS-20 verifier output.
   Files likely changed: `PRODUCTION_FINISH_AUDIT_AND_GAP_PLAN.md`, `AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md`.
   Commands/verifiers: AWS-20 verifier, route integration, durable enqueue dry-run, rollback, observability, diff/status.
   Live spend: no extra if recording proof only.
   Owner approval needed: yes for proof source, no for docs.
   Expected commit message: `Record AWS live rehearsal proof`.
   Done criteria: docs state only proven live actions and readiness changes conservatively.
   Do not do list: no AWS-21 row or cutover.

3. Task name: Prove durable worker lifecycle with synthetic jobs.
   Goal: show job persist, queue, claim, retry, fail/complete, and status polling.
   Why now: infrastructure proof alone does not fulfill customer work.
   Files to inspect: worker runtime, queue adapter, route integration, status adapter.
   Files likely changed: worker verifier and minimal worker/status code if gaps are found.
   Commands/verifiers: worker lifecycle verifier, durable enqueue verifier, status adapter verifier.
   Live spend: possible AWS test queue/RDS usage.
   Owner approval needed: yes for live AWS-backed test.
   Expected commit message: `Prove durable worker lifecycle`.
   Done criteria: no duplicate processing, terminal states durable, failure path supportable.
   Do not do list: no paid providers.

4. Task name: Close asset delivery proof.
   Goal: prove generated/final assets can be stored, retrieved, opened, and downloaded safely.
   Why now: paid customers need tangible deliverables.
   Files to inspect: S3 boundary, durable asset store, media asset routes, portal UI.
   Files likely changed: asset delivery runtime/routes/verifier.
   Commands/verifiers: asset delivery verifier, frontend build, route fixtures.
   Live spend: possible low AWS S3 usage.
   Owner approval needed: yes for live S3.
   Expected commit message: `Prove durable asset delivery`.
   Done criteria: client-safe URL/view works, admin sees recovery metadata, no raw local paths/secrets.
   Do not do list: no real customer assets.

5. Task name: Prove billing credit spend governance.
   Goal: enforce package, credit, approval, and provider-cost audit around execution.
   Why now: paid launch without spend governance is unsafe.
   Files to inspect: billing ledger, entitlement boundary, Stripe routes, media preflight.
   Files likely changed: billing/credit runtime and verifier.
   Commands/verifiers: billing ledger verifier, entitlement verifier, Stripe test verifier.
   Live spend: Stripe test or live depending approval.
   Owner approval needed: yes for live mode.
   Expected commit message: `Prove billing credit spend governance`.
   Done criteria: reserve/finalize/reverse/refund paths reconcile and block unauthorized execution.
   Do not do list: no unapproved Stripe live charges.

6. Task name: Prove Complete Media UX under durable status.
   Goal: make client/admin media status, diagnostics, retry, preview, and download reliable.
   Why now: the popup is core to paid media value.
   Files to inspect: `UniversalCompleteMediaRunAgentPanel.tsx`, media status routes, direct media runtime.
   Files likely changed: frontend component, route mapping, renderer verifier.
   Commands/verifiers: frontend build, portal renderer verifier, media preflight/script/duration verifiers.
   Live spend: no for fixtures; yes for provider smoke.
   Owner approval needed: only for live provider smoke.
   Expected commit message: `Close complete media status UX proof`.
   Done criteria: friendly status rows, client-safe errors, admin diagnostics, final playable asset path.
   Do not do list: no broad redesign or unapproved provider calls.

7. Task name: Prove observability, support, and rollback operations.
   Goal: ensure incidents can be detected, explained, and reversed.
   Why now: pilot support will fail without operational proof.
   Files to inspect: observability, rollback, admin diagnostics, support routes, runbooks.
   Files likely changed: runbooks, diagnostics routes, verifiers.
   Commands/verifiers: observability verifier, rollback verifier, support recovery fixtures.
   Live spend: possible AWS logging if enabled.
   Owner approval needed: yes for live AWS logging.
   Expected commit message: `Wire launch observability evidence`.
   Done criteria: incident path is redacted, actionable, and rollback-safe.
   Do not do list: no external logging of secrets.

8. Task name: Prove security, privacy, and likeness consent.
    Goal: prove tenant isolation, secret redaction, retention/deletion, and human/avatar consent handling.
    Why now: private pilot cannot safely expand without privacy and likeness controls.
    Files to inspect: auth/session/tenant helpers, media asset consent handling, client/admin filters, privacy docs.
    Files likely changed: privacy/security verifiers and small policy/runtime fixes if gaps are found.
    Commands/verifiers: tenant isolation tests, redaction tests, dependency/security scan, frontend build.
    Live spend: no.
    Owner approval needed: yes for policy decisions.
    Expected commit message: `Close launch security privacy audit`.
    Done criteria: client views are filtered, tenant boundaries hold, likeness mode requires consent evidence.
    Do not do list: no real customer data or unapproved media generation.

9. Task name: Run load and backpressure smoke proof.
    Goal: prove synthetic job acceptance/status/queue pressure does not break launch-critical paths.
    Why now: private pilot should not be the first time the queue/status path sees concurrent work.
    Files to inspect: route integration, queue/status adapters, frontend polling behavior.
    Files likely changed: load smoke verifier and possibly throttling/backpressure docs.
    Commands/verifiers: synthetic load smoke, route/status verifiers, no-provider worker fixtures.
    Live spend: possible AWS test-resource cost if run against AWS.
    Owner approval needed: yes for live AWS load.
    Expected commit message: `Add launch load smoke proof`.
    Done criteria: p95/p99, error rate, backpressure behavior, and rollback state are recorded.
    Do not do list: no provider calls, no customer traffic, no public cutover.

10. Task name: Prepare controlled private paid pilot runbook.
    Goal: define pilot customers, spend caps, support coverage, refunds, rollback, and stop criteria.
    Why now: private pilot is the next launch state after P0 proof.
    Files to inspect: production audit, master plan, billing/media/support docs.
    Files likely changed: pilot runbook docs.
    Commands/verifiers: full launch gate verifier set, frontend build, backend compile.
    Live spend: no until pilot starts.
    Owner approval needed: yes.
    Expected commit message: `Add private paid pilot launch runbook`.
    Done criteria: owner can run a pilot with clear limits and rollback/refund paths.
    Do not do list: no public launch or open signup expansion.

## 7. Spend And Approval Map

| Action | Risk/spend type | Needs owner approval? | Safe default? | Notes |
| --- | --- | --- | --- | --- |
| Live AWS RDS/SQS/S3 rehearsal | Low AWS infrastructure usage and possible persistent test artifact if cleanup fails | Yes | Off | Synthetic only; no customer data; no cutover. |
| AWS-20 SQS-focused rehearsal | Low AWS SQS request cost | Already approved and passed on 2026-06-17 | Off | Passed with non-customer, non-executable message and sanitized hash-only message ID proof. |
| AWS-20 S3-focused rehearsal | Low AWS S3 request/storage cost | Already approved and passed on 2026-06-17 | Off | Passed with tiny synthetic marker write/read/delete, cleanup performed, and sanitized bucket/object hash proof only. |
| Provider calls | Paid media/API credits | Yes | Off/preflighted | Must require preflight, credit risk, and durable attempt evidence. |
| Media generation | Provider spend and customer-facing output risk | Yes for live providers | Dry-run/preflight | Smoke tests should be capped and explicit. |
| Long videos | High visual provider credit risk | Yes | Confirmation gated | Segment count drives cost; use owner confirmation. |
| Worker loops | AWS/compute/queue side effects and possible duplicate execution | Yes for live | Off until proven | Must be synthetic before customer jobs. |
| Stripe test mode | No real charge but billing-state mutation risk in test data | Yes | Off unless configured | Useful before private pilot. |
| Stripe live mode | Real customer charges/refunds | Yes | Off | Requires reconciliation and support path. |
| Credit mutations | Customer entitlement/spend accounting | Yes | Placeholder/no-mutation today | Must be audited and reversible. |
| Load tests | AWS/compute cost and possible service pressure | Yes if using live resources | Off | Use synthetic no-provider jobs. |
| Public cutover | Production customer impact | Yes | Off | Requires all gates through private pilot. |
| Private paid pilot | Real customer trust, billing, provider spend | Yes | Not active | Requires caps, support, refund, rollback. |

## 8. Readiness Percentage Model

Current percentages, unchanged by creating this plan:

| Area | Current readiness |
| --- | ---: |
| AWS migration readiness | 93% |
| Full SaaS production launch readiness | 74% |
| Media generation production readiness | 72% |
| Durable backend/job readiness | 62% |
| Client UX readiness | 68% |
| Admin ops readiness | 74% |
| Billing/credit readiness | 58% |
| Observability/support readiness | 70% |
| Security/privacy readiness | 66% |

Target percentages after gate closure:

| Gate closed | AWS migration | Full SaaS launch | Media production | Durable backend/jobs | Client UX | Admin ops | Billing/credit | Observability/support | Security/privacy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gate 0 | 93% | 74% | 72% | 62% | 68% | 74% | 58% | 70% | 66% |
| Gate 1 | 95% | 77% | 72% | 65% | 68% | 76% | 58% | 72% | 67% |
| Gate 2 | 96% | 82% | 75% | 78% | 70% | 79% | 60% | 75% | 68% |
| Gate 3 | 96% | 85% | 79% | 80% | 80% | 83% | 61% | 77% | 70% |
| Gate 4 | 96% | 89% | 82% | 82% | 82% | 85% | 78% | 79% | 72% |
| Gate 5 | 97% | 92% | 84% | 84% | 84% | 90% | 80% | 88% | 78% |
| Gate 6 | 98% | 95% | 89% | 88% | 88% | 92% | 86% | 90% | 82% |
| Gate 7 | 99% | 98% | 94% | 94% | 94% | 96% | 94% | 96% | 92% |

These targets are not automatic. They require verifier evidence, live proof where applicable, and owner approval.

## 9. No-Launch And Go-Launch Criteria

No-launch conditions:
- AWS-20 live RDS/SQS/S3 proof incomplete; SQS send and S3 marker write/read/delete are proven, but final consolidated proof remains open.
- Durable worker lifecycle unproven.
- Billing/credit/provider spend governance unproven.
- Client views expose internal diagnostics, secrets, raw infrastructure identifiers, or raw technical packets.
- Provider execution can happen without preflight, entitlement/credit approval, or audited owner override.
- No rollback, support, or incident response path for stuck paid jobs.

Internal-only conditions:
- Safe-default verifiers pass.
- Live AWS/provider/Stripe actions are explicitly owner-approved and synthetic where possible.
- No customer traffic or public promise is active.
- Failures can be investigated without customer harm.

Private paid pilot conditions:
- AWS-20 live infrastructure proof passes.
- Durable job lifecycle and status proof exists.
- Billing/credit governance works in test or approved pilot mode.
- Complete Media and core customer workflows have supportable status and recovery.
- Spend caps, refund path, support rota, and rollback plan are owner-approved.

Full public launch conditions:
- Private pilot proves successful paid workflows and clean recovery from failures.
- AWS durable operations are stable.
- Billing/credits/refunds reconcile.
- Provider cost caps and media quality are proven.
- Observability, runbooks, rollback, backup/restore, load, security, and privacy gates pass.
- Owner signs the final launch checklist.

## 10. Owner Decision Required Now

Recommended immediate next action: record the AWS-20 S3-focused live rehearsal proof in production docs, then consolidate final AWS-20 RDS/SQS/S3 proof after confirming the RDS rollback evidence.

Why: the production plan must reflect that SQS and S3 are individually proven, while AWS-20 is still not formally closed until consolidated RDS/SQS/S3 evidence is recorded.

What it will prove: proof recording spends nothing and keeps the launch plan accurate; final consolidation will prove whether AWS-20 can be treated as closed without creating AWS-21.

What it will not prove: proof recording does not prove durable worker processing, DLQ recovery, provider execution, media generation, billing, credits, Stripe, customer readiness, public launch readiness, or durable route cutover.

Whether it spends money: recording proof spends nothing. Any future live AWS consolidation run would require explicit owner approval.

Whether it can affect customers: it should not affect customers if the message remains `aws20_rehearsal`, `non_customer`, and `non_executable`, and workers remain off.

Whether it requires owner approval: recording proof does not require live approval. Any additional live AWS action requires explicit owner approval.
