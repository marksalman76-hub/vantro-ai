from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
BACKUP = ROOT / "backups" / f"production_scaling_foundation_docs_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

RUNBOOK = """# Production Scaling Foundation Runbook

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
"""

SCALING_PLAN = """# Production Scaling Implementation Plan

## Stage 1 — Config foundation

- Add render.yaml or equivalent deployment manifest.
- Add explicit start command.
- Add WEB_CONCURRENCY.
- Keep current backend entrypoint unchanged until verified.

## Stage 2 — Rate shaping

- Add per-route rate limits.
- Protect health/readiness routes separately.
- Add admin bypass only where owner/admin authenticated.
- Log throttled requests safely.

## Stage 3 — Queue isolation

- Add Redis broker.
- Move long-running provider and external actions to worker process.
- Keep request/response routes fast.
- Persist job status in Postgres.

## Stage 4 — Worker scaling

- Add dedicated worker process.
- Add retry worker.
- Add reconciliation worker.
- Add queue depth monitoring.

## Stage 5 — Production validation

- Run paced k6 tests.
- Validate p95 latency.
- Validate failure rate under realistic concurrency.
- Validate no governance bypass.
- Validate no secret exposure.
"""

def write(path: Path, content: str):
    if path.exists():
        BACKUP.mkdir(parents=True, exist_ok=True)
        (BACKUP / path.name).write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def main():
    write(DOCS / "production-scaling-foundation-runbook.md", RUNBOOK)
    write(DOCS / "production-scaling-implementation-plan.md", SCALING_PLAN)

    print("PRODUCTION_SCALING_FOUNDATION_DOCS_INSTALLED")
    print("Backup folder:", BACKUP)
    print("Created/updated:")
    print("-", DOCS / "production-scaling-foundation-runbook.md")
    print("-", DOCS / "production-scaling-implementation-plan.md")

if __name__ == "__main__":
    main()