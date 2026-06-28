# Post-Launch Runbook — T+1 through T+7

**Product:** Vantro.ai  
**Admin:** mark.salman76@gmail.com  
**Stack:** FastAPI / Next.js 16 / PostgreSQL (RDS) / AWS ECS Fargate (cluster: `vantro`, service: `backend`) / SQS / ECR / Stripe  
**Related runbooks:** `deploy.md`, `incident-response.md`, `database.md`, `agent-worker.md`  
**Monitoring:** CloudWatch namespace `Vantro/*`, Sentry

---

## Table of Contents

1. [Daily Morning Sweep (T+1 → T+7)](#1-daily-morning-sweep)
2. [Hotfix Deploy Procedure](#2-hotfix-deploy-procedure)
3. [Financial Review Queue — Daily Drain](#3-financial-review-queue--daily-drain)
4. [HITL-3 Backlog Check](#4-hitl-3-backlog-check)
5. [Credit Anomaly Check](#5-credit-anomaly-check)
6. [Onboarding Health / Activation Rate](#6-onboarding-health--activation-rate)
7. [Support Ticket Triage](#7-support-ticket-triage)
8. [T+7 Retrospective](#8-t7-retrospective)
9. [Go/No-Go for T+14 Expansion](#9-gonogo-for-t14-expansion)

---

## 1. Daily Morning Sweep

Run every morning T+1 through T+7. Target completion: within 30 minutes of start of day.

### 1.1 Infrastructure Health

```bash
# ECS service status — confirm desired == running count
aws ecs describe-services \
  --cluster vantro \
  --services backend \
  --query 'services[0].{desired:desiredCount,running:runningCount,pending:pendingCount,status:status}'

# SQS queue depth — agent job queue should not be climbing
aws sqs get-queue-attributes \
  --queue-url https://sqs.<region>.amazonaws.com/<account-id>/vantro-jobs \
  --attribute-names ApproximateNumberOfMessages,ApproximateNumberOfMessagesNotVisible \
  --query 'Attributes'

# Health check
curl -sf https://vantro.ai/api/health | jq .

# Confirm agent worker is responding
curl -sf https://vantro.ai/api/admin/worker/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq .
```

### 1.2 CloudWatch Metrics

```bash
# API error rate (5xx) — last 24h
aws cloudwatch get-metric-statistics \
  --namespace Vantro/* \
  --metric-name ErrorRate5xx \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 3600 \
  --statistics Average \
  --query 'Datapoints[*].{time:Timestamp,value:Average}' \
  --output table

# P99 latency — last 24h
aws cloudwatch get-metric-statistics \
  --namespace Vantro/* \
  --metric-name RequestLatency \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 3600 \
  --statistics p99 \
  --query 'Datapoints[*].{time:Timestamp,p99:p99}' \
  --output table

# ECS CPU / memory utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ClusterName,Value=vantro Name=ServiceName,Value=backend \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Average \
  --output table
```

Open Sentry → Filter by "last 24h" → review any **new error groups** introduced since yesterday. Any new group with >5 occurrences → investigate before proceeding.

### 1.3 Database Checks

Connect to RDS:

```bash
psql "$DATABASE_URL"
```

Run the following queries in sequence:

```sql
-- New signups in last 24h
SELECT COUNT(*) AS new_orgs
FROM organizations
WHERE created_at > NOW() - INTERVAL '24 hours';

-- Agent jobs by status last 24h
SELECT status, COUNT(*) AS count
FROM agent_jobs
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY status
ORDER BY count DESC;

-- Failed jobs with error detail (last 24h, newest first)
SELECT id, agent_id, error_message, created_at
FROM agent_jobs
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC
LIMIT 20;

-- Credits-depleted workspaces (balance at or below zero)
SELECT w.id, w.name, ca.balance
FROM workspaces w
JOIN credits_accounts ca ON ca.workspace_id = w.id
WHERE ca.balance <= 0;

-- Pending financial review backlog
SELECT COUNT(*) AS backlog_count, MIN(created_at) AS oldest_item
FROM agent_jobs
WHERE status = 'pending_financial_review';
```

### 1.4 Daily Sweep Checklist

- [ ] ECS desired == running count, no pending tasks stuck
- [ ] SQS queue depth stable (not growing unboundedly)
- [ ] `/api/health` returns 200
- [ ] 5xx error rate < 1%
- [ ] P99 latency < 3000 ms
- [ ] No new Sentry error groups with >5 hits
- [ ] Failed jobs reviewed and root cause identified
- [ ] No credits-depleted workspaces with active subscriptions
- [ ] Financial review backlog noted (see Section 3)
- [ ] HITL-3 backlog noted (see Section 4)

---

## 2. Hotfix Deploy Procedure

### 2.1 Severity Classification

| Severity | Definition | Deploy Path |
|----------|-----------|-------------|
| **P0** | Data loss, auth broken, all agent jobs failing, security breach | Fast-track (this section) |
| **P1** | Single agent type failing, billing errors, integration down | Full cycle — staging → prod |
| **P2** | Performance degradation, UX issue, non-critical bug | Full cycle, next sprint |

Use fast-track **only** for P0. For P1+, follow `deploy.md`.

### 2.2 Fast-Track Steps

```bash
# 1. Branch from main
git checkout main && git pull origin main
git checkout -b hotfix/<short-description>

# 2. Fix the bug, commit
git add <changed files>
git commit -m "hotfix: <description> — P0"
git push origin hotfix/<short-description>

# 3. Open PR and get review
#    Self-review is acceptable for P0 — add a note in the PR body:
#    "P0 self-reviewed — [brief justification]"
gh pr create --title "hotfix: <description>" \
  --body "P0 hotfix. Self-reviewed. Root cause: <description>." \
  --base main

# 4. Merge (squash) directly to main
gh pr merge --squash --auto

# 5. Build and push Docker image to ECR
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=<region>
export IMAGE_TAG=$(git rev-parse --short HEAD)
export ECR_REPO="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/vantro-backend"

aws ecr get-login-password --region $AWS_REGION \
  | docker login --username AWS --password-stdin $ECR_REPO

docker build -t $ECR_REPO:$IMAGE_TAG -t $ECR_REPO:latest .
docker push $ECR_REPO:$IMAGE_TAG
docker push $ECR_REPO:latest

# 6. Force new ECS deployment
aws ecs update-service \
  --cluster vantro \
  --service backend \
  --force-new-deployment

# 7. Wait for rollout to stabilise (blocks until stable or timeout)
aws ecs wait services-stable \
  --cluster vantro \
  --services backend

echo "Deployment stable."

# 8. Smoke tests
curl -sf https://vantro.ai/api/health | jq .
curl -sf https://vantro.ai/api/agents \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq 'length'
curl -sf https://vantro.ai/api/admin/worker/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq .

# 9. Monitor Sentry for 15 min post-deploy — watch for new error spikes
```

### 2.3 Rollback (if smoke tests fail)

```bash
# Re-deploy previous image tag (find it in ECR or git log)
export PREV_TAG=<previous-image-tag>

aws ecs update-service \
  --cluster vantro \
  --service backend \
  --task-definition $(aws ecs describe-task-definition \
    --task-definition vantro-backend \
    --query 'taskDefinition.taskDefinitionArn' --output text)

# Or override the image directly via a new task definition revision pointing to $PREV_TAG
# See deploy.md § Rollback for full procedure
```

---

## 3. Financial Review Queue — Daily Drain

### 3.1 What This Queue Means

Every agent response is scanned by `scan_for_financial_actions` (backend: `app/agents/agent_executor.py`). A match routes the job to `pending_financial_review` and emails mark.salman76@gmail.com. Matches may be genuine financial action attempts **or** false positives (e.g., an agent quoting a price in its output).

Review this queue **every day before noon**.

### 3.2 Procedure

```sql
-- View full pending_financial_review backlog
SELECT id,
       agent_id,
       workspace_id,
       LEFT(output_preview, 300) AS output_snippet,
       created_at
FROM agent_jobs
WHERE status = 'pending_financial_review'
ORDER BY created_at ASC;
```

For each job, read `output_snippet` and assess:

**Approve (false positive — output is safe):**

```sql
UPDATE agent_jobs
SET status      = 'completed',
    reviewed_by = 'mark.salman76@gmail.com',
    reviewed_at = NOW()
WHERE id = '<job_id>';
```

Or via API:

```bash
curl -X POST https://vantro.ai/api/admin/jobs/<job_id>/approve \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Block (genuine financial action detected):**

```sql
UPDATE agent_jobs
SET status        = 'failed',
    error_message = 'Blocked: financial action detected in output',
    reviewed_by   = 'mark.salman76@gmail.com',
    reviewed_at   = NOW()
WHERE id = '<job_id>';
```

Or via API:

```bash
curl -X POST https://vantro.ai/api/admin/jobs/<job_id>/reject \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Financial action detected in agent output"}'
```

### 3.3 Daily Drain Checklist

- [ ] Backlog query run
- [ ] Every job reviewed (no job left in `pending_financial_review` older than 24h)
- [ ] False positive count logged for today
- [ ] If >5 false positives today → open ticket to tune `scan_for_financial_actions` patterns

### 3.4 Pattern Tuning Trigger

If false positive rate exceeds 5 per day for 2+ consecutive days, review the scanner:

```bash
# Location of financial action patterns
grep -n "scan_for_financial_actions\|FINANCIAL_PATTERNS" \
  backend/app/agents/agent_executor.py
```

Tighten regex patterns to reduce noise. Test against known-safe sample outputs before deploying.

---

## 4. HITL-3 Backlog Check

HITL-3 is the highest approval tier. Jobs from **business** and **enterprise** workspaces that trigger HITL-3 agents are held at `pending_approval` until manually approved by the owner. Customers are actively waiting.

**SLA: no job should sit in `pending_approval` for more than 4 hours.**

### 4.1 Check Pending Approvals

```sql
-- All pending_approval jobs with age
SELECT id,
       agent_id,
       workspace_id,
       created_at,
       NOW() - created_at AS age
FROM agent_jobs
WHERE status = 'pending_approval'
ORDER BY created_at ASC;
```

Flag any row where `age > INTERVAL '4 hours'` as requiring immediate action.

### 4.2 Approve a Job

```bash
curl -X POST https://vantro.ai/api/admin/jobs/<job_id>/approve \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 4.3 Reject a Job

```bash
curl -X POST https://vantro.ai/api/admin/jobs/<job_id>/reject \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Spend/scale action not approved at this time"}'
```

After rejecting, email the customer directly at the address on the workspace to explain and offer alternatives.

### 4.4 HITL-3 Checklist

- [ ] `pending_approval` query run
- [ ] All jobs < 4h old — no action required unless ready
- [ ] All jobs >= 4h old reviewed and approved or rejected
- [ ] Customer emailed for any rejection

---

## 5. Credit Anomaly Check

### 5.1 Negative Balance Detection

```sql
-- Workspaces with negative credit balance
SELECT w.id,
       w.name,
       ca.balance,
       ca.updated_at
FROM workspaces w
JOIN credits_accounts ca ON ca.workspace_id = w.id
WHERE ca.balance < 0;
```

A negative balance indicates either a race condition in the credit deduction path or a refund that was applied incorrectly. Investigate immediately — these workspaces may be running jobs without valid credit.

### 5.2 High-Usage Anomaly Detection

```sql
-- Top 10 workspaces by credits consumed last 24h
SELECT workspace_id,
       SUM(credits_used) AS total_credits
FROM agent_jobs
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY workspace_id
ORDER BY total_credits DESC
LIMIT 10;
```

Expected ranges by tier (approximate — adjust as actuals accumulate):

| Tier | Expected 24h Usage | Anomaly Threshold |
|------|--------------------|-------------------|
| starter | 10–100 credits | > 1,000 |
| growth | 100–500 credits | > 5,000 |
| business | 500–2,000 credits | > 20,000 |
| enterprise | 2,000+ credits | > 50,000 |

Any workspace exceeding 10x their tier average in 24h → investigate for abuse or an agent loop bug.

### 5.3 Credit Anomaly Checklist

- [ ] No negative balance workspaces
- [ ] Top-10 usage list reviewed — all within expected ranges
- [ ] Any anomalies investigated and documented

---

## 6. Onboarding Health / Activation Rate

**Definition:** An organization is "activated" if at least one agent job was run within 48 hours of signup.

**Target:** >40% activation rate within 48h.

### 6.1 Activation Rate Query

```sql
SELECT
  COUNT(DISTINCT o.id)            AS total_orgs,
  COUNT(DISTINCT aj.workspace_id) AS activated_orgs,
  ROUND(
    100.0 * COUNT(DISTINCT aj.workspace_id)
    / NULLIF(COUNT(DISTINCT o.id), 0),
    1
  )                               AS activation_rate_pct
FROM organizations o
LEFT JOIN workspaces w
  ON w.organization_id = o.id
LEFT JOIN agent_jobs aj
  ON aj.workspace_id = w.id
 AND aj.created_at > o.created_at + INTERVAL '48 hours'
WHERE o.created_at > NOW() - INTERVAL '7 days';
```

### 6.2 Funnel Diagnostics (run if activation rate < 40%)

```sql
-- Orgs that signed up but never ran a job
SELECT o.id, o.name, o.created_at
FROM organizations o
LEFT JOIN workspaces w ON w.organization_id = o.id
LEFT JOIN agent_jobs aj ON aj.workspace_id = w.id
WHERE o.created_at > NOW() - INTERVAL '7 days'
  AND aj.id IS NULL
ORDER BY o.created_at DESC;

-- First job attempt errors for new workspaces
SELECT aj.workspace_id, aj.status, aj.error_message, aj.created_at
FROM agent_jobs aj
JOIN workspaces w ON w.id = aj.workspace_id
JOIN organizations o ON o.id = w.organization_id
WHERE o.created_at > NOW() - INTERVAL '7 days'
  AND aj.status = 'failed'
ORDER BY aj.created_at ASC
LIMIT 30;
```

If activation rate is below 40% for 2+ consecutive days:
1. Check for errors in first-job submissions (query above)
2. Review onboarding flow in the frontend for friction or broken steps
3. Consider a direct email to non-activated orgs offering support

### 6.3 Activation Checklist

- [ ] Activation rate query run and logged
- [ ] Rate >= 40% (green) or < 40% (investigate)
- [ ] Failed first-job patterns reviewed if rate is below target

---

## 7. Support Ticket Triage

**Inbound channels:** email to mark.salman76@gmail.com, in-app feedback form.

### 7.1 Priority Matrix

| Priority | Definition | Response SLA |
|----------|-----------|-------------|
| **P0** | Can't log in, all jobs failing, data missing or corrupted | < 1 hour |
| **P1** | Specific agent failing, billing issue, integration broken | < 4 hours |
| **P2** | Feature request, UX confusion, performance complaint | < 24 hours |

### 7.2 Triage Procedure

1. Read all new inbound tickets at the start of each day (and again at midday during T+1 to T+7).
2. Assign priority using the matrix above.
3. For P0: stop current work, address immediately, follow `incident-response.md` if systemic.
4. For P1: acknowledge within 4h, investigate, resolve or escalate.
5. For P2: acknowledge within 24h, add to backlog.

### 7.3 Response Templates

**Acknowledgment (all tiers):**
> "Hi [name], thanks for reaching out. We've received your report and are looking into it now. We'll update you shortly."

**Investigating (P0/P1):**
> "We've confirmed the issue and are actively working on a fix. Current status: [brief description]. We'll have an update within [X] hours."

**Resolved:**
> "This has been resolved as of [time]. Here's what happened and what we fixed: [brief summary]. Please let us know if you see any recurrence."

### 7.4 Daily Support Checklist

- [ ] All new tickets read and triaged
- [ ] No unacknowledged P0 older than 1h
- [ ] No unacknowledged P1 older than 4h
- [ ] P2 backlog updated

---

## 8. T+7 Retrospective

Run at end of Day 7. Collect all metrics, write a brief summary, and make the T+14 go/no-go decision.

### 8.1 Uptime

Calculate from CloudWatch alarm history or incident log in `incident-response.md`:

```
Uptime % = (10080 - total_downtime_minutes) / 10080 * 100
```

(10080 = minutes in 7 days)

### 8.2 Signup and Activation Metrics

```sql
-- Total signups since launch
SELECT COUNT(*) AS total_orgs
FROM organizations
WHERE created_at > '<launch_date>';

-- Activation rate — 7-day window
SELECT
  COUNT(DISTINCT o.id)            AS total_orgs,
  COUNT(DISTINCT aj.workspace_id) AS activated_orgs,
  ROUND(
    100.0 * COUNT(DISTINCT aj.workspace_id)
    / NULLIF(COUNT(DISTINCT o.id), 0),
    1
  )                               AS activation_rate_pct
FROM organizations o
LEFT JOIN workspaces w ON w.organization_id = o.id
LEFT JOIN agent_jobs aj
  ON aj.workspace_id = w.id
 AND aj.created_at > o.created_at + INTERVAL '48 hours'
WHERE o.created_at > '<launch_date>';
```

### 8.3 Agent Job Metrics

```sql
-- Total jobs and status breakdown since launch
SELECT status, COUNT(*) AS count
FROM agent_jobs
WHERE created_at > '<launch_date>'
GROUP BY status
ORDER BY count DESC;

-- Jobs by agent type
SELECT agent_id, COUNT(*) AS count
FROM agent_jobs
WHERE created_at > '<launch_date>'
GROUP BY agent_id
ORDER BY count DESC;
```

### 8.4 Incident Count

Reference the incident log in `incident-response.md`. Count:
- P0 incidents
- P1 incidents
- Total time-to-resolution per incident

### 8.5 Financial Governance Summary

```sql
-- Financial review queue — total processed and false positive rate
SELECT
  COUNT(*)                                                  AS total_reviewed,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)   AS approved_false_positives,
  SUM(CASE WHEN status = 'failed'    THEN 1 ELSE 0 END)   AS blocked_genuine,
  ROUND(
    100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)
    / NULLIF(COUNT(*), 0),
    1
  )                                                         AS false_positive_rate_pct
FROM agent_jobs
WHERE reviewed_at > '<launch_date>'
  AND reviewed_by = 'mark.salman76@gmail.com';
```

### 8.6 Revenue

```sql
-- Revenue from Stripe charges since launch (if stripe_charges table is synced)
SELECT SUM(amount) / 100.0 AS revenue_usd
FROM stripe_charges
WHERE created > '<launch_date>'
  AND status = 'succeeded';
```

Or check Stripe Dashboard directly for authoritative figures.

### 8.7 Support Ticket Summary

Count tickets received, resolved, and average response time by priority. Note any recurring complaint themes.

### 8.8 NPS (if collected)

If a post-job NPS survey is active, pull scores:

```sql
-- If nps_responses table exists
SELECT
  ROUND(AVG(score), 1) AS avg_nps,
  COUNT(*)             AS responses
FROM nps_responses
WHERE created_at > '<launch_date>';
```

### 8.9 Retro Template

Fill in and save to `launch/retro-t7.md`:

```
Date: <date>
Attendees: Mark Salman (sole reviewer)

Uptime:             ___ %
Incidents:          ___ P0, ___ P1
Total signups:      ___
Activation rate:    ___ %
Total agent jobs:   ___
Failed job rate:    ___ %
FR false positives: ___ %
Revenue:            $___
Support tickets:    ___ received, ___ resolved
NPS:                ___

Key wins:
- 

Key issues:
-

Action items:
-

T+14 decision: GO / NO-GO / CONDITIONAL
```

---

## 9. Go/No-Go for T+14 Expansion

T+14 expansion = wider marketing push, PR, paid ads. Decision made at T+7 retro.

### 9.1 Criteria Table

| Criterion | Target | Status | Notes |
|-----------|--------|--------|-------|
| Uptime | >= 99% | — | Hard no-go if below |
| Open P0 bugs | 0 | — | Hard no-go if any open |
| Activation rate | >= 40% within 48h | — | Amber if below — evaluate before decision |
| Open P1s older than 24h | 0 | — | Hard no-go if any unresolved |
| FR false positive rate | < 20% per day | — | Amber if higher — tune scanner first |
| Customer feedback | Net positive | — | No systematic complaints about core functionality |
| Negative credit balances | 0 active cases | — | Hard no-go if unresolved |
| HITL-3 SLA compliance | No job > 4h wait | — | Operational readiness signal |

### 9.2 Decision Logic

- **GO:** All hard criteria met, amber criteria evaluated and accepted.
- **CONDITIONAL GO:** 1–2 amber criteria — proceed with T+14 expansion **only** after specific remediation (document what must be fixed first).
- **NO-GO:** Any hard criterion fails — delay T+14 until resolved. Re-assess at T+10.

### 9.3 Expansion Preparation Checklist (only run on GO)

- [ ] CloudWatch alarms verified to cover increased traffic
- [ ] ECS auto-scaling policy reviewed — confirm max task count is sufficient
- [ ] RDS read replica confirmed active (`DATABASE_REPLICA_URL` set)
- [ ] Stripe webhook handling tested at higher event volume
- [ ] Rate limits reviewed — `10/min` on auth routes sufficient for projected inbound?
- [ ] Onboarding email sequence confirmed active for new signups
- [ ] Landing page and marketing copy reviewed for tech-stack opacity (no mention of Claude, AWS, etc.)
- [ ] Support inbox tooling ready to handle increased volume

---

*Last updated: T+0 (launch day). Owner: mark.salman76@gmail.com.*
