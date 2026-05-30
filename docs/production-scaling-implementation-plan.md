# Production Scaling Implementation Plan

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
