# Vantro.ai — Production Monitoring & Metrics Runbook

**Version:** 1.0  
**Last updated:** 2026-06-27  
**Owner:** Mark Salman (mark.salman76@gmail.com)

---

## 1. Overview

This document defines the Service Level Objectives (SLOs), Key Performance Indicators (KPIs), CloudWatch metric names, alert thresholds, baseline capture procedure, and first-72h monitoring runbook for the Vantro.ai production environment.

**Audience:** On-call engineers and ops team members responsible for maintaining platform health during and after launch.

**Scope:** Covers the full stack — FastAPI backend (ECS/Fargate), PostgreSQL (RDS), SQS job queues, and the 27-agent AI workforce. Does not cover frontend CDN health (handled separately via Vercel dashboards).

**Do not share this document externally.** It contains internal metric names, alert thresholds, and escalation paths. All references to AI/LLM infrastructure use generic terminology per the platform's provider-opacity policy.

---

## 2. Availability SLO

### 2.1 Targets

| SLO | Target | Measurement Window |
|-----|--------|--------------------|
| Uptime | 99.5% | Rolling 30-day calendar month |
| HTTP 5xx error rate | < 0.1% of all responses | Rolling 1-hour window |
| P95 API latency | < 500ms | Per-endpoint, rolling 5-minute window |

### 2.2 Error Budget

At 99.5% uptime over a 30-day month:

- Total minutes in month: `30 × 24 × 60 = 43,200 minutes`
- Allowed downtime: `43,200 × 0.005 = 216 minutes` (~3h 36m per month)
- Error budget burn rate: if a 30-minute outage occurs, that consumes **13.9%** of the monthly budget

**Error budget tracking formula:**
```
budget_remaining_minutes = 216 - SUM(actual_downtime_minutes_this_month)
burn_rate = actual_downtime_last_hour / (216 / 720)
```

A burn rate > 1.0 means the budget is being consumed faster than it accrues. Alert if burn rate > 2.0 for 30 minutes.

### 2.3 Measurement Source

- **Uptime / 5xx rate:** CloudWatch → Application Load Balancer → `HTTPCode_ELB_5XX_Count` / `RequestCount`
- **P95 latency:** CloudWatch → ALB → `TargetResponseTime` with `p95` statistic
- **Alarm evaluation:** 1-minute periods, 5 consecutive datapoints to trigger (reduces noise)

### 2.4 SLO Dashboard

Create a CloudWatch Dashboard named `Vantro-SLO-Dashboard` with these widgets:

1. **Uptime %** — calculated metric: `(1 - (5xxCount / RequestCount)) × 100`
2. **Error rate %** — `5xxCount / RequestCount × 100` (threshold line at 0.1%)
3. **P95 Latency** — `TargetResponseTime p95` (threshold line at 500ms)
4. **Error budget remaining** — calculated from cumulative downtime this month

---

## 3. Growth KPIs

All queries run against the primary RDS instance (read-replica preferred for dashboards). Use UTC timestamps throughout.

### 3.1 Signups Per Hour

Tracks new organization registrations as a proxy for top-of-funnel growth.

```sql
-- Signups per hour (last 24 hours)
SELECT
    DATE_TRUNC('hour', created_at) AS hour_bucket,
    COUNT(*) AS new_organizations
FROM organizations
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY 1
ORDER BY 1 DESC;
```

```sql
-- Signups per hour with subscription tier breakdown (last 24 hours)
SELECT
    DATE_TRUNC('hour', o.created_at) AS hour_bucket,
    o.subscription_tier,
    COUNT(*) AS new_organizations
FROM organizations o
WHERE o.created_at >= NOW() - INTERVAL '24 hours'
GROUP BY 1, 2
ORDER BY 1 DESC, 2;
```

### 3.2 Activation Rate

A workspace is "activated" if it has run at least one agent job. This is the single most important product health metric at launch.

```sql
-- Overall activation rate (all time)
SELECT
    COUNT(DISTINCT w.id) AS total_workspaces,
    COUNT(DISTINCT aj.workspace_id) AS activated_workspaces,
    ROUND(
        COUNT(DISTINCT aj.workspace_id)::NUMERIC / NULLIF(COUNT(DISTINCT w.id), 0) * 100,
        2
    ) AS activation_rate_pct
FROM workspaces w
LEFT JOIN agent_jobs aj ON aj.workspace_id = w.id;
```

```sql
-- Activation rate by subscription tier (cohort view)
SELECT
    o.subscription_tier,
    COUNT(DISTINCT w.id) AS total_workspaces,
    COUNT(DISTINCT aj.workspace_id) AS activated_workspaces,
    ROUND(
        COUNT(DISTINCT aj.workspace_id)::NUMERIC / NULLIF(COUNT(DISTINCT w.id), 0) * 100,
        2
    ) AS activation_rate_pct
FROM workspaces w
JOIN organizations o ON o.id = w.organization_id
LEFT JOIN agent_jobs aj ON aj.workspace_id = w.id
GROUP BY o.subscription_tier
ORDER BY activation_rate_pct DESC;
```

```sql
-- New-cohort activation rate: workspaces created in last 7 days
SELECT
    COUNT(DISTINCT w.id) AS new_workspaces_7d,
    COUNT(DISTINCT aj.workspace_id) AS activated_from_new_cohort,
    ROUND(
        COUNT(DISTINCT aj.workspace_id)::NUMERIC / NULLIF(COUNT(DISTINCT w.id), 0) * 100,
        2
    ) AS activation_rate_pct
FROM workspaces w
LEFT JOIN agent_jobs aj ON aj.workspace_id = w.id
WHERE w.id IN (
    SELECT id FROM workspaces WHERE id IN (
        SELECT w2.id FROM workspaces w2
        JOIN organizations o2 ON o2.id = w2.organization_id
        WHERE o2.created_at >= NOW() - INTERVAL '7 days'
    )
);
```

### 3.3 Weekly Active Workspaces (WAW)

```sql
-- Weekly active workspaces (distinct workspaces with ≥1 job in last 7 days)
SELECT
    COUNT(DISTINCT workspace_id) AS weekly_active_workspaces
FROM agent_jobs
WHERE created_at >= NOW() - INTERVAL '7 days'
  AND status IN ('completed', 'failed', 'pending_financial_review', 'pending_approval', 'running');
```

```sql
-- WAW trend: last 4 weeks, one row per week
SELECT
    DATE_TRUNC('week', created_at) AS week_start,
    COUNT(DISTINCT workspace_id) AS weekly_active_workspaces
FROM agent_jobs
WHERE created_at >= NOW() - INTERVAL '28 days'
GROUP BY 1
ORDER BY 1 DESC;
```

```sql
-- WAW by subscription tier
SELECT
    o.subscription_tier,
    COUNT(DISTINCT aj.workspace_id) AS weekly_active_workspaces
FROM agent_jobs aj
JOIN workspaces w ON w.id = aj.workspace_id
JOIN organizations o ON o.id = w.organization_id
WHERE aj.created_at >= NOW() - INTERVAL '7 days'
GROUP BY o.subscription_tier
ORDER BY weekly_active_workspaces DESC;
```

---

## 4. Agent Job KPIs

### 4.1 Jobs Per Hour (Last 24h)

```sql
SELECT
    DATE_TRUNC('hour', created_at) AS hour_bucket,
    COUNT(*) AS jobs_created,
    COUNT(*) FILTER (WHERE status = 'completed') AS jobs_completed,
    COUNT(*) FILTER (WHERE status = 'failed') AS jobs_failed,
    COUNT(*) FILTER (WHERE status = 'pending_financial_review') AS jobs_flagged
FROM agent_jobs
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY 1
ORDER BY 1 DESC;
```

### 4.2 Credit Consumption Rate

Credit consumption is derived from the `credits_accounts` balance plus `audit_logs` for debit events.

```sql
-- Current credit balance across all accounts (snapshot)
SELECT
    o.subscription_tier,
    COUNT(ca.id) AS account_count,
    SUM(ca.balance) AS total_balance,
    SUM(ca.reserved) AS total_reserved,
    SUM(ca.balance - ca.reserved) AS total_available,
    AVG(ca.balance) AS avg_balance_per_workspace,
    MIN(ca.balance) AS min_balance
FROM credits_accounts ca
JOIN workspaces w ON w.id = ca.workspace_id
JOIN organizations o ON o.id = w.organization_id
GROUP BY o.subscription_tier
ORDER BY o.subscription_tier;
```

```sql
-- Credit debit events from audit_logs (last 24h)
SELECT
    DATE_TRUNC('hour', created_at) AS hour_bucket,
    COUNT(*) AS debit_events,
    resource_type
FROM audit_logs
WHERE action = 'credit_debit'
  AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY 1, resource_type
ORDER BY 1 DESC;
```

```sql
-- Workspaces with critically low credit balance (< 10 credits)
SELECT
    w.id AS workspace_id,
    w.name AS workspace_name,
    o.name AS org_name,
    o.subscription_tier,
    ca.balance,
    ca.reserved,
    (ca.balance - ca.reserved) AS available_credits
FROM credits_accounts ca
JOIN workspaces w ON w.id = ca.workspace_id
JOIN organizations o ON o.id = w.organization_id
WHERE ca.balance < 10
ORDER BY ca.balance ASC;
```

### 4.3 Pending Financial Review Queue Depth

Any non-zero value here requires immediate ops attention — a job has been flagged for potential financial action.

```sql
-- Current pending_financial_review queue depth
SELECT COUNT(*) AS pending_financial_review_count
FROM agent_jobs
WHERE status = 'pending_financial_review';
```

```sql
-- Detailed: how long have flagged jobs been waiting?
SELECT
    id AS job_id,
    workspace_id,
    agent_id,
    created_at,
    NOW() - created_at AS time_in_queue,
    status
FROM agent_jobs
WHERE status = 'pending_financial_review'
ORDER BY created_at ASC;
```

### 4.4 HITL-3 Backlog

HITL-3 jobs are held `pending_approval` and require manual owner sign-off before execution. A growing backlog indicates either high enterprise usage (expected) or a broken approval workflow (investigate).

```sql
-- Current HITL-3 backlog
SELECT COUNT(*) AS pending_approval_count
FROM agent_jobs
WHERE status = 'pending_approval';
```

```sql
-- HITL-3 backlog detail with aging
SELECT
    id AS job_id,
    workspace_id,
    agent_id,
    created_at,
    NOW() - created_at AS waiting_duration,
    CASE
        WHEN NOW() - created_at > INTERVAL '4 hours' THEN 'STALE'
        WHEN NOW() - created_at > INTERVAL '1 hour' THEN 'AGING'
        ELSE 'FRESH'
    END AS staleness
FROM agent_jobs
WHERE status = 'pending_approval'
ORDER BY created_at ASC;
```

### 4.5 Job Success Rate

```sql
-- Overall job success rate (last 24h)
SELECT
    COUNT(*) FILTER (WHERE status = 'completed') AS completed,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed,
    COUNT(*) FILTER (WHERE status IN ('completed', 'failed')) AS terminal_jobs,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'completed')::NUMERIC /
        NULLIF(COUNT(*) FILTER (WHERE status IN ('completed', 'failed')), 0) * 100,
        2
    ) AS success_rate_pct
FROM agent_jobs
WHERE created_at >= NOW() - INTERVAL '24 hours';
```

```sql
-- Success rate by agent_id (last 24h, identify failing agents)
SELECT
    agent_id,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'completed')::NUMERIC /
        NULLIF(COUNT(*) FILTER (WHERE status IN ('completed', 'failed')), 0) * 100,
        2
    ) AS success_rate_pct
FROM agent_jobs
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY agent_id
HAVING COUNT(*) FILTER (WHERE status IN ('completed', 'failed')) > 0
ORDER BY success_rate_pct ASC;
```

### 4.6 Average Job Duration

```sql
-- Average job duration for completed jobs (last 24h)
SELECT
    AVG(completed_at - created_at) AS avg_duration,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (completed_at - created_at))) AS p50_seconds,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (completed_at - created_at))) AS p90_seconds,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (completed_at - created_at))) AS p95_seconds,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (completed_at - created_at))) AS p99_seconds,
    MAX(completed_at - created_at) AS max_duration
FROM agent_jobs
WHERE status = 'completed'
  AND completed_at IS NOT NULL
  AND created_at >= NOW() - INTERVAL '24 hours';
```

```sql
-- Average job duration by agent_id (last 24h)
SELECT
    agent_id,
    COUNT(*) AS completed_count,
    ROUND(AVG(EXTRACT(EPOCH FROM (completed_at - created_at))), 2) AS avg_duration_seconds,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (completed_at - created_at)))::NUMERIC, 2) AS p95_seconds
FROM agent_jobs
WHERE status = 'completed'
  AND completed_at IS NOT NULL
  AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY agent_id
ORDER BY avg_duration_seconds DESC;
```

---

## 5. Infrastructure KPIs

### 5.1 ECS / Fargate

| Metric | CloudWatch Name | Target | Warning | Critical |
|--------|----------------|--------|---------|----------|
| CPU Utilization | `CPUUtilization` (ECS service) | < 70% sustained | > 70% | > 85% |
| Memory Utilization | `MemoryUtilization` (ECS service) | < 80% | > 80% | > 90% |
| Running task count | `RunningTaskCount` | ≥ desired count | < desired | 0 |

**Scaling policy:** Target-tracking on CPU at 65% — allows headroom before the warning threshold triggers. Scale-out cooldown: 60s. Scale-in cooldown: 300s (prevents thrash).

**ECS services to monitor:**
- `vantro-api` — FastAPI backend
- `vantro-worker` — agent_worker background loop

### 5.2 RDS PostgreSQL

| Metric | CloudWatch Name | Target | Warning | Critical |
|--------|----------------|--------|---------|----------|
| CPU Utilization | `CPUUtilization` | < 60% | > 70% | > 85% |
| DB Connections | `DatabaseConnections` | < 60% of max | > 80% of max | > 90% of max |
| Free Storage | `FreeStorageSpace` | > 20GB | < 10GB | < 5GB |
| Read Latency | `ReadLatency` | < 5ms | > 10ms | > 50ms |
| Write Latency | `WriteLatency` | < 10ms | > 20ms | > 100ms |
| Replica Lag | `ReplicaLag` | < 1s | > 5s | > 30s |
| Freeable Memory | `FreeableMemory` | > 512MB | < 256MB | < 128MB |

**Max connections reference:** For `db.t3.medium` = 420 connections; for `db.r6g.large` = 1000 connections. Set alert to 80% of your specific instance's limit.

**SQLAlchemy pool config** (from `backend/app/db/session.py`): ensure `pool_size` + `max_overflow` stays under 80% of RDS `max_connections` divided by number of ECS tasks.

### 5.3 SQS

| Queue | Metric | Warning | Critical | Notes |
|-------|--------|---------|----------|-------|
| Main job queue | `ApproximateNumberOfMessagesVisible` | > 50 | > 100 | Worker falling behind |
| Main job queue | `ApproximateAgeOfOldestMessage` | > 60s | > 300s | Jobs stuck |
| DLQ | `ApproximateNumberOfMessagesVisible` | > 0 | > 0 | Any DLQ message = incident |
| DLQ | Message count delta | Any increase | — | Alert on first message |

**DLQ policy:** Zero tolerance. Any message in the DLQ indicates a job that failed processing after all retry attempts. Trigger an immediate page to the on-call engineer.

### 5.4 CloudWatch Alarms — Required List

The following alarms must exist in CloudWatch before launch:

```
vantro-prod-alb-5xx-rate-warning
vantro-prod-alb-5xx-rate-critical
vantro-prod-alb-p95-latency-warning
vantro-prod-alb-p95-latency-critical
vantro-prod-ecs-api-cpu-warning
vantro-prod-ecs-api-cpu-critical
vantro-prod-ecs-api-memory-warning
vantro-prod-ecs-api-memory-critical
vantro-prod-ecs-worker-cpu-warning
vantro-prod-ecs-worker-cpu-critical
vantro-prod-ecs-worker-memory-warning
vantro-prod-ecs-worker-memory-critical
vantro-prod-rds-cpu-warning
vantro-prod-rds-cpu-critical
vantro-prod-rds-connections-warning
vantro-prod-rds-connections-critical
vantro-prod-rds-free-storage-warning
vantro-prod-rds-free-storage-critical
vantro-prod-rds-replica-lag-warning
vantro-prod-sqs-main-depth-warning
vantro-prod-sqs-main-depth-critical
vantro-prod-sqs-main-age-warning
vantro-prod-sqs-main-age-critical
vantro-prod-sqs-dlq-any-message
vantro-prod-financial-review-queue-depth
vantro-prod-hitl3-backlog-depth
vantro-prod-low-credit-workspace-count
```

---

## 6. CloudWatch Custom Metric Names

All custom metrics are published by the FastAPI backend and agent worker. Namespace prefix: `Vantro/`.

### 6.1 Vantro/AgentJobs

| Metric Name | Unit | Description |
|-------------|------|-------------|
| `JobsCreated` | Count | New agent_job rows inserted |
| `JobsCompleted` | Count | Jobs transitioned to `completed` |
| `JobsFailed` | Count | Jobs transitioned to `failed` |
| `JobsStarted` | Count | Jobs picked up by worker (status → `running`) |
| `JobDurationSeconds` | Seconds | Time from created_at to completed_at |
| `QueueDepth` | Count | Jobs in `pending` status |
| `FinancialReviewQueueDepth` | Count | Jobs in `pending_financial_review` |
| `ApprovalBacklog` | Count | Jobs in `pending_approval` (HITL-3) |
| `FinancialFlagRate` | Percent | Ratio of flagged to total completed |

**Dimensions:** `AgentId`, `WorkspaceId`, `SubscriptionTier`, `Environment`

### 6.2 Vantro/Credits

| Metric Name | Unit | Description |
|-------------|------|-------------|
| `CreditsConsumed` | Count | Credits debited per job completion |
| `CreditsAdded` | Count | Credits added (top-up or subscription renewal) |
| `LowBalanceCount` | Count | Workspaces with available balance < 10 |
| `ZeroBalanceCount` | Count | Workspaces with available balance = 0 |
| `TotalBalanceSnapshot` | Count | Sum of all available credits (snapshot) |
| `ReservedCredits` | Count | Total credits currently reserved (jobs in-flight) |

**Dimensions:** `WorkspaceId`, `SubscriptionTier`, `Environment`

### 6.3 Vantro/FinancialReview

| Metric Name | Unit | Description |
|-------------|------|-------------|
| `QueueDepth` | Count | Current depth of pending_financial_review queue |
| `ReviewedCount` | Count | Jobs manually reviewed and resolved |
| `EscalatedCount` | Count | Jobs escalated beyond first-line review |
| `TimeToReviewSeconds` | Seconds | Latency from flagging to admin action |

**Dimensions:** `AgentId`, `Environment`

### 6.4 Vantro/HITL

| Metric Name | Unit | Description |
|-------------|------|-------------|
| `PendingApprovalCount` | Count | Current HITL-3 backlog |
| `ApprovalLatencySeconds` | Seconds | Time from job created to approved |
| `ApprovedCount` | Count | HITL-3 jobs approved this period |
| `RejectedCount` | Count | HITL-3 jobs rejected/cancelled |

**Dimensions:** `AgentId`, `WorkspaceId`, `SubscriptionTier`, `Environment`

### 6.5 Vantro/Auth

| Metric Name | Unit | Description |
|-------------|------|-------------|
| `LoginAttempts` | Count | Total auth attempts |
| `LoginFailures` | Count | Failed auth attempts |
| `RateLimitHits` | Count | Requests blocked by rate limiter |
| `SuspiciousPathBlocked` | Count | Requests blocked by path scanner |

**Dimensions:** `Environment`

### 6.6 Metric Publishing Convention

```python
# Example boto3 call from backend
cloudwatch.put_metric_data(
    Namespace="Vantro/AgentJobs",
    MetricData=[{
        "MetricName": "JobsCompleted",
        "Value": 1,
        "Unit": "Count",
        "Dimensions": [
            {"Name": "AgentId", "Value": agent_id},
            {"Name": "SubscriptionTier", "Value": subscription_tier},
            {"Name": "Environment", "Value": "production"}
        ]
    }]
)
```

Publish at job state transitions, not on a polling timer. Exception: queue depth and balance snapshot metrics — publish every 60 seconds from worker heartbeat.

---

## 7. Alert Thresholds Table

| Metric | Warning Threshold | Critical Threshold | Action | Owner |
|--------|------------------|-------------------|--------|-------|
| **Uptime (ALB 5xx rate)** | > 0.05% of requests over 5min | > 0.1% of requests over 5min | Check ECS task health, recent deploys | On-call |
| **P95 API Latency** | > 350ms for 5min | > 500ms for 5min | Check ECS CPU, RDS query times, LLM provider latency | On-call |
| **ECS API CPU** | > 70% for 5min | > 85% for 3min | Trigger manual scale-out if auto-scaling not reacting | On-call |
| **ECS API Memory** | > 80% for 5min | > 90% for 3min | Check for memory leaks, restart task, scale out | On-call |
| **ECS Worker CPU** | > 70% for 10min | > 85% for 5min | Scale worker tasks, check SQS queue depth | On-call |
| **ECS Worker Memory** | > 80% for 10min | > 90% for 5min | Restart worker, check for runaway jobs | On-call |
| **RDS CPU** | > 70% for 5min | > 85% for 3min | Check slow queries, EXPLAIN ANALYZE, scale instance | On-call |
| **RDS Connections** | > 80% of max_connections | > 90% of max_connections | Check SQLAlchemy pool config, kill idle connections | On-call |
| **RDS Free Storage** | < 10GB | < 5GB | Expand storage immediately (no downtime for RDS autoscaling) | On-call |
| **RDS Replica Lag** | > 5s | > 30s | Pause replica reads, investigate replication I/O | On-call |
| **SQS Main Queue Depth** | > 50 messages | > 100 messages | Check worker health, scale worker tasks | On-call |
| **SQS Message Age** | > 60s oldest | > 300s oldest | Worker may be stuck; restart, check DLQ | On-call |
| **SQS DLQ Depth** | > 0 (any message) | > 5 messages | Page immediately; inspect failed message, fix root cause | Owner |
| **Pending Financial Review Queue** | > 0 (any job) | > 5 jobs | Admin reviews flagged jobs immediately; do not auto-clear | Owner |
| **HITL-3 Approval Backlog** | > 10 jobs | > 25 jobs | Review and approve/reject pending jobs in admin portal | Owner |
| **Low Credit Balance (workspaces)** | > 3 workspaces below 10 credits | > 10 workspaces below 10 credits | Trigger in-app low-balance notifications, contact affected orgs | Owner |
| **Zero Credit Balance** | > 1 workspace | > 5 workspaces | Immediate outreach; jobs will fail for these workspaces | Owner |
| **Auth Rate Limit Hits** | > 50/min | > 200/min | Check for credential stuffing attack; block IPs | On-call |
| **Suspicious Path Blocked** | > 10/min | > 100/min | Possible scanning/attack; check WAF rules | On-call |
| **LLM Error Rate** | > 1% of LLM calls failing | > 5% of LLM calls failing | Check LLM provider status page, fall back if applicable | Owner |

**SNS Topic for alerts:** `arn:aws:sns:us-east-1:<account-id>:vantro-prod-alerts`  
**On-call:** mark.salman76@gmail.com  
**Escalation:** Same contact (sole operator at launch)

---

## 8. Baseline Capture Procedure

Run this procedure on **T-1** (the day before launch). Store all captured values in `launch/monitoring/baseline.json`. The baseline is used for anomaly detection during the first 72 hours post-launch.

### Step 1: Run SQL Baselines

Connect to the RDS read replica and run each of the following, recording the output:

```bash
# Connect to RDS (use AWS Secrets Manager for credentials)
psql "host=<rds-read-replica-endpoint> dbname=vantro user=vantro_readonly sslmode=require"
```

Queries to run and record:

1. **Total organizations:** `SELECT COUNT(*) FROM organizations;`
2. **Total workspaces:** `SELECT COUNT(*) FROM workspaces;`
3. **Activated workspaces:** (use the activation rate query from §3.2)
4. **Total agent jobs (all time):** `SELECT COUNT(*) FROM agent_jobs;`
5. **Agent jobs last 7 days:** `SELECT COUNT(*) FROM agent_jobs WHERE created_at >= NOW() - INTERVAL '7 days';`
6. **Average job duration (last 7d):** (use the duration query from §4.6 with a 7-day window)
7. **Total credits balance:** `SELECT SUM(balance) FROM credits_accounts;`
8. **Current queue depth:** `SELECT COUNT(*) FROM agent_jobs WHERE status = 'pending';`
9. **Subscription tier distribution:** `SELECT subscription_tier, COUNT(*) FROM organizations GROUP BY 1;`

### Step 2: Export CloudWatch Metrics (Last 7 Days)

```bash
# Export ALB metrics for last 7 days
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --start-time $(date -d '7 days ago' -u +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 3600 \
  --statistics p95 Average \
  --dimensions Name=LoadBalancer,Value=<alb-arn-suffix> \
  --output json > launch/monitoring/cloudwatch_latency_7d.json

# Export ECS CPU for last 7 days
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --start-time $(date -d '7 days ago' -u +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 3600 \
  --statistics Average Maximum \
  --dimensions Name=ClusterName,Value=vantro-prod Name=ServiceName,Value=vantro-api \
  --output json > launch/monitoring/cloudwatch_ecs_cpu_7d.json

# Export RDS connections for last 7 days
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --start-time $(date -d '7 days ago' -u +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 3600 \
  --statistics Average Maximum \
  --dimensions Name=DBInstanceIdentifier,Value=vantro-prod \
  --output json > launch/monitoring/cloudwatch_rds_connections_7d.json
```

### Step 3: Record ECS and RDS Baseline Utilization

```bash
# Current ECS task counts
aws ecs describe-services \
  --cluster vantro-prod \
  --services vantro-api vantro-worker \
  --query 'services[*].{name:serviceName,running:runningCount,desired:desiredCount,pending:pendingCount}' \
  --output json > launch/monitoring/ecs_baseline.json

# Current RDS instance state
aws rds describe-db-instances \
  --db-instance-identifier vantro-prod \
  --query 'DBInstances[0].{Class:DBInstanceClass,Status:DBInstanceStatus,MultiAZ:MultiAZ,StorageGB:AllocatedStorage,IOPS:Iops}' \
  --output json > launch/monitoring/rds_baseline.json

# Current SQS queue attributes
aws sqs get-queue-attributes \
  --queue-url <main-queue-url> \
  --attribute-names All \
  --output json > launch/monitoring/sqs_baseline.json
```

### Step 4: Compile baseline.json

Create `launch/monitoring/baseline.json` with the following schema:

```json
{
  "captured_at": "2026-06-27T00:00:00Z",
  "environment": "production",
  "sql": {
    "total_organizations": 0,
    "total_workspaces": 0,
    "activated_workspaces": 0,
    "activation_rate_pct": 0.0,
    "total_agent_jobs_alltime": 0,
    "agent_jobs_last_7d": 0,
    "avg_job_duration_seconds_7d": 0.0,
    "p95_job_duration_seconds_7d": 0.0,
    "total_credits_balance": 0.0,
    "current_pending_queue_depth": 0,
    "subscription_tier_distribution": {
      "starter": 0,
      "growth": 0,
      "business": 0,
      "enterprise": 0
    }
  },
  "cloudwatch_7d": {
    "alb_p95_latency_ms": {
      "avg": 0.0,
      "max": 0.0
    },
    "alb_5xx_rate_pct": {
      "avg": 0.0,
      "max": 0.0
    },
    "ecs_api_cpu_pct": {
      "avg": 0.0,
      "max": 0.0
    },
    "ecs_worker_cpu_pct": {
      "avg": 0.0,
      "max": 0.0
    },
    "rds_connections": {
      "avg": 0.0,
      "max": 0.0
    },
    "rds_cpu_pct": {
      "avg": 0.0,
      "max": 0.0
    },
    "sqs_main_queue_depth": {
      "avg": 0.0,
      "max": 0.0
    }
  },
  "ecs": {
    "api_desired_count": 0,
    "api_running_count": 0,
    "worker_desired_count": 0,
    "worker_running_count": 0
  },
  "rds": {
    "instance_class": "",
    "allocated_storage_gb": 0,
    "multi_az": false,
    "max_connections_limit": 0
  },
  "anomaly_thresholds_first_72h": {
    "signups_per_hour_warn_above": 0,
    "jobs_per_hour_warn_above": 0,
    "ecs_cpu_warn_above_pct": 70,
    "rds_connections_warn_above_pct": 80,
    "p95_latency_warn_above_ms": 350,
    "sqs_depth_warn_above": 50
  }
}
```

### Step 5: Set Anomaly Detection Thresholds

After recording baseline values, compute the first-72h anomaly thresholds:

- `signups_per_hour_warn_above` = baseline `avg_signups_per_hour × 10` (spike detection)
- `jobs_per_hour_warn_above` = baseline `avg_jobs_per_hour × 5` (traffic spike)
- All other thresholds remain fixed (from §7)

Commit the completed `baseline.json` to git before launch. It becomes the historical record for the launch event.

---

## 9. First 72h Monitoring Runbook

### Pre-Launch Checklist (T-0, before traffic)

- [ ] All CloudWatch alarms in `OK` state
- [ ] SQS DLQ is empty
- [ ] No jobs in `pending_financial_review` or `pending_approval`
- [ ] ECS services show desired task counts running
- [ ] RDS shows < 30% connections utilized
- [ ] `baseline.json` committed to git
- [ ] SNS alert subscriptions confirmed (email received for test alarm)
- [ ] Admin portal accessible at `/admin`
- [ ] Agent worker heartbeat log visible in CloudWatch Logs

---

### Every 15 Minutes (First 24h)

Open the `Vantro-SLO-Dashboard` and check:

1. **5xx rate** — should be < 0.05%. Any spike: check ECS task logs immediately.
2. **P95 latency** — should be < 300ms at low traffic. Rising trend = check RDS or LLM response times.
3. **SQS DLQ** — must be 0. Any message: stop and investigate before continuing.
4. **Financial review queue** — any job flagged: open admin portal, review, resolve.
5. **ECS running task count** — matches desired. Any `stopped` tasks: check CloudWatch Logs for crash reason.
6. **Active signups** — confirm signup flow is working end-to-end (test with a real account if unsure).

**Log command for quick task health:**
```bash
aws ecs describe-services \
  --cluster vantro-prod \
  --services vantro-api vantro-worker \
  --query 'services[*].{name:serviceName,running:runningCount,desired:desiredCount}'
```

---

### Every Hour (First 72h)

1. **Activation rate** — run the §3.2 query. Is it trending up from baseline? < 10% activation after 4h = investigate onboarding flow.
2. **Job success rate** — run §4.5 query. Should be > 95%. < 90% = agent-level investigation needed.
3. **Average job duration** — compare p95 to baseline. > 50% increase = check LLM response times and worker CPU.
4. **Credit balance scan** — run the low-balance query from §4.2. Reach out to any workspace below 10 credits.
5. **RDS slow query log** — check `aws rds describe-db-log-files` for `slowquery` log; download and scan if new entries.
6. **ECS auto-scaling activity** — `aws application-autoscaling describe-scaling-activities --service-namespace ecs` — confirm scale-out events are completing in < 3 minutes.
7. **Error log review** — open CloudWatch Log Insights and run:

```
fields @timestamp, @message
| filter @message like /ERROR/ or @message like /Exception/
| sort @timestamp desc
| limit 50
```

Namespace: `/vantro/prod/api` and `/vantro/prod/worker`

8. **Stripe webhook delivery** — check Stripe dashboard for any failed webhook deliveries (credit top-ups, subscription changes).

---

### Escalation Path

#### Level 1 — On-Call Engineer (You: Mark Salman)

Trigger: Any CloudWatch alarm transitions to `ALARM` state.

**Immediate response (first 5 minutes):**
1. Open AWS console → CloudWatch → Alarms — identify which alarm fired
2. Open relevant CloudWatch Logs group for context
3. Determine if the issue is: (a) infrastructure, (b) application code, (c) upstream dependency (LLM provider, Stripe), or (d) data/query

**For infrastructure issues:**
```bash
# Force new ECS deployment (if app-level crash)
aws ecs update-service --cluster vantro-prod --service vantro-api --force-new-deployment

# Scale out immediately if CPU/memory critical
aws ecs update-service --cluster vantro-prod --service vantro-api --desired-count <current+2>
```

**For database issues:**
```bash
# Check active connections
psql -c "SELECT count(*), state, wait_event_type, wait_event FROM pg_stat_activity GROUP BY state, wait_event_type, wait_event ORDER BY count DESC;"

# Kill idle connections older than 10 minutes
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND query_start < NOW() - INTERVAL '10 minutes' AND pid <> pg_backend_pid();"
```

**For SQS DLQ:**
1. Pull the failed message: `aws sqs receive-message --queue-url <dlq-url>`
2. Inspect the message body and the `ApproximateFirstReceiveTimestamp`
3. Find the corresponding `agent_jobs` row and check backend logs for the failure reason
4. Fix root cause, then either re-drive the message or mark the job failed manually

#### Level 2 — Critical Incident (Sustained Outage > 15 Minutes)

If the issue cannot be resolved within 15 minutes:

1. **Activate maintenance mode** — update ALB listener rule to return a 503 with a maintenance page (preserves error budget visibility)
2. **Snapshot the database** — manual RDS snapshot before any destructive recovery action
3. **Document the incident** — create an entry in `launch/monitoring/incidents/` with timestamp, symptoms, actions taken
4. **Stripe pause** — if billing is affected, pause Stripe payment processing via dashboard to prevent charging for a degraded service

#### Level 3 — Data Integrity Issue

Trigger: Any job in `pending_financial_review` that cannot be explained, or any unexplained credit balance drop.

1. **Do not auto-resolve** — these require human judgment per the platform's financial governance rules
2. Pull full audit log for the affected workspace:
   ```sql
   SELECT * FROM audit_logs
   WHERE resource_type = 'credit' OR resource_type = 'agent_job'
   ORDER BY created_at DESC
   LIMIT 100;
   ```
3. Review the flagged job's output in the admin portal
4. If financial action was taken by an agent: escalate to legal review before clearing the flag
5. Document resolution in `launch/monitoring/financial_review_log.md`

---

### 72h Post-Launch Review

At T+72h, run a structured debrief:

1. **SLO compliance:** Was uptime > 99.5%? What was the actual 5xx rate? P95 latency?
2. **Error budget consumed:** How many minutes of downtime occurred? What % of monthly budget?
3. **Growth metrics:** Total signups, activation rate, WAW — vs. projections
4. **Incident count:** How many alarms fired? How many were actionable vs. noise?
5. **Threshold calibration:** Adjust warning/critical thresholds based on observed traffic patterns
6. **Baseline update:** Update `baseline.json` with the T+72h actual values
7. **Runbook update:** Document any response patterns that should be codified here

Store the debrief in `launch/monitoring/72h_review.md`.

---

## Appendix A — Useful CloudWatch Log Insights Queries

### Recent errors by type
```
fields @timestamp, @message
| filter @message like /ERROR/
| parse @message "ERROR * *" as error_type, error_detail
| stats count() by error_type
| sort count desc
```

### Agent job failures by agent_id (from structured logs)
```
fields @timestamp, agent_id, error_message
| filter status = "failed"
| stats count() as failure_count by agent_id
| sort failure_count desc
```

### Request latency percentiles (last 1h)
```
fields @timestamp, duration_ms, path
| filter ispresent(duration_ms)
| stats pct(duration_ms, 50) as p50, pct(duration_ms, 95) as p95, pct(duration_ms, 99) as p99 by bin(5m)
```

### Rate limit hits by IP
```
fields @timestamp, client_ip, path
| filter @message like /rate_limit_exceeded/
| stats count() as hits by client_ip
| sort hits desc
| limit 20
```

---

## Appendix B — Quick Reference

| URL / Resource | Value |
|---------------|-------|
| CloudWatch Dashboard | `Vantro-SLO-Dashboard` |
| ECS Cluster | `vantro-prod` |
| RDS Identifier | `vantro-prod` |
| SNS Alert Topic | `vantro-prod-alerts` |
| Main Log Group (API) | `/vantro/prod/api` |
| Main Log Group (Worker) | `/vantro/prod/worker` |
| Baseline File | `launch/monitoring/baseline.json` |
| On-Call Contact | mark.salman76@gmail.com |
| Alert Evaluation Period | 1 minute |
| Alert Trigger Periods | 5 consecutive (warnings), 3 consecutive (critical) |
