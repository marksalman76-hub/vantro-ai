# Vantro Session Report - Creative Routing Completion, Environment Stabilization, and Scale Readiness

Date: 2026-06-30  
Repository: `marksalman76-hub/vantro-ai`  
Continuation of: `docs/session-reports/2026-06-30-vantro-admin-media-routing-session-report.md`  
Latest GitHub commits covered:

- `146e4d16 Add creative agent provider entitlements`
- `ad9e89f5 Fix admin creative media routing`
- `565d9fdd Prepare agent worker for safe scaling`
- `c87dd5ce Add reusable AWS scaling policy files`

## Executive Summary

This follow-up report records the work completed after the prior session report. The focus moved from basic admin/Create Media recovery into three larger themes:

1. Locking creative-provider entitlement routing so each creative agent can only access the Higgsfield/Nano Banana model tier it is allowed to use.
2. Stabilizing the local Python/tooling environment so tests run from the correct project virtual environment instead of drifting into another project or Python launcher.
3. Preparing the live AWS worker/API deployment for safe horizontal scaling, including atomic worker job claiming, Docker image rebuilds, ECS redeploys, and live autoscaling targets.

The most important production outcome is that Vantro is no longer running as only one API task and one worker task. The live API is now configured with ECS autoscaling min `2`, max `20`; the live worker is configured with ECS autoscaling min `2`, max `50`, and the worker service autoscaled up to `10` running tasks during verification.

This is meaningful scale readiness, but it is not yet "thousands of simultaneous tasks." The platform now has safer horizontal worker scaling, but true launch-grade high-volume execution still requires queue-depth autoscaling, DB pool sizing, RDS capacity increase, provider rate-limit contracts, and load testing.

## Creative Provider Entitlement Routing

After the prior report, the creative routing work was tightened so that creative agents do not all receive the same provider/model permissions.

The user clarified the business requirement:

- Vantro will sell creative agents both as a team and separately.
- Lower-tier creative agents should only access lower-tier video/image software.
- Premium creative agents should be allowed to access premium Higgsfield/Nano Banana capabilities.

Implemented routing model:

- Video `720p` routes to Higgsfield `Kling 3.0 Turbo`.
- Video `1080p` routes to Higgsfield `Kling 3.0`.
- Video `4K` routes to Higgsfield `Cinema Studio 4K`.
- Standard/product image routes to `Nano Banana 2`.
- Premium/pro image routes to `Nano Banana Pro`.

Important design correction:

- The initial Create Media flow still treated media generation as "run `ugc_media_agent`."
- That was wrong for premium 4K work because `ugc_media_agent` is a lower-tier executable identity.
- The clean model became: Create Media selects the right creative identity, while the backend can still normalize execution to an underlying catalog agent where needed.

Result:

- Creative agents now resolve through a canonical routing layer.
- Agent capability limits can be enforced separately from the generic execution path.
- The system can sell agents separately without every creative agent receiving blanket access to all provider models.

## Create Media 4K Failure Root Cause

The browser continued showing failures from `admin.vantro.ai/admin/create-media`, including:

- `500` responses from `/api/admin/agents/ugc_media_agent/run`
- later `400` responses from `/api/admin-run-agent`
- console messages like `Agent submission failed`

Root cause:

- Admin Create Media was still sending premium requests through `ugc_media_agent`.
- The entitlement layer correctly blocked `ugc_media_agent` from premium `Cinema Studio 4K`.
- `ugc_creative_agent` was a premium creative identity, but the backend normalized it to the executable `ugc_media_agent` too early.
- Because entitlement resolution used the normalized ID, the premium identity was lost before model selection.

Fix:

- The admin Create Media frontend now selects the creative agent identity based on media type and quality.
- 4K video requests use `ugc_creative_agent`.
- Image requests use `product_image_agent`.
- Lower-tier video requests can still use `ugc_media_agent`.
- Backend admin and agent routes preserve the requested creative identity for entitlement routing while still allowing execution to normalize internally.

Files changed:

- `frontend/app/admin/create-media/page.tsx`
- `backend/app/routes/admin.py`
- `backend/app/routes/agents.py`
- `backend/tests/test_admin_run_agent.py`
- `backend/tests/test_creative_provider_routing.py`

Verification:

- Creative routing tests passed.
- Admin route regression tests passed.
- The regression test proves a 4K request sent to `ugc_creative_agent` resolves to Higgsfield `Cinema Studio 4K` while still executing through the normalized catalog agent.

Commit:

- `ad9e89f5 Fix admin creative media routing`

## Python and Virtual Environment Stabilization

The session exposed why local Python appeared to "forget" installed packages.

Observed issue:

- `py -m pytest` used Python `3.14` from:
  - `C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\python.exe`
- That Python did not have `pytest`.
- `python -m pytest` sometimes used a stale virtual environment inherited from another local project session.
- The actual repo virtual environment was:
  - `C:\Users\User\OneDrive\Desktop\ecommerce-ai-agent-platform\.venv`

Important discovery:

- The system was not literally forgetting installed programs.
- Different terminals, launchers, PATHs, and virtual environments were resolving different Python installations and package sets.
- Installing packages into the wrong interpreter made it look like packages were missing even after installation.

Correct operating model:

- Install global Python 3.11 once as the base interpreter.
- Keep this repo isolated through `.venv`.
- Run tests through the active project venv:
  - `.\.venv\Scripts\Activate.ps1`
  - `python -m pytest ...`
- Avoid plain `py -m pytest` unless explicitly targeting Python 3.11:
  - `py -3.11 -m pytest ...`

Packages installed or corrected in the project venv:

- `sqlalchemy`
- `slowapi`
- `passlib`
- `bcrypt`
- `python-jose`
- `boto3`
- `psycopg2`
- `PyJWT`
- `python-multipart`

Dependency drift fixed:

- Root `requirements.txt` had loose auth dependencies.
- `bcrypt 5.0.0` broke compatibility with `passlib 1.7.4`.
- The root requirements were pinned to match the backend container behavior:
  - `passlib[bcrypt]==1.7.4`
  - `bcrypt==3.2.2`

Utility scripts added:

- `tools/doctor.ps1`
- `tools/test-creative-routing.ps1`

Purpose:

- Make future environment problems visible quickly.
- Give a standard one-command path for creative-routing regression tests.
- Stop switching between unrelated project virtual environments.

## Test Verification After Environment Repair

After the correct `.venv` was active and the missing dependencies were installed, backend tests ran successfully.

Important successful test runs:

- `python -m pytest backend\tests\test_creative_provider_routing.py -q`
  - `53 passed`
- Focused backend suite after admin routing fix:
  - `backend/tests/test_admin_run_agent.py`
  - `backend/tests/test_creative_provider_routing.py`
  - passed
- Worker scaling safety suite after later changes:
  - `backend/tests/test_agent_worker_scaling.py`
  - passed
- Combined focused suite:
  - `backend/tests/test_agent_worker_scaling.py`
  - `backend/tests/test_admin_run_agent.py`
  - `backend/tests/test_creative_provider_routing.py`
  - `59 passed`

Known warnings:

- Starlette `TestClient` deprecation warning.
- SQLAlchemy drop-table warning in SQLite tests due to cyclic foreign keys.

These warnings did not block test success.

## GitHub, Vercel, Docker, and AWS Sync

The deployment stack was re-synced multiple times after fixes.

GitHub:

- Changes were committed and pushed to `main`.
- Key commits:
  - `146e4d16 Add creative agent provider entitlements`
  - `ad9e89f5 Fix admin creative media routing`
  - `565d9fdd Prepare agent worker for safe scaling`
  - `c87dd5ce Add reusable AWS scaling policy files`

Vercel:

- Vercel CLI was used through:
  - `C:\Users\User\AppData\Roaming\npm\vercel.cmd`
- Vercel production deployments were checked after pushes.
- Final observed Vercel production deployment:
  - State: `READY`
  - Commit: `c87dd5ce34cb6983b6fa68dfaf7e9db5ecbcbb6c`
  - Message: `Add reusable AWS scaling policy files`

Docker/ECR:

- API and worker images were built and pushed to the Vantro production ECR repositories.

AWS ECS:

- API and worker services were force redeployed.
- ECS reached stable state after each deployment.
- Live API health endpoint returned:
  - `{"status":"healthy","service":"vantro-api","version":"1.0.0"}`

## Worker Scaling Safety

Before increasing worker count, a key safety issue was identified.

Original worker behavior:

- Each worker polled the database for jobs with status `pending` or `approved`.
- The worker then loaded a job and changed its status to `running`.
- With multiple workers, two workers could theoretically select the same pending job before either committed the status change.

Risk:

- Simply increasing ECS worker count could duplicate job execution.
- Duplicate execution could waste credits, create duplicate provider calls, and confuse users.

Fix:

- Added `_claim_job_for_execution(db, job_id)`.
- The claim step atomically updates a job from `pending` or `approved` to `running`.
- If the update count is not exactly one, the worker skips the job.
- This prevents multiple workers from claiming the same job.

Tests added:

- `test_agent_worker_claim_is_atomic_for_parallel_workers`
- `test_agent_worker_claim_supports_approved_jobs`
- `test_positive_int_env_uses_default_for_invalid_values`
- `test_positive_int_env_reads_positive_values`

File added:

- `backend/tests/test_agent_worker_scaling.py`

File changed:

- `backend/app/agents/agent_worker.py`

Commit:

- `565d9fdd Prepare agent worker for safe scaling`

## Worker Runtime Tunability

The worker's hardcoded concurrency settings were made configurable.

Before:

- `POLL_INTERVAL_SECONDS = 5`
- `MAX_CONCURRENT_JOBS = 3`

After:

- `POLL_INTERVAL_SECONDS = _positive_int_env("AGENT_WORKER_POLL_INTERVAL_SECONDS", 5)`
- `MAX_CONCURRENT_JOBS = _positive_int_env("AGENT_WORKER_MAX_CONCURRENT_JOBS", 3)`

Why this matters:

- Per-worker concurrency can be tuned without changing application code.
- ECS task count and per-task job concurrency can be managed separately.
- This is necessary for controlled load testing and launch tuning.

Current implication:

- If worker concurrency remains at default `3`, then:
  - `10` worker tasks means roughly `30` parallel agent executions.
  - `50` worker tasks means roughly `150` parallel agent executions.

This is safer than immediately trying to run thousands of concurrent jobs without database, provider, and quota planning.

## Live AWS Autoscaling Changes

After the atomic job-claim fix was verified and deployed, live AWS scaling was configured.

API service:

- ECS service: Vantro production API service
- Autoscaling target:
  - min capacity: `2`
  - max capacity: `20`
- Existing CPU target-tracking policy:
  - `vantro-cpu-scaling`
  - target: `70%`

Worker service:

- ECS service: `vantro-worker`
- Autoscaling target:
  - min capacity: `2`
  - max capacity: `50`
- New CPU target-tracking policy:
  - `vantro-worker-cpu-60`
  - target: `60%`

Reusable policy files added:

- `tools/aws-scaling-policy-api-cpu.json`
- `tools/aws-scaling-policy-worker-cpu.json`

Commit:

- `c87dd5ce Add reusable AWS scaling policy files`

Final observed live AWS state:

- API:
  - desired: `2`
  - running: `2`
  - pending: `0`
  - rollout: `COMPLETED`
- Worker:
  - desired: `10`
  - running: `10`
  - pending: `0`
  - rollout: `COMPLETED`

Important note:

- The worker autoscaling policy reacted and raised the worker service above the requested minimum.
- This proves autoscaling is active, but it also means cost and provider usage should be watched closely.

## Current Scaling Reality

Current state is much stronger than before:

- The API is redundant at two tasks.
- The worker service is horizontally scalable.
- The worker claim path is safe for multiple ECS tasks.
- The live worker service has already autoscaled to `10` tasks.

However, Vantro is not yet configured for thousands of simultaneous tasks.

Why:

- Worker max is currently `50` tasks.
- Default per-worker concurrency is `3`.
- This implies a rough maximum of `150` parallel agent executions before tuning.
- Database capacity, connection pooling, provider rate limits, queue design, and cost ceilings have not yet been load-tested for thousands.

Conclusion:

- Vantro is now scale-ready for controlled growth.
- Vantro is not yet launch-certified for massive burst traffic.
- The next step is not blindly raising max capacity; the next step is measured launch-readiness validation.

## Standing Launch-Readiness Reminder

Before final public launch, remind the owner and engineering team that the following must be completed:

1. Queue-depth autoscaling.
2. DB pool sizing.
3. RDS capacity increase.
4. Provider rate-limit contracts.
5. Load testing.

This is now a standing pre-launch gate. Do not mark Vantro fully launch-ready until these items are addressed, verified, and documented.

## Why This Was Difficult

Several separate systems were failing or drifting at the same time:

- Frontend admin routing and backend admin routing were not identical.
- Creative provider identity was being normalized too early.
- Higgsfield routing selection worked conceptually, but provider execution depends on backend credentials and production worker behavior.
- Python commands were resolving different interpreters and virtual environments.
- Live AWS service names did not perfectly match older Terraform naming defaults.
- Existing scaling configuration existed in the repo, but live production was only running one API task and one worker task before this follow-up work.

The hard part was not one bug. It was system alignment:

- correct creative agent identity
- correct provider entitlement
- correct backend execution route
- correct Python environment
- correct Docker images
- correct Vercel deployment
- correct ECS rollout
- correct autoscaling target
- safe multi-worker job claiming

## Locked-In Current State

As of this report:

- GitHub main is updated through `c87dd5ce`.
- Vercel production is `READY` on `c87dd5ce`.
- Docker/ECR has scaling-safe API and worker images from `565d9fd`.
- AWS ECS API is healthy and running two tasks.
- AWS ECS worker is healthy and running ten tasks after autoscaling.
- API health endpoint is healthy.
- Creative routing tests pass.
- Admin run/creative routing tests pass.
- Worker scaling safety tests pass.

Remaining local uncommitted files at the time of this report were unrelated:

- `.superpowers/sdd/*` review/task artifacts
- `frontend/tsconfig.tsbuildinfo`

They were intentionally not included in the production commits.
