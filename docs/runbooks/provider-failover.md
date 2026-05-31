# Provider Failover Runbook

## Trigger
Provider latency, failure rate, timeout, quota issue, or degraded generation quality.

## Response
1. Mark provider degraded.
2. Route eligible jobs to fallback provider.
3. Keep owner approval required for live external actions.
4. Preserve audit trail.
5. Notify owner before spend-impacting changes.
