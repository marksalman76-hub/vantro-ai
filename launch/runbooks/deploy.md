# Vantro.ai Production Deployment Runbook

**Target:** AWS ECS Fargate — cluster `vantro-prod`
**Services:** `vantro-backend`, `vantro-frontend`
**ECR pattern:** `<ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/vantro-backend` / `vantro-frontend`
**Secrets:** `vantro/prod/backend` in AWS Secrets Manager
**Alembic chain:** 001 → 021 (head)

---

## Pre-Deploy Checklist

Run these locally before touching AWS.

```powershell
# 1. Backend tests
cd backend
$env:PYTHONPATH = "."; $env:TESTING = "1"; pytest tests/ -q
```

```powershell
# 2. Frontend build
cd frontend
npm run build
```

```powershell
# 3. Migration chain integrity
cd backend
alembic history          # verify linear chain, no gaps, no branches
alembic heads            # must show exactly ONE head
```

- [ ] All tests passing locally
- [ ] Frontend builds clean (zero errors, warnings acceptable)
- [ ] `alembic heads` shows a single head (021)
- [ ] List every agent handler file changed in this release
- [ ] List every DB schema change (new columns, new tables, index changes)
- [ ] If schema change: confirm new columns have a DEFAULT or are nullable (never add NOT NULL without default to existing table)
- [ ] Confirm `assert len(AGENT_CATALOGUE) == 22` still holds (or deliberate change approved) — grep: `backend/app/agents/agent_registry.py`
- [ ] Note current task definition revisions (rollback targets):

```powershell
aws ecs describe-services `
  --cluster vantro-prod `
  --services vantro-backend vantro-frontend `
  --query "services[*].{name:serviceName,taskDef:taskDefinition}" `
  --output table
```

Record the output here before proceeding: `vantro-backend:<REV>` / `vantro-frontend:<REV>`

---

## Build & Push Docker Images

Set these once for the session:

```powershell
$ACCOUNT_ID = "<ACCOUNT_ID>"
$REGION     = "<REGION>"
$IMAGE_TAG  = "<IMAGE_TAG>"   # e.g. git rev-parse --short HEAD
```

### ECR Login

```powershell
aws ecr get-login-password --region $REGION |
  docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
```

### Backend

```powershell
cd backend

docker build -t vantro-backend:$IMAGE_TAG .

docker tag vantro-backend:$IMAGE_TAG `
  "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/vantro-backend:$IMAGE_TAG"

docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/vantro-backend:$IMAGE_TAG"
```

Also push `:latest` so the migration task can reference it by tag:

```powershell
docker tag vantro-backend:$IMAGE_TAG `
  "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/vantro-backend:latest"

docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/vantro-backend:latest"
```

### Frontend

```powershell
cd frontend

docker build -t vantro-frontend:$IMAGE_TAG .

docker tag vantro-frontend:$IMAGE_TAG `
  "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/vantro-frontend:$IMAGE_TAG"

docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/vantro-frontend:$IMAGE_TAG"
```

Verify both images appear in ECR:

```powershell
aws ecr describe-images --repository-name vantro-backend --region $REGION `
  --query "imageDetails[?contains(imageTags, '$IMAGE_TAG')].[imageTags,imagePushedAt]" `
  --output table

aws ecr describe-images --repository-name vantro-frontend --region $REGION `
  --query "imageDetails[?contains(imageTags, '$IMAGE_TAG')].[imageTags,imagePushedAt]" `
  --output table
```

---

## Run Alembic Migrations Against RDS

**Always run migrations as a one-off ECS task — never run `alembic upgrade head` locally against production.**
The task uses the production `DATABASE_URL` from Secrets Manager automatically (injected via task definition secret).

### Step 1 — Get the subnet and security group for the migration task

```powershell
# Reuse the same network config as the backend service
aws ecs describe-services `
  --cluster vantro-prod `
  --services vantro-backend `
  --query "services[0].networkConfiguration" `
  --output json
```

Note the `subnets` and `securityGroups` values.

### Step 2 — Run the migration task

```powershell
aws ecs run-task `
  --cluster vantro-prod `
  --task-definition vantro-backend `
  --launch-type FARGATE `
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_ID>],securityGroups=[<SG_ID>],assignPublicIp=DISABLED}" `
  --overrides '{
    "containerOverrides": [{
      "name": "vantro-backend",
      "command": ["alembic", "upgrade", "head"]
    }]
  }' `
  --query "tasks[0].taskArn" `
  --output text
```

Save the returned task ARN: `$MIGRATION_TASK_ARN`

### Step 3 — Wait for completion

```powershell
aws ecs wait tasks-stopped `
  --cluster vantro-prod `
  --tasks $MIGRATION_TASK_ARN

echo "Migration task stopped"
```

### Step 4 — Check exit code (must be 0)

```powershell
aws ecs describe-tasks `
  --cluster vantro-prod `
  --tasks $MIGRATION_TASK_ARN `
  --query "tasks[0].containers[0].{exitCode:exitCode,reason:reason,lastStatus:lastStatus}" `
  --output table
```

- Exit code `0` → proceed to Deploy Sequence
- Exit code non-zero → **STOP. Do not deploy.** Check CloudWatch logs:

```powershell
aws logs tail /ecs/vantro-backend --follow --since 10m
```

Fix the migration, re-push the image with the fix, re-run the migration task.

---

## Deploy Sequence

**Order is mandatory:** backend first, verify stable, then frontend.
Desired count must be >= 2 on each service for zero-downtime rolling deploy.

### 1 — Update backend service

```powershell
# Force new deployment with the newly pushed image tag
# (ECS will pull the new image on the next task launch)
aws ecs update-service `
  --cluster vantro-prod `
  --service vantro-backend `
  --force-new-deployment `
  --output json | Select-String "serviceArn"
```

If you registered a new task definition with the explicit image tag (recommended for auditability):

```powershell
aws ecs update-service `
  --cluster vantro-prod `
  --service vantro-backend `
  --task-definition vantro-backend:<NEW_REVISION> `
  --output json | Select-String "serviceArn"
```

### 2 — Wait for backend stability

```powershell
aws ecs wait services-stable `
  --cluster vantro-prod `
  --services vantro-backend

echo "Backend stable"
```

This waits up to 10 minutes. If it times out, check `aws ecs describe-services` for deployment failures and CloudWatch for crash logs before proceeding.

### 3 — Quick backend smoke test before touching frontend

```powershell
curl -s https://api.vantro.ai/health
# Expected: {"status":"healthy"} or similar 200 JSON
```

If health check fails: rollback backend now (see Rollback Procedure) before touching frontend.

### 4 — Update frontend service

```powershell
aws ecs update-service `
  --cluster vantro-prod `
  --service vantro-frontend `
  --force-new-deployment `
  --output json | Select-String "serviceArn"
```

Or with explicit task definition revision:

```powershell
aws ecs update-service `
  --cluster vantro-prod `
  --service vantro-frontend `
  --task-definition vantro-frontend:<NEW_REVISION> `
  --output json | Select-String "serviceArn"
```

### 5 — Wait for frontend stability

```powershell
aws ecs wait services-stable `
  --cluster vantro-prod `
  --services vantro-frontend

echo "Frontend stable"
```

---

## Post-Deploy Verification

Run all of these within 10 minutes of the deploy completing.

### Health endpoint

```powershell
curl -s https://api.vantro.ai/health
# Must return HTTP 200
```

### Auth endpoint (unauthenticated probe)

```powershell
curl -s -o /dev/null -w "%{http_code}" -X OPTIONS https://api.vantro.ai/api/auth/login
# Expect 200 or 204 (CORS preflight). 5xx means the backend is broken.
```

### CloudWatch — watch for errors in first 5 minutes

```powershell
aws logs tail /ecs/vantro-backend --follow --since 5m
```

Red flags to look for:
- `Exception` / `Traceback` at startup
- `alembic.exc` — migration not applied
- `asyncpg` / `sqlalchemy` connection errors
- `FINANCIAL_CONSTRAINT_BLOCK` absent from logs (means executor is broken)
- `scan_for_financial_actions` not imported / NameError

### Verify migration version in DB

Connect via RDS bastion or a one-off ECS task with `psql`, then:

```sql
SELECT version_num FROM alembic_version;
-- Must return: 021
```

One-off ECS task approach (no bastion needed):

```powershell
aws ecs run-task `
  --cluster vantro-prod `
  --task-definition vantro-backend `
  --launch-type FARGATE `
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_ID>],securityGroups=[<SG_ID>],assignPublicIp=DISABLED}" `
  --overrides '{
    "containerOverrides": [{
      "name": "vantro-backend",
      "command": ["python", "-c",
        "import os; import psycopg2; conn = psycopg2.connect(os.environ[\"DATABASE_URL\"]); cur = conn.cursor(); cur.execute(\"SELECT version_num FROM alembic_version\"); print(cur.fetchone())"]
    }]
  }'
```

### SQS queue drain check

```powershell
aws sqs get-queue-attributes `
  --queue-url https://sqs.<REGION>.amazonaws.com/<ACCOUNT_ID>/vantro-agent-jobs `
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible `
  --output table
```

After 2-3 minutes: `ApproximateNumberOfMessages` should be draining (agent_worker is picking up). If messages pile up and never move, the worker is broken — check logs.

### Run one test agent job

Log into the admin portal → run a low-stakes agent job (e.g. research or summarisation) → confirm:
- Job transitions: `pending` → `completed` (or `pending_financial_review` if financial keywords present)
- No `failed` status
- Credits deducted correctly

### Final checklist

- [ ] `/health` returns 200
- [ ] CloudWatch shows no startup exceptions
- [ ] `alembic_version` = `021`
- [ ] SQS draining
- [ ] Test job completed successfully
- [ ] No `pending_financial_review` jobs stuck in queue unexpectedly

---

## Rollback Procedure

### Rollback backend service

```powershell
# List recent task definitions (newest first)
aws ecs list-task-definitions `
  --family-prefix vantro-backend `
  --sort DESC `
  --max-results 5 `
  --output table

# Roll back to the previous revision (recorded in Pre-Deploy Checklist)
aws ecs update-service `
  --cluster vantro-prod `
  --service vantro-backend `
  --task-definition vantro-backend:<PREV_REVISION> `
  --output json | Select-String "serviceArn"

aws ecs wait services-stable `
  --cluster vantro-prod `
  --services vantro-backend
```

### Rollback frontend service

```powershell
aws ecs list-task-definitions `
  --family-prefix vantro-frontend `
  --sort DESC `
  --max-results 5 `
  --output table

aws ecs update-service `
  --cluster vantro-prod `
  --service vantro-frontend `
  --task-definition vantro-frontend:<PREV_REVISION> `
  --output json | Select-String "serviceArn"

aws ecs wait services-stable `
  --cluster vantro-prod `
  --services vantro-frontend
```

### Rollback a database migration

**Decision rule: only downgrade if zero new data was written against the new schema. Once real users have written data to a new column or table, DO NOT downgrade — you will lose data. Fix forward instead.**

If you are certain no new data was written (e.g. migration ran but deploy failed before any traffic):

```powershell
aws ecs run-task `
  --cluster vantro-prod `
  --task-definition vantro-backend:<PREV_REVISION> `
  --launch-type FARGATE `
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_ID>],securityGroups=[<SG_ID>],assignPublicIp=DISABLED}" `
  --overrides '{
    "containerOverrides": [{
      "name": "vantro-backend",
      "command": ["alembic", "downgrade", "-1"]
    }]
  }' `
  --query "tasks[0].taskArn" `
  --output text
```

Wait for it to stop and check exit code (same process as migration step above).

---

## Environment Variables / Secrets

All secrets are stored in `vantro/prod/backend` in AWS Secrets Manager as a JSON object:

```json
{
  "DATABASE_URL": "...",
  "SECRET_KEY": "...",
  "OPENAI_API_KEY": "...",
  "INTEGRATION_ENCRYPTION_KEY": "...",
  "ENVIRONMENT": "production"
}
```

### Read current secret (for auditing, never log the output)

```powershell
aws secretsmanager get-secret-value `
  --secret-id vantro/prod/backend `
  --query SecretString `
  --output text
```

### Update a single key

Pull current secret, update the key, push back:

```powershell
# 1. Get current values into a variable
$secret = aws secretsmanager get-secret-value `
  --secret-id vantro/prod/backend `
  --query SecretString `
  --output text | ConvertFrom-Json

# 2. Update the key (example: rotate OPENAI_API_KEY)
$secret.OPENAI_API_KEY = "sk-..."

# 3. Push back as JSON string
aws secretsmanager put-secret-value `
  --secret-id vantro/prod/backend `
  --secret-string ($secret | ConvertTo-Json -Compress)
```

### Apply the new secret to ECS

ECS picks up `:AWSCURRENT` automatically on the next task launch. Force a redeploy:

```powershell
aws ecs update-service `
  --cluster vantro-prod `
  --service vantro-backend `
  --force-new-deployment

aws ecs wait services-stable `
  --cluster vantro-prod `
  --services vantro-backend
```

**Security rule:** The decrypted `INTEGRATION_ENCRYPTION_KEY` and `SECRET_KEY` values must never appear in logs, API responses, or shell history. Clear your terminal history after any session that involved printing secret values.

---

## Notes

- **Financial governance is always active.** `scan_for_financial_actions` runs on every LLM response. If a deploy causes unexpected `pending_financial_review` jobs, check that `FINANCIAL_CONSTRAINT_BLOCK` is still prepended in `agent_executor.py` — it must survive any refactor.
- **OpenAPI docs are disabled in production.** `ENVIRONMENT=production` in Secrets Manager enforces `docs_url=None`. Never set `ENVIRONMENT=development` in production secrets.
- **Server header is suppressed.** `SecurityHeadersMiddleware` in `app/main.py` strips the `Server` header. Verify with: `curl -I https://api.vantro.ai/health | grep -i server` — should return nothing.
- **HITL-3 jobs** (Opus-tier, spend approval) will be held `pending_approval` after deploy. This is correct behavior — they require manual owner approval before the worker executes them.
- **Skill RAG re-indexes** on startup and every 6 hours automatically. No action needed after deploy unless you added new skills to `~/.claude/skills/` and want to force-index: `POST /api/admin/skills/index` (admin token required).
