# Vantro.ai Launch Master Document

**Owner:** Mark Salman (mark.salman76@gmail.com)
**Platform:** Multi-tenant SaaS — 27 AI agents automating e-commerce and marketing workflows
**Stack:** FastAPI / ECS Fargate · Next.js 16 / Vercel · PostgreSQL RDS · SQS · Secrets Manager · CloudWatch

---

## Overview

Vantro.ai is a multi-tenant AI agent platform. Organizations create Workspaces, buy Credits, and dispatch any of 27 specialised agents (starter → enterprise tiers). Every agent job goes through a governed pipeline: credit gate → HITL tier check → LLM execution → financial scanner → credit deduction. Financial actions are never executed autonomously — any agent output containing spend/scale/sign language is held in `pending_financial_review` and emailed to the admin. HITL-3 jobs additionally hold at `pending_approval` until the owner manually unblocks them via `/admin`.

---

## Launch Timeline

| Phase | Date (T-) | Owner | Key Activities |
|-------|-----------|-------|----------------|
| **T-7** | 7 days before | Mark | Run `alembic upgrade head` against production RDS; confirm current head is `021_team_runs.py`. Pin ECS task definition to the release image digest. Create CloudWatch log groups: `/ecs/vantro-backend`, `/ecs/vantro-worker`. Enable RDS automated backups (7-day retention). Snapshot RDS manually: `aws rds create-db-snapshot --db-instance-identifier vantro-prod --db-snapshot-identifier vantro-pre-launch-t7`. |
| **T-3** | 3 days before | Mark | Populate Secrets Manager with all 4 required secrets: `ANTHROPIC_API_KEY`, `DATABASE_URL`, `SECRET_KEY`, `INTEGRATION_ENCRYPTION_KEY`. Set `ENVIRONMENT=production` in ECS task definition env vars. Set `AGENTS_MAY_NOT_SPEND=True`, `AGENTS_MAY_NOT_SCALE_PAID=True`, `AGENTS_MAY_NOT_SIGN_AGREEMENTS=True`. Smoke-test all 27 agent endpoints via staging: `POST /api/agents/{id}/run` for each. Confirm `/docs` returns 404 in staging with `ENVIRONMENT=production`. Register Stripe live webhook at `https://api.vantro.ai/api/stripe/webhook`. |
| **T-1** | 1 day before | Mark | Stage DNS cutover in Route 53 (low TTL — set TTL=60 24h in advance). Activate Stripe live keys. Take final pre-launch RDS snapshot: `aws rds create-db-snapshot --db-instance-identifier vantro-prod --db-snapshot-identifier vantro-pre-launch-final`. Run full Go/No-Go checklist (see below) — all hard blockers must be green. Verify `len(AGENT_CATALOGUE) == 27` in a live Python shell against production image. Test HITL-3 flow end-to-end on staging: submit a HITL-3 agent job → confirm `pending_approval` status → approve via `/admin` → confirm execution. |
| **T-0 (Launch Day)** | Launch | Mark | Deploy ECS service: `aws ecs update-service --cluster vantro-prod --service vantro-backend --force-new-deployment`. Verify SQS queue `vantro-agent-jobs` is live and consumer (worker) is pulling messages. Confirm health checks pass: `GET /health` returns 200 on all ECS tasks. Confirm CloudWatch "Vantro/AgentJobs" custom metrics are publishing. Flip DNS cutover in Route 53. Post launch announcement. Monitor admin portal at `/admin` for first 2 hours. |
| **T+7** | 7 days after | Mark | Pull CloudWatch "Vantro/AgentJobs" metrics dashboard — review completion rate, failure rate, and HITL queue depth. Audit credit deduction accuracy: spot-check 20 completed jobs, verify `credits_used = tokens_used / 1000` (TOKENS_PER_CREDIT=1000). Review `pending_financial_review` queue — every entry should be a genuine flag. Review `pending_approval` queue depth (target: cleared within 24h). Check RDS connection count trends. Review auth rate limit hits in CloudWatch. Rotate `SECRET_KEY` if any suspicion of exposure (requires re-signing all JWTs). |

---

## Key Metrics to Track at Launch

| Metric | Target | Where to Check |
|--------|--------|----------------|
| Agent job completion rate | >95% | CloudWatch namespace `Vantro/AgentJobs`, metric `job_completed` vs `job_failed` |
| Credit deduction accuracy | 100% — `tokens_used / TOKENS_PER_CREDIT` applied on every completed job | `CreditsAccount` table, spot-check via admin portal or direct SQL |
| Workspace creation success rate | >99% | CloudWatch or RDS query on `workspaces` table creation timestamps vs errors |
| HITL-3 approval queue depth | <5 pending at any time | `/admin` portal HITL queue view, or `SELECT COUNT(*) FROM agent_jobs WHERE status='pending_approval'` |
| `pending_financial_review` queue | 0 unless genuine flag — any entry triggers admin email to mark.salman76@gmail.com | `/admin` portal or `SELECT * FROM agent_jobs WHERE status='pending_financial_review'` |
| ECS task CPU | <70% sustained | CloudWatch ECS metrics, `CPUUtilization` per task |
| ECS task memory | <70% sustained | CloudWatch ECS metrics, `MemoryUtilization` per task |
| Auth rate limit hits | <1% of login attempts | CloudWatch or FastAPI rate-limit middleware logs (`/ecs/vantro-backend`) |
| RDS connection count | <80% of `max_connections` | CloudWatch RDS `DatabaseConnections` metric; tune SQLAlchemy pool size if approaching limit |
| SQS queue depth | <50 messages (worker keeping up) | CloudWatch SQS `ApproximateNumberOfMessagesVisible` for `vantro-agent-jobs` |

---

## Go / No-Go Criteria

Run this checklist on **T-1**. Every hard blocker must be green before flipping DNS on T-0.

### Hard Blockers (ALL must pass)

- [ ] `alembic upgrade head` runs clean against production RDS with no errors — current head confirmed as revision `021`

  ```bash
  # From backend/ with production DATABASE_URL set
  alembic upgrade head
  alembic current  # must show: 021_team_runs (head)
  ```

- [ ] `len(AGENT_CATALOGUE) == 27` assertion passes in production image

  ```bash
  # Exec into running ECS task or run locally with prod env
  python -c "from app.agents.agent_registry import AGENT_CATALOGUE; assert len(AGENT_CATALOGUE) == 27, f'Got {len(AGENT_CATALOGUE)}'; print('PASS: 27 agents')"
  ```

- [ ] `ENVIRONMENT=production` → OpenAPI docs disabled — `curl https://api.vantro.ai/docs` returns 404

  ```bash
  curl -o /dev/null -w "%{http_code}" https://api.vantro.ai/docs   # must be 404
  curl -o /dev/null -w "%{http_code}" https://api.vantro.ai/redoc  # must be 404
  ```

- [ ] Financial governance env vars confirmed in ECS task definition

  ```bash
  # Check via AWS CLI or ECS console
  aws ecs describe-task-definition --task-definition vantro-backend \
    --query 'taskDefinition.containerDefinitions[0].environment'
  # Must show: AGENTS_MAY_NOT_SPEND=True, AGENTS_MAY_NOT_SCALE_PAID=True, AGENTS_MAY_NOT_SIGN_AGREEMENTS=True
  ```

- [ ] Financial scanner active: submit a test job where output contains "I will purchase" — confirm job routes to `pending_financial_review` (not `completed`)

- [ ] `Server` header absent from all API responses

  ```bash
  curl -I https://api.vantro.ai/health | grep -i server
  # Must return nothing — SecurityHeadersMiddleware is stripping it
  ```

- [ ] Stripe live keys configured in Secrets Manager; webhook endpoint `https://api.vantro.ai/api/stripe/webhook` registered and signature verified in Stripe dashboard

- [ ] RDS automated backups enabled, 7-day retention — verify in RDS console under Maintenance & backups

- [ ] `ANTHROPIC_API_KEY` loaded from Secrets Manager, NOT from a `.env` file bundled in the image

  ```bash
  # Confirm no .env file in the Docker image
  docker run --rm <image> ls -la /app/.env  # must fail or be absent
  ```

- [ ] `INTEGRATION_ENCRYPTION_KEY` set — `WorkspaceIntegration` Fernet encryption live: create a test integration, verify `encrypted_value` column is populated and the raw key value does not appear in any API response

- [ ] HITL-3 end-to-end flow: submit a HITL-3 agent job → status is `pending_approval` → approve via `/admin` → worker picks up and executes → status transitions to `completed`

### Soft Checks (warn, do not block launch)

- [ ] Stripe Customer Portal live and accessible to workspace owners
- [ ] Welcome email flow firing: new user registration triggers `send_welcome` in auth router — verify via email delivery log
- [ ] Skill RAG auto-indexing working: `OPENAI_API_KEY` set in ECS task definition; check startup logs for "Skill RAG indexed N chunks" in `/ecs/vantro-backend`; manual trigger: `POST /api/admin/skills/index`

---

## Stakeholder Sign-Off

| Domain | Sign-Off Owner | Status | Date |
|--------|---------------|--------|------|
| Technical / Backend | Mark Salman | [ ] | |
| Technical / Frontend | Mark Salman | [ ] | |
| Security | Mark Salman | [ ] | |
| Billing / Stripe | Mark Salman | [ ] | |
| Operations / AWS | Mark Salman | [ ] | |
| Go-to-Market | Mark Salman | [ ] | |

---

## Emergency Contacts & Rollback

### Contacts
- Admin portal: `https://vantro.ai/admin` — login: mark.salman76@gmail.com
- CloudWatch dashboard: namespace `Vantro/AgentJobs`, region where ECS cluster is deployed
- AWS account: access via IAM console or `aws sts get-caller-identity` to confirm

### Rollback Procedure

**ECS service rollback** (bad deploy — new task crashes or health checks fail):

```bash
# List recent task definitions
aws ecs list-task-definitions --family-prefix vantro-backend --sort DESC

# Roll back to previous stable revision (replace N with the last known-good revision number)
aws ecs update-service \
  --cluster vantro-prod \
  --service vantro-backend \
  --task-definition vantro-backend:N
```

**Database rollback** (bad migration):

```bash
# Downgrade one revision
alembic downgrade -1

# Or downgrade to a specific revision
alembic downgrade 020

# If catastrophic, restore from RDS automated snapshot via AWS console:
# RDS → Databases → vantro-prod → Actions → Restore to point in time
# Or from manual snapshot: aws rds restore-db-instance-from-db-snapshot
```

**Critical: JWT signing key**

If `SECRET_KEY` changes during rollback (restoring from old snapshot), all existing JWT tokens are invalidated — all users will be logged out. This is acceptable in a break-glass scenario. Confirm the `SECRET_KEY` in Secrets Manager matches the one used to sign JWTs in the environment you are rolling back to.

```bash
# Verify current SECRET_KEY in Secrets Manager
aws secretsmanager get-secret-value --secret-id vantro/prod/SECRET_KEY --query SecretString
```

**SQS message drain** (if worker is crashing and re-processing bad messages):

```bash
# Purge the queue to stop retries (DESTRUCTIVE — loses in-flight jobs)
aws sqs purge-queue --queue-url https://sqs.<region>.amazonaws.com/<account>/vantro-agent-jobs

# Or set redrive policy to dead-letter queue and stop the worker ECS service
aws ecs update-service --cluster vantro-prod --service vantro-worker --desired-count 0
```

**Incident checklist during an outage:**
1. Check ECS task status: `aws ecs list-tasks --cluster vantro-prod --service-name vantro-backend`
2. Pull logs: CloudWatch → log group `/ecs/vantro-backend` → most recent log stream
3. Check RDS: connection count, CPU — if DB is the bottleneck, scale instance class or reduce SQLAlchemy pool size
4. Check SQS queue depth: if >1000, worker is down — check `/ecs/vantro-worker` logs
5. If `pending_financial_review` queue is flooding: a financial scanner trigger loop — check `scan_for_financial_actions()` in `agent_executor.py` for a pattern match bug
6. Rollback ECS to previous task definition revision if deploy is the cause
