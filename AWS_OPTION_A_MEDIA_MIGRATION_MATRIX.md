# AWS Option A Media Production Migration Matrix

Created: 2026-06-13T02:59:50

## Decision

The production paid-client media execution path will migrate from the current Vercel/Render single-runtime approach to AWS Option A:

- ECS/Fargate backend API service
- ECS/Fargate media worker service with ffmpeg
- SQS media queue
- SQS dead-letter queue
- RDS PostgreSQL for durable job/customer/asset/audit state
- S3 for durable media/object storage
- CloudWatch logs
- Secrets Manager for provider credentials
- IAM task roles
- ALB/API endpoint

The frontend may remain on Vercel temporarily, but the production media path must not depend on Vercel API routes, Render-local runtime_outputs, or in-memory job state.

## Current Proven Media Capabilities

| Capability | Current status | Production migration requirement |
|---|---:|---|
| Self-contained Create Media popup | Working | Preserve |
| Popup does not depend on main Run Agent section | Working | Preserve |
| Popup creative agent selection | Working | Preserve |
| Multi-agent payload rules | Working | Preserve |
| Universal complete media workflow | Working | Move to durable API/worker |
| Runway visual generation | Working | Worker provider adapter |
| ElevenLabs voice/audio generation | Working | Worker provider adapter |
| ffmpeg composition | Working | Worker container with ffmpeg |
| Popup status polling | Working enough for staging | Poll durable RDS-backed status |
| Runtime local file outputs | Not production safe | Replace with S3 |
| In-memory job state | Not production safe | Replace with RDS/SQS |
| Render deploy/runtime restarts | Not production safe | ECS services + durable queue/state |

## Locked Media Requirements

| Area | Requirement |
|---|---|
| Use cases | Not ecommerce-only. Must support ecommerce, product demos, service promos, ads, social, education, training, presentations, podcasts/audio, brand storytelling, cinematic content, human-led media, and other creative/business media. |
| Video length | Client can request as long as they want, governed by allocated credits, provider feasibility, queue capacity, and production orchestration. |
| Long video handling | Scene planning, provider-safe segmentation, staged/parallel generation, full voiceover timing, captions, music/SFX, stitching, composition, retries, one final deliverable. |
| Credits/billing | Duration, quality mode, provider cost, number of segments, audio/music/caption/composition work, and revisions must affect usage. |
| Creative controls | Cinematic style, scene planning, angles, shots, camera movement, lighting, color grade, composition, transitions, pacing, realism, references, props, environments, brand style, platform format, captions, music, SFX, voiceover, voice style, tone, pace, language, accent, emotion, pronunciation, pauses, delivery style. |
| Human mode | Required first-class field: 1. No human/avatar, 2. Generate new avatar/person, 3. Use client-uploaded face/likeness, 4. Use saved brand spokesperson/avatar. |
| Human controls | Gender presentation, age range, ethnicity/cultural appearance, skin tone, face shape, facial features, hair style/color, eye color, body/build, wardrobe, grooming, expressions, emotion, speaking style, accent, body language, gestures, eye contact, posture, energy, realism level, likeness consistency. |
| Facial performance | Lifelike eyes, natural blinking, micro-expressions, gaze direction/consistency, smile/frown/concern/confidence/enthusiasm, believable lip sync, natural mouth movement, head movement, posture, gestures, body language. |
| Uploaded likeness | Explicit consent, privacy-safe durable storage, client control, likeness consistency, same facial performance/quality guardrails. |
| Guardrails | No dead eyes, frozen expressions, robotic blank faces, uncanny faces, stiff gestures, warped hands, disappearing/morphing objects, bad reflections, mismatched motion, poor sync, choppy audio, robotic voiceover, off-brand output. |
| Prompting | Provider prompts stay natural and cinematic; internal guardrails are stored and applied separately. |

## Migration Workstreams

| Row | Workstream | Goal | Files / components | Done when |
|---:|---|---|---|---|
| A1 | Migration matrix | Lock production migration plan | AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md | Matrix committed |
| A2 | Durable media domain schema | Define jobs, assets, events, controls, human mode, credit metadata | backend/app/runtime or backend/app/media | Schema exists and tests pass |
| A3 | MediaJobStore abstraction | Create/update/read/list durable jobs | local JSON now, Postgres later | API calls no longer depend on memory |
| A4 | MediaAssetStore abstraction | Save raw/final media, metadata, signed URLs | local now, S3 later | assets referenced by store key, not local path |
| A5 | MediaQueue abstraction | enqueue, claim, retry, DLQ | local in-process now, SQS later | job accepted quickly and processed by worker |
| A6 | Media worker runtime | Move provider execution/composition out of web request | backend/app/workers/media_worker.py | worker can process one queued job |
| A7 | API route normalization | Popup calls job API, not provider-specific routes | backend/app/main.py + frontend proxy | POST returns job_id immediately |
| A8 | Status polling | Durable status route | backend/app/main.py | survives deploy/restart |
| A9 | AWS env config | Add env var contract for RDS/S3/SQS/Secrets | .env.example / docs | all required vars documented |
| A10 | Docker API image | Containerize backend API | Dockerfile.api | API image builds |
| A11 | Docker worker image | Containerize worker with ffmpeg | Dockerfile.worker | Worker image builds and ffmpeg available |
| A12 | AWS infra templates | ECS, SQS, S3, RDS, IAM, CloudWatch, ALB | infra/aws | deployable templates created |
| A13 | Provider secrets migration | Move keys to Secrets Manager | runtime config | no provider key in frontend/runtime logs |
| A14 | S3 asset delivery | Final media served from durable signed URLs | AssetStore/S3 | final media survives restart |
| A15 | Credit estimation | Estimate usage before enqueue | billing/credit layer | long jobs blocked/charged correctly |
| A16 | Duration-aware orchestration | Segment 30s+ media jobs | media planner/worker | long videos become multi-segment jobs |
| A17 | Human likeness workflow | Upload/use/saved avatar modes | UI + backend + asset store | consent + metadata + provider routing |
| A18 | Quality orchestration | Creative director + voice director + quality guard | worker pipeline | less robotic output, guarded continuity |
| A19 | Observability | Logs, progress events, provider diagnostics | CloudWatch + DB events | admin can diagnose every stage |
| A20 | Cutover | Move production API from Render to AWS | DNS/env/deploy | paid media path runs on AWS |

## Immediate Rule

Do not continue turning the Render runtime into the final media engine. Use Render only for temporary staging while we build the AWS-ready durable interfaces.

---

# Source-Aware AWS Option A Implementation Matrix

Updated: 2026-06-15

## Current Source Assumption Inventory

| Area inspected | Current Render/local assumption | Source evidence | AWS Option A implication |
|---|---|---|---|
| Backend API startup/config | Backend still relies on environment variables scattered across `backend/app/main.py`, frontend proxies, and docs. No single AWS Option A contract existed before AWS-01. | `backend/app/main.py`, `backend/app/config.py`, `.env.example`, `frontend/src/app/api/**/route.ts` | Add a shared AWS contract first, then wire services row by row without breaking Render/Vercel compatibility. |
| Media execution | Universal complete media still executes through backend runtime paths; an AWS-ready worker skeleton exists but is not yet the paid production executor. | `backend/app/runtime/direct_media_provider_execution_runtime.py`, `backend/app/workers/media_worker.py` | Move provider execution/composition into the worker only after queue/job/store contracts are stable. |
| Runtime outputs/local assets | Multiple media paths still write to `runtime_outputs` or local preview paths. | `backend/app/runtime/universal_media_pipeline_orchestrator.py`, `backend/app/runtime/durable_media_asset_store.py`, provider adapters | Replace local object persistence with S3-backed storage while preserving local compatibility during migration. |
| Job status persistence | Durable local JSON job/queue/asset abstractions exist, but production status still has local store overlays. | `backend/app/runtime/durable_media_job_store.py`, `backend/app/runtime/durable_media_queue.py`, `backend/app/runtime/async_media_job_foundation.py` | Swap local JSON implementations to RDS/SQS adapters behind the same interface. |
| Provider credentials | Provider readiness and adapters read process env values; frontend proxies redact known secrets. | `backend/app/runtime/*provider*`, `frontend/src/app/api/admin-real-media-generation-providers/route.ts` | Move provider/API keys to Secrets Manager, expose only readiness/diagnostics metadata. |
| Portal API routes | Frontend proxies continue to point at `BACKEND_URL`/`NEXT_PUBLIC_BACKEND_URL`, allowing Vercel frontend to stay while backend moves to AWS ALB/API. | `frontend/src/app/api/admin-universal-complete-media/route.ts`, `frontend/src/app/api/universal-complete-media/route.ts`, `frontend/src/app/api/run-agent/route.ts` | Keep frontend stable; update backend endpoint and auth contract after API service is deployed. |
| Billing/credits/package enforcement | Backend has owner/admin bypass and client credit/package gates; frontend has advisory package/credit helpers. | `backend/app/main.py`, `frontend/src/lib/packageCreditEnforcement.ts`, billing API routes | RDS-backed credit ledger and package enforcement must be migrated before paid client cutover. |
| Admin/client authority separation | Portal authority context already distinguishes unrestricted admin vs client-safe governed execution. | `backend/app/runtime/portal_authority_context.py`, `frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx` | Preserve this boundary in every AWS API/worker/status/asset route. |

## Ordered Implementation Rows

The target architecture remains the requested full-stack AWS Option A shape:
ECS/Fargate backend API service; Separate ECS/Fargate media worker service with ffmpeg;
SQS media queue and dead-letter queue; RDS PostgreSQL durable job/customer/asset/audit data;
S3 durable media/object storage; CloudWatch logs/metrics/alarms; Secrets Manager; IAM roles;
and ALB/API routing while the frontend may remain on Vercel during backend/media stabilization.

| Row id | Component | Current state | AWS target | Files likely affected | Risk | Verification command/test | Done criteria |
|---|---|---|---|---|---|---|---|
| AWS-01 | AWS environment contract/config foundation | AWS variables are documented in older docs but not codified as a runtime contract. | Shared config contract for ECS API, ECS media worker, RDS, S3, SQS, Secrets Manager, IAM, CloudWatch, with Render/Vercel compatibility defaults. | `backend/app/runtime/aws_option_a_runtime_contract.py`, `.env.example`, `AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md`, `verify_aws_option_a_runtime_contract.py` | Low | `python -X utf8 verify_aws_option_a_runtime_contract.py` | Contract defaults to local-safe disabled mode, reports missing AWS vars only when enabled, never exposes secret values, matrix/env template updated. |
| AWS-02 | Durable media job/status model adapter boundary | Completed additive durable status adapter boundary over the local/runtime status shape; existing endpoints still use current behavior. | Canonical internal durable job record plus admin-safe job status view and client-safe job status view, ready for future RDS PostgreSQL persistence without requiring AWS/RDS credentials today. | `backend/app/runtime/durable_media_job_status_adapter.py`, `verify_durable_media_job_status_adapter.py`, existing `backend/app/runtime/durable_media_job_store.py` | Medium | `python -X utf8 verify_durable_media_job_status_adapter.py`; `python -X utf8 test_durable_media_job_store.py` when store behavior changes | Adapter preserves popup payload fields, redacts secrets, keeps admin/client diagnostic separation, and leaves production behavior/local compatibility unchanged. |
| AWS-03 | Media queue adapter boundary | Completed additive media queue adapter boundary with local/no-op queue behavior; existing local file queue and worker behavior remain unchanged. | SQS-ready message envelope for media jobs now, with task/workflow markers that do not block future non-media queues for agents, billing, support, integrations, generated sites, approvals, and audit work. | `backend/app/runtime/media_queue_adapter_boundary.py`, `verify_media_queue_adapter_boundary.py`, existing `backend/app/runtime/durable_media_queue.py` | Medium | `python -X utf8 verify_media_queue_adapter_boundary.py`; `python -X utf8 test_media_worker_foundation.py` when worker/claim behavior changes | Queue message preserves popup payload fields, redacts secrets, includes approval/credit/audit placeholders, exposes future SQS/DLQ metadata, requires no AWS credentials, and does not start SQS, Stripe, portal auth, or paid provider side effects. |
| AWS-04 | Durable asset storage adapter boundary | Completed additive durable asset storage adapter boundary with local/no-op asset reference persistence; existing local asset store, upload routes, and portal output behavior remain unchanged. | S3-ready asset reference shape for media, uploads, generated sites, documents, evidence, support attachments, thumbnails/previews, captions/transcripts/audio, and future non-media agent outputs, with client/admin safe views. | `backend/app/runtime/durable_asset_storage_adapter_boundary.py`, `verify_durable_asset_storage_adapter_boundary.py`, existing `backend/app/runtime/durable_media_asset_store.py` | Medium | `python -X utf8 verify_durable_asset_storage_adapter_boundary.py`; existing asset store tests when byte persistence behavior changes | Asset references preserve local compatibility, include future S3 placeholders, redact secrets, hide local paths from clients, expose admin support detail safely, require no AWS credentials, and do not upload to S3 or change paid media execution. |
| AWS-05 | API job acceptance boundary | Completed additive accepted job envelope facade that composes durable job status, local/no-op queue acceptance, asset placeholders, and AWS runtime readiness; existing routes and direct media execution remain unchanged. | Future ECS backend API can accept complete media and broader SaaS jobs quickly, then persist to RDS/enqueue SQS/upload S3 in later cutover rows. This row provides local/no-op queue acceptance and future SaaS job acceptance markers without live side effects. | `backend/app/runtime/api_job_acceptance_boundary.py`, `verify_api_job_acceptance_boundary.py`, existing `media_job_acceptance_service.py` | High | `python -X utf8 verify_api_job_acceptance_boundary.py`; portal submit/status verifier when routes are wired | Accepted job envelope preserves popup payload fields, agent selection, approval/credit placeholders, audit correlation, admin/client safe views, and local compatibility while requiring no AWS credentials and starting no RDS, SQS, S3, Stripe, billing, portal auth, or paid provider side effects. |
| AWS-06 | ECS/Fargate media worker execution boundary | Completed additive local/no-op worker processing boundary that consumes AWS-05 accepted envelopes or AWS-03 queue messages; existing worker loops, routes, direct media execution, providers, billing, and asset persistence remain unchanged. | Future ECS/Fargate media worker can process accepted jobs through a lifecycle with provider execution, duration-aware segmentation, ffmpeg composition, asset persistence, status updates, audit evidence, billing finalization, retry, and DLQ hooks. This row provides local/no-op worker processing and future SaaS worker model markers without live side effects or final 27-agent catalogue changes. | `backend/app/runtime/ecs_media_worker_execution_boundary.py`, `verify_ecs_media_worker_execution_boundary.py`, existing `backend/app/workers/media_worker.py` | High | `python -X utf8 verify_ecs_media_worker_execution_boundary.py`; worker integration smoke only when live worker/claim behavior is intentionally wired | Worker boundary preserves queue/envelope fields, agent selection references, authority, provider preferences, duration/aspect, audit correlation, and admin/client safe views while requiring no AWS credentials and starting no worker loop, ECS/Fargate task, SQS polling, provider/API call, ffmpeg composition, asset persistence, Stripe/billing/credit finalization, or agent catalogue migration. |
| AWS-07 | ffmpeg worker image/readiness boundary | Completed additive ffmpeg worker readiness contract referenced by the local/no-op worker boundary; no Docker image build, ffmpeg composition, provider execution, AWS call, or portal behavior change. | Future ECS/Fargate worker image can require Python/backend import readiness, ffmpeg availability, writable temp/workdir contract, safe input/output mounts, no local `runtime_outputs` dependency after AWS cutover, future S3 input/output contract, CloudWatch log readiness, and safe missing-ffmpeg handling. | `backend/app/runtime/ffmpeg_worker_readiness_boundary.py`, `backend/app/runtime/ecs_media_worker_execution_boundary.py`, `verify_ffmpeg_worker_readiness_boundary.py`, future `Dockerfile.worker` | Medium | `python -X utf8 verify_ffmpeg_worker_readiness_boundary.py`; worker image build + ffmpeg version command only when container row is intentionally wired | Readiness reports missing ffmpeg safely, exposes admin diagnostics without client internals, requires no AWS credentials, starts no ECS/S3/CloudWatch/provider calls, performs no composition/media generation, and preserves future S3 input/output contract. |
| AWS-08 | RDS PostgreSQL schema/readiness boundary | Completed additive RDS PostgreSQL schema inventory/readiness contract; no database migration or connection, credential requirement, route change, local persistence change, billing mutation, provider call, or AWS call. | Future RDS schema covers full paid SaaS data: accounts/customers, users/sessions, final 27 visible agents, internal capabilities/runtime layers for folded system agents, agent tasks/jobs, media jobs, queue/worker attempts, assets/uploads/generated outputs, billing/credits/packages, Stripe event references, approvals, provider attempts, audit/evidence, support recovery, integrations, learning/memory/governance, observability/correlation, and admin/client visibility rules. | `backend/app/runtime/rds_postgres_schema_readiness_boundary.py`, `verify_rds_postgres_schema_readiness_boundary.py`, existing catalogue/runtime boundary files | High | `python -X utf8 verify_rds_postgres_schema_readiness_boundary.py`; migration dry-run only when migrations are intentionally introduced | Readiness proves full-SaaS table coverage, keeps database mode disabled by default, exposes no secrets, starts no RDS/AWS/Stripe/provider calls, models visible agents only from the final 27 `CLIENT_FACING_AGENTS`, and models the six folded `SYSTEM_AGENTS` only as internal capabilities/runtime layers. |
| AWS-09 | S3 asset delivery boundary | Completed additive S3 object reference/readiness boundary; no S3 upload or AWS call, credential requirement, route change, local file movement, provider call, media composition, billing mutation, or portal behavior change. | Future S3 delivery can map local runtime assets, uploads, provider outputs, generated media, sites, documents, evidence, and support attachments into durable bucket/key references with signed URL delivery. | `backend/app/runtime/s3_asset_delivery_boundary.py`, `verify_s3_asset_delivery_boundary.py`, existing asset storage/readiness boundary files | High | `python -X utf8 verify_s3_asset_delivery_boundary.py`; live S3 adapter and signed URL tests only when upload/delivery wiring is intentionally introduced | Readiness defines canonical S3 asset metadata, customer/job key strategy, public access default false, signed URL default true, client-safe asset delivery views, and admin-safe support/recovery views while exposing no secrets and preserving final 27 visible agent catalogue rules. |
| AWS-10 | Secrets Manager config boundary | Completed additive Secrets Manager secret/config readiness boundary; no AWS/Secrets Manager call, secret fetch, credential requirement, provider execution change, Stripe/billing change, auth/session change, frontend change, or secret rotation. | Future Secrets Manager migration covers the full paid SaaS secret/config surface: Runway, ElevenLabs, Kling, OpenAI/LLM providers, broad media capability groups for video, image, audio/voice, avatar/human presenter, lip-sync, music/SFX, caption/transcription, composition/rendering, storage/delivery, moderation/safety, fallback, pluggable media provider adapters, Stripe secrets/webhooks, RDS credentials, S3/SQS config references, auth/session/admin tokens, client portal session secrets, integrations/webhooks, observability, and future per-tenant references. | `backend/app/runtime/secrets_manager_config_boundary.py`, `verify_secrets_manager_config_boundary.py`, existing AWS runtime contract | High | `python -X utf8 verify_secrets_manager_config_boundary.py`; live Secrets Manager fetch tests only when secret retrieval wiring is intentionally introduced | Readiness exposes value_present booleans only, future Secrets Manager name placeholders, admin-safe configuration diagnostics, client-safe generic readiness, no raw values, no AWS credentials required, broad media capability groups, pluggable media provider adapters, and no change to current environment-variable behavior. |
| AWS-11 | API acceptance entitlement boundary | Completed additive API acceptance entitlement boundary metadata; no Stripe, AWS, provider, queue, or credit mutation, no RDS write, no frontend change, and no live route switch. | Future durable API acceptance can enforce credit/package/approval enforcement before paid enqueue across media jobs, generated site jobs, integration jobs, support/admin actions, and other approved-agent work while preserving admin owner authority and final 27-agent catalogue rules. | `backend/app/runtime/api_acceptance_entitlement_boundary.py`, `backend/app/runtime/api_job_acceptance_boundary.py`, `verify_api_acceptance_entitlement_boundary.py` | High | `python -X utf8 verify_api_acceptance_entitlement_boundary.py`; live credit reservation/approval tests only when billing ledger and API routes are intentionally wired | Readiness produces canonical allowed/blocked decisions with final 27-agent validation, client active entitlement checks, credit reservation placeholders, approval placeholders, dry-run/preflight/smoke no-mutation behavior, client-safe denial reasons, admin-safe diagnostics, and audit/correlation evidence. |
| AWS-12 | billing/credit ledger boundary | Completed additive billing/credit ledger boundary; no Stripe, AWS, provider, RDS, queue, or credit mutation, no customer charge/refund, no live route change, and no frontend behavior change. | Future durable accepted jobs can record reservation/finalization/refund/reversal placeholders, provider cost estimates/actuals, approval references, Stripe references, package entitlement references, admin overrides, and billing audit evidence across media jobs, generated site jobs, integration jobs, support/admin actions, and approved 27-agent execution jobs. | `backend/app/runtime/billing_credit_ledger_boundary.py`, `verify_billing_credit_ledger_boundary.py`, existing AWS-11 enforcement and AWS-05 acceptance boundaries | High | `python -X utf8 verify_billing_credit_ledger_boundary.py`; live Stripe/credit ledger tests only when billing persistence and route enforcement are intentionally wired | Readiness proves reservation/finalization/refund/reversal placeholders, no-mutation dry-run/preflight/smoke evidence, final 27-agent validation, admin override audit-only behavior, client-safe billing summaries, admin-safe billing diagnostics, and no Stripe, AWS, provider, RDS, queue, or credit mutation. |
| AWS-13 | RDS repository persistence boundary | Completed additive RDS repository persistence boundary; no database connection, migration, credential requirement, or write, no AWS/Stripe/provider call, no queue mutation, no credit mutation, no live route switch, and no frontend behavior change. | Future repository interface can persist accepted jobs/tasks, media job status, generated site/output jobs, assets/uploads/S3 references, queue messages, worker attempts, provider attempts, billing ledger entries, Stripe references, approvals, audit/evidence, support/admin recovery actions, integrations, learning/memory/governance, observability/correlation IDs, final approved 27 visible agents, and internal runtime layers. | `backend/app/runtime/rds_repository_persistence_boundary.py`, `verify_rds_repository_persistence_boundary.py`, existing schema, acceptance, asset, queue, worker, and billing boundary modules | High | `python -X utf8 verify_rds_repository_persistence_boundary.py`; live repository tests only when migrations and RDS adapter wiring are intentionally introduced | Readiness proves full SaaS repository interface coverage, accepted-envelope and billing-ledger consumption, asset/S3/queue/worker/provider plan support, final 27-agent validation, client-safe persistence status, admin-safe diagnostics, and no DB/AWS/Stripe/provider/credit mutation. |
| AWS-14 | AWS live adapter scaffolding | Completed compressed live adapter scaffolding for RDS migration/repository writes, SQS/DLQ sends, S3 uploads/signed delivery, and Secrets Manager retrieval; disabled by default with service-specific enable flags and no DB/RDS/SQS/S3/Secrets Manager/AWS calls, no credentials required, no route switch, no frontend change, no billing/credit/provider mutation, and no SDK/network execution. | Future AWS-14 through AWS-20 cutover work can wire these scaffolds into real adapters after explicit owner approval, migrations, IAM policy review, route cutover plans, and live integration tests. | `backend/app/runtime/aws_live_adapter_scaffolding.py`, `verify_aws_live_adapter_scaffolding.py`, existing RDS/SQS/S3/Secrets boundaries | High | `python -X utf8 verify_aws_live_adapter_scaffolding.py`; live AWS adapter tests only when the owner explicitly approves AWS spend and live service calls | Readiness proves adapters remain disabled by default, require `AWS_OPTION_A_ENABLED=true` plus service-specific enable flags, expose admin-safe readiness and client-safe generic status, preserve final 27-agent rules and broad media provider classes, and perform no database connection, migration, SQS send, S3 upload, Secrets Manager fetch, AWS call, provider call, or credit mutation. |
| AWS-15 | Controlled AWS validation and API/status cutover readiness | AWS-15A controlled AWS environment validation is complete, AWS-15C local env loading is redacted, AWS-15E adds API/status route cutover boundary decision plumbing, AWS-16 wires backend acceptance/status route integration behind explicit flags, AWS-17 prepares durable repository/queue adapters in dry-run mode behind those same route gates, AWS-18 adds a rollback and kill-switch control boundary, AWS-19 adds an observability and incident diagnostics boundary, and AWS-20 adds a controlled live AWS integration rehearsal boundary. Live AWS route behavior remains disabled unless `AWS_OPTION_A_ENABLED`, `AWS_OPTION_A_ROUTE_CUTOVER_ENABLED`, and the operation-specific `AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED` or `AWS_OPTION_A_STATUS_CUTOVER_ENABLED` flag are enabled with IAM/RDS/SQS/S3/Secrets validation evidence; route mode alone still does not write RDS or send SQS, rollback controls can force compatibility fallback before durable repository and queue packets are prepared, observability only prepares sanitized diagnostics, and AWS-20 rehearsal requires explicit rehearsal enabled + owner approved + per-resource rehearsal flags. | Remaining route work was compressed into AWS-17 through AWS-20; AWS-17 durable repository/queue adapters are now dry-run prepared, AWS-18 rollback controls are implemented/tested, AWS-19 observability is implemented/tested, AWS-20 safe default verifier passes, and live rehearsal pending owner-approved mode. | `live_validate_aws_option_a_environment.py`, `verify_live_aws_option_a_environment_validation.py`, `backend/app/runtime/aws_option_a_route_cutover_boundary.py`, `verify_aws_option_a_route_cutover_boundary.py`, `backend/app/runtime/aws_option_a_route_integration.py`, `backend/app/runtime/aws_option_a_rollback_controls.py`, `backend/app/runtime/aws_option_a_observability.py`, `backend/app/runtime/aws_option_a_live_rehearsal.py`, `verify_aws_option_a_route_integration.py`, `verify_aws_option_a_durable_enqueue_dry_run.py`, `verify_aws_option_a_rollback_controls.py`, `verify_aws_option_a_observability.py`, `verify_aws_option_a_live_rehearsal.py`, `backend/app/main.py` | High | `python -X utf8 live_validate_aws_option_a_environment.py`; `python -X utf8 verify_live_aws_option_a_environment_validation.py`; `python -X utf8 verify_aws_option_a_route_cutover_boundary.py`; `python -X utf8 verify_aws_option_a_route_integration.py`; `python -X utf8 verify_aws_option_a_durable_enqueue_dry_run.py`; `python -X utf8 verify_aws_option_a_rollback_controls.py`; `python -X utf8 verify_aws_option_a_observability.py`; `python -X utf8 verify_aws_option_a_live_rehearsal.py`; owner-approved live rehearsal only with `AWS_OPTION_A_LIVE_REHEARSAL_ENABLED=true`, `AWS_OPTION_A_LIVE_REHEARSAL_OWNER_APPROVED=true`, and service-specific rehearsal resource flags | AWS-15/AWS-16/AWS-17/AWS-18/AWS-19/AWS-20 now prove controlled validation has default no-live/no-network behavior, uses service-specific live validation flags, local env loading is redacted, backend route integration defaults to `compatibility_runtime_path`, existing route output remains unchanged unless diagnostics or AWS cutover intent are explicit, AWS cutover cannot activate from `AWS_OPTION_A_ENABLED` alone, acceptance/status cutovers are independently gated, validation evidence is required, durable repository and queue packets are prepared only when the route is ready and rollback controls are clear, kill switch and force-fallback controls block durable write/send planning, observability prepares admin-safe diagnostic snapshots/client-safe support summaries/internal incident events without external logging, AWS-20 safe default mode blocks rehearsal unless owner-approved resource flags are present, live rehearsal artifacts are synthetic/non-customer/non-executable, missing validation short-circuits before write/send preparation, admin/client views are separated, final 27-agent rules are preserved, and no provider/Stripe/billing/credit/media-worker mutation occurs. |

## AWS-01 Row 1 Scope

AWS-01 is intentionally a compatibility layer only. It does not:
- rip out Render
- change portal routes
- move frontend hosting
- enable paid provider calls
- switch storage/queue/database implementations

It does:
- define the required AWS Option A environment variables
- keep `AWS_OPTION_A_ENABLED=false` as the default
- report missing RDS/S3/SQS/Secrets values only when AWS mode is enabled
- preserve admin/client authority and self-contained Create Media popup guardrail markers
- provide `verify_aws_option_a_runtime_contract.py` as the first AWS migration verifier

## AWS-01 Environment Contract

| Variable | Purpose | Required when `AWS_OPTION_A_ENABLED=true` | Secret value? |
|---|---|---:|---:|
| `AWS_OPTION_A_ENABLED` | Explicit migration switch; defaults off for Render/Vercel compatibility. | Yes | No |
| `APP_ENV` | Runtime environment label. | Recommended | No |
| `AWS_REGION` | Region for ECS, SQS, S3, RDS, Secrets Manager, CloudWatch. | Yes | No |
| `AWS_BACKEND_SERVICE_MODE` | Service mode marker such as `local_dev` or `aws_option_a`. | Recommended | No |
| `AWS_MEDIA_WORKER_ENABLED` | Identifies the media worker process when enabled. | Recommended | No |
| `DATABASE_URL` | RDS PostgreSQL connection URL, or use `AWS_RDS_SECRET_ARN`. | One of this or RDS secret ARN | Yes |
| `AWS_RDS_SECRET_ARN` | Secrets Manager reference for RDS credentials. | One of this or database URL | No value, ARN only |
| `AWS_MEDIA_S3_BUCKET` | Durable generated media/object storage bucket. | Yes | No |
| `AWS_UPLOADS_S3_BUCKET` | Durable client upload/reference/likeness bucket. | Recommended | No |
| `AWS_MEDIA_QUEUE_URL` | SQS media queue URL. | Yes | No |
| `AWS_MEDIA_DLQ_URL` | SQS media dead-letter queue URL. | Yes | No |
| `AWS_PROVIDER_SECRETS_PREFIX` | Secrets Manager prefix for provider/API keys. | Yes | No value, prefix only |
| `AWS_CLOUDWATCH_LOG_GROUP` | CloudWatch log group for API/worker observability. | Recommended before cutover | No |
| `AWS_API_TASK_ROLE_ARN` | IAM task role for ECS backend API. | Recommended before deploy | No |
| `AWS_WORKER_TASK_ROLE_ARN` | IAM task role for ECS media worker. | Recommended before deploy | No |

---

# Full-Stack AWS Option A Scope Addendum

Updated: 2026-06-13T03:11:16

## Correction

AWS Option A migration is not media-only. The production migration must cover the full paid-client platform stack and both portals.

## Full Stack Areas Covered

| Stack area | AWS migration requirement |
|---|---|
| Admin portal | Preserve unrestricted owner/admin authority, full diagnostics, provider details, infrastructure visibility, job controls, retries, refunds, credit assignment, and full audit visibility. |
| Client portal | Preserve client-safe status, package/credit governance, approvals, privacy-safe outputs, usable assets, billing visibility, and support flows. |
| Media generation | Move paid-client media execution to durable API + queue + worker + object storage. |
| Agent execution | Route execution through durable job records, provider events, audit logs, and portal-safe status views. |
| Billing and credits | Durable credit ledger, package enforcement, usage estimates, provider-cost tracking, refunds, and admin credit assignment. |
| Package enforcement | Client entitlement checks before paid execution; admin owner bypass preserved. |
| Approvals | Owner approval controls for governed spend/actions; client request visibility without internal leakage. |
| Provider execution | Provider adapters run server-side only; provider secrets are never exposed to frontend or client views. |
| Creative assets | Durable asset storage with S3-backed delivery and portal-safe metadata. |
| Client uploads | Durable uploads, privacy-safe handling, uploaded likeness consent, and access control. |
| Generated sites | Durable generated-site records/assets and deployment evidence. |
| Integrations | Durable integration connection state, health checks, and client-safe connection status. |
| Execution evidence | Store outputs, provider events, timestamps, screenshots/files when relevant, and audit history. |
| Learning/memory/governance | Preserve governed learning, memory rules, admin visibility, and client-safe boundaries. |
| Security/session handling | Portal-specific authentication, authorization, session hardening, and no secret leakage. |
| Observability | CloudWatch logs, metrics, incident readiness, dead-letter queue visibility, and admin-only diagnostics. |
| Support flows | Client support requests and admin handling must remain functional after migration. |

## Portal Authority Model

| Capability | Admin / owner portal | Client portal |
|---|---|---|
| Execute jobs | Unrestricted owner execution | Governed by package, credits, approvals |
| View provider diagnostics | Full visibility | Hidden |
| View provider secrets/config | Never raw secrets, but admin diagnostics allowed | Hidden |
| Retry/requeue/cancel jobs | Allowed | Limited/client-safe request flow only |
| Assign credits | Allowed | Not allowed |
| Spend approvals | Owner/admin controls | Request/status only |
| Refunds | Admin controls | Request/status only |
| Uploaded likeness | Full admin audit visibility | Consent-based client control |
| Assets | Full asset visibility | Own/client-safe assets only |
| Infrastructure status | Full | Hidden or simplified status only |
| Audit logs | Full | Own/client-safe history only |

## Non-Negotiable Migration Rule

Do not migrate media in isolation in a way that breaks or ignores the wider stack.

Every AWS-backed production service must preserve:
- admin/client authority separation
- package and credit enforcement
- owner/admin unrestricted operations
- provider secret protection
- durable job/status/asset records
- auditability
- client-safe output visibility

