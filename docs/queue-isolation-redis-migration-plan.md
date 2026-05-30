# Queue Isolation + Redis Migration Plan

## Purpose

Separate fast web/API requests from long-running provider, integration, retry, reporting, and reconciliation workloads.

## Current foundation

This foundation is policy-only. It does not connect to Redis and does not change live runtime behaviour.

## Target queues

- client_agent_execution_queue
- provider_generation_queue
- external_integration_action_queue
- reporting_queue
- retry_reconciliation_queue
- admin_internal_queue

## Safety rules

- Provider generation remains owner-approved.
- Live external calls remain disabled by default.
- CRM/email/calendar/store actions require governance before live execution.
- Client entitlement checks must remain before queue admission.
- Owner/admin bypass applies only to client/package limits, not audit or high-risk governance.

## Redis migration stages

1. Add managed Redis connection settings.
2. Add queue adapter abstraction.
3. Keep in-memory/local queue as fallback for development.
4. Add Redis-backed enqueue/dequeue implementation.
5. Add dedicated worker process.
6. Add retry and dead-letter handling.
7. Add queue depth and worker health telemetry.
8. Add admin visibility before scaling live workload volume.

## Do not activate automatically

Do not enable live external provider calls, budgeted actions, autonomous scaling, or spending based only on queue installation.
