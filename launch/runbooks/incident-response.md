# Vantro.ai — Production Incident Response Runbook

**Last updated:** 2026-06-28  
**On-call:** mark.salman76@gmail.com (sole responder)  
**AWS region default:** us-east-1  
**Cluster:** vantro-prod  

Set these shell variables before running commands below — paste and export once per terminal session:

```bash
export AWS_DEFAULT_REGION=us-east-1
export CLUSTER=vantro-prod
export BACKEND_SVC=vantro-backend
export FRONTEND_SVC=vantro-frontend
export DB_ID=vantro-prod-db
export SQS_URL=https://sqs.us-east-1.amazonaws.com/<ACCOUNT_ID>/vantro-agent-jobs
export LOG_GROUP_BACKEND=/ecs/vantro-backend
export LOG_GROUP_FRONTEND=/ecs/vantro-frontend
export ADMIN_URL=https://vantro.ai/admin
```

---

## Severity Classification

| Level | Condition | Target acknowledge | Target resolve |
|-------|-----------|-------------------|----------------|
| **P0** | Complete outage: DB unreachable, all ECS tasks crashed, error rate >5% of requests over 5-min window | 5 min | 60 min |
| **P1** | Degraded: agent jobs stuck >15 min, HITL-3 queue backed up >10 jobs, financial scanner triggered, single ECS task in crash loop | 15 min | 2 h |
| **P2** | Minor: elevated latency (<5% errors), single-user issue, non-critical feature broken | 1 h | next business day |

---

## First 60 Seconds — Any Incident

1. Open the CloudWatch dashboard (bookmark this):  
   `https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:`

2. Hit the health endpoint from your phone as a sanity check:
   ```bash
   curl -sf https://vantro.ai/health && echo "UP" || echo "DOWN"
   ```

3. Classify severity using the table above.

4. If P0: post a holding message on the status page / email list before diving in (template at bottom of this doc).

---

## P0 Response Procedure — Complete Outage

### Step 1 — Establish what is down (2 min)

Check ECS service health for both services:

```bash
aws ecs describe-services \
  --cluster $CLUSTER \
  --services $BACKEND_SVC $FRONTEND_SVC \
  --query "services[*].{name:serviceName,running:runningCount,desired:desiredCount,pending:pendingCount,status:status}"
```

Expected: `running == desired` for both. If `running == 0`, ECS tasks have all crashed.

Check RDS:

```bash
aws rds describe-db-instances \
  --db-instance-identifier $DB_ID \
  --query "DBInstances[0].{Status:DBInstanceStatus,MultiAZ:MultiAZ,Endpoint:Endpoint.Address}"
```

Expected: `Status: available`. If `Status: failed` or `rebooting`, jump to [RDS Down](#rds-down).

### Step 2 — Read the crash reason (3 min)

List the most recently stopped tasks:

```bash
aws ecs list-tasks \
  --cluster $CLUSTER \
  --service-name $BACKEND_SVC \
  --desired-status STOPPED \
  --query "taskArns[:5]"
```

Describe the stopped task (paste one ARN from above):

```bash
aws ecs describe-tasks \
  --cluster $CLUSTER \
  --tasks <TASK_ARN> \
  --query "tasks[0].containers[*].{name:name,reason:reason,exitCode:exitCode,lastStatus:lastStatus}"
```

Also check the `stopCode` and `stoppedReason` on the task itself:

```bash
aws ecs describe-tasks \
  --cluster $CLUSTER \
  --tasks <TASK_ARN> \
  --query "tasks[0].{stopCode:stopCode,stoppedReason:stoppedReason}"
```

Common stop codes:
- `TaskFailedToStart` → image pull failed or container entrypoint error; check ECR / env vars
- `EssentialContainerExited` → application crash; tail logs next
- `ServiceSchedulerInitiated` → ECS replaced it (usually health check failure)

### Step 3 — Tail live logs (continuous)

```bash
aws logs tail $LOG_GROUP_BACKEND --follow --since 15m
```

For frontend:

```bash
aws logs tail $LOG_GROUP_FRONTEND --follow --since 15m
```

Filter for errors only:

```bash
aws logs filter-log-events \
  --log-group-name $LOG_GROUP_BACKEND \
  --start-time $(date -d '15 minutes ago' +%s)000 \
  --filter-pattern "ERROR"
```

### Step 4 — Force new deployment (most common fix)

If the task is crashing but the image and config are believed good (transient fault, memory pressure, etc.):

```bash
aws ecs update-service \
  --cluster $CLUSTER \
  --service $BACKEND_SVC \
  --force-new-deployment
```

Watch rollout:

```bash
aws ecs wait services-stable \
  --cluster $CLUSTER \
  --services $BACKEND_SVC
echo "Backend stable"
```

Do the same for frontend if needed:

```bash
aws ecs update-service \
  --cluster $CLUSTER \
  --service $FRONTEND_SVC \
  --force-new-deployment

aws ecs wait services-stable \
  --cluster $CLUSTER \
  --services $FRONTEND_SVC
echo "Frontend stable"
```

### Step 5 — Verify recovery

```bash
curl -sf https://vantro.ai/health && echo "RECOVERED" || echo "STILL DOWN"
```

---

### RDS Down

Check status:

```bash
aws rds describe-db-instances \
  --db-instance-identifier $DB_ID \
  --query "DBInstances[0].{Status:DBInstanceStatus,MultiAZ:MultiAZ,LatestRestorableTime:LatestRestorableTime}"
```

**If Multi-AZ = true and status is `failed`** — initiate failover to standby:

```bash
aws rds reboot-db-instance \
  --db-instance-identifier $DB_ID \
  --force-failover
```

Wait for reboot (takes 1–3 min):

```bash
aws rds wait db-instance-available \
  --db-instance-identifier $DB_ID
echo "RDS available"
```

**If Multi-AZ = false and DB is down** — only option is to wait for RDS auto-recovery or restore from snapshot. Get latest snapshot:

```bash
aws rds describe-db-snapshots \
  --db-instance-identifier $DB_ID \
  --query "sort_by(DBSnapshots, &SnapshotCreateTime)[-1].{Id:DBSnapshotIdentifier,Created:SnapshotCreateTime,Status:Status}"
```

Restore (last resort — creates a NEW instance, then you must update the DB endpoint in Secrets Manager):

```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier vantro-prod-db-restored \
  --db-snapshot-identifier <SNAPSHOT_ID> \
  --db-instance-class db.t3.medium \
  --multi-az
```

Update the `DATABASE_URL` secret in Secrets Manager after the new instance endpoint is available.

### ECS task count at zero — environment variable or secret issue

If all tasks fail to start and logs show `KeyError` / `ValidationError` / missing env var:

Check Secrets Manager secrets used by the task definition:

```bash
aws secretsmanager list-secrets \
  --query "SecretList[?contains(Name,'vantro')].{Name:Name,LastChanged:LastChangedDate}"
```

Check a specific secret exists and has been updated recently:

```bash
aws secretsmanager describe-secret \
  --secret-id vantro/prod/backend \
  --query "{LastChanged:LastChangedDate,VersionIds:VersionIdsToStages}"
```

If a secret was deleted or rotated incorrectly, restore the previous version:

```bash
aws secretsmanager get-secret-value \
  --secret-id vantro/prod/backend \
  --version-stage AWSPREVIOUS
```

---

## P1 Response Procedure — Degraded Service

### Agent jobs stuck in `pending` or `pending_approval`

**Check SQS queue depth:**

```bash
aws sqs get-queue-attributes \
  --queue-url $SQS_URL \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible
```

- `ApproximateNumberOfMessages` = messages waiting (worker not picking up)
- `ApproximateNumberOfMessagesNotVisible` = messages in-flight (being processed)

If `ApproximateNumberOfMessages` is growing and `NotVisible` is near zero, the worker is down. Check ECS:

```bash
aws ecs describe-services \
  --cluster $CLUSTER \
  --services $BACKEND_SVC \
  --query "services[0].{running:runningCount,desired:desiredCount}"
```

If running < desired, force new deployment (see P0 Step 4).

**Find stuck jobs via admin API:**

```
GET https://vantro.ai/api/admin/jobs?status=pending&created_before=<ISO_TIMESTAMP_15MIN_AGO>
Authorization: Bearer <ADMIN_TOKEN>
```

**Manually reset stuck jobs** (connect to RDS via bastion or psql from ECS exec):

```bash
# ECS exec into running backend task
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER --service-name $BACKEND_SVC --desired-status RUNNING --query "taskArns[0]" --output text)

aws ecs execute-command \
  --cluster $CLUSTER \
  --task $TASK_ARN \
  --container vantro-backend \
  --interactive \
  --command "/bin/bash"
```

Inside the container, run psql against RDS (DB creds from Secrets Manager):

```sql
-- Find jobs stuck in pending for >15 minutes
SELECT id, status, agent_id, workspace_id, created_at
FROM agent_jobs
WHERE status = 'pending'
  AND created_at < NOW() - INTERVAL '15 minutes'
ORDER BY created_at ASC
LIMIT 20;

-- Reset to failed if you want them re-submitted
UPDATE agent_jobs
SET status = 'failed', error_message = 'Reset by on-call: worker stall incident'
WHERE id IN (<comma-separated-ids>);
```

### Financial scanner triggered (`pending_financial_review`)

The financial scanner fires when an LLM response contains phrases matching spend/scale/agreement patterns. Every trigger sends an email to mark.salman76@gmail.com.

**Check what's in review:**

```
GET https://vantro.ai/api/admin/jobs?status=pending_financial_review
```

Or via psql:

```sql
SELECT id, agent_id, workspace_id, created_at, output_preview
FROM agent_jobs
WHERE status = 'pending_financial_review'
ORDER BY created_at DESC;
```

**Decision tree:**

1. Read the flagged output. Does it actually authorize spend / agree to a contract / instruct scaling?
   - **YES (true positive):** The financial guard worked correctly. Reject the job. Notify the workspace owner. Review agent prompt for injection vectors.
   - **NO (false positive):** The LLM output mentioned keywords innocuously (e.g., "I recommend scaling your content strategy"). Safe to approve.

2. Approve or reject via admin API:
   ```
   POST https://vantro.ai/api/admin/jobs/<JOB_ID>/approve
   POST https://vantro.ai/api/admin/jobs/<JOB_ID>/reject
   Authorization: Bearer <ADMIN_TOKEN>
   ```

3. If false positives are frequent for a specific agent, add finer-grained pattern exclusions to `scan_for_financial_actions` in `backend/app/services/` — do NOT loosen the scan broadly.

### HITL-3 backlog >10 jobs (`pending_approval`)

HITL-3 jobs are held until the owner approves. This is by design for high-spend/high-scale operations. If the queue is backing up:

**List pending approvals:**

```
GET https://vantro.ai/api/admin/jobs?status=pending_approval&limit=50
Authorization: Bearer <ADMIN_TOKEN>
```

**Approve individually** (admin portal: `https://vantro.ai/admin/jobs?status=pending_approval`):

```
POST https://vantro.ai/api/admin/jobs/<JOB_ID>/approve
Authorization: Bearer <ADMIN_TOKEN>
```

**If the backlog is from a runaway client submitting HITL-3 jobs in bulk**, throttle them:

```sql
-- Check which workspace is flooding
SELECT workspace_id, COUNT(*) as cnt
FROM agent_jobs
WHERE status = 'pending_approval'
  AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY workspace_id
ORDER BY cnt DESC;

-- Temporarily suspend the workspace (set flag if exists, or disable via admin portal)
UPDATE workspaces SET is_active = false WHERE id = '<WORKSPACE_ID>';
```

### Single ECS task crash-looping (P1 not P0 — other tasks are healthy)

ECS will reschedule. Let it run 2 more cycles (about 4 min) before intervening. If it keeps crashing:

```bash
# Get the failing task ARN
aws ecs list-tasks --cluster $CLUSTER --service-name $BACKEND_SVC --desired-status STOPPED --query "taskArns[0]" --output text

# Read crash reason
aws ecs describe-tasks --cluster $CLUSTER --tasks <TASK_ARN> \
  --query "tasks[0].containers[0].{reason:reason,exitCode:exitCode}"

# Tail its logs (use the task ID portion of ARN)
TASK_ID=$(echo <TASK_ARN> | cut -d'/' -f3)
aws logs filter-log-events \
  --log-group-name $LOG_GROUP_BACKEND \
  --log-stream-names "ecs/vantro-backend/$TASK_ID" \
  --query "events[*].message"
```

If a specific task is poison due to a bad job payload:

```sql
-- Find which job the task was processing at time of crash
SELECT id, status, agent_id, created_at FROM agent_jobs
WHERE status = 'pending'
  AND updated_at BETWEEN '<crash_time - 5min>' AND '<crash_time>'
ORDER BY updated_at DESC LIMIT 5;

-- Mark that job failed to unblock the worker
UPDATE agent_jobs SET status = 'failed', error_message = 'Killed task — marked failed by on-call'
WHERE id = '<JOB_ID>';
```

---

## Rollback Decision Tree

**Rollback if ANY of:**
- Two or more P0 incidents within 30 minutes pointing to the same deploy
- The deploy included a DB migration AND you cannot forward-fix without more migrations
- Error rate >20% and root cause is clearly in the new image

**Hotfix instead if:**
- Only 1 P0 and you can see the fix clearly in logs
- DB migration has already committed and users have written data against the new schema (rolling back the schema would corrupt data)
- Error is isolated to one agent or one workspace

### Get available task definition revisions

```bash
aws ecs list-task-definitions \
  --family-prefix vantro-backend \
  --sort DESC \
  --query "taskDefinitionArns[:10]"
```

The latest is what is currently deployed. The one above it is the previous revision.

### Roll back ECS to previous revision

```bash
# Set PREV_REVISION to the ARN of the task definition you want to revert to
PREV_REVISION=vantro-backend:<PREVIOUS_REVISION_NUMBER>

aws ecs update-service \
  --cluster $CLUSTER \
  --service $BACKEND_SVC \
  --task-definition $PREV_REVISION

aws ecs wait services-stable --cluster $CLUSTER --services $BACKEND_SVC
echo "Rolled back and stable"
```

Do the same for frontend if the frontend was also updated:

```bash
PREV_REVISION_FE=vantro-frontend:<PREVIOUS_REVISION_NUMBER>

aws ecs update-service \
  --cluster $CLUSTER \
  --service $FRONTEND_SVC \
  --task-definition $PREV_REVISION_FE

aws ecs wait services-stable --cluster $CLUSTER --services $FRONTEND_SVC
```

### Roll back a DB migration

**STOP. Read this before running.**

Only do this if:
- The migration ran within the last deploy
- No users have submitted data that depends on the new schema columns/tables

```bash
# Connect to the backend task and run alembic
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER --service-name $BACKEND_SVC --desired-status RUNNING --query "taskArns[0]" --output text)

aws ecs execute-command \
  --cluster $CLUSTER \
  --task $TASK_ARN \
  --container vantro-backend \
  --interactive \
  --command "/bin/bash"

# Inside the container:
cd /app
alembic current          # confirm current head
alembic downgrade -1     # step back one revision
alembic current          # verify
```

If you need to run the downgrade as a one-off ECS task instead (safer — avoids touching a running container):

```bash
aws ecs run-task \
  --cluster $CLUSTER \
  --task-definition vantro-backend:<CURRENT_REVISION> \
  --overrides '{"containerOverrides":[{"name":"vantro-backend","command":["alembic","downgrade","-1"]}]}' \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_ID>],securityGroups=[<SG_ID>],assignPublicIp=DISABLED}"
```

**NEVER downgrade DB if:**
- Users have already written to new columns → data loss
- The downgrade script is destructive (drops columns) and data is irreplaceable → hotfix instead

---

## User Communication Template

Use this verbatim. Do not mention AWS, ECS, Fargate, PostgreSQL, or any technology name.

### P0 — Initial Notification (send within 5 min of confirming outage)

**Subject:** Vantro.ai — Service Disruption Notice

> We are currently experiencing a service disruption affecting the Vantro.ai platform. Our team has been alerted and is actively investigating.
>
> During this time, you may be unable to access the platform or submit new tasks. Existing task results are safe and will be available once service is restored.
>
> We will send an update within 30 minutes or when service is restored, whichever comes first.
>
> We apologise for the inconvenience.
>
> — The Vantro.ai Team

### P0 — Resolution Notice (send within 15 min of recovery)

**Subject:** Vantro.ai — Service Restored

> The service disruption affecting Vantro.ai has been resolved as of [TIME UTC].
>
> All platform functions are now operating normally. If you were in the middle of a task when the disruption occurred, please resubmit it.
>
> We are conducting a full review to prevent recurrence. We apologise for the impact this caused.
>
> — The Vantro.ai Team

### P1 — Degraded Service Notice (send only if users are likely to notice)

**Subject:** Vantro.ai — Elevated Processing Times

> We are currently experiencing elevated processing times for AI tasks on the Vantro.ai platform. The platform remains accessible and all submitted tasks will be processed — they may take longer than usual to complete.
>
> We expect to return to normal processing times within [ESTIMATE]. No action is required on your part.
>
> — The Vantro.ai Team

---

## Post-Incident Checklist (complete within 24 hours)

- [ ] Write incident timeline: time detected, time acknowledged, each action taken, time resolved
- [ ] Root cause identified and documented (add to this runbook if a new failure mode was discovered)
- [ ] Check CloudWatch metrics for precursor signals: was CPU/memory ramping up before the crash? Was SQS depth growing?
  ```bash
  aws cloudwatch get-metric-statistics \
    --namespace AWS/ECS \
    --metric-name CPUUtilization \
    --dimensions Name=ClusterName,Value=$CLUSTER Name=ServiceName,Value=$BACKEND_SVC \
    --start-time $(date -u -d '2 hours ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
    --period 60 \
    --statistics Average
  ```
- [ ] Check if alarm existed and fired. If no alarm caught this: add a CloudWatch alarm for the failure mode.
  ```bash
  # Create alarm for backend task count dropping to 0
  aws cloudwatch put-metric-alarm \
    --alarm-name "vantro-backend-no-running-tasks" \
    --alarm-description "All backend ECS tasks stopped" \
    --metric-name RunningTaskCount \
    --namespace AWS/ECS \
    --dimensions Name=ClusterName,Value=$CLUSTER Name=ServiceName,Value=$BACKEND_SVC \
    --statistic Average \
    --period 60 \
    --threshold 1 \
    --comparison-operator LessThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:<ACCOUNT_ID>:vantro-alerts \
    --ok-actions arn:aws:sns:us-east-1:<ACCOUNT_ID>:vantro-alerts
  ```
- [ ] Was the incident caused by a deploy? Add a canary health check step to the CI/CD pipeline.
- [ ] Were any jobs lost? If so, identify affected workspaces and offer re-runs.
- [ ] Update this runbook if a gap was found (new failure mode, missing command, wrong assumption).
- [ ] If DB failover was needed: verify replica is re-synced and Multi-AZ is active again.
  ```bash
  aws rds describe-db-instances \
    --db-instance-identifier $DB_ID \
    --query "DBInstances[0].{Status:DBInstanceStatus,MultiAZ:MultiAZ,SecondaryAZ:SecondaryAvailabilityZone}"
  ```

---

## Quick Reference Card (print this or pin it)

| Task | Command |
|------|---------|
| Health check | `curl -sf https://vantro.ai/health` |
| ECS service status | `aws ecs describe-services --cluster vantro-prod --services vantro-backend vantro-frontend` |
| Tail backend logs | `aws logs tail /ecs/vantro-backend --follow --since 10m` |
| SQS queue depth | `aws sqs get-queue-attributes --queue-url $SQS_URL --attribute-names ApproximateNumberOfMessages` |
| Force redeploy backend | `aws ecs update-service --cluster vantro-prod --service vantro-backend --force-new-deployment` |
| List task def revisions | `aws ecs list-task-definitions --family-prefix vantro-backend --sort DESC` |
| Rollback backend | `aws ecs update-service --cluster vantro-prod --service vantro-backend --task-definition vantro-backend:<N>` |
| RDS status | `aws rds describe-db-instances --db-instance-identifier vantro-prod-db` |
| RDS failover | `aws rds reboot-db-instance --db-instance-identifier vantro-prod-db --force-failover` |
| ECS exec (shell) | `aws ecs execute-command --cluster vantro-prod --task <ARN> --container vantro-backend --interactive --command /bin/bash` |
| DB migrate up | `alembic upgrade head` (inside container) |
| DB migrate down | `alembic downgrade -1` (inside container) |
| Admin portal | `https://vantro.ai/admin` |
| Jobs in review | `GET /api/admin/jobs?status=pending_financial_review` |
| HITL-3 queue | `GET /api/admin/jobs?status=pending_approval` |
