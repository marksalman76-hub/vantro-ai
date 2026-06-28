# Agent Worker Operations Runbook — Vantro.ai

**Owner:** mark.salman76@gmail.com  
**Service:** `vantro-backend` ECS Fargate task (agent_worker embedded in FastAPI lifespan)  
**Log group:** `/ecs/vantro-backend`  
**CW metrics namespace:** `Vantro/AgentJobs`  
**SQS queue:** `vantro-agent-jobs` _(future dedicated worker; current worker polls DB directly)_  
**Last updated:** 2026-06-28

---

## Architecture quick reference

```
POST /api/agents/{id}/run
        │
        ▼
AgentJob row  status=pending
        │
        ▼
run_agent_worker() — asyncio loop, polls every 5 s
  MAX_CONCURRENT_JOBS = 3  (semaphore-gated)
        │
        ▼
_process_job(job_id)
  1. status → running
  2. Inject: workspace business_context, brand_profile, workspace memory
  3. RAG: retrieve_relevant_skills()  (requires OPENAI_API_KEY)
  4. Few-shot: get_few_shot_examples()
  5. Composio creds: get_composio_credentials()
        │
        ▼
execute_agent()
  Prompt order: FINANCIAL_CONSTRAINT_BLOCK → INJECTION_GUARD → AGENT_BOUNDARY_BLOCK
                → few-shot → skill context → brand_profile → agent core
  Provider: Anthropic primary (HITL model map below) → OpenAI gpt-4o fallback
  Tool-use: up to 5 rounds (analytics tools + Composio tools if connected)
  Timeout: 90 s per LLM call
  scan_for_financial_actions() on every response
        │
        ▼
status → completed | pending_financial_review | failed | pending_approval
```

**HITL model map**
| HITL level | Model | Use case |
|---|---|---|
| HITL-0 | Haiku | Low-stakes, high-volume |
| HITL-1/2 | Sonnet (primary) | Standard agents |
| HITL-3 | Opus | Spend/scale approval — job held `pending_approval` first |

**Periodic tasks running inside the worker loop**
| Task | Interval |
|---|---|
| Stale job recovery (`_recover_stale_jobs`) | 60 s |
| Skill RAG reindex (`_reindex_new_skills`) | 6 h (fires immediately on startup) |
| Weekly report scheduler (`_run_weekly_reports`) | 1 h |
| Scheduled agent runs (`_run_scheduled_agents`) | 5 min |
| Billing reminder emails | 24 h |
| Data retention sweep (jobs >90d, audit >365d, webhooks >30d) | 24 h |

---

## 1. Worker Health Check

### 1.1 Verify ECS task is running

```bash
aws ecs describe-services \
  --cluster vantro-prod \
  --services vantro-backend \
  --query 'services[0].{running:runningCount,desired:desiredCount,pending:pendingCount}' \
  --region <REGION>
```

Expected: `running == desired` (typically 1). If `running == 0` the worker is down — see section 2.

### 1.2 Tail worker logs

```bash
# All worker activity
aws logs tail /ecs/vantro-backend --follow --filter-pattern "agent_worker" --region <REGION>

# Job completions only
aws logs tail /ecs/vantro-backend --follow \
  --filter-pattern '"Job" "completed"' --region <REGION>

# Errors only
aws logs tail /ecs/vantro-backend --follow \
  --filter-pattern '"ERROR"' --region <REGION>
```

### 1.3 Check SQS queue depth (future dedicated worker)

```bash
aws sqs get-queue-attributes \
  --queue-url https://sqs.<REGION>.amazonaws.com/<ACCOUNT_ID>/vantro-agent-jobs \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible \
  --region <REGION>
```

### 1.4 Check CloudWatch custom metrics

```bash
# Jobs completed in the last hour
aws cloudwatch get-metric-statistics \
  --namespace Vantro/AgentJobs \
  --metric-name AgentJobsCompleted \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  --region <REGION>

# Jobs failed in the last hour
aws cloudwatch get-metric-statistics \
  --namespace Vantro/AgentJobs \
  --metric-name AgentJobsFailed \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  --region <REGION>
```

### 1.5 Quick DB job counts

```sql
SELECT status, count(*) 
FROM agent_jobs 
GROUP BY status 
ORDER BY count(*) DESC;
```

### Signs of a healthy worker
- Logs show `"Worker: executing agent=<id> job=<id>"` followed by `"Worker: job <id> completed via anthropic/..."` cycling through.
- `pending` count in DB stays near 0 (jobs picked up within 5–10 s of creation).
- `AgentJobsCompleted` metric is incrementing; `AgentJobsFailed` is low.

### Signs of a sick worker
- No `"Worker: executing"` log lines in the past 5 minutes.
- `pending` count in DB is growing and not draining.
- ECS `runningCount == 0` or task in `STOPPED` state.
- `AgentJobsFailed` spiking without corresponding `AgentJobsCompleted`.
- CloudWatch logs show repeated `"Worker poll error:"` entries.

---

## 2. Stuck Job Recovery

Jobs stuck in `pending` or `running` for >15 minutes are automatically force-failed by `_recover_stale_jobs()` (runs every 60 s). Credits are refunded automatically on force-fail. If auto-recovery isn't working, follow these steps.

### Step 1 — Identify stuck jobs

```sql
SELECT id, status, agent_id, workspace_id, created_at, updated_at, error_message
FROM agent_jobs
WHERE status IN ('pending', 'running')
  AND created_at < NOW() - INTERVAL '15 minutes'
ORDER BY created_at;
```

### Step 2 — Verify worker is alive

Run the health check in section 1. If the worker is down, fix that first (step 3).

### Step 3 — Restart the worker (if down)

```bash
aws ecs update-service \
  --cluster vantro-prod \
  --service vantro-backend \
  --force-new-deployment \
  --region <REGION>

# Watch rollout
aws ecs wait services-stable \
  --cluster vantro-prod \
  --services vantro-backend \
  --region <REGION>
```

After restart, the worker calls `_recover_stale_jobs()` within 60 s of first poll. Verify stuck jobs moved to `failed` in the DB.

### Step 4 — Manually fail a stuck job (if worker is alive but job is stuck)

Reasons a job stays `running` with a live worker: runaway LLM call (90 s timeout usually catches this), Composio integration timeout, DB commit failure mid-execution.

```sql
-- First verify the job is genuinely stuck (still running, no recent updated_at)
SELECT id, status, agent_id, updated_at FROM agent_jobs WHERE id = '<job_id>';

-- Manually fail it (credits are refunded by the stale-job auto-recovery; 
-- if doing this manually before auto-recovery fires, also zero out credits_used)
UPDATE agent_jobs
SET status = 'failed',
    error_message = 'Job timed out — manually failed by operator',
    credits_used = 0,
    updated_at = NOW()
WHERE id = '<job_id>'
  AND status IN ('pending', 'running');

-- Verify
SELECT id, status, credits_used, error_message FROM agent_jobs WHERE id = '<job_id>';
```

**Note on credit refund:** The worker auto-refunds pre-committed credits when it sets a job to `failed`. If you manually fail a job, also refund credits manually:

```sql
-- Find the workspace credits account and refund
UPDATE credits_accounts ca
SET used_credits = GREATEST(0, ca.used_credits - aj.credits_used),
    updated_at = NOW()
FROM agent_jobs aj
JOIN workspaces w ON w.id = aj.workspace_id
WHERE ca.workspace_id = aj.workspace_id
  AND aj.id = '<job_id>';
```

### Step 5 — Check for runaway tool-use loop

```bash
# Look for a job cycling through tool_use rounds repeatedly
aws logs filter-log-events \
  --log-group-name /ecs/vantro-backend \
  --filter-pattern '"tool_use"' \
  --region <REGION> \
  --query 'events[*].message' \
  --output text | grep '<job_id>'
```

The executor caps tool-use at 5 rounds (`for _ in range(5)`). A true infinite loop is only possible if the worker itself has hung. Force-restart ECS in that case (step 3).

---

## 3. Financial Review Queue

When `scan_for_financial_actions()` detects a matched phrase (e.g. "i have authorised", "budget allocated", "order confirmed") in the agent's output, the job is routed to `pending_financial_review` and an email is sent to `mark.salman76@gmail.com`.

The matched phrase list lives in `backend/app/agents/agent_executor.py` → `FINANCIAL_ACTION_PATTERNS`.

### Step 1 — List the queue

**Via admin API:**
```bash
curl -s "https://api.vantro.ai/api/admin/jobs?status=pending_financial_review" \
  -H "Authorization: Bearer <ADMIN_JWT>" | jq '.'
```

**Via SQL:**
```sql
SELECT id, workspace_id, agent_id, created_at,
       LEFT(output_data, 500) AS output_preview
FROM agent_jobs
WHERE status = 'pending_financial_review'
ORDER BY created_at DESC;
```

### Step 2 — Identify the matched phrase

The email from the worker includes the matched phrase. You can also find it in the log:

```bash
aws logs filter-log-events \
  --log-group-name /ecs/vantro-backend \
  --filter-pattern '"held for financial review"' \
  --region <REGION> \
  --query 'events[*].message' \
  --output text
```

Read the full output in the DB:
```sql
SELECT output_data FROM agent_jobs WHERE id = '<job_id>';
```

### Step 3 — Decision

**Safe output (false positive) — release as completed:**
```sql
UPDATE agent_jobs
SET status = 'completed',
    updated_at = NOW()
WHERE id = '<job_id>'
  AND status = 'pending_financial_review';
```

**Genuine financial action attempt — block and investigate:**
```sql
UPDATE agent_jobs
SET status = 'failed',
    error_message = 'Financial action blocked by governance policy',
    updated_at = NOW()
WHERE id = '<job_id>'
  AND status = 'pending_financial_review';
```

Then investigate the workspace: check the task input for prompt injection, review the agent config, consider banning the task pattern.

### Step 4 — Fix false positives permanently

If the matched phrase is a safe false positive (e.g. "payment has been made" appearing in a quoted customer testimonial), add it to the ignore logic in:

`backend/app/agents/agent_executor.py` → `scan_for_financial_actions()`

The current implementation is a substring match against `FINANCIAL_ACTION_PATTERNS`. The simplest fix is to narrow the pattern or add a context-aware exclusion before the match loop. Deploy the fix via normal ECS deployment.

---

## 4. HITL-3 Approval Queue

HITL-3 agents (Opus-level) write a `pending_approval` job row and hold until the owner approves. The workspace user sees a "pending approval" state in their dashboard and is notified by email. SLA: review within 4 business hours — the user is blocked.

A second path to `pending_approval`: any job where the agent output contains `[CONFIDENCE: LOW]` is escalated regardless of HITL level.

### Step 1 — List pending approvals

**Via admin API:**
```bash
curl -s "https://api.vantro.ai/api/admin/jobs?status=pending_approval" \
  -H "Authorization: Bearer <ADMIN_JWT>" | jq '.'
```

**Via SQL:**
```sql
SELECT id, workspace_id, agent_id, hitl_level, created_at,
       LEFT(input_data, 300) AS task_preview
FROM agent_jobs
WHERE status = 'pending_approval'
ORDER BY created_at;
```

### Step 2 — Review a specific job

```bash
curl -s "https://api.vantro.ai/api/admin/jobs/<job_id>" \
  -H "Authorization: Bearer <ADMIN_JWT>" | jq '.'
```

Check: workspace, agent_id, task input. For HITL-3 agents this is a spend/scale/high-stakes operation. For `[CONFIDENCE: LOW]` escalations, read the partial output to decide.

### Step 3 — Approve

```bash
curl -s -X POST "https://api.vantro.ai/api/admin/jobs/<job_id>/approve" \
  -H "Authorization: Bearer <ADMIN_JWT>" \
  -H "Content-Type: application/json"
```

After approval the job transitions to `approved`. The worker picks it up on the next 5 s poll (checks `status IN ('pending', 'approved')`).

### Step 4 — Reject

```bash
curl -s -X POST "https://api.vantro.ai/api/admin/jobs/<job_id>/reject" \
  -H "Authorization: Bearer <ADMIN_JWT>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Out of scope — manual review required"}'
```

### Step 5 — Bulk check (SQL)

```sql
-- All pending_approval jobs older than 4 hours
SELECT id, workspace_id, agent_id, hitl_level, created_at,
       NOW() - created_at AS age
FROM agent_jobs
WHERE status = 'pending_approval'
  AND created_at < NOW() - INTERVAL '4 hours'
ORDER BY created_at;
```

---

## 5. Skill RAG Reindex

Skills live in `~/.claude/skills/*/SKILL.md` on the ECS task's filesystem (or S3-backed volume). The worker auto-indexes on startup and every 6 hours via `_reindex_new_skills()`. This requires `OPENAI_API_KEY` — it silently skips if the key is missing (no error is raised, no log warning).

If agents are returning irrelevant RAG results or you've installed new skills:

### Step 1 — Trigger manual reindex

```bash
curl -s -X POST "https://api.vantro.ai/api/admin/skills/index" \
  -H "Authorization: Bearer <ADMIN_JWT>" \
  -H "Content-Type: application/json"
```

### Step 2 — Verify it ran

```bash
# CloudWatch: look for "Indexed N skill chunks"
aws logs filter-log-events \
  --log-group-name /ecs/vantro-backend \
  --filter-pattern '"skill auto-index complete"' \
  --region <REGION> \
  --query 'events[*].message' \
  --output text
```

```sql
-- Check total indexed chunks
SELECT count(*) AS total_chunks FROM skill_chunks;

-- Check which skills are indexed and when
SELECT skill_name, indexed_at 
FROM skill_chunks 
GROUP BY skill_name, indexed_at 
ORDER BY indexed_at DESC;
```

### Step 3 — Diagnose if reindex is silently skipping

```bash
# Verify OPENAI_API_KEY is present in ECS task environment
aws ecs describe-task-definition \
  --task-definition vantro-backend \
  --query 'taskDefinition.containerDefinitions[0].environment' \
  --region <REGION> | grep -i openai

# Or check Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id vantro/prod/openai-api-key \
  --region <REGION> \
  --query 'SecretString' --output text | python3 -c "import sys,json; d=json.load(sys.stdin); print('OPENAI_API_KEY present:', bool(d.get('OPENAI_API_KEY')))"
```

If `OPENAI_API_KEY` is missing from the task definition env, add it via Secrets Manager injection in the ECS task definition and redeploy.

### Step 4 — Force re-index all skills (not just new/updated)

If you need a full wipe and reindex:
```sql
-- Wipe existing chunks
TRUNCATE TABLE skill_chunks;
```
Then trigger manual reindex (step 1). The indexer will re-embed all skills.

---

## 6. Kill a Runaway Agent Job

Symptoms: CloudWatch logs show the same job ID in repeated tool-use calls, or a job has been `running` for >5 minutes (normal jobs complete in 30–90 s).

### Step 1 — Identify the runaway

```bash
# Find job IDs that appear repeatedly in tool_use logs
aws logs filter-log-events \
  --log-group-name /ecs/vantro-backend \
  --filter-pattern '"tool_use"' \
  --start-time $(date -u -d '10 minutes ago' +%s000) \
  --region <REGION> \
  --query 'events[*].message' \
  --output text
```

```sql
-- Jobs running longer than 5 minutes
SELECT id, agent_id, workspace_id, updated_at, NOW() - updated_at AS running_for
FROM agent_jobs
WHERE status = 'running'
  AND updated_at < NOW() - INTERVAL '5 minutes'
ORDER BY updated_at;
```

### Step 2 — Mark the job failed

```sql
UPDATE agent_jobs
SET status = 'failed',
    error_message = 'Killed by operator — runaway tool loop',
    credits_used = 0,
    updated_at = NOW()
WHERE id = '<job_id>'
  AND status = 'running';
```

**Note:** The worker does not currently re-check job status mid-execution (the LLM call is blocking inside `asyncio.run_in_executor`). The DB update will prevent the worker from re-picking the job after it finishes, but it will NOT abort an in-flight LLM call. To hard-kill an in-flight call, force-restart the ECS task (step 3).

### Step 3 — Force-restart the worker

```bash
aws ecs update-service \
  --cluster vantro-prod \
  --service vantro-backend \
  --force-new-deployment \
  --region <REGION>
```

The old task is stopped (killing any in-flight LLM calls). The new task starts, picks up `pending` jobs only (the runaway job is now `failed`).

### Step 4 — Investigate root cause

- Check what tool the agent was calling when it looped.
- Check whether the Composio integration for that workspace is valid: `GET /api/admin/workspaces/<workspace_id>/integrations`.
- Check whether the agent prompt is triggering a reflexive tool-use pattern (agent calls tool → result triggers another call indefinitely). The executor caps at 5 rounds; if the loop completed 5 rounds and still returned no `end_turn`, the model returned `[Agent did not produce a text response]` — check the output_data.
- If a specific agent is repeatedly causing loops, review its prompt in `backend/app/agents/agent_prompts.py`.

---

## 7. Worker Configuration Reference

**Key constants in `backend/app/agents/agent_worker.py`:**

| Constant | Value | Notes |
|---|---|---|
| `POLL_INTERVAL_SECONDS` | 5 | How often worker checks DB for new jobs |
| `MAX_CONCURRENT_JOBS` | 3 | Semaphore; increase cautiously (LLM rate limits) |
| `STALE_JOB_MINUTES` | 15 | Jobs `running` longer than this are auto-failed |
| `STALE_CHECK_INTERVAL` | 60 s | How often `_recover_stale_jobs()` runs |
| `SKILL_REINDEX_INTERVAL` | 21600 s (6 h) | Auto-reindex fires immediately on startup too |
| `LLM_TIMEOUT_S` | 90 | Per-LLM-call timeout in `agent_executor.py` |
| `MAX_TOKENS` | 4096 | Max output tokens per LLM call |
| `TOKENS_PER_CREDIT` | 1000 | 1 credit = 1,000 tokens |

**Environment variable flags:**

| Variable | Effect |
|---|---|
| `TESTING=1` | Prevents worker loop from starting — **never set in prod** |
| `ANTHROPIC_API_KEY` | Primary LLM provider key |
| `OPENAI_API_KEY` | Fallback LLM provider + skill RAG embeddings |
| `ADMIN_EMAIL` | Receives financial review alert emails (set to `mark.salman76@gmail.com`) |
| `INTEGRATION_ENCRYPTION_KEY` | Fernet key for WorkspaceIntegration credentials |

**Credit deduction timing:**

Credits are deducted in `_process_job()` after `execute_agent()` returns — based on real token usage, not the pre-committed estimate. The delta (actual − pre-committed) is applied to `credits_accounts.used_credits`. If the job fails before `execute_agent()` returns, the pre-committed credits are refunded (set to 0) in the `except` block. No partial charges.

---

## 8. Common Failure Scenarios

| Symptom | Likely cause | Fix |
|---|---|---|
| All jobs stuck `pending` | Worker crash / ECS task stopped | Section 1 health check → section 2 step 3 restart |
| Job stuck `running` >15 min | LLM call hung, Composio timeout | Auto-recovery fires at 60 s; manual: section 2 step 4 |
| `pending_financial_review` spike | Model output matching financial patterns, possibly false positives | Section 3 — review + either release or add to exclusion list |
| Skill RAG returning garbage | Skills not indexed, `OPENAI_API_KEY` missing | Section 5 |
| `No LLM provider is configured` error in logs | `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` both missing or invalid | Check Secrets Manager → redeploy |
| `Both providers failed` error | Network issue or API key revoked | Check CloudWatch logs for upstream error → verify keys |
| HITL-3 jobs never executing | Waiting for approval | Section 4 approval queue |
| `[CONFIDENCE: LOW]` jobs stuck `pending_approval` | Agent uncertain, escalated for human review | Section 4 — review and approve/reject |
| Tool-use jobs returning `[Agent did not produce a text response]` | 5-round tool-use limit hit without `end_turn` | Investigate prompt + Composio tool behaviour; section 6 |
| Credits not refunding on failure | `credits_used` set to 0 on `failed` jobs; credits_account delta correction may fail if DB is down during exception path | Manually run credit refund SQL from section 2 step 4 |
