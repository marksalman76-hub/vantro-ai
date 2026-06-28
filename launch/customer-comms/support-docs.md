# Vantro.ai — Internal Support Team Knowledge Base

**Classification:** Internal Only — Do not share with customers
**Maintained by:** Mark Salman (mark.salman76@gmail.com)
**Last updated:** 2026-06-27

---

## Table of Contents

1. [How Credits Work](#1-how-credits-work)
2. [Agent Job Lifecycle](#2-agent-job-lifecycle)
3. [HITL-3 Explained](#3-hitl-3-explained)
4. [Financial Review Queue](#4-financial-review-queue)
5. [Common User Errors and Responses](#5-common-user-errors-and-responses)
6. [Manual Credit Refund](#6-manual-credit-refund)
7. [Integration Issues](#7-integration-issues)
8. [Escalation Path](#8-escalation-path)
9. [Useful Support Queries](#9-useful-support-queries)

---

## 1. How Credits Work

### Credit Account Structure

Every workspace has exactly one row in `credits_accounts`. Two fields govern spending:

| Field | Description |
|---|---|
| `balance` | Available credits the workspace can spend right now |
| `reserved` | Credits held in escrow while a job is actively running (prevents double-spend) |

**Effective available credits** = `balance - reserved`. This is what the frontend shows users.

### Credit Flow During a Job

**On job start:**
- `reserved += job_estimate` (credits held)
- `balance -= job_estimate` (credits deducted upfront)

**On job completion (success):**
- `reserved -= job_estimate`
- Net effect: balance is already reduced from job start; no further change

**On job failure:**
- `balance += job_estimate` (refund issued automatically)
- `reserved -= job_estimate` (hold released)
- Net effect: credits fully restored to the workspace

> **Note:** The automatic refund on failure is handled by `agent_worker._process_job()`. If you see a failed job where credits were NOT refunded, escalate to Tier 2 — this indicates a worker crash mid-job that bypassed the cleanup path.

### Checking a Workspace's Credit Balance

```sql
-- Check current balance and reserved credits for a workspace
SELECT
    ca.balance,
    ca.reserved,
    (ca.balance - ca.reserved) AS effective_available,
    w.name AS workspace_name
FROM credits_accounts ca
JOIN workspaces w ON w.id = ca.workspace_id
WHERE ca.workspace_id = 'YOUR-WORKSPACE-UUID-HERE';
```

### Manually Topping Up Credits

**Safety rule: always log every manual top-up in `audit_logs`. Never skip this.**

```sql
-- Step 1: Confirm current balance before touching anything
SELECT balance, reserved FROM credits_accounts WHERE workspace_id = 'X';

-- Step 2: Add credits
UPDATE credits_accounts
SET balance = balance + 100  -- replace 100 with agreed top-up amount
WHERE workspace_id = 'X';

-- Step 3: Write audit log entry (see Section 6 for full INSERT)
```

Confirm the top-up amount with the workspace owner before running the UPDATE. If adding credits to resolve a billing dispute, loop in Tier 3 first.

### Stripe Top-Up Flow

When a user completes a Stripe checkout for a credit pack:

1. Stripe fires a `checkout.session.completed` webhook to the backend
2. The webhook handler verifies the event signature and resolves the workspace via `metadata.workspace_id`
3. `credits_accounts.balance` is incremented by the purchased amount
4. An audit log entry is written with `action = 'stripe_credit_topup'`
5. User sees updated balance immediately on next page load

If a user says "I paid but my credits didn't arrive":
- Check Stripe dashboard for the payment event and whether the webhook delivered successfully (look for failed webhook attempts)
- Check `audit_logs` for a recent `stripe_credit_topup` entry for that workspace
- If the webhook failed, you can manually top up (Section 6) and log it with `action = 'manual_credit_topup_stripe_recovery'`

---

## 2. Agent Job Lifecycle

### Status Flow

```
[User submits job]
        |
        v
    PENDING ──────────────────────────────────────────────────────► PENDING_APPROVAL
        |                                                            (HITL-3 agents only)
        |  (worker picks up job)                                           |
        |                                                    (owner approves via admin portal)
        v                                                                  |
    RUNNING ◄─────────────────────────────────────────────────────────────┘
        |
        ├──────────────────────────────► COMPLETED
        |                                 (normal path)
        |
        ├──────────────────────────────► FAILED
        |                                 (auto-refund credits)
        |
        └──────────────────────────────► PENDING_FINANCIAL_REVIEW
                                          (output scanner flagged response)
```

### Status Reference

#### `pending`
- **Meaning:** Job has been written to `agent_jobs`, credits have been reserved and deducted, waiting for the worker loop to pick it up.
- **Expected duration:** Under 30 seconds in normal operation. The worker polls every few seconds.
- **If stuck:** A job stuck in `pending` for more than 2 minutes suggests the worker is down or the SQS queue is backed up. Escalate to Tier 2. Check ECS task health and SQS queue depth.

#### `running`
- **Meaning:** Worker has claimed the job and is actively calling the LLM pipeline. Credits are still reserved.
- **Expected duration:** 10 seconds to 5 minutes depending on agent complexity. High-context agents (e.g. deep research, competitive analysis) can take longer.
- **If stuck:** A job stuck in `running` for more than 15 minutes suggests a worker crash mid-execution. The job will NOT self-recover — escalate to Tier 2. Check CloudWatch logs for the ECS task. Credits may need to be manually refunded (Section 6).

#### `completed`
- **Meaning:** Agent finished successfully. Result is stored in `agent_jobs.result` (JSONB). Credits remain deducted.
- **Expected duration:** Terminal state.
- **If user disputes the output:** Review `agent_jobs.result` directly. Do not re-run the job automatically — direct user to submit a new job.

#### `failed`
- **Meaning:** Agent encountered an error. `agent_jobs.error_message` contains the internal error (do not share raw error messages with users — they may contain stack traces or internal detail). Credits auto-refunded.
- **Expected duration:** Terminal state.
- **Support action:** Check `error_message` for root cause. Common causes: malformed user input, integration credential expired, LLM timeout. See Section 5.2.

#### `pending_financial_review`
- **Meaning:** The agent produced output but the output scanner detected a phrase associated with financial action (e.g. "purchase", "subscribe", "commit budget"). The output is held pending human review. Credits remain deducted until the job is released or rejected.
- **Expected duration:** Should be reviewed within 4 business hours by an admin.
- **If stuck:** Check the Financial Review queue in the admin portal. Escalate to Tier 3 if queue has not been cleared within 8 hours.

#### `pending_approval`
- **Meaning:** This is a HITL-3 agent. The job was submitted but the worker will not execute it until an owner/admin explicitly approves it. Credits are reserved at submission time.
- **Expected duration:** Should be approved within 4 business hours.
- **If stuck:** See Section 3 for escalation steps.

---

## 3. HITL-3 Explained

### What Is HITL-3

HITL-3 (Human-in-the-Loop, Level 3) is the highest oversight tier. Agents designated HITL-3 handle decisions that involve spend commitments, scaling infrastructure, or signing agreements — actions that cannot be undone automatically. These agents are gated behind mandatory owner/admin approval before the LLM pipeline executes.

**HITL-3 is not a bug.** If a user says "my job is stuck pending approval," this is by design.

### How the Hold Works

1. User submits a job for a HITL-3 agent
2. Job is written to `agent_jobs` with `status = 'pending_approval'`
3. Credits are reserved (`reserved += estimate`, `balance -= estimate`)
4. Worker loop skips any job with `status = 'pending_approval'`
5. Job remains frozen until an admin acts

### How Admin Approves or Rejects

Via the admin portal:

1. Navigate to **Admin → Jobs → Pending Approval**
2. Find the job by workspace or job ID
3. Review the submitted task input
4. Click **Approve** or **Reject**
   - **Approve** → sends `PATCH /api/admin/jobs/{id}/approve` → status transitions to `pending` → worker picks it up normally
   - **Reject** → sends `PATCH /api/admin/jobs/{id}/reject` → status transitions to `failed` → credits auto-refunded

### Checking HITL-3 Backlog

```sql
-- All jobs currently waiting for HITL-3 approval
SELECT
    aj.id AS job_id,
    aj.workspace_id,
    w.name AS workspace_name,
    aj.agent_id,
    aj.created_at,
    NOW() - aj.created_at AS waiting_duration
FROM agent_jobs aj
JOIN workspaces w ON w.id = aj.workspace_id
WHERE aj.status = 'pending_approval'
ORDER BY aj.created_at ASC;
```

### SLA

| Threshold | Action |
|---|---|
| < 4 business hours | Normal — admin should approve via portal |
| 4–8 business hours | Follow up with admin directly |
| > 8 business hours | Escalate to mark.salman76@gmail.com immediately |

If the owner is unavailable and a HITL-3 job is blocking a customer, Tier 3 can make the call to reject and ask the customer to resubmit when the approval flow can be handled.

---

## 4. Financial Review Queue

### What Triggers Financial Review

Every completed agent response is passed through `scan_for_financial_actions()`. This scanner checks the raw LLM output for phrases associated with financial commitments, including but not limited to:

- "purchase", "buy", "order"
- "subscribe", "sign up for"
- "pay", "payment", "invoice"
- "commit budget", "allocate funds"
- "sign agreement", "contract"

If any matched phrase is found, the job is immediately routed to `pending_financial_review` instead of `completed`, and an automated email alert is sent to the admin.

**This is a hard safety rail.** Agents on this platform must never initiate spend or binding agreements. The scanner is the enforcement mechanism.

### What Happens to the Job

- `agent_jobs.status` → `'pending_financial_review'`
- The result is stored in `agent_jobs.result` but not delivered to the user
- Admin receives an email alert with the job ID
- Credits remain deducted (not refunded until the job is resolved)

### How to Review

1. Admin portal → **Financial Review** tab
2. Locate the flagged job
3. Read the full agent output carefully
4. Determine: is this a false positive or a true positive?

**False positive** (benign context — e.g. agent wrote "competitors pay an average of $X per click"):
- The phrase matched the scanner but does not represent an agent-initiated financial action
- Support can **Release** the job → status transitions to `completed`, output delivered to user

**True positive** (agent appears to have attempted to commit spend or sign something):
- Do **not** release the job
- Escalate immediately to mark.salman76@gmail.com
- Document the job ID, agent ID, and the specific flagged phrase

### Checking Queue Depth

```sql
-- All jobs currently in financial review
SELECT
    aj.id AS job_id,
    aj.workspace_id,
    w.name AS workspace_name,
    aj.agent_id,
    aj.created_at,
    NOW() - aj.created_at AS held_duration
FROM agent_jobs aj
JOIN workspaces w ON w.id = aj.workspace_id
WHERE aj.status = 'pending_financial_review'
ORDER BY aj.created_at ASC;
```

### What to Tell Users

If a user asks why their job output hasn't arrived: tell them the job requires a brief compliance review and they will receive the output shortly. Do not mention the scanner, financial action detection, or any internal mechanism. Target: resolved within 4 business hours.

---

## 5. Common User Errors and Responses

### 5.1 "Not Enough Credits" / Job Won't Submit

**What the user sees:** An error at job submission time saying they don't have enough credits to run the agent.

**Root cause:** `credits_accounts.balance - credits_accounts.reserved` is less than the credit estimate for the requested agent. The estimate varies by agent type and is fixed at submission time.

**Support response:** Confirm how many credits the user has vs. how many the agent requires.

```sql
-- Check workspace balance
SELECT balance, reserved, (balance - reserved) AS effective_available
FROM credits_accounts
WHERE workspace_id = 'WORKSPACE-UUID';
```

**Resolution steps:**
1. Share the effective available balance with the user (not the raw `balance` field — `balance - reserved` is what matters)
2. If their balance is genuinely insufficient, direct them to the billing page to purchase a credit top-up
3. If their balance looks correct but the error persists, check for a stuck `running` job holding a large `reserved` amount that should have been released
4. If a stuck job is causing the issue, escalate to Tier 2 to resolve the stuck job — do not manually adjust `reserved` directly

### 5.2 "Agent Job Failed" — Investigating Failures

**What the user sees:** Job status shows "failed."

**Root cause:** Variable — check the internal error message.

```sql
-- Get error details for a specific job
SELECT
    id,
    agent_id,
    status,
    error_message,
    created_at,
    completed_at
FROM agent_jobs
WHERE id = 'JOB-UUID';
```

**Common causes and resolutions:**

| error_message pattern | Cause | Resolution |
|---|---|---|
| Mentions timeout or connection | LLM service or downstream API timed out | Ask user to retry; if recurring, escalate to Tier 2 |
| Mentions integration / credential | Connected app credential expired or invalid | Ask user to reconnect the integration (Section 7) |
| Mentions input validation | User input malformed or too long | Ask user to review and resubmit with cleaner input |
| Generic / unexpected exception | Worker-level bug | Escalate to Tier 2 with the job ID |

**Important:** Do not share the raw `error_message` text with users. Paraphrase. It may contain stack traces, internal service names, or infrastructure detail.

Credits are automatically refunded on failure. Confirm the refund was applied before closing the ticket:

```sql
-- Verify credits were refunded (balance should reflect the refund)
SELECT balance, reserved FROM credits_accounts WHERE workspace_id = 'WORKSPACE-UUID';
```

### 5.3 "I Can't See This Agent"

**What the user sees:** An agent advertised on the platform is not visible or accessible in their workspace.

**Root cause:** Package tier gate. Agents are gated by subscription tier: `starter → growth → business → enterprise`. Lower tiers have access to a subset of the 27-agent catalogue.

**Support response:**
1. Check the organization's current tier:

```sql
SELECT name, subscription_tier FROM organizations WHERE id = 'ORG-UUID';
```

2. If the agent they want is above their tier, explain that it's available on a higher plan and direct them to the upgrade page
3. Do not manually override agent access in the database — tier gates are enforced in `agent_registry.py` and bypassing them in the DB will cause inconsistencies

### 5.4 "My Job Has Been Pending for a Long Time"

**What the user sees:** Job submitted but status has not moved from `pending` for several minutes.

**Root cause:** Worker is not picking up the job. Possible causes: ECS task crashed, SQS queue backed up, or job is HITL-3 and awaiting approval (check status carefully — `pending_approval` is different from `pending`).

**Resolution steps:**
1. Confirm the exact status:

```sql
SELECT status, created_at, NOW() - created_at AS age FROM agent_jobs WHERE id = 'JOB-UUID';
```

2. If `pending_approval` → see Section 3. This is expected behavior.
3. If `pending` for more than 2 minutes → escalate to Tier 2 immediately
4. Tier 2 should check: ECS task health in AWS console, SQS queue depth, CloudWatch logs for worker errors
5. Do not ask the user to resubmit until the root cause is identified — if they resubmit and the worker comes back, they may get double-charged (credits reserved for both jobs)

### 5.5 "Job Is pending_financial_review — What Does That Mean?"

**What to tell the user:**
> "Your job output is currently undergoing a brief automated compliance review. This is a standard step for certain outputs on our platform. Our team will process it within a few hours and you'll receive the results shortly. No action is needed on your end."

**What NOT to say:** Do not mention output scanners, financial phrase detection, LLMs, or any internal mechanism. Do not speculate on why their specific output triggered review.

**Internally:** Check the queue (Section 4), determine false positive vs. true positive, and act accordingly.

### 5.6 "I Accidentally Ran the Wrong Agent"

**What the user sees:** Job already submitted and they want to undo it.

**Root cause:** No undo mechanism exists once a job is submitted. Credits are deducted immediately.

**If the job has NOT yet started (status = `pending` or `pending_approval`):**
- In theory the job could be cancelled before the worker picks it up, but there is no cancel endpoint currently
- Escalate to Tier 2 who can update the status to `failed` in the database (which triggers auto-refund) if caught quickly enough

**If the job is `running` or beyond:**
- No refund is automatic for user error
- If the job completes successfully, credits are consumed; assess the situation and use manual refund discretion (Section 6)
- If the job fails, credits are automatically refunded regardless

**Support response:** Apologize, confirm the job's current status, and if the job hasn't started, escalate to Tier 2 for a potential cancellation. If it has run, offer to review the output with the user — sometimes the "wrong agent" still produces useful results. If completely useless, use judgment on a goodwill credit refund.

### 5.7 "I Can't Connect My Integrations"

**What the user sees:** Error when trying to connect a third-party app, or connected app appears connected but isn't working.

**Root cause:** Integration credentials stored in `workspace_integrations.encrypted_value`. Possible issues: bad credential on save, expired token, or encryption key mismatch.

**Checking integrations for a workspace:**

```sql
-- Check which integrations a workspace has configured
SELECT
    id,
    integration_type,
    created_at,
    CASE WHEN encrypted_value IS NOT NULL AND encrypted_value != '' THEN 'present' ELSE 'missing' END AS credential_status
FROM workspace_integrations
WHERE workspace_id = 'WORKSPACE-UUID';
```

**CRITICAL: Never query or display `encrypted_value` to yourself, the user, or in any log.** The column exists for the worker only. Even support staff must not retrieve the raw encrypted value.

**Resolution steps:**
1. Confirm whether the integration row exists and has a non-null `encrypted_value`
2. If missing: ask user to connect the integration from scratch via the integrations settings page
3. If present but failing: the credential is likely stale (expired OAuth token, rotated API key). Ask user to disconnect and reconnect
4. If reconnect fails repeatedly: escalate to Tier 2 — may be an encryption key environment issue

---

## 6. Manual Credit Refund

Manual refunds are a last resort for cases the automatic refund path did not cover (worker crash, user error, goodwill gesture). Every manual refund must be documented without exception.

### Step-by-Step Process

**Step 1: Confirm the job and workspace**

Get the job ID and workspace ID from the user or ticket. Verify they match:

```sql
SELECT id, workspace_id, agent_id, status, error_message, created_at
FROM agent_jobs
WHERE id = 'JOB-UUID';
```

**Step 2: Confirm the refund amount**

Agree the refund amount with the user before touching any data. Default is the credit cost of the specific job. For goodwill refunds, use your discretion or check with Tier 3 if the amount is significant (> 100 credits).

**Step 3: Check current balance**

```sql
SELECT balance, reserved FROM credits_accounts WHERE workspace_id = 'WORKSPACE-UUID';
```

Note the current balance. You will record the before/after values in your audit log entry.

**Step 4: Apply the refund**

```sql
-- REPLACE workspace_uuid and amount before running
UPDATE credits_accounts
SET balance = balance + [AMOUNT]
WHERE workspace_id = 'WORKSPACE-UUID';
```

Verify the row was updated (check that `1 row affected`).

**Step 5: Log in audit_logs**

```sql
-- Insert audit trail entry — fill in all placeholder values
INSERT INTO audit_logs (
    id,
    user_id,
    action,
    resource_type,
    ip_address,
    created_at
) VALUES (
    gen_random_uuid(),
    'SUPPORT-STAFF-USER-UUID',   -- your own user ID
    'manual_credit_refund',
    'credits_account',
    'support-portal',            -- or your actual IP
    NOW()
);
```

> **Note:** The `audit_logs` schema does not have a `metadata` column in the base schema above, so use the `action` and `resource_type` fields to encode context. If there is a `details` or `metadata` column in the live schema, use it to record job ID, amount, and reason.

**Step 6: Notify the user**

Send an email confirming:
- The refund amount applied
- The new credit balance (after refund)
- A brief reason (e.g. "credits refunded for failed job JOB-UUID")

Do not include job `error_message` content in the user email.

### Warnings

- Always confirm the amount with the user before running the UPDATE
- Never run a manual refund without a corresponding audit log entry
- For disputes over large amounts (> 500 credits), get Tier 3 sign-off first
- If the user has already received an automatic refund for the same job and is asking for a second refund, verify before proceeding — check `agent_jobs.status` and the transaction history

---

## 7. Integration Issues

### No Connected Apps — "Read-Only Mode"

If a workspace has no rows in `workspace_integrations`, agents run without live tool access. They still function — they use the LLM and any context provided by the user — but they cannot pull real-time data from external services (e.g. Shopify orders, Google Analytics, etc.).

This is not an error state. Some users intentionally run agents without integrations. If a user asks why the agent didn't pull live data, confirm whether they have integrations connected.

### Integration Present but Agent Failing

If `workspace_integrations` shows a row with `encrypted_value` present, but the agent is failing or returning stale data:

1. The credential is likely expired (OAuth tokens expire; API keys get rotated)
2. Ask the user to disconnect and reconnect the integration via Settings → Integrations
3. After reconnect, the new credential is encrypted and stored; previous value is overwritten

If reconnection fails:
- Check whether the failure is at the OAuth redirect level (user-side) or at the server level (escalate to Tier 2 if server-side)

### Checking Integrations for a Workspace

```sql
-- List all integrations for a workspace (safe — does NOT expose encrypted_value)
SELECT
    id AS integration_id,
    integration_type,
    created_at,
    CASE WHEN encrypted_value IS NOT NULL AND encrypted_value != '' THEN 'present' ELSE 'missing' END AS credential_status
FROM workspace_integrations
WHERE workspace_id = 'WORKSPACE-UUID'
ORDER BY integration_type;
```

### Security Constraint — Non-Negotiable

**Never retrieve `encrypted_value` from `workspace_integrations`.** Never log it, display it, copy it, or pass it anywhere. The column is consumed exclusively by the worker at job execution time. Support staff have no legitimate need to read it. Accessing it is a security violation.

If you accidentally SELECT the column and it appears in a query result, close the result immediately, do not copy or record the value, and report it to mark.salman76@gmail.com.

---

## 8. Escalation Path

### Tier 1 — Support Team (First Response)

**Handles:**
- Credit balance questions and top-up issues
- Job status questions (excluding infrastructure causes)
- Tier gate / agent access questions
- Integration setup guidance
- HITL-3 explanations (not approvals)
- Financial review status updates for users
- Minor goodwill credit refunds (< 100 credits)

**Does not handle:** Worker outages, infrastructure issues, data incidents, billing disputes > $100, true-positive financial review flags.

### Tier 2 — Operations

**Handles:**
- Stuck jobs (worker not picking up `pending` jobs)
- Worker health: ECS task inspection, SQS queue depth, CloudWatch logs
- Jobs stuck in `running` state (likely worker crash)
- Integration server-side failures
- Database-level interventions (status corrections, stuck reserved credits)

**Escalate when:** Any infrastructure alert, any job stuck > 15 minutes, SQS queue depth > 50 messages.

### Tier 3 — Owner

**Contact:** mark.salman76@gmail.com

**Handles:**
- Data incidents or security concerns of any kind
- Billing disputes or refund requests > 500 credits
- HITL-3 backlogs > 8 hours with no admin available
- Any `pending_financial_review` job that looks like a true positive
- Stripe webhook failures causing missing credits at scale
- Escalations from Tier 2 that require code changes or policy decisions

**Response expectation:** Tier 3 should be contacted via email with a clear subject line: `[Vantro Support Escalation] - [brief description]`. Include job IDs, workspace IDs, and a concise summary of what you've already investigated.

---

## 9. Useful Support Queries

The following queries are safe to run in a read-only support context. Always substitute the placeholder UUIDs before running. Never SELECT `encrypted_value` from `workspace_integrations`.

```sql
-- ─────────────────────────────────────────────────────────
-- 9.1 Find all jobs for a specific workspace (most recent first)
-- ─────────────────────────────────────────────────────────
SELECT
    id AS job_id,
    agent_id,
    status,
    created_at,
    completed_at,
    ROUND(EXTRACT(EPOCH FROM (COALESCE(completed_at, NOW()) - created_at)) / 60, 1) AS duration_minutes
FROM agent_jobs
WHERE workspace_id = 'WORKSPACE-UUID'
ORDER BY created_at DESC
LIMIT 50;
```

```sql
-- ─────────────────────────────────────────────────────────
-- 9.2 Find a workspace's credit balance
-- ─────────────────────────────────────────────────────────
SELECT
    ca.balance,
    ca.reserved,
    (ca.balance - ca.reserved) AS effective_available,
    w.name AS workspace_name,
    o.subscription_tier
FROM credits_accounts ca
JOIN workspaces w ON w.id = ca.workspace_id
JOIN organizations o ON o.id = w.organization_id
WHERE ca.workspace_id = 'WORKSPACE-UUID';
```

```sql
-- ─────────────────────────────────────────────────────────
-- 9.3 Find all failed jobs in the last 24 hours (platform-wide)
-- ─────────────────────────────────────────────────────────
SELECT
    aj.id AS job_id,
    aj.workspace_id,
    w.name AS workspace_name,
    aj.agent_id,
    aj.error_message,
    aj.created_at,
    aj.completed_at
FROM agent_jobs aj
JOIN workspaces w ON w.id = aj.workspace_id
WHERE aj.status = 'failed'
  AND aj.created_at >= NOW() - INTERVAL '24 hours'
ORDER BY aj.created_at DESC;
```

```sql
-- ─────────────────────────────────────────────────────────
-- 9.4 Find all jobs in pending_financial_review (queue depth)
-- ─────────────────────────────────────────────────────────
SELECT
    aj.id AS job_id,
    aj.workspace_id,
    w.name AS workspace_name,
    aj.agent_id,
    aj.created_at,
    NOW() - aj.created_at AS held_duration
FROM agent_jobs aj
JOIN workspaces w ON w.id = aj.workspace_id
WHERE aj.status = 'pending_financial_review'
ORDER BY aj.created_at ASC;
```

```sql
-- ─────────────────────────────────────────────────────────
-- 9.5 Find all HITL-3 jobs pending owner approval
-- ─────────────────────────────────────────────────────────
SELECT
    aj.id AS job_id,
    aj.workspace_id,
    w.name AS workspace_name,
    o.name AS org_name,
    aj.agent_id,
    aj.created_at,
    NOW() - aj.created_at AS waiting_duration
FROM agent_jobs aj
JOIN workspaces w ON w.id = aj.workspace_id
JOIN organizations o ON o.id = w.organization_id
WHERE aj.status = 'pending_approval'
ORDER BY aj.created_at ASC;
```

```sql
-- ─────────────────────────────────────────────────────────
-- 9.6 Find organizations by subscription tier
-- ─────────────────────────────────────────────────────────
SELECT
    id AS org_id,
    name,
    subscription_tier,
    created_at
FROM organizations
WHERE subscription_tier = 'starter'  -- change to: starter / growth / business / enterprise
ORDER BY created_at DESC;
```

```sql
-- ─────────────────────────────────────────────────────────
-- 9.7 Find recent audit log entries for a specific user
-- ─────────────────────────────────────────────────────────
SELECT
    id AS log_id,
    action,
    resource_type,
    ip_address,
    created_at
FROM audit_logs
WHERE user_id = 'USER-UUID'
ORDER BY created_at DESC
LIMIT 100;
```

```sql
-- ─────────────────────────────────────────────────────────
-- 9.8 Find all jobs stuck in running for more than 15 minutes
-- (signals potential worker crash — escalate to Tier 2)
-- ─────────────────────────────────────────────────────────
SELECT
    aj.id AS job_id,
    aj.workspace_id,
    w.name AS workspace_name,
    aj.agent_id,
    aj.created_at,
    NOW() - aj.created_at AS stuck_duration
FROM agent_jobs aj
JOIN workspaces w ON w.id = aj.workspace_id
WHERE aj.status = 'running'
  AND aj.created_at < NOW() - INTERVAL '15 minutes'
ORDER BY aj.created_at ASC;
```

```sql
-- ─────────────────────────────────────────────────────────
-- 9.9 Find a workspace by organization name (when user only gives org name)
-- ─────────────────────────────────────────────────────────
SELECT
    w.id AS workspace_id,
    w.name AS workspace_name,
    o.id AS org_id,
    o.name AS org_name,
    o.subscription_tier
FROM workspaces w
JOIN organizations o ON o.id = w.organization_id
WHERE o.name ILIKE '%PARTIAL-ORG-NAME%'
ORDER BY o.name, w.name;
```

---

*End of document. For corrections or additions, contact mark.salman76@gmail.com.*
