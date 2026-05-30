# Production Scaling Foundation Runbook

## Current finding

The platform runtime is stable, but infrastructure scaling config is incomplete.

## Confirmed gaps

- No render.yaml
- No Dockerfile
- No Procfile
- No explicit production worker count
- No Redis/distributed broker configured
- No controlled rate shaping layer confirmed

## Required production scaling direction

1. Add explicit production process command.
2. Configure multi-worker backend execution.
3. Add Redis-backed distributed queue before high-volume live workloads.
4. Separate web request handling from provider execution workers.
5. Add controlled rate shaping before relying on edge rejection.
6. Keep owner governance, entitlement isolation, audit logging, and customer-safe delivery intact.

## Safe production process target

Preferred hosted process model:

- Web process: FastAPI app serving API routes.
- Worker process: queue/background execution.
- Scheduler process: retry and reconciliation loop.
- Optional admin process: monitoring and internal controls.

## Recommended environment variables

WEB_CONCURRENCY=2
WORKER_CONCURRENCY=2
QUEUE_BACKEND=redis
REDIS_URL=<managed redis url>
DATABASE_URL=<managed postgres url>
LIVE_EXTERNAL_CALLS_ENABLED=false unless owner-approved
OWNER_APPROVAL_REQUIRED=true

## Do not enable automatically

Do not automatically enable live external execution, provider spending, autonomous scaling, or client entitlement bypass.

## Completion criteria

- Production worker strategy documented.
- Queue migration path documented.
- Rate shaping path documented.
- No production behaviour changed by this docs-only foundation.
