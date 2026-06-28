# Vantro.ai Launch Day Runbook

**Platform:** Multi-tenant B2B SaaS — 27-agent AI workforce
**Stack:** FastAPI (ECS Fargate) · Next.js 16 (Vercel/ECS) · PostgreSQL (RDS) · SQS · Stripe
**Cluster:** `vantro` · Service: `backend`
**Admin:** mark.salman76@gmail.com
**War Room:** #vantro-launch (Slack)
**Related runbooks:** `deploy.md` · `incident-response.md` · `database.md` · `agent-worker.md`

---

## Pre-Launch Go/No-Go Gate

Before starting the T-1h countdown, confirm all of the following. Do not proceed until every box is checked.

- [ ] `deploy.md` full deploy completed and all smoke tests passed in staging
- [ ] Alembic migration at head 021 in production RDS
- [ ] ECS service `backend` running ≥ 2 tasks (desired count)
- [ ] Stripe webhook endpoint registered and receiving test events
- [ ] CloudWatch alarms in OK state (zero ALARM)
- [ ] Sentry project `vantro-backend` and `vantro-frontend` — zero unresolved critical issues from last 24h
- [ ] Comms-hold confirmed lifted — announcement copy approved
- [ ] Mark has sole go/no-go authority

Record go/no-go decision and timestamp here: `____________________`

---

## T-1h: Final Systems Check

Work through each section in order. All checks must pass before T-0.

### 1. ECS Service Health

```bash
aws ecs describe-services \
  --cluster vantro \
  --services backend \
  --query 'services[0].{running:runningCount,desired:desiredCount,pending:pendingCount}'
```

Expected: `running == desired`, `pending == 0`. Any other result: investigate before proceeding.

```bash
# Confirm current task definition revision (note this as rollback target)
aws ecs describe-services \
  --cluster vantro \
  --services backend \
  --query 'services[0].taskDefinition' \
  --output text
```

Record rollback target: `backend:<REV>` → `____________________`

- [ ] running == desired, pending == 0
- [ ] Rollback task definition revision recorded

### 2. RDS Connections Headroom

```bash
# Substitute your RDS instance identifier
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=<RDS_INSTANCE_ID> \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Average \
  --output table
```

Expected: current connections well below `max_connections` (check with `SHOW max_connections;` via psql). At launch traffic, headroom should be > 50%.

```bash
# Direct check via psql
psql "$DATABASE_URL" -c "SELECT count(*) AS active_connections FROM pg_stat_activity WHERE state = 'active';"
psql "$DATABASE_URL" -c "SHOW max_connections;"
```

- [ ] Active connections < 50% of max_connections

### 3. SQS Queue Depth

```bash
# Get queue URL first if not known
aws sqs get-queue-url --queue-name vantro-agent-jobs --output text

aws sqs get-queue-attributes \
  --queue-url <SQS_QUEUE_URL> \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible ApproximateNumberOfMessagesDelayed
```

Expected: `ApproximateNumberOfMessages == 0` (no backlog before launch). `NotVisible` reflects in-flight — acceptable if worker is active.

- [ ] Queue depth == 0 (no pre-launch backlog)

### 4. CloudWatch Alarm Sweep

```bash
aws cloudwatch describe-alarms \
  --state-value ALARM \
  --output table
```

Expected: empty result set. Any alarm in ALARM state must be investigated and resolved before proceeding.

```bash
# Also check INSUFFICIENT_DATA alarms (misconfigured or new metrics)
aws cloudwatch describe-alarms \
  --state-value INSUFFICIENT_DATA \
  --output table
```

- [ ] Zero alarms in ALARM state
- [ ] Zero critical alarms in INSUFFICIENT_DATA

### 5. Sentry Review

Log in to Sentry → project `vantro-backend` and `vantro-frontend`:
- Filter: last 24h, level=critical or level=error
- Expected: zero unresolved issues not already triaged
- Check "Issues" tab and confirm no new spike in the last 2h

- [ ] No unresolved critical Sentry issues

### T-1h Checkpoint

All five checks passed? If yes, proceed to T-0.

- [ ] **GO for T-0 deploy**

---

## T-0: Production Deploy

> **Note:** If this is a code deploy (new image). If launch is config/DNS-only with existing image, skip to "Enable Public Traffic".

### 1. Trigger Rolling Deploy

```bash
aws ecs update-service \
  --cluster vantro \
  --service backend \
  --force-new-deployment
```

### 2. Watch Rollout

```bash
# Blocks until stable or timeout (~10 min). Safe to Ctrl-C and re-run.
aws ecs wait services-stable \
  --cluster vantro \
  --services backend
```

While waiting, tail CloudWatch logs in a second terminal:

```bash
aws logs tail /vantro/backend --follow
```

### 3. Verify New Revision is Running

```bash
aws ecs describe-services \
  --cluster vantro \
  --services backend \
  --query 'services[0].{running:runningCount,desired:desiredCount,taskDef:taskDefinition}'
```

Confirm the task definition revision number is higher than the rollback target recorded at T-1h.

- [ ] New task definition revision running
- [ ] running == desired, pending == 0

### 4. Rollback (if deploy fails)

If `aws ecs wait` exits non-zero, or health checks fail after deploy:

```bash
# Replace <PREVIOUS_TASK_DEF_ARN> with the revision recorded at T-1h
aws ecs update-service \
  --cluster vantro \
  --service backend \
  --task-definition <PREVIOUS_TASK_DEF_ARN>

aws ecs wait services-stable \
  --cluster vantro \
  --services backend
```

Then invoke `incident-response.md`. Do not proceed to smoke tests after a rollback without root-cause analysis.

---

## Alembic Migration via ECS One-Off Task

Run this **before** the smoke test if this release includes schema changes. Skip if migration was already applied.

### 1. Run Migration Task

```bash
aws ecs run-task \
  --cluster vantro \
  --launch-type FARGATE \
  --task-definition backend \
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_ID_1>,<SUBNET_ID_2>],securityGroups=[<SECURITY_GROUP_ID>],assignPublicIp=DISABLED}" \
  --overrides '{
    "containerOverrides": [{
      "name": "backend",
      "command": ["alembic", "upgrade", "head"]
    }]
  }'
```

Note the `taskArn` returned. The task will run and exit (one-off).

### 2. Tail Migration Logs

```bash
aws logs tail /vantro/migration --follow
```

Wait for the task to reach STOPPED state:

```bash
aws ecs describe-tasks \
  --cluster vantro \
  --tasks <TASK_ARN> \
  --query 'tasks[0].{status:lastStatus,exitCode:containers[0].exitCode}'
```

Expected: `status == STOPPED`, `exitCode == 0`.

### 3. Verify Migration Applied

```bash
psql "$DATABASE_URL" -c "SELECT version_num FROM alembic_version;"
```

Expected output: `021` (current head).

- [ ] Alembic version == 021
- [ ] Migration task exit code == 0

---

## Smoke Test Production (10 Points)

Run against `https://vantro.ai`. All 10 must pass before announcing launch.

### 1. Health Endpoint

```bash
curl -f https://vantro.ai/api/health
```

Expected: HTTP 200, body contains `{"status":"ok"}` or similar.

- [ ] Health check 200

### 2. Signup

```bash
curl -s -X POST https://vantro.ai/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"smoketest+launch@vantro.ai","password":"LaunchTest2026!","name":"Smoke Test"}' \
  | jq '{status: .status, email: .email}'
```

Expected: 201 or 200 with user object. If 409 (already exists), proceed to login.

- [ ] Signup returns user

### 3. Login and Capture JWT

```bash
TOKEN=$(curl -s -X POST https://vantro.ai/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"smoketest+launch@vantro.ai","password":"LaunchTest2026!"}' \
  | jq -r '.access_token')
echo "TOKEN: $TOKEN"
```

Expected: non-null JWT string.

- [ ] JWT token captured

### 4. Create Workspace

```bash
curl -s -X POST https://vantro.ai/api/workspaces \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Smoke Test Workspace","tier":"starter"}' \
  | jq '{id: .id, name: .name, tier: .tier}'
```

Expected: workspace object with `id` and `tier == starter`.

```bash
# Capture workspace ID for subsequent calls
WORKSPACE_ID=$(curl -s https://vantro.ai/api/workspaces \
  -H "Authorization: Bearer $TOKEN" | jq -r '.[0].id')
echo "WORKSPACE_ID: $WORKSPACE_ID"
```

- [ ] Workspace created

### 5. Credits Balance

```bash
curl -s https://vantro.ai/api/workspaces/$WORKSPACE_ID/credits \
  -H "Authorization: Bearer $TOKEN" \
  | jq '{balance: .balance, tier: .tier}'
```

Expected: non-null balance, tier matches workspace tier.

- [ ] Credits balance returns

### 6. Agent Catalogue Count

```bash
curl -s https://vantro.ai/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  | jq 'length'
```

Expected: `27`

- [ ] Agent count == 27

### 7. Submit Starter-Tier Agent Job

```bash
JOB_ID=$(curl -s -X POST https://vantro.ai/api/agents/research_agent/run \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"workspace_id\":\"$WORKSPACE_ID\",\"task\":\"Summarise the key benefits of AI automation for small businesses in 3 bullet points.\"}" \
  | jq -r '.job_id')
echo "JOB_ID: $JOB_ID"
```

- [ ] Job submitted, job_id returned

### 8. Poll Job to Completion

```bash
# Poll every 10s, timeout 120s
for i in $(seq 1 12); do
  STATUS=$(curl -s https://vantro.ai/api/jobs/$JOB_ID \
    -H "Authorization: Bearer $TOKEN" | jq -r '.status')
  echo "[$i] status: $STATUS"
  if [[ "$STATUS" == "completed" || "$STATUS" == "failed" ]]; then break; fi
  sleep 10
done
echo "Final status: $STATUS"
```

Expected: `completed`. If `failed`, check Sentry and CloudWatch logs immediately.

- [ ] Job status == completed

### 9. Financial Review Queue Clear

```bash
curl -s https://vantro.ai/api/admin/jobs?status=pending_financial_review \
  -H "Authorization: Bearer $TOKEN" \
  | jq 'length'
```

Expected: `0`. If non-zero, the smoke-test job triggered a false-positive financial flag — investigate before launch.

- [ ] pending_financial_review count == 0

### 10. Stripe Webhook Endpoint Alive

```bash
curl -I https://vantro.ai/api/webhooks/stripe
```

Expected: HTTP 405 (Method Not Allowed on GET) — confirms the route exists and is reachable. A 404 means the route is not registered.

- [ ] Stripe webhook returns 405 (not 404)

### Smoke Test Gate

- [ ] **All 10 points passed — GO for public traffic**

---

## Enable Public Traffic / DNS

### Option A: Route 53 Weighted Routing Cutover

If traffic has been held behind a weighted routing policy (e.g. weight=0 on production record):

```bash
# Switch production record to weight=100
aws route53 change-resource-record-sets \
  --hosted-zone-id <HOSTED_ZONE_ID> \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "vantro.ai",
        "Type": "A",
        "SetIdentifier": "production",
        "Weight": 100,
        "AliasTarget": {
          "HostedZoneId": "<ALB_HOSTED_ZONE_ID>",
          "DNSName": "<ALB_DNS_NAME>",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

### Option B: CloudFront / ALB Already Pointing to Production

If Route 53 already resolves to the production ALB (no weighted split), no DNS change is required. Confirm:

```bash
dig vantro.ai +short
```

Expected: resolves to the production ALB or CloudFront distribution IP.

```bash
curl -I https://vantro.ai
```

Expected: HTTP 200 (frontend) or redirect. Check `Server` header is absent (SecurityHeadersMiddleware must strip it).

- [ ] DNS resolves to production target
- [ ] `Server` header absent from response headers
- [ ] HTTPS working (no certificate errors)

---

## Send Customer Announcement

1. **Who sends:** Mark Salman (mark.salman76@gmail.com) — sole authority to send
2. **Channels (in order):**
   - Email list (primary — transactional ESP, e.g. Resend/Postmark)
   - LinkedIn post (company page + personal)
   - X/Twitter post
3. **Pre-send checks:**
   - [ ] Comms-hold confirmed lifted
   - [ ] All 10 smoke-test points passed
   - [ ] DNS resolving correctly
   - [ ] No active incidents

4. **Send and timestamp:**

```
Announcement sent at: ____________________  UTC
Channels sent:        [ ] Email  [ ] LinkedIn  [ ] X/Twitter
Sent by:              Mark Salman
```

---

## T+1h: First Monitoring Sweep

Run at **T+0 + 1 hour**. Document all values.

### CloudWatch Error Rate (last 1h)

```bash
aws cloudwatch get-metric-statistics \
  --namespace Vantro \
  --metric-name ErrorRate \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Average Maximum \
  --output table
```

Threshold: Average < 1%, Maximum < 5%. Breach → invoke `incident-response.md`.

### Latency P95 (last 1h)

```bash
aws cloudwatch get-metric-statistics \
  --namespace Vantro \
  --metric-name RequestLatencyP95 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics p95 \
  --output table
```

Threshold: P95 < 2000ms. Breach → invoke `incident-response.md`.

### Signup Count (last 1h)

```bash
psql "$DATABASE_URL" -c "
SELECT COUNT(*) AS signups_last_1h
FROM organizations
WHERE created_at > NOW() - INTERVAL '1 hour';
"
```

### Agent Job Count by Status (last 1h)

```bash
psql "$DATABASE_URL" -c "
SELECT status, COUNT(*) AS cnt
FROM agent_jobs
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY status
ORDER BY cnt DESC;
"
```

Expected statuses: mostly `completed`. Any large `failed` count → investigate.

### Financial Review Queue

```bash
psql "$DATABASE_URL" -c "
SELECT COUNT(*) AS pending_financial_review
FROM agent_jobs
WHERE status = 'pending_financial_review';
"
```

Threshold: < 10. Above 10 → possible false-positive storm in `scan_for_financial_actions` — see escalation triggers.

### HITL-3 Backlog

```bash
psql "$DATABASE_URL" -c "
SELECT COUNT(*) AS stale_hitl3_jobs
FROM agent_jobs
WHERE status = 'pending_approval'
  AND created_at < NOW() - INTERVAL '30 minutes';
"
```

Any result > 0 means Opus-tier jobs are waiting on Mark's manual approval. Log in to admin portal and review.

### T+1h Summary

```
Signups (1h):                ____
Jobs completed (1h):         ____
Jobs failed (1h):            ____
Error rate avg:              ____%
P95 latency:                 ____ms
pending_financial_review:    ____
HITL-3 backlog (>30m):       ____
```

- [ ] All metrics within thresholds
- [ ] War room update posted to #vantro-launch

---

## T+4h: Stakeholder Update

Send to mark.salman76@gmail.com (self / investors / board):

```
Subject: Vantro.ai Launch Update — T+4h

Launch timestamp: <DATE TIME UTC>

Metrics (first 4 hours):
- Signups:         ____
- Agent jobs run:  ____
- Error rate:      ____%
- P95 latency:     ____ms
- Uptime:          100% / issues: ____

Active incidents: none / [describe if any]

Next update: T+12h
```

- [ ] T+4h update sent

---

## T+12h: Second Monitoring Sweep

Repeat T+1h SQL queries with a 12h window.

### Signups (12h)

```bash
psql "$DATABASE_URL" -c "
SELECT COUNT(*) AS signups_last_12h
FROM organizations
WHERE created_at > NOW() - INTERVAL '12 hours';
"
```

### Agent Jobs (12h)

```bash
psql "$DATABASE_URL" -c "
SELECT status, COUNT(*) AS cnt
FROM agent_jobs
WHERE created_at > NOW() - INTERVAL '12 hours'
GROUP BY status
ORDER BY cnt DESC;
"
```

### Financial Review Queue (cumulative)

```bash
psql "$DATABASE_URL" -c "
SELECT COUNT(*) AS total_pending_financial_review
FROM agent_jobs
WHERE status = 'pending_financial_review';
"
```

### Stripe Webhook Events (last 12h)

Log in to Stripe Dashboard → Developers → Webhooks → select endpoint → filter last 12h.
- Confirm `checkout.session.completed`, `customer.subscription.created`, and/or `invoice.paid` events received and delivered (200).
- Any failed delivery: retry from Stripe dashboard and investigate handler logs.

- [ ] Stripe webhook events received and 200'd

### Sentry New Error Patterns

Review Sentry → Issues → sort by "First Seen" → filter last 12h.
- Identify any error patterns not present pre-launch.
- Triage: is it a new code path, a client data edge case, or a regression?

- [ ] Sentry reviewed, new patterns triaged

### T+12h Summary

```
Signups (12h):               ____
Jobs completed (12h):        ____
Jobs failed (12h):           ____
Stripe successful charges:   ____
Error rate avg:              ____%
Open Sentry issues (new):    ____
```

- [ ] T+12h update posted to #vantro-launch

---

## Escalation Triggers

The following thresholds require immediate invocation of `incident-response.md`.
Mark has sole go/no-go authority on rollback decisions.

| Metric | Threshold | Action |
|--------|-----------|--------|
| API error rate | > 1% sustained 5 min | Page Mark, invoke `incident-response.md` |
| P95 latency | > 2000ms sustained 5 min | Investigate ECS task CPU/memory, RDS slow queries |
| `pending_financial_review` queue | > 10 jobs | Possible false-positive storm — review `scan_for_financial_actions` patterns, pause agent queue if needed |
| ECS running tasks < desired | Any duration | Investigate task failures, check ECS events, possible rollback |
| RDS CPU | > 90% sustained 5 min | Scale instance class or add read replica immediately |
| SQS queue depth | > 500 messages | Worker is falling behind — check ECS task count, consider scaling service desired count |
| Stripe webhook failures | > 5 consecutive 5xx | Billing processing broken — escalate, do not dismiss |
| Sentry critical spike | > 50 new errors in 5 min | Likely regression — consider rollback |

**Rollback decision authority:** Mark Salman only.

**Rollback command:**

```bash
aws ecs update-service \
  --cluster vantro \
  --service backend \
  --task-definition <ROLLBACK_TASK_DEF_ARN>

aws ecs wait services-stable \
  --cluster vantro \
  --services backend
```

---

## War Room

| Item | Value |
|------|-------|
| Slack channel | #vantro-launch |
| Primary on-call | mark.salman76@gmail.com |
| Update cadence | Every 30 min for first 4h, then hourly until T+12h |
| Go/no-go authority | Mark Salman (sole) |
| Rollback authority | Mark Salman (sole) |

**Update template for #vantro-launch:**

```
[T+Xh] Status: GREEN / YELLOW / RED
Signups: ____  |  Jobs: ____  |  Errors: ____%  |  P95: ____ms
Active issues: none / [describe]
Next update: [time]
```

---

## Post-Launch Cleanup (T+24h)

- [ ] Delete smoke-test user `smoketest+launch@vantro.ai` from database
- [ ] Archive this runbook with timestamps filled in to `launch/runbooks/archive/launch-day-<DATE>.md`
- [ ] File retrospective notes in `launch/retro.md` (what went well, what to improve)
- [ ] Confirm CloudWatch alarms remain in OK state
- [ ] Schedule T+7d review: signups, retention, first agent job conversion rate

---

*Runbook version: 1.0 — Vantro.ai launch. Related: `deploy.md`, `incident-response.md`, `database.md`, `agent-worker.md`.*
