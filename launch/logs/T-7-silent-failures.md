# T-7 Silent Failure Hunt — 2026-06-28

---

## Critical Path Silent Failures (fix before launch)

### 1. `agent_worker.py:261-273` — Financial review email passes `None` as HTML body
**Pattern:** `_send(admin_email, subject, body_text, None)` — `_send` does `{"Html": {"Data": body_html, ...}}` where `body_html=None`. SES will raise `ParamValidationError` because `None` is not a string.  
**Risk:** Financial review email to admin **always fails** when a financial-action violation is caught. Admin is never notified. Job is correctly held as `pending_financial_review` (the `db.commit()` is outside the try-block so the status saves), but the admin notification is silently broken.  
**Fix:** Pass a non-None HTML body or convert `body_text` to minimal HTML.

---

### 2. `agent_worker.py:126-127` — Workspace memory injected from `encrypted_value` column without decryption
**Pattern:**
```python
context["_workspace_memory"] = "\n".join(r[0] for r in _mem_rows)
```
Reads `encrypted_value` directly from `workspace_integrations`. This injects Fernet ciphertext (base64 blob) into the agent's context, not the plaintext summary. The agent sees garbage.  
**Risk:** Workspace memory enrichment silently delivers corrupted context to every agent execution. Feature is completely broken post-deployment.  
**Fix:** Call `decrypt(r[0])` before injecting.

---

### 3. `agents/agent_executor.py:399-405` / `412-438` / `444-473` — `except Exception: pass` in analytics tool stubs
**Pattern:** All three analytics stub functions (`_query_ga4`, `_query_shopify`, `_query_crm`) have bare:
```python
except Exception:
    pass
```
inside a `try/finally: db.close()`. If the DB query raises, the exception is swallowed and falls through to the **not-connected fallback return** at the end of the function, making every DB error look like "not connected."  
**Risk:** A transient DB error (connection timeout, pool exhaustion) causes the agent to be told "GA4/Shopify not connected" rather than surfacing the real error. Misleading output; debugging is impossible.  
**Fix:** Log the exception before the `pass`, or re-raise so `_execute_analytics_tool` can handle it at a higher level.

---

### 4. `agents/agent_worker.py:806-808` (in `_composio_tools` fetch inside `execute_agent`)
**Pattern:**
```python
except Exception:
    pass
```
Composio tool discovery fails silently. This is documented as intentional, but if the API key is misconfigured the agent silently runs without live tools and neither the workspace owner nor admin is told.  
**Risk (medium-critical):** Workspace has paid for Composio integration, submits job, agent runs without tools, delivers generic output. Owner assumes the integration worked. No audit trail.  
**Fix (non-critical path):** Log a `warning` instead of bare-pass so at least CloudWatch captures it.

---

### 5. `routes/stripe.py:300-342` — Stripe webhook `checkout.session.completed` / `invoice.payment_succeeded`: no `db.rollback()` on exception path
**Pattern:** The entire webhook body runs inside one `try` block (implicit — there is none), then `db.commit()` is called at line 380. If any operation between line 300 and 379 raises an unhandled exception (e.g., `_assign_credits` raises because `Organization` doesn't exist), the exception propagates out of the route handler. FastAPI returns 500 to Stripe, Stripe retries. The webhook idempotency guard at line 296 does NOT fire on retry because `stripe_webhook_events` was **not committed** (the commit at line 380 never ran). Stripe will re-deliver the event, potentially re-running the entire block on retry.  
**Risk:** Double credit assignment on retry. On a $279/month Growth subscription this means assigning 400 credits instead of 200.  
**Fix:** Wrap the entire event processing block in `try/except`, call `db.rollback()` in the except block, log the error, and return HTTP 200 (or re-raise as 500 only after rollback). The idempotency record must be written BEFORE the commit.

---

### 6. `agents/agent_worker.py:542-596` — `_run_scheduled_agents` creates jobs without checking credit balance
**Pattern:** Scheduled agent jobs are created (`credits_used=credit_cost`) with no credit pre-check or pre-deduction on the `CreditsAccount`. The only credit deduction happens when the job is picked up by `_process_job`, but the job is already written to the DB with a `pending` status.  
**Risk:** A workspace with 0 credits still gets scheduled jobs queued and burned against the credit balance. The regular `/run` endpoint has a TOCTOU-safe credit check (`with_for_update()`). Scheduled runs bypass this entirely.  
**Fix:** Query `CreditsAccount` with `with_for_update()` before creating the scheduled job, skip job creation if balance is insufficient, log a warning.

---

### 7. `routes/agents.py:277-283` — HITL-3 admin notification silently discarded
**Pattern:**
```python
try:
    send_approval_needed(admin_email, job.id, norm_id, user.email)
except Exception:
    pass  # non-fatal
```
Email failure is truly swallowed. Comment says "non-fatal" but the admin is the only actor who can approve HITL-3 jobs. If SES is down at launch, **all HITL-3 jobs queue silently forever** with no admin awareness.  
**Risk:** Admin never sees HITL-3 job requests. Jobs pile up in `pending_approval` and never execute.  
**Fix:** Log at `logger.error` level (not just pass) so CloudWatch alarm can trigger.

---

### 8. `routes/agents.py:575-579` — 5-star example save eats DB exception but commits outer rating
**Pattern:**
```python
if body.rating == 5 and job.output_data:
    try:
        ...
        db.add(eg)
    except Exception:
        pass
db.commit()  # always runs
```
If `AgentExample` model doesn't exist or has a schema mismatch, the `db.add(eg)` call can corrupt the SQLAlchemy session state. The subsequent `db.commit()` may commit a partially-dirty session or raise, potentially losing the user's rating entirely.  
**Fix:** Call `db.rollback()` in the except block before falling through, or move the example-save to a separate session.

---

### 9. `routes/billing.py:312-338` — `handle_first_payment_succeeded` swallows all exceptions silently
**Pattern:**
```python
def handle_first_payment_succeeded(user, plan, subscription_id, db):
    try:
        ...
        send_activation_link(...)
    except Exception as exc:
        logger.error("handle_first_payment_succeeded error for user %s: %s", user.id, exc)
```
The exception is logged but the caller (stripe webhook at line 340) continues and commits the `subscription_status = "active"` change. The user's payment is confirmed, they're marked active, but **they never receive the activation link**.  
**Risk:** User pays, subscription is active in DB, Stripe shows payment, but user has no activation link and cannot access the platform. Support ticket. Churn.  
**Fix:** Re-raise after logging, or store a `activation_failed` flag and alert admin to manually resend.

---

### 10. `routes/auth.py:244-253` — JTI revocation on logout swallows all exceptions
**Pattern:**
```python
try:
    ...
    revoke_jti(jti, remaining)
except Exception:
    pass
```
If Redis is down at launch, logout does NOT revoke the access token JTI. The token remains valid until natural expiry (1 hour). This is a security failure on a critical path (logout = token invalidation).  
**Risk:** If Redis goes down and a user logs out, their token stays valid for up to 1 hour. Anyone with the token can continue to use the API.  
**Fix:** Log at `logger.warning` minimum. Consider returning HTTP 503 if Redis is unavailable rather than silently succeeding.

---

## Non-Critical Silent Failures (monitor post-launch)

### NC-1. `agent_worker.py:122-126` — Workspace context injection bare `except: pass`
Business context and brand profile injection both silently swallow all exceptions. If the `organizations` table query fails (e.g., FK migration not applied), agents run without workspace context. Output quality degrades with no signal to the operator.

### NC-2. `agent_worker.py:139-146` — Skill RAG bare `except: pass`
RAG enrichment is correctly documented as "best-effort". However, a misconfigured pgvector extension will cause persistent silent failure on every job. Add `logger.warning` at minimum.

### NC-3. `agent_worker.py:148-155` — Few-shot example retrieval bare `except: pass`
Same as NC-2. Silent on every job if the `agent_examples` table is missing (migration not applied).

### NC-4. `agent_worker.py:157-164` — Composio credential retrieval bare `except: pass`
Correctly logged in `composio_service.py`, but the outer worker also has a bare-pass. Duplicate silent suppression.

### NC-5. `routes/users.py:170-176` — Support ticket scrub on account deletion bare `except: pass`
GDPR erasure of support ticket data silently fails. Personal data in `support_tickets` is not scrubbed. The account itself is anonymised but historical ticket messages leak email/content. Regulatory risk.  
**Fix:** Log at `logger.error` and consider re-raising (account deletion should fail loudly if GDPR erasure cannot complete).

### NC-6. `routes/users.py:111-112` / `120-121` — GDPR export silently returns empty arrays on DB errors
If the `agent_jobs` or `support_tickets` query fails, the export returns `[]` for those arrays silently. A user requesting their data under GDPR rights gets an incomplete response with no indication that data was missing.

### NC-7. `routes/platform.py:53` — Subscription tier check swallows all exceptions, returns "all"
Auth errors and DB failures both silently return "all" (widest access). Acceptable for a public platform status page but should be logged.

### NC-8. `agent_worker.py:463-465` — Weekly report failure per workspace is logged but outer loop continues
This is handled correctly. Included for completeness — the pattern of logging per-workspace failure and continuing is intentional.

### NC-9. `routes/stripe.py:358` — Payment failed email swallowed (uses `logger.exception`)
Actually handled correctly — `logger.exception` logs the full traceback. Not a silent failure.

### NC-10. `agent_worker.py:504-539` — `_save_workspace_outcome_memory` bare `except` at top level
Correctly documented as best-effort. The `logger.debug` means it won't appear in production logs by default. Consider `logger.info` so memory failures are visible without turning on debug logging.

---

## Summary

| Severity | Count | Highest Impact |
|----------|-------|----------------|
| Critical — fix before launch | 10 | Items 1, 2, 5, 9 |
| Non-critical — monitor post-launch | 10 | Items NC-5 (GDPR), NC-1 (context) |

**Top 4 must-fix before launch:**

1. **Item 1** (`agent_worker.py:270`) — Financial review admin email passes `None` HTML → always crashes SES call silently. Admin never notified of financial violations.
2. **Item 2** (`agent_worker.py:179`) — Workspace memory injected as raw ciphertext, not plaintext. Feature completely broken.
3. **Item 5** (`routes/stripe.py` webhook) — No rollback in exception path. Double credit assignment on Stripe webhook retry.
4. **Item 9** (`routes/billing.py:312`) — Activation link send failure is swallowed. User pays but cannot access platform.
