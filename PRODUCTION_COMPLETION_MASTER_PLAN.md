# Production Completion Master Plan

Date: 2026-06-18

Scope: owner-facing production completion plan plus consolidated AWS-20 live infrastructure proof, live no-provider worker consumption/delete proof, AWS-backed synthetic DLQ recovery proof, synthetic durable asset delivery proof, synthetic production route cutover readiness proof, synthetic billing/credit spend governance proof, and blocked capped complete-media final deliverable proof. This document does not approve public launch, AWS cutover, provider calls, media generation, worker loops, Stripe live charges, billing or credit mutations, customer traffic, or AWS-21+ work.

## 1. Executive Owner Summary

Current launch recommendation: no full paid public launch. AWS-20 live infrastructure proof, synthetic durable asset delivery proof, synthetic production route cutover readiness proof, and synthetic billing/credit spend governance proof are now closed. The owner-approved two-provider 5s complete-media smoke proof was attempted safely and blocked before provider execution because Runway/ElevenLabs credentials were not loaded for provider readiness; the platform should remain internal-only until real provider final deliverables, Stripe/test billing reconciliation, status UX, support recovery, observability, and private-pilot proof exist.

Current AWS migration readiness: 99%.

Current full SaaS production readiness: 89%.

Biggest blocker: AWS-20 live infrastructure proof, bounded live synthetic durable handoff, local synthetic durable worker lifecycle proof, local synthetic failed-job/DLQ recovery proof, live no-provider worker consumption/delete proof, AWS-backed synthetic DLQ recovery proof, synthetic durable asset storage/retrieval/open/download proof, synthetic production route cutover readiness proof, and synthetic billing/credit spend governance proof are closed, but real provider-generated final media delivery, Stripe/test billing reconciliation, live provider execution, and support/observability drills remain unproven. The latest capped final deliverable proof now shows the exact blocker: the two-provider 5s cap is implemented, but provider readiness could not be verified because Runway and ElevenLabs credentials were not loaded.

Biggest cost/control risk: paid provider execution and long-form media jobs still require live proof that credits, package approval, provider-cost caps, retries, and failure recovery stay synchronized across real job execution.

Biggest customer-trust risk: a customer could see unclear status, delayed results, failed media, or missing downloadable assets if the durable job, worker, asset, and portal status loops are not proven end to end.

Biggest operational/support risk: support and incident handling are currently backed by strong boundaries and synthetic recovery diagnostics, but production-scale recovery from route-cutover worker failures, billing mismatches, or asset failures has not been rehearsed.

One-sentence truth statement: the platform has serious safety architecture, but it is not public paid-launch ready until live infrastructure, durable worker execution, billing reconciliation, and support recovery are proven with synthetic and controlled pilot evidence.

## 2. Current Proven Foundation

| Area | Evidence | What is proven | Limits |
| --- | --- | --- | --- |
| Production finish audit | Commit `3cbc50f Add production finish audit and gap plan`; `PRODUCTION_FINISH_AUDIT_AND_GAP_PLAN.md` | Owner-facing gap plan exists and launch recommendation is conservative. | The audit is planning proof, not live execution proof. |
| AWS-20 safe-default rehearsal boundary | Commit `75d7895 Add AWS live rehearsal boundary`; `backend/app/runtime/aws_option_a_live_rehearsal.py`; `verify_aws_option_a_live_rehearsal.py` | Rehearsal is disabled by default, requires owner approval and per-resource flags, uses synthetic non-customer markers, and avoids providers, Stripe, billing, credits, workers, and cutover. | Future rehearsal or cutover remains owner-gated; AWS-20 proof does not enable live routes or workers. |
| AWS-20 SQS-focused live rehearsal | Sanitized AWS-20 SQS proof recorded from the owner-approved 2026-06-17 SQS-focused run. | `sqs_attempted=true`, `sqs_send_attempted=true`, `sqs_passed=true`, `sqs_message_non_customer=true`, `sqs_message_non_executable=true`, and `sqs_message_id_hash_prefix=5e86bff755a4`. No provider calls, media workers, Stripe calls, billing mutations, credit mutations, customer traffic, or public cutover occurred. | Proves SQS send only; does not prove S3, worker consumption, DLQ handling, final asset delivery, or the full media lifecycle. |
| AWS-20 S3-focused live rehearsal | Sanitized AWS-20 S3 proof recorded from the owner-approved 2026-06-17 S3-focused run. | `s3_upload_attempted=true`, `read_back_passed=true`, `s3_delete_attempted=true`, `cleanup_performed=true`, `object_key_hash=9d04e4154bf1`, and `bucket_reference.sha256_12=88eb3f25047d`. No RDS write, SQS send, provider calls, media workers, Stripe calls, billing mutations, credit mutations, customer traffic, or public cutover occurred. | Proves tiny synthetic S3 marker write/read/delete only; does not prove final asset lifecycle, signed delivery, worker output persistence, customer assets, or worker output delivery. |
| AWS-20 RDS rollback-only live rehearsal | Sanitized AWS-20 RDS proof recorded from the owner-approved 2026-06-17 RDS-only run. | `insert_read_passed=true`, `update_read_passed=true`, and `transaction_rolled_back=true`. SQS and S3 resource flags were disabled, no provider calls, media workers, Stripe calls, billing mutations, credit mutations, customer traffic, or public cutover occurred. | Proves bounded synthetic RDS rollback only; does not prove durable route cutover, persistent repository writes, worker consumption, DLQ recovery, customer data migration, or billing/provider execution. |
| AWS-20 consolidated live infrastructure proof | Sanitized RDS rollback-only, SQS-focused, and S3-focused runs recorded in production docs. | RDS rollback path: proven. SQS send: proven. S3 write/read/delete cleanup: proven. | AWS-20 is formally closed, but this does not mean public launch, durable worker execution, provider execution, billing/credit execution, or client delivery is complete. |
| AWS route gates | `backend/app/runtime/aws_option_a_route_integration.py`; `verify_aws_option_a_route_cutover_boundary.py`; `verify_aws_option_a_route_integration.py` | AWS route behavior stays behind explicit route, validation, and operation flags; default path remains compatibility runtime. | Live durable route cutover is not enabled or proven. |
| Dry-run durable enqueue | Commit `45c61bf Add AWS durable enqueue dry-run boundary`; `verify_aws_option_a_durable_enqueue_dry_run.py` | Durable repository and queue packets are prepared in dry-run mode without RDS write or SQS send. | Bounded live synthetic write/send/status handoff and synthetic route readiness are now proven separately; public/customer route cutover, provider execution, and billing/credit mutation remain unproven. |
| Route-gated synthetic durable job handoff | `verify_route_gated_durable_job_handoff.py`; `backend/app/runtime/aws_option_a_route_integration.py`; `verify_durable_media_job_status_adapter.py` | Proves explicit AWS route flags are required, a synthetic non-customer accepted job gets a rollback-safe durable proof record, queue handoff is prepared through the approved boundary, status readback is prepared with a redacted customer-safe status, admin diagnostics are actionable, rollback blocks execution, and no worker, provider, Stripe, billing, credit, public cutover, or AWS call starts. Markers: `durable_repository_dry_run_prepared`, `queue_enqueue_dry_run_prepared`, `durable_status_read_dry_run_prepared`. | Dry-run proof only; does not perform live durable RDS write, SQS send, worker claim, DLQ recovery, provider execution, billing/credit mutation, or final asset delivery. |
| Production route cutover readiness proof | `verify_production_route_cutover_readiness.py`; existing route, rollback, observability, worker, DLQ, and asset proof boundaries. | Synthetic proof records `route_cutover_readiness_attempted=true`, `route_cutover_readiness_passed=true`, `public_cutover_default_disabled=true`, `owner_flags_required=true`, `rollback_kill_switch_blocked_execution=true`, `compatibility_fallback_available=true`, `synthetic_route_reached_aws_durable_path=true`, `synthetic_status_readback_passed=true`, `synthetic_asset_result_metadata_passed=true`, `client_safe_view_redacted=true`, `admin_diagnostics_redacted=true`, `provider_call_attempted=false`, `media_generation_attempted=false`, `stripe_call_attempted=false`, `billing_mutation_attempted=false`, `credit_mutation_attempted=false`, `customer_traffic_attempted=false`, `public_cutover_enabled=false`, `render_removal_attempted=false`, and `aws21_or_later_work_attempted=false`. | Proves readiness selection and redacted synthetic fixture coordination only. It does not enable public cutover, remove Render, start workers, call providers, mutate billing/credits, handle customer traffic, or prove real provider-generated final deliverables. |
| Live synthetic durable write/send/status handoff | Owner-approved 2026-06-17 run through `backend/app/runtime/aws_option_a_live_durable_handoff.py`; `verify_live_synthetic_durable_handoff.py` | `live_durable_write_attempted=true`, `live_durable_write_passed=true`, `live_status_readback_attempted=true`, `live_status_readback_passed=true`, `live_queue_send_attempted=true`, `live_queue_send_passed=true`, `synthetic_non_customer_job=true`, `queue_packet_non_customer=true`, `queue_packet_non_executable=true`, `rollback_or_cleanup_performed=true`, `client_safe_status_redacted=true`, `admin_diagnostics_redacted=true`, `rollback_controls_blocked_when_enabled=true`, `worker_started=false`, `provider_call_attempted=false`, `stripe_call_attempted=false`, `billing_mutation_attempted=false`, `credit_mutation_attempted=false`, and `public_cutover_enabled=false`. Sanitized proof includes `durable_job_reference_hash=3f0b5a060474` and `sqs_message_id_hash_prefix=902b0fcdf208`. | Proves one bounded synthetic durable DB write/read/status cleanup and one non-customer non-executable SQS handoff only. It does not enable production route cutover, worker consumption, DLQ handling, provider execution, billing/credit execution, or client delivery. |
| Live no-provider worker consumption/delete proof | Owner-approved 2026-06-17 compact live rerun through `backend/app/runtime/aws_option_a_live_no_provider_worker_consumption.py`; `verify_live_no_provider_worker_consumption.py` | `live_worker_consumption_attempted=true`, `live_worker_consumption_passed=true`, `owner_flags_required=true`, `synthetic_queue_message_received=true`, `queue_message_non_customer=true`, `queue_message_non_executable=true`, `durable_job_claim_once_passed=true`, `duplicate_claim_blocked=true`, `processing_status_passed=true`, `terminal_status_passed=true`, `queue_message_delete_or_ack_attempted=true`, `queue_message_delete_or_ack_passed=true`, `client_safe_status_redacted=true`, `admin_diagnostics_redacted=true`, `rollback_controls_blocked_when_enabled=true`, `provider_call_attempted=false`, `media_generation_attempted=false`, `stripe_call_attempted=false`, `billing_mutation_attempted=false`, `credit_mutation_attempted=false`, `customer_traffic_attempted=false`, and `public_cutover_enabled=false`. Sanitized proof includes `synthetic_job_reference_hash=3bb4afc64527` and `queue_message_id_hash_prefix=902b0fcdf208`. | Proves one synthetic non-customer, non-executable SQS worker message can be received, claimed through durable synthetic status, terminally statused, and deleted/acked without providers, media generation, Stripe, billing, credits, customer traffic, public cutover, or a long-running worker loop. It does not prove provider execution, billing/credit execution, final asset delivery, or public launch. |
| AWS-backed synthetic DLQ recovery proof | Owner-approved 2026-06-17 run through `backend/app/runtime/aws_backed_synthetic_dlq_recovery.py`; `verify_aws_backed_synthetic_dlq_recovery.py` | `aws_backed_dlq_recovery_attempted=true`, `aws_backed_dlq_recovery_passed=true`, `owner_flags_required=true`, `synthetic_dlq_message_present=true`, `dlq_message_non_customer=true`, `dlq_message_non_executable=true`, `dlq_reference_redacted=true`, `failure_classification_passed=true`, `retry_exhaustion_or_failed_terminal_represented=true`, `admin_recovery_action_represented=true`, `recovery_or_requeue_attempted=true`, `recovery_or_requeue_passed=true`, `client_safe_failed_or_recovered_status_redacted=true`, `admin_diagnostics_redacted=true`, `rollback_controls_blocked_when_enabled=true`, `customer_queue_message_consumed=false`, `provider_call_attempted=false`, `media_generation_attempted=false`, `stripe_call_attempted=false`, `billing_mutation_attempted=false`, `credit_mutation_attempted=false`, `customer_traffic_attempted=false`, and `public_cutover_enabled=false`. Sanitized proof includes `synthetic_job_reference_hash=7e1f64978bd4` and `dlq_reference_hash=7131a9384b2b`. | Proves one bounded AWS-backed synthetic DLQ-shaped recovery record can be classified, statused, recovered, read back, redacted, and cleaned up without customer queue consumption, providers, media generation, Stripe, billing, credits, customer traffic, public cutover, or a long-running worker loop. It does not prove production route cutover, paid provider execution, billing/credit execution, real provider-generated final asset delivery, or public launch. |
| Synthetic durable asset delivery proof | Owner-approved 2026-06-18 run through `backend/app/runtime/aws_synthetic_durable_asset_delivery.py`; `verify_synthetic_durable_asset_delivery.py` | `durable_asset_proof_attempted=true`, `durable_asset_proof_passed=true`, `owner_flags_required=true`, `synthetic_asset_non_customer=true`, `synthetic_asset_non_executable=true`, `asset_store_attempted=true`, `asset_store_passed=true`, `asset_job_link_passed=true`, `asset_metadata_readback_passed=true`, `asset_open_or_download_proof_passed=true`, `client_safe_asset_view_redacted=true`, `admin_asset_diagnostics_redacted=true`, `cleanup_or_retention_safe_state_passed=true`, `rollback_controls_blocked_when_enabled=true`, `provider_call_attempted=false`, `media_generation_attempted=false`, `customer_asset_used=false`, `stripe_call_attempted=false`, `billing_mutation_attempted=false`, `credit_mutation_attempted=false`, `customer_traffic_attempted=false`, `public_cutover_enabled=false`, and `signed_url_exposed=false`. Sanitized proof includes `synthetic_asset_reference_hash=9fc8e9825ba2`, `synthetic_job_reference_hash=72a3968c271e`, `object_key_hash_prefix=52e272ee4d0f`, and `metadata_object_key_hash_prefix=cd8c38fa3f5d`. | Proves one synthetic non-customer, non-executable asset can be stored in durable AWS-backed storage, linked to a synthetic job, read back as metadata/content, internally opened/downloaded through a signed-url proof without exposing the signed URL, presented as client-safe/admin-actionable metadata, and cleaned up. It does not prove real customer asset upload, provider-generated final MP4 delivery, production route cutover, billing/credit execution, or public launch. |
| Synthetic durable worker lifecycle proof | `backend/app/runtime/synthetic_durable_worker_lifecycle.py`; `verify_synthetic_durable_worker_lifecycle.py` | Synthetic durable worker lifecycle proof passed with `synthetic_worker_lifecycle_attempted=true`, `synthetic_worker_lifecycle_passed=true`, `queued_status_represented=true`, `claim_once_passed=true`, `duplicate_claim_blocked=true`, `processing_status_passed=true`, `retry_state_represented=true`, `failure_status_passed=true`, `completed_status_represented=true`, `terminal_status_readback_passed=true`, `dlq_or_recovery_shape_present=true`, `client_safe_status_redacted=true`, `admin_diagnostics_redacted=true`, `rollback_controls_blocked_when_enabled=true`, `provider_call_attempted=false`, `media_generation_attempted=false`, `stripe_call_attempted=false`, `billing_mutation_attempted=false`, `credit_mutation_attempted=false`, and `public_cutover_enabled=false`. | Proves local/safe synthetic worker lifecycle shape only. It does not start a worker loop, consume customer queues, call AWS, call providers, generate media, mutate billing/credits, or prove live DLQ recovery. |
| Synthetic failed-job and DLQ recovery proof | `backend/app/runtime/synthetic_failed_job_recovery.py`; `verify_synthetic_failed_job_recovery.py` | Synthetic failed-job and DLQ recovery proof passed with `synthetic_failed_job_recovery_attempted=true`, `synthetic_failed_job_recovery_passed=true`, `failure_classification_passed=true`, `retry_exhaustion_represented=true`, `dlq_shape_present=true`, `dlq_reference_redacted=true`, `admin_recovery_action_represented=true`, `client_safe_failed_status_redacted=true`, `admin_diagnostics_redacted=true`, `recovered_or_requeued_state_represented=true`, `terminal_failed_readback_passed=true`, `terminal_recovered_or_completed_represented=true`, `rollback_controls_blocked_when_enabled=true`, `provider_call_attempted=false`, `media_generation_attempted=false`, `stripe_call_attempted=false`, `billing_mutation_attempted=false`, `credit_mutation_attempted=false`, and `public_cutover_enabled=false`. | Proves local/safe synthetic failure classification, retry exhaustion, DLQ/recovery shape, admin recovery representation, client-safe failure status, terminal failed readback, and synthetic recovered/completed state only. It does not start a live worker loop, consume customer queues, call AWS, call providers, generate media, mutate billing/credits, or prove live DLQ recovery. |
| Rollback controls | Commit `8eb71c9 Add AWS rollback control boundary`; `backend/app/runtime/aws_option_a_rollback_controls.py`; `verify_aws_option_a_rollback_controls.py` | Kill switch and forced compatibility fallback can block route execution and report sanitized admin/client states. | Live incident rollback drill is not proven. |
| Observability diagnostics | Commit `0b943fb Add AWS observability diagnostics boundary`; `backend/app/runtime/aws_option_a_observability.py`; `verify_aws_option_a_observability.py` | Redacted diagnostic bundle and incident event shapes exist without CloudWatch/external logging side effects. | Live CloudWatch/alerting/dashboard proof is not present. |
| AWS migration matrix through AWS-20 | `AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md` | AWS-01 through AWS-20 boundaries and AWS-20 RDS/SQS/S3 proof are documented without AWS-21+ expansion. | Matrix proof does not enable route cutover, worker execution, provider execution, billing/credit execution, or client delivery. |
| Frontend build baseline | Production audit records `cd frontend && npm.cmd run build` passed. | Current frontend compiles. | Build success does not prove live user workflow quality. |
| Media cost and preflight guardrails | `backend/app/runtime/direct_media_provider_execution_runtime.py`; `verify_media_provider_preflight_safety.py`; `verify_duration_aware_media_segments.py`; `verify_complete_media_portal_renderer.py` | Complete media has preflight, duration-aware segments, credit-risk confirmation, and safer portal rendering. | Live provider reliability and real provider-generated final asset delivery under production route conditions remain unproven. |
| Billing credit spend governance proof | `backend/app/runtime/billing_credit_spend_governance.py`; `verify_billing_credit_spend_governance.py`; existing entitlement and billing ledger boundaries. | Synthetic proof records `billing_credit_governance_attempted=true`, `billing_credit_governance_passed=true`, `package_entitlement_required=true`, `credit_reserve_before_execution_passed=true`, `provider_cost_cap_blocked_without_approval=true`, `owner_override_audited=true`, `credit_finalize_after_success_represented=true`, `credit_reversal_after_failure_represented=true`, `refund_or_reconciliation_shape_present=true`, `client_billing_view_redacted=true`, `admin_billing_diagnostics_redacted=true`, `stripe_live_charge_attempted=false`, `provider_call_attempted=false`, `media_generation_attempted=false`, `real_customer_billing_mutation_attempted=false`, `real_customer_credit_mutation_attempted=false`, `customer_traffic_attempted=false`, `public_cutover_enabled=false`, and `render_removal_attempted=false`. | Proves synthetic/test-mode governance shape only. It does not perform a Stripe live charge, real customer billing mutation, real customer credit mutation, provider call, media generation, customer traffic, public cutover, or Render removal. |
| Complete media final deliverable proof | `backend/app/runtime/complete_media_final_deliverable_proof.py`; `verify_complete_media_final_deliverable_proof.py`; complete-media runtime source inspection; injected synthetic durable asset proof. | Safety proof records `complete_media_final_deliverable_attempted=true`, `complete_media_final_deliverable_passed=false`, `owner_provider_approval_required=true`, `provider_cost_cap_enforced=true`, `provider_call_attempted=false`, `provider_call_count=0`, `visual_provider_call_count=0`, `audio_provider_call_count=0`, `provider_retry_count=0`, `long_form_generation_blocked_or_not_requested=true`, `multi_agent_provider_fanout_blocked=true`, `synthetic_non_customer_request=true`, `customer_asset_used=false`, `customer_likeness_used=false`, `billing_mutation_attempted=false`, `credit_mutation_attempted=false`, `stripe_live_charge_attempted=false`, `durable_status_flow_passed=true`, `provider_output_or_failure_recorded=true`, `durable_asset_storage_passed=true`, `client_safe_result_view_redacted=true`, `admin_provider_diagnostics_redacted=true`, `failure_path_supportable=true`, `public_cutover_enabled=false`, `render_removal_attempted=false`, and `aws21_or_later_work_attempted=false`; blocked reason is `blocked_provider_readiness_not_verified`. | Proves the two-provider cap and readiness gate prevented an unsafe live provider attempt. It does not prove a real provider-generated final deliverable. Next owner action is to load/verify Runway and ElevenLabs credentials in the execution environment, then rerun one bounded two-provider-call 5s smoke with the same caps. |
| Final 27-agent catalogue | Commit `2e1ea9f Lock final 27 agent catalogue visibility`; `verify_final_27_agent_catalogue_visibility.py` | Client-visible catalogue count is 27 and system agents are internal layers. | Agent quality across all workflows still needs sampled production QA. |

## 3. Current Unproven Areas

- Live durable AWS job lifecycle after AWS-20, handoff proof, synthetic worker lifecycle proof, synthetic failed-job recovery proof, live no-provider worker consumption/delete proof, AWS-backed synthetic DLQ recovery proof, synthetic durable asset delivery proof, and synthetic production route readiness proof: RDS rollback, SQS send, S3 marker write/read/delete cleanup, dry-run route-gated handoff, one bounded live synthetic durable write/send/status proof, local synthetic claim/retry/fail/complete lifecycle proof, local synthetic failed-job/DLQ recovery proof, one live no-provider synthetic worker receive/status/delete proof, one AWS-backed synthetic DLQ recovery proof, one synthetic durable asset store/read/open/download/cleanup proof, and synthetic route-readiness coordination are complete, but public cutover, billing/credit reconciliation, and real provider-generated final media delivery are not proven.
- Durable worker lifecycle: local synthetic worker claim, duplicate-claim block, retry, failure, completion, terminal readback, DLQ/recovery shape, retry exhaustion, admin recovery action, recovered/requeued state, one live synthetic no-provider receive/status/delete path, AWS-backed synthetic DLQ-shaped recovery, and synthetic route-readiness coordination are proven; production-scale worker routing under paid/customer workloads remains unproven.
- S3 synthetic asset lifecycle: synthetic upload/store, metadata readback, signed/open/download proof, cleanup, and client/admin views are proven; real provider-generated final media delivery through the production route remains unproven.
- Live provider orchestration under cost caps: Runway/ElevenLabs and fallbacks have guardrails, but provider execution under durable job, cost cap, credit, and status governance is not fully proven. The owner-approved two-provider 5s proof was blocked because provider readiness could not be verified without loaded Runway/ElevenLabs credentials.
- Client popup job status/result UX under real jobs: the portal renderer is structurally improved, but async live status and final asset behavior need evidence.
- Billing/credit reconciliation under execution: synthetic governance now proves entitlement, reservation, finalization, reversal/refund shape, admin override audit, and provider-cost cap blocking, but Stripe test/live reconciliation, persistent real ledger mutation, and provider actual-cost reconciliation under real attempts still need proof.
- Support recovery and DLQ handling: AWS-backed synthetic DLQ-shaped recovery is proven, but production-scale operator recovery from route-cutover worker failures, stuck jobs, billing mismatches, or asset failures is not rehearsed.
- Load/scale readiness: queue backpressure, concurrent job acceptance, status polling, and provider throttling behavior are not measured.
- Security/privacy/likeness handling proof: secret redaction exists, but tenant isolation, avatar/likeness consent, retention, and deletion workflows need audit evidence.
- Production deployment and rollback drill: local/verifier safety exists, but release rollback across frontend, backend, worker, AWS flags, and provider flags is not rehearsed.

## 4. Launch Gates

| Gate | Objective | Why it matters | Required work | Files likely touched | Commands/verifiers | Live spend involved? | Owner approval required? | Exact done criteria | Stop condition | Expected commit message |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gate 0: Repo clean and audit baseline | Keep a trustworthy baseline before live proof. | Prevents accidental launch changes while investigating infrastructure. | Confirm clean status, audit exists, matrix stays through AWS-20. | Docs only if baseline notes change. | `git status --short`; `git diff --check`; safe build/compile as needed. | No | No | Clean worktree except intentional docs/code changes; no AWS-21+ rows. | Dirty unrelated files or matrix expansion. | `Record production baseline evidence` |
| Gate 1: AWS live infrastructure proof | Prove bounded RDS, SQS, and S3 rehearsal resources. | AWS cutover cannot proceed until the foundation actually works. | Closed: RDS rollback-only proof, SQS-focused send proof, and S3-focused marker write/read/delete cleanup proof are recorded with sanitized non-customer evidence. | `aws_option_a_live_rehearsal.py`; `verify_aws_option_a_live_rehearsal.py`; proof docs. | AWS-20 verifier, route/rollback/observability regressions. | Low AWS test-resource usage | Yes for live runs; no for docs-only recording | RDS rollback, SQS non-customer non-executable send, S3 marker write/read/delete all pass with sanitized output and consolidated proof is recorded. | Any secret exposure, customer data, executable queue message, failed cleanup, or broad AWS call. | `Record AWS RDS rollback proof` |
| Gate 2: Durable job lifecycle proof | Prove accepted jobs persist, queue, process, retry, and finish safely. | Paid workflows need durable state and recoverable status. | Closed for synthetic no-provider/no-billing/no-credit route readiness: live synthetic durable write/send/status handoff, local synthetic worker lifecycle, local synthetic failed-job/DLQ recovery, live no-provider worker consumption/delete, AWS-backed synthetic DLQ recovery, synthetic durable asset delivery, and production route cutover readiness are proven. | Route integration, repository, queue, worker, status, and asset adapters/verifiers. | Durable enqueue verifier; worker lifecycle verifier; status adapter verifier; DLQ/recovery verifier; live no-provider worker verifier; AWS-backed DLQ recovery verifier; synthetic asset delivery verifier; production route cutover readiness verifier. | Possible AWS SQS/RDS/S3 test usage | Yes for live runs; no for this synthetic fixture | Synthetic job accepted, persisted, queued, claimed once, status-updated, deleted/acked, retried/failed/recovered/completed, linked to a cleaned-up synthetic asset, and route-selected safely with no providers. | Duplicate processing, missing terminal state, unsafe retry, failed delete/ack, failed recovery, asset leakage, failed cleanup, unredacted diagnostics, public cutover, provider call, or billing/credit mutation. | `Prove production route cutover readiness` |
| Gate 3: Admin/client UX proof | Prove users and operators see useful status and recovery actions. | Trust fails when jobs are technically running but UX is confusing. | QA queued/running/failed/retry/completed/final asset states. | Admin/client portal components, status routes, support routes, verifiers. | Frontend build; portal renderer verifier; route fixtures; screenshot QA if available. | No, unless using live AWS/provider fixtures | Sometimes | Client-safe views hide internals; admin sees actionable diagnostics; final outputs open/download. | Raw packet/secrets in client view, stale status, or unclear failure messaging. | `Close launch status and support UX proof` |
| Gate 4: Billing/credits/spend governance proof | Prove paid work cannot escape package, credit, and approval controls. | This protects customer fairness and owner cost. | Closed for synthetic/test-mode governance: entitlement, credit reservation, cost-cap blocking, owner override audit, finalization, reversal/refund, reconciliation shape, and redacted client/admin views are proven without live charges or mutations. Remaining work is Stripe test/live reconciliation and persistent real ledger mutation only when owner-approved. | Billing, credit, entitlement, Stripe runtimes and verifiers. | Billing ledger verifier; entitlement verifier; billing governance verifier; Stripe webhook tests when approved. | No for current synthetic proof; Stripe test/live depending future mode | Yes for live or charge-affecting work | Provider execution is represented as blocked without entitlement/credit or explicit audited owner override. | Live charge without entitlement, credit mismatch, un-audited override, secret leak, or provider execution bypassing cost cap. | `Prove billing credit spend governance` |
| Gate 5: Observability/support/rollback proof | Prove incidents are detected, diagnosed, and reversible. | Paid SaaS needs operations, not just code. | Redacted logs/metrics/alerts, runbooks, rollback drill, support recovery fixtures. | Observability, admin diagnostics, runbook docs, support routes. | Observability verifier; rollback verifier; incident drill; optional CloudWatch test. | Possible AWS logging usage | Yes for live AWS logging | Owner can identify stuck/failed jobs, rollback, and recover without secret exposure. | No alert path, no runbook, rollback cannot stop execution, or secrets in logs. | `Wire launch observability evidence` |
| Gate 6: Controlled private paid pilot | Validate a narrow paid workflow with known users and cost caps. | Real customers reveal workflow gaps, but blast radius must be tiny. | Pilot package, spend cap, support rota, refund path, daily review. | Pilot docs, billing config, provider caps, support docs. | Full gate verifier set; pilot checklist; manual owner signoff. | Yes, bounded | Yes | Several controlled paid workflows complete or recover cleanly with reconciled billing and assets. | Any uncontrolled spend, unresolved customer failure, or billing inconsistency. | `Add private paid pilot launch runbook` |
| Gate 7: Full paid public launch | Open beyond private pilot only after operational proof. | Public launch magnifies every unproven edge case. | Final launch checklist, load/security proof, backup/restore, support staffing. | Launch docs, deployment configs, runbooks, tests. | Full regression, load smoke, security/privacy audit, backup/restore drill. | Yes | Yes | Owner signs full launch after all P0/P1 launch blockers are closed. | Any unresolved P0, missing rollback, missing billing reconciliation, or unreliable media flow. | `Approve full paid public launch readiness` |

## 5. Prioritized Production Backlog

| Rank | Priority | Work item | Domain | Why it matters | Current evidence | Required implementation | Required verification | Owner approval needed? | Can be done without live spend? | Readiness gain if completed | Dependencies |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | P0 | Complete media live provider final deliverable proof | Media/provider | Paid customers need a complete output, not just infrastructure and synthetic asset proof. | Preflight, scripting, duration, portal, worker, recovery, asset, route-readiness, billing-governance, and blocked final-deliverable safety proofs exist; real provider-generated final MP4 delivery is not proven through the durable production path. | Load/verify Runway and ElevenLabs credentials, then rerun the explicitly approved two-provider-call 5s smoke with one visual call, one audio call, zero retries, no customer assets, and no billing/credit mutation. | Media preflight/script/duration/portal verifiers plus live evidence capture after provider readiness is verified. | Yes for paid providers | No | +4% media | Billing credit spend governance proof closed |
| 2 | P0 | Stripe test billing reconciliation proof | Billing | Revenue state must match platform access before private pilot. | Synthetic billing governance and ledger shapes exist; Stripe test/live reconciliation is not proven. | Test-mode checkout/webhook/refund/subscription-state reconciliation with redacted audit evidence. | Stripe test verifier and ledger proof. | Yes for Stripe mode | Test mode may spend no money | +5% billing | Item 1 can run as provider-only only if billing remains no-mutation; full pilot needs this |
| 3 | P0 | Media job status/result visibility inside Create Media popup | Frontend/media | Customers and admins need accurate job state. | Portal renderer guard exists and synthetic asset delivery proof has a client-safe/admin-actionable shape. | Live/durable status mapping for queued, running, failed, retry, complete, preview, and download. | Frontend build, renderer verifier, route fixture tests. | No for fixtures | Yes | +3% client UX | Items 1-2 |
| 4 | P0 | Client-safe status/errors | Client UX/security | Clients must not see internals or secrets. | Client-safe views exist in several boundaries and live handoff client status was redacted. | End-to-end client error/status filtering. | Client route snapshots and redaction verifier. | No | Yes | +2% client UX | Items 2-3 |
| 5 | P0 | Admin full diagnostics/support view | Admin ops | Owner needs recovery detail without secrets. | Admin diagnostics exist in AWS/media paths and live handoff diagnostics were hash-only. | Consolidate job, provider, queue, billing, asset, support evidence. | Admin fixture verifier. | No | Yes | +3% admin ops | Items 1-3 |
| 6 | P0 | Provider-cost and credit ledger reconciliation | Billing/spend | Estimated provider risk must match actual cost and credit usage. | Preflight estimates and placeholder ledger boundaries exist. | Compare provider attempts, actual cost, reservation, finalization, reversal, and admin override evidence. | Provider cost/credit ledger verifier. | Yes for live provider evidence | Partly | +5% billing | Items 1, 3 |
| 7 | P0 | Persistent billing ledger mutation proof | Billing | Synthetic ledger shapes must become durable only when safe. | No-mutation billing governance proof exists. | Persist reservation/finalization/reversal/refund with idempotency and rollback controls. | Persistent ledger verifier and rollback/reconciliation proof. | Yes for persistent/live mode | Partly | +5% billing | Items 2 and 6 |
| 8 | P0 | Provider execution cost cap and owner approval proof | Media/spend | Prevents credit burn on failed or long jobs. | Preflight/high-risk confirmation exists. | Tie provider attempts to credit/cost cap and durable job evidence. | Media preflight, duration, provider attempt verifier, pilot smoke. | Yes for live providers | Fixtures yes | +4% media | Items 1, 6 |
| 9 | P1 | Media output quality proof under broad use cases | Media quality | Commercial output must be client-ready. | Media script quality verifier exists. | Sample multiple industries, durations, platforms, avatar/no-avatar modes. | Fixture QA and owner review set. | No unless live generation | Yes | +3% media | Item 8 |
| 10 | P1 | Human/avatar likeness consent and quality proof | Privacy/media | Likeness misuse is high trust/legal risk. | Human/avatar modes exist. | Consent record, asset linkage, client-safe messaging, no-human compliance. | Consent/privacy verifier and media fixtures. | Yes for policy | Yes | +3% security | Items 3, 9 |
| 11 | P1 | Observability/logging/runbook proof | Ops | Incidents need detection and response. | AWS-19 diagnostics exist. | Redacted logs, alerts, dashboards, incident runbooks. | Observability verifier plus incident drill. | Yes for live AWS logging | Partly | +4% ops | Items 1-3 |
| 12 | P1 | Load/scale smoke proof | Scale | Avoid first-pilot queue/status overload. | No load evidence. | Synthetic concurrent acceptance/status/queue test. | Load report with p95/p99 and no provider spend. | Yes if AWS resources used | Partly | +3% SaaS | Items 1-3 |
| 13 | P1 | Security/privacy audit proof | Security | Tenant/privacy errors can kill trust. | Redaction helpers and client/admin separation exist. | Tenant isolation, secret redaction, session, retention, deletion checks. | Security/privacy verifier and dependency scan. | Yes for policy | Yes | +4% SaaS | Items 4, 10 |
| 14 | P1 | Private paid pilot plan | Launch | Pilot needs explicit caps and support. | Audit recommends limited private pilot only. | Pilot runbook, spend caps, rollback/refund/support process. | Owner-approved checklist. | Yes | Yes until pilot starts | +2% launch | Items 1-13 P0/P1 |
| 15 | P1 | Full launch checklist | Launch | Full public launch needs gate discipline. | Production audit and this plan. | Final checklist with P0/P1 proof links and owner signoff. | Full launch review. | Yes | Yes | +2% launch | Private pilot success |

## 6. The Next 10 Codex Tasks

1. Task name: Load provider credentials and rerun two-provider 5s Complete Media smoke.
   Goal: prove a real provider-generated final asset with one visual provider call, one audio provider call, and zero retries.
   Why now: route readiness, synthetic billing/credit spend governance, and the blocked final-deliverable safety proof are proven; the two-provider cap is now the approved shape, but provider readiness could not be verified because credentials were not loaded.
   Files to inspect: media provider runtime, durable asset delivery, route/status boundaries, Complete Media popup.
   Files likely changed: docs/verifier only if the live proof outcome is recorded.
   Commands/verifiers: complete-media final-deliverable verifier, media preflight/script/duration/portal verifiers, synthetic asset verifier, provider-smoke evidence capture after credentials are loaded.
   Live spend: yes, exactly one visual provider call and one audio provider call.
   Owner approval needed: already approved for this bounded two-provider 5s smoke; any retry or longer job needs fresh approval.
   Expected commit message: `Prove complete media final asset delivery`.
   Done criteria: provider output is durable, downloadable, client-safe, admin-diagnostic, and reconciled to job status.
   Do not do list: no retries, no third provider call, no unbounded provider calls, no public cutover, no billing mutation unless separately approved.

2. Task name: Prove Stripe test billing reconciliation.
   Goal: prove checkout/webhook/refund/subscription reconciliation in test mode without live charges.
   Why now: synthetic billing governance is proven, but Stripe test reconciliation is still needed before private paid pilot.
   Files to inspect: Stripe checkout route, webhook/refund routes, billing ledger boundary, entitlement activation runtime.
   Files likely changed: Stripe test verifier/runtime guards only if a defect is found.
   Commands/verifiers: billing governance verifier, billing ledger verifier, Stripe test webhook verifier.
   Live spend: no real money in test mode; live mode remains disallowed.
   Owner approval needed: yes for Stripe test-mode actions.
   Expected commit message: `Prove Stripe test billing reconciliation`.
   Done criteria: test checkout/webhook/refund shape reconciles to entitlement/ledger without secrets or live charges.
   Do not do list: no Stripe live charges, no real customer billing mutation.

3. Task name: Prove Complete Media UX under durable status.
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

4. Task name: Prove observability, support, and rollback operations.
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

5. Task name: Prove security, privacy, and likeness consent.
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

6. Task name: Run load and backpressure smoke proof.
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

7. Task name: Prepare controlled private paid pilot runbook.
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

8. Task name: Prepare full paid launch checklist after private pilot evidence.
    Goal: convert verified pilot evidence into final public-launch gates and owner signoff.
    Why now: this keeps public launch clearly separated from infrastructure and pilot proof.
    Files to inspect: production master plan, audit plan, pilot runbook, billing/media/support/security proof docs.
    Files likely changed: final launch checklist docs only unless a blocker is found.
    Commands/verifiers: full gate verifier set, frontend build, backend compile, security/privacy/load proof references.
    Live spend: no until launch approval.
    Owner approval needed: yes.
    Expected commit message: `Prepare final paid launch checklist`.
    Done criteria: every P0/P1 gate has evidence, stop/go criteria are explicit, and owner signs the final launch decision.
    Do not do list: no public launch, no open signup expansion, and no live provider/billing/cutover action.

9. Task name: Prove backup and restore readiness.
    Goal: prove RDS/S3 recovery can restore durable job, asset, audit, and support evidence after failure.
    Why now: paid SaaS needs disaster recovery before expanding beyond a controlled pilot.
    Files to inspect: RDS schema/readiness boundaries, S3 asset boundary, backup/restore docs, audit/evidence stores.
    Files likely changed: backup/restore verifier and runbook docs.
    Commands/verifiers: restore drill verifier, asset recovery verifier, backend compile.
    Live spend: possible low AWS test-resource usage if owner approves a non-prod restore drill.
    Owner approval needed: yes for live AWS restore testing.
    Expected commit message: `Prove backup restore readiness`.
    Done criteria: restore evidence is redacted, repeatable, and tied to RPO/RTO expectations without customer data exposure.
    Do not do list: no customer data restore, no production destructive action, no public cutover.

10. Task name: Review legal and commercial policy alignment.
    Goal: make sure terms, refunds, privacy, support promises, and runtime behavior match before private paid pilot.
    Why now: infrastructure proof does not protect the owner if commercial promises exceed what the system can enforce.
    Files to inspect: legal pages, refund routes, billing docs, privacy docs, support docs, production audit.
    Files likely changed: owner-facing legal/commercial checklist docs.
    Commands/verifiers: policy checklist review, billing/refund route verifier if available.
    Live spend: no.
    Owner approval needed: yes for policy decisions.
    Expected commit message: `Review launch legal commercial alignment`.
    Done criteria: launch promises, refund path, support expectations, privacy/likeness rules, and current runtime enforcement are aligned.
    Do not do list: no legal claim expansion, no public launch, no billing changes without approval.

## 7. Spend And Approval Map

| Action | Risk/spend type | Needs owner approval? | Safe default? | Notes |
| --- | --- | --- | --- | --- |
| Live AWS RDS/SQS/S3 rehearsal | Low AWS infrastructure usage and possible persistent test artifact if cleanup fails | Yes | Off | Synthetic only; no customer data; no cutover. |
| Live synthetic durable write/send/status handoff | Low AWS/RDS/SQS test-resource usage | Already approved and passed on 2026-06-17 | Off | Passed with synthetic non-customer durable DB write/read/status cleanup and non-customer non-executable SQS handoff. Sanitized proof only: `durable_job_reference_hash=3f0b5a060474`, `sqs_message_id_hash_prefix=902b0fcdf208`; workers, providers, Stripe, billing, credits, customer traffic, and public cutover remained off. |
| Live no-provider worker consumption/delete proof | Low AWS/RDS/SQS test-resource usage | Already approved and passed on 2026-06-17 | Off | Passed with one synthetic non-customer, non-executable SQS message receive, durable claim/status update, duplicate claim block, terminal status, and delete/ack. Sanitized proof only: `synthetic_job_reference_hash=3bb4afc64527`, `queue_message_id_hash_prefix=902b0fcdf208`; providers, media generation, Stripe, billing, credits, customer traffic, and public cutover remained off. |
| AWS-backed synthetic DLQ recovery proof | Low AWS/RDS test-resource usage | Already approved and passed on 2026-06-17 | Off | Passed with synthetic DLQ-shaped durable recovery proof. Sanitized proof only: `synthetic_job_reference_hash=7e1f64978bd4`, `dlq_reference_hash=7131a9384b2b`; customer queue consumption, providers, media generation, Stripe, billing, credits, customer traffic, and public cutover remained off. |
| Synthetic durable asset delivery proof | Low AWS/S3 test-resource usage | Already approved and passed on 2026-06-18 | Off | Passed with one synthetic non-customer, non-executable asset store/read/metadata/open-download proof and cleanup. Sanitized proof only: `synthetic_asset_reference_hash=9fc8e9825ba2`, `synthetic_job_reference_hash=72a3968c271e`, `object_key_hash_prefix=52e272ee4d0f`, `metadata_object_key_hash_prefix=cd8c38fa3f5d`, and `signed_url_exposed=false`; providers, media generation, customer assets, Stripe, billing, credits, customer traffic, and public cutover remained off. |
| Synthetic durable worker lifecycle proof | No live AWS or provider spend | Completed locally with safe synthetic fixtures | Off | Passed without live AWS calls, worker loops, customer queue consumption, providers, media generation, Stripe, billing, credits, customer traffic, or public cutover. |
| Synthetic failed-job and DLQ recovery proof | No live AWS or provider spend | Completed locally with safe synthetic fixtures | Off | Passed without live AWS calls, worker loops, customer queue consumption, providers, media generation, Stripe, billing, credits, customer traffic, or public cutover. Proves failure classification, retry exhaustion, redacted DLQ shape, admin recovery representation, client-safe failure status, and synthetic recovered/completed state only. |
| AWS-20 SQS-focused rehearsal | Low AWS SQS request cost | Already approved and passed on 2026-06-17 | Off | Passed with non-customer, non-executable message and sanitized hash-only message ID proof. |
| AWS-20 S3-focused rehearsal | Low AWS S3 request/storage cost | Already approved and passed on 2026-06-17 | Off | Passed with tiny synthetic marker write/read/delete, cleanup performed, and sanitized bucket/object hash proof only. |
| AWS-20 RDS rollback-only rehearsal | Low AWS/RDS test-resource usage | Already approved and passed on 2026-06-17 | Off | Passed with synthetic rollback-only proof: `insert_read_passed=true`, `update_read_passed=true`, `transaction_rolled_back=true`; no raw database identifiers recorded. |
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

Current percentages after AWS-20 RDS/SQS/S3 proof consolidation, live synthetic durable handoff proof, synthetic durable worker lifecycle proof, synthetic failed-job/DLQ recovery proof, live no-provider worker consumption/delete proof, AWS-backed synthetic DLQ recovery proof, synthetic durable asset delivery proof, synthetic production route cutover readiness proof, and synthetic billing/credit spend governance proof:

| Area | Current readiness |
| --- | ---: |
| AWS migration readiness | 99% |
| Full SaaS production launch readiness | 89% |
| Media generation production readiness | 76% |
| Durable backend/job readiness | 82% |
| Client UX readiness | 72% |
| Admin ops readiness | 83% |
| Billing/credit readiness | 68% |
| Observability/support readiness | 76% |
| Security/privacy readiness | 68% |

Target percentages after gate closure:

| Gate closed | AWS migration | Full SaaS launch | Media production | Durable backend/jobs | Client UX | Admin ops | Billing/credit | Observability/support | Security/privacy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gate 0 | 99% | 89% | 76% | 82% | 72% | 83% | 68% | 76% | 68% |
| Gate 1 | 99% | 89% | 76% | 82% | 72% | 83% | 68% | 76% | 68% |
| Gate 2 | 99% | 89% | 76% | 82% | 72% | 83% | 68% | 76% | 68% |
| Gate 3 | 96% | 90% | 79% | 82% | 80% | 84% | 69% | 77% | 70% |
| Gate 4 | 96% | 92% | 82% | 82% | 82% | 85% | 78% | 79% | 72% |
| Gate 5 | 97% | 93% | 84% | 84% | 84% | 90% | 80% | 88% | 78% |
| Gate 6 | 98% | 95% | 89% | 88% | 88% | 92% | 86% | 90% | 82% |
| Gate 7 | 99% | 98% | 94% | 94% | 94% | 96% | 94% | 96% | 92% |

These targets are not automatic. They require verifier evidence, live proof where applicable, and owner approval.

## 9. No-Launch And Go-Launch Criteria

No-launch conditions:
- Durable worker lifecycle unproven.
- Public cutover and paid/customer route execution remain unproven even though synthetic route readiness is proven.
- Stripe test/live reconciliation and persistent billing/credit mutation unproven beyond synthetic governance.
- Client views expose internal diagnostics, secrets, raw infrastructure identifiers, or raw technical packets.
- Provider execution can happen without preflight, entitlement/credit approval, or audited owner override.
- No rollback, support, or incident response path for stuck paid jobs.

Internal-only conditions:
- Safe-default verifiers pass.
- Live AWS/provider/Stripe actions are explicitly owner-approved and synthetic where possible.
- No customer traffic or public promise is active.
- Failures can be investigated without customer harm.

Private paid pilot conditions:
- AWS-20 live infrastructure proof is closed.
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

Recommended immediate next action: load/verify Runway and ElevenLabs credentials in the execution environment, then rerun the already approved two-provider-call 5s complete-media smoke with the same caps, while keeping public cutover, customer traffic, Stripe live charges, billing/credit mutation, and AWS-21+ off unless separately owner-approved.

Why: AWS-20 is now closed for RDS rollback, SQS send, and S3 marker lifecycle proof; bounded live synthetic durable write/send/status handoff is proven; local synthetic worker claim/retry/fail/complete lifecycle is proven; local synthetic failed-job/DLQ recovery is proven; one live no-provider worker receive/status/delete path is proven; AWS-backed synthetic DLQ recovery is proven; synthetic durable asset storage/retrieval/open/download with cleanup is proven; synthetic production route cutover readiness is proven; synthetic billing/credit spend governance is proven; and the capped final-deliverable proof correctly blocked before provider execution because provider readiness was not verified. The next paid SaaS risk is whether a real provider-generated final deliverable can complete under the approved two-provider-call budget.

What it will prove: the next approved proof should establish whether provider output can be produced, persisted, opened/downloaded, statused, and diagnosed without bypassing preflight, credit, package, cost-cap, provider-call-count, or recovery controls.

What it will not prove: a capped final deliverable proof will not by itself prove Stripe live billing, public launch readiness, support staffing, load, backup/restore, security/privacy, or private pilot success.

Whether it spends money: the current blocked proof spent nothing and made no provider calls. The next proof spends provider credits only after Runway and ElevenLabs credentials are loaded and readiness passes. Stripe live charges remain out of scope unless separately approved.

Whether it can affect customers: it should not affect customers if tests remain synthetic/internal, public cutover remains off, and live customer charges remain blocked.

Whether it requires owner approval: docs and local verifiers do not require live approval. Any Stripe live, provider live, customer-affecting, or additional AWS live action requires explicit owner approval.
