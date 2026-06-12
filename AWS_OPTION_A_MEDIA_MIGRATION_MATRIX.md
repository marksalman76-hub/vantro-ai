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

