# T-7 Code Review — 2026-06-28

Scope: `backend/app/` — routes, models, services, agents, middleware.
Reviewed files: all routes (15), all models (10), agent_executor, agent_worker, agent_registry, database.py, main.py.

---

## Critical (must fix before launch)

### C-1 — `backend/app/agents/agent_worker.py:314` — Provider name written into job output returned to clients
```python
job.output_data = f"<!-- provider:{provider_used} -->\n{output}"
```
`provider_used` is set to `"anthropic/claude-sonnet-4-6"` or `"openai/gpt-4o"`. This string is stored in the DB and returned raw to any client polling `GET /api/agents/jobs/{id}` (routes/agents.py:331 returns `job.output_data` without stripping the comment). The only stripping of `split(" -->\n", 1)[-1]` is in the 5-star rating path (agents.py:568) — not in the main polling route. Direct violation of tech-stack opacity rule.

**Fix:** Change line 314 to `job.output_data = output` and log `provider_used` server-side only. Or strip on read at agents.py:331.

---

### C-2 — `backend/app/routes/agents.py:503` — Model name leaked in SSE stream to every streaming client
```python
yield f'data: {json.dumps({"type": "start", "agent_id": normalized, "model": model})}\n\n'
```
`model` is the literal Anthropic model string from `HITL_MODEL_MAP` (e.g. `"claude-sonnet-4-6"`). Every client streaming a response receives it.

**Fix:** Remove `"model"` from the SSE start event, or replace with an opaque tier name (`"hitl_1"`).

---

### C-3 — `backend/app/routes/admin.py:720` — AWS account ID and ECS service names hardcoded and returned in API response
```python
"account_id": "685570573617",
...
{"name": "ECS API Service", "detail": "Vantro API — Fargate 256 CPU / 512 MB"},
{"name": "ECS Worker Service", "detail": "vantro-worker — Fargate 512 CPU / 1024 MB"},
```
The `GET /api/admin/infrastructure` endpoint returns the real AWS account ID (fingerprinting target) and internal service names. Anyone who gains admin access — including a compromised admin session — can enumerate the entire cloud footprint.

**Fix:** Move the account ID to an env var (`AWS_ACCOUNT_ID`). Do not return it in API responses. Replace internal ECS service names with generic labels (`"api-service"`, `"worker-service"`).

---

### C-4 — `backend/app/routes/agents.py:499-500` — Provider name in SSE error event
```python
yield f'data: {json.dumps({"type": "error", "message": "ANTHROPIC_API_KEY not configured"})}\n\n'
```
The literal env var name `"ANTHROPIC_API_KEY"` reveals the provider to any client who triggers this code path.

**Fix:** Replace with `"AI service not configured"`.

---

## High (should fix before launch)

### H-1 — `backend/app/routes/stripe.py:108,138,153,179,198` — Raw Stripe exception message returned to clients
```python
raise HTTPException(status_code=400, detail=str(e))
```
Five separate locations in stripe.py forward the raw Stripe Python SDK exception as the API response detail. Stripe exceptions can contain internal request IDs, parameter names, and API error details. Log the real exception, return a generic message.

---

### H-2 — `backend/app/routes/agents.py:515-516` — Raw LLM exception forwarded to clients in SSE stream
```python
yield f'data: {json.dumps({"type": "error", "message": str(e)})}\n\n'
```
`str(e)` on an Anthropic SDK exception can contain internal error details, response headers, or stack fragments. Replace with `"Stream error occurred"` and log `exc_info=True` server-side.

---

### H-3 — `backend/app/models/agent_system.py` — Critical indexes missing on all high-frequency FK columns
All of these columns are queried on every API request or every worker polling cycle — none have `index=True`:
- `WorkspaceIntegration.workspace_id` (credential lookup per agent run)
- `AgentJob.workspace_id` (every job list, worker polling)
- `AgentJob.status` (worker poll loop: `WHERE status='pending'` — full table scan that degrades daily)
- `ScheduledRun.workspace_id` and `is_active`
- `APIKey.workspace_id` (API key auth on every API-key request)
- `PackageDownload.workspace_id`
- `TeamRun.workspace_id`

**Fix:** Add `index=True` to all of the above. Add a composite index on `(status, created_at)` on `AgentJob` since the worker orders by `created_at`.

---

### H-4 — `backend/app/models/reports.py:20,38,57` — No FK constraints on workspace_id columns
`WorkspaceReportSettings`, `WeeklyReport`, and `ReportFeedback` all have `workspace_id = Column(String, nullable=False)` with **no** `ForeignKey("workspaces.id")`. Zero referential integrity — rows survive workspace deletion indefinitely. No indexes either.

**Fix:** Add `ForeignKey("workspaces.id", ondelete="CASCADE")` and `index=True` to all three.

---

### H-5 — `backend/app/models/workspace.py:11` and `models/organization.py:10` — Missing indexes on primary join columns
- `Workspace.organization_id`: no index — every multi-tenant workspace lookup scans the table
- `Organization.owner_id`: no index — every "which org does this user own" call scans
- `MediaJob.workspace_id`: no index — every media job query scans

---

### H-6 — `backend/app/database.py:8-11` — Dev credentials in fallback connection string
```python
DATABASE_URL = get_config(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/multi_industrial_dev",
)
```
If `DATABASE_URL` is missing from the ECS task environment, the app silently attempts to connect to `localhost:5432` with `postgres:postgres`. It will fail to connect, but only at runtime — not on startup. Should raise `ValueError` at startup if `DATABASE_URL` is unset.

---

### H-7 — `backend/app/models/skill_chunk.py:13` — Embeddings stored as Text, not pgvector
```python
embedding = Column(Text, nullable=True)
```
CLAUDE.md describes pgvector RAG, but embeddings are stored as JSON text in a `Text` column. This means no `ivfflat`/`hnsw` index can be built. RAG cosine similarity requires a full-table decode and compute on every query.

**Fix:** Add `pgvector` extension, change column to `Vector(1536)` (or appropriate dimension), add `ivfflat` index.

---

### H-8 — `backend/app/main.py:312,324` — DB and Redis connection details leaked in unauthenticated health endpoint
```python
checks["database"] = f"error: {exc}"
checks["redis"] = f"error: {exc}"
```
`GET /health/ready` is unauthenticated. If the DB is unreachable, `str(exc)` from SQLAlchemy contains the full connection string (including any embedded credentials and hostname). Same for Redis.

**Fix:** Replace with `"error: database unreachable"` / `"error: redis unreachable"`.

---

## Medium (fix in T+7)

### M-1 — `backend/app/routes/auth.py:282` — No rate limit on `POST /api/auth/change-password`
Every other auth endpoint has `@limiter.limit(...)`. An attacker with a valid token can hammer this endpoint to brute-force `current_password`.

---

### M-2 — `backend/app/routes/workspaces.py:147` — Invite acceptance does not verify invited email matches authenticated user
The `POST /api/workspaces/invites/accept` endpoint verifies the token exists and has not expired, but does not check that `invited_email` (row[5]) matches `user.email`. Any authenticated user who obtains an invite token can accept an invite intended for someone else.

---

### M-3 — `backend/app/routes/support.py:101,120` — Admin check uses only `ADMIN_EMAIL`, ignores `is_admin` flag
`GET /api/support/tickets/all` and `PATCH /api/support/tickets/{id}` check only `user.email.lower() != admin_email.lower()`. Multi-admins granted via `is_admin=True` in the DB cannot access these endpoints. Inconsistent with admin.py.

**Fix:** `if not (user.is_admin or user.email.lower() == admin_email.lower()): raise 403`

---

### M-4 — `backend/app/agents/agent_worker.py:362` — No `db.rollback()` in inner failure handler
When the main `except` fires and the subsequent DB status-update also fails, there is no `db.rollback()` before `db.close()`. The session may be left in a broken/inconsistent state.

---

### M-5 — `backend/app/agents/agent_executor.py:830` — RuntimeError message contains provider names
```python
raise RuntimeError(f"Both providers failed: {e}") from e
```
Worker stores `str(exc)[:2000]` into `job.error_message`. Verify no client-facing endpoint returns `error_message`. Confirmed: `admin.py:264,360,394,534,824` return it to the admin API — acceptable since admin is internal. But if a future client-facing endpoint is added that returns `error_message`, the provider names leak.

**Fix:** Change error_message to `"Agent execution failed"` and log the real error server-side only.

---

### M-6 — `backend/app/routes/admin.py:1493` — Duplicate `GET /api/admin/audit-logs` route (dead code)
Route registered at line 907 (`list_audit_logs`) and again at line 1493 (`get_audit_logs`). FastAPI matches the first. The second (with date filtering support) is unreachable dead code.

---

### M-7 — `backend/app/models/agent_system.py:31` — `AgentJob.status` no index
Worker polling loop runs `WHERE status = 'pending'` every 5 seconds. No index on `status`. Full table scan on every poll cycle. Degrades linearly as the jobs table grows.

---

### M-8 — `backend/app/models/audit_log.py` — No `workspace_id` column
Active `AuditLog` model has no `workspace_id`. Multi-tenant compliance queries ("all audit events for workspace X") require joining through users. The legacy `models.py` had `workspace_id + organization_id + indexes`. This is a regression.

---

### M-9 — `backend/app/routes/platform.py:50` — `user.organization_id` attribute likely does not exist
```python
Workspace.organization_id == user.organization_id
```
The `User` model links to orgs via `Organization.owner_id == user.id` everywhere else. If `User` has no `organization_id` column, this query always returns None and `_get_workspace_tier` returns `"all"` for every user, disabling tier-based feature gating on the platform page.

---

### M-10 — `backend/app/models/workspace.py` — Missing `ondelete` cascade rules
`CreditsAccount.workspace_id`, `MediaJob.workspace_id` — no `ondelete` rule. Deleting a workspace will raise FK violation or leave orphans. Same for `Workspace.organization_id`.

---

## Low (fix in T+14)

### L-1 — `backend/app/database.py:38-56` — `get_db()` / `get_read_db()` missing explicit rollback
Pattern is `try: yield db / finally: db.close()`. If a route raises mid-transaction, SQLAlchemy rolls back on close implicitly but non-deterministically on broken connections. Safer: `except: db.rollback(); raise`.

### L-2 — `backend/app/routes/auth.py:252,269` — Swallowed exceptions in logout
Two `except Exception: pass` blocks in logout — JTI revocation failure and user_id extraction failure. Neither is logged. If Redis is down, the token is not revoked and the admin has no telemetry. Use `logger.warning`.

### L-3 — `backend/app/agents/agent_worker.py:127,145,150,153,163,180,202` — 7 silent enrichment failures
All `except Exception: pass` blocks for RAG, few-shot, Composio, brand profile, memory. Individually acceptable (best-effort), but there is zero telemetry — a persistent silent failure (e.g. RAG always broken) is invisible in logs. Add `logger.debug`.

### L-4 — `backend/app/routes/contact.py` — No rate limit on `POST /api/contact/enterprise`
Unauthenticated, no rate limit. A bot can flood admin inbox.

### L-5 — `backend/app/routes/users.py:105,114,171` — Swallowed exceptions in GDPR export and account deletion with no logging
Three `except Exception: pass/jobs=[]` blocks. If DB fails during GDPR export, partial data returned silently. During account deletion, if ticket scrubbing fails, it proceeds without logging.

### L-6 — `backend/app/routes/reports.py:90` — `_get_admin_user` checks `is_admin` flag only, not `ADMIN_EMAIL` env var
Bootstrap admin (`ADMIN_EMAIL` env match) cannot access admin report routes unless `is_admin=True` is also set in DB.

### L-7 — `backend/app/models/user.py:22` — `locked_agent_ids` stored as String column containing JSON
Should be `JSON` / `JSONB` column type for correctness and queryability. `Column(String)` containing a JSON array is fragile.

### L-8 — `backend/app/models/` — `created_at` nullable with no server default on User, Workspace, AgentJob, MediaJob
`created_at = Column(DateTime, nullable=True)` without `server_default=func.now()`. New rows may have NULL timestamps, breaking time-sorted queries.

### L-9 — `backend/app/models/activation_token.py:10` — Business policy value hardcoded
`TOKEN_TTL_DAYS = 7` — should be `int(os.getenv("ACTIVATION_TOKEN_TTL_DAYS", "7"))`.

### L-10 — `backend/app/routes/admin.py:847` — Ticket status not validated in PATCH handler
`new_status = body.get("status", "resolved")` with bare `dict`, no Pydantic validation. Any arbitrary string can be set as ticket status. Use an enum.

### L-11 — `backend/app/models.py` — Legacy shadow models file with separate `Base` (dead code)
`models.py` defines a parallel schema with its own `declarative_base()`. These classes are invisible to Alembic and will cause confusion. Delete or reconcile.

### L-12 — `backend/app/routes/workspaces.py:154` — Missing `db.rollback()` before `raise HTTPException` on invite insert failure
Session left in broken state if INSERT fails mid-transaction.

### L-13 — `backend/app/agents/agent_worker.py:338` — No `db.rollback()` before status update in main failure handler
If `execute_agent` fails mid-DB-operation, session may be dirty when failure handler runs.

### L-14 — Rate limiter falls back to in-memory when `REDIS_URL` not set
`limiter.py:11` — `_storage_uri = REDIS_URL if REDIS_URL else "memory://"`. In-memory rate limits are per-process, per-replica — useless with multiple ECS tasks. Log a warning on startup if Redis is not configured.

---

---

## Additional Critical Findings (app/api/, services/, core/, billing/, auth/)

### C-5 — `backend/app/api/stripe_checkout_routes.py:28` — Header default grants admin access to any unauthenticated caller
```python
x_actor_role: str = Header(default="owner")
```
If the `X-Actor-Role` header is absent, the role defaults to `"owner"` — passing every admin guard on these routes automatically. Any unauthenticated request to `/admin/billing/stripe-checkout-readiness` and `/admin/billing/create-checkout-session` is implicitly treated as an owner.

**Note:** The entire `app/api/` directory is NOT wired into `main.py` — none of those routers are registered. This is the only reason these endpoints are not currently exploitable. If any of these routers are mounted in the future, C-5 through C-8 become immediately live.

---

### C-6 — `backend/app/api/refund_routes.py:18,23` — Refund submit and lookup are completely unauthenticated
`POST /billing/refund-request` and `GET /billing/refund-request/{refund_id}` have zero authentication. Any anonymous caller can submit refund requests or enumerate refund details by ID.

---

### C-7 — `backend/app/api/subscription_policy_routes.py:208` — Stripe webhook skips signature verification in non-production
```python
if production_mode and not signature_result.get("verified"):
```
The signature check is conditional on `production_mode`. In staging or dev, forged Stripe events are accepted. An attacker who can reach staging can forge `checkout.session.completed` to unlock paid tiers.

---

### C-8 — `backend/app/api/` — All admin routes use client-asserted role header, no JWT
Every route in `admin_deployment_control_routes.py`, `operational_recovery_routes.py`, `admin_industry_agent_store_routes.py` guards with `x_actor_role: Optional[str] = Header(default=None)` — no JWT, no secret, no server-side identity. Anyone can send `X-Actor-Role: owner` and pass every guard.

---

### C-9 — `backend/app/services/encryption_service.py:42` — Fernet encryption key falls back to hardcoded string
```python
secret = os.getenv("SECRET_KEY", "vantro-default-secret-change-in-production")
```
If `INTEGRATION_ENCRYPTION_KEY` is absent and `SECRET_KEY` is not set, all workspace credentials are encrypted with the public literal string. There is no startup guard equivalent to the JWT key check. The JWT and Fernet encryption share the same `SECRET_KEY` — a single secret compromise breaks both auth and all stored credentials.

---

### C-10 — `backend/app/services/encrypted_column.py:37-39` — Decrypt failure silently returns ciphertext as plaintext
```python
except Exception:
    return value  # raw ciphertext returned as "plaintext"
```
Comment says "legacy unencrypted rows." But if the Fernet key is wrong or corrupted, the raw base64 ciphertext blob is returned to callers as if it were the credential value. Any downstream code (e.g. Composio API call) silently passes the ciphertext as an API key.

---

### C-11 — `backend/app/services/stripe_service.py:54-57,136-141` — Bare `except:` on subscription cancel and webhook verification
Two bare `except:` blocks (not `except Exception`) that catch `KeyboardInterrupt`/`SystemExit` and return `False`/`None` with zero logging. Webhook signature failure is indistinguishable from network error — both silently return `None`.

---

### C-12 — `backend/app/core/security_hardening_runtime.py:73` and `core/rate_shaping_middleware.py:28` — In-memory rate limiters ineffective under multi-worker ECS deployment
Both middleware rate limiters use process-local `dict + deque`. With multiple Uvicorn workers or multiple ECS tasks, each process has its own counter — a client gets N×limit requests before blocking. `RateShapingMiddleware` defaults to `observe` mode unless `RATE_SHAPING_MODE=enforce` is explicitly set. Effective rate limiting under production load is only `slowapi` (which IS Redis-backed when `REDIS_URL` is set per `limiter.py`).

---

### C-13 — `backend/app/core/safe_openai_live_connector.py:183-200` — No `FINANCIAL_CONSTRAINT_BLOCK` in OpenAI connector prompt
The `_build_client_safe_input()` function constructs the actual prompt sent to OpenAI without prepending `FINANCIAL_CONSTRAINT_BLOCK` or `INJECTION_GUARD`. This code path bypasses the financial governance layer entirely.

---

### H-9 — `backend/app/auth/jwt.py:41` — Token revocation silently fails open on Redis outage
When Redis is unavailable, `verify_token()` catches all exceptions and returns the payload unchecked (`pass  # Redis unavailable — fail open`). Revoked tokens (from logout) remain valid up to their 1-hour natural expiry with zero logging during outage. Change to `logger.warning`.

---

### H-10 — `backend/app/api/media_routes.py:36` and `storage_routes.py:28` — Unauthenticated endpoints with fallback demo tenant
`_tenant()` returns `"client_demo_001"` when `X-Tenant-Id` is absent instead of rejecting. No authentication required. Any caller can read/write media assets and trigger upload references.

---

### M-11 — `backend/app/routes/agents.py:73-93` — Plan tier inferred from credit balance, not a plan field
`_workspace_tier()` infers `starter/growth/business` by comparing `total_credits` against hardcoded thresholds. An admin top-up of a starter account to 200 credits silently grants growth-tier agent access without the customer paying for growth. There is no authoritative `plan` field.

---

### M-12 — `backend/app/auth/jwt.py:9` — Same `SECRET_KEY` used for both JWT signing and Fernet encryption key derivation
A single secret compromise breaks both authentication and all stored workspace credentials. These must be independent secrets.

---

### M-13 — `backend/app/core/session_auth_hardening_runtime.py:258-271` — Security block reason returned in response body
```python
content["debug_visibility"] = {"reasons": assessment.get("reasons", [])}
```
When a request is blocked, the response body includes the list of security reasons (e.g. `"csrf_token_or_origin_missing_for_state_change"`), telling an attacker exactly what to fix to bypass the block.

---

### M-14 — `backend/app/tenant/tenant_isolation.py` — File is empty
The module name implies a dedicated enforcement layer. It contains no code. Tenant isolation is enforced only inline in individual routes, with no architectural guarantee.

---

## Clean Files (no findings)

- `backend/app/routes/auth.py` — Auth flow, JWT handling, refresh rotation, bcrypt hashing: clean. CSRF exempt/safe method logic: correct.
- `backend/app/routes/dashboard.py` — All queries filter by `Organization.owner_id == user.id`. Clean.
- `backend/app/routes/agents.py` — Job isolation (`AgentJob.workspace_id == ws.id` on all queries). Credit TOCTOU guard (`with_for_update()`): correct.
- `backend/app/routes/api_v1.py` — API key auth (SHA-256 hash). Workspace isolation on all job queries. Clean.
- `backend/app/routes/team_routes.py` — TOCTOU credit guard. Workspace filters on all queries. Clean.
- `backend/app/agents/agent_executor.py` — FINANCIAL_CONSTRAINT_BLOCK + INJECTION_GUARD always first in system prompt. scan_for_financial_actions cannot throw. Opacity patterns strip provider names from output. Clean.
- `backend/app/routes/stripe.py:273-381` — Webhook: signature verified before processing, idempotency guard present. Clean.
- `backend/app/models/refresh_token.py` — `user_id` CASCADE, `token_hash` unique, `expires_at` non-null. Clean.
- `backend/app/models/admin_models.py` — Platform-global tables, correct indexes. Clean.
- `backend/app/main.py` — Docs disabled in production. Server header suppressed. Generic exception handler (no stack traces). CSRF middleware. Clean (except H-8 health probe).

---

## Summary

| Severity | Count |
|---|---|
| Critical (launch blocker) | 13 |
| High (pre-launch) | 10 |
| Medium (T+7) | 14 |
| Low (T+14) | 14 |
| **Total** | **51** |

### Top 10 to fix before launch (ordered by impact):

1. **C-9/C-10** — `encryption_service.py:42` + `encrypted_column.py:37` — hardcoded Fernet fallback key + decrypt failure returns raw ciphertext. All workspace credentials at risk.
2. **C-1** — Strip `<!-- provider:anthropic/claude-sonnet-4-6 -->` from `job.output_data` (agent_worker.py:314). One-line fix.
3. **C-2/C-4** — Remove model name from SSE start event and "ANTHROPIC_API_KEY" from SSE error (agents.py:503, 499).
4. **C-3** — Remove hardcoded AWS account ID `685570573617` from infrastructure API response (admin.py:720).
5. **C-11** — Fix bare `except:` blocks in stripe_service.py (subscription cancel + webhook verification).
6. **C-12** — Confirm `REDIS_URL` is set in all ECS tasks so `slowapi` (the only Redis-backed limiter) actually works across replicas.
7. **C-13** — Add `FINANCIAL_CONSTRAINT_BLOCK` + `INJECTION_GUARD` to `safe_openai_live_connector.py` prompt builder.
8. **C-5 through C-8** — `app/api/` routers: do NOT mount until auth is added. Document this explicitly.
9. **H-3** — Add DB indexes: `AgentJob.workspace_id`, `AgentJob.status`, `APIKey.workspace_id`, `WorkspaceIntegration.workspace_id`.
10. **H-4** — Add FK constraints on `WorkspaceReportSettings`, `WeeklyReport`, `ReportFeedback`.

### One-line fixes (do now):
- `agent_worker.py:314`: change to `job.output_data = output`
- `agents.py:503`: remove `"model": model` from SSE start event JSON
- `agents.py:499`: change to `"AI service not configured"`
- `agents.py:515`: change to `"Stream error occurred"`
- `stripe.py:108,138,153,179,198`: change all `detail=str(e)` to `detail="Payment processing error"`
- `main.py:312,324`: change to `"error: database unreachable"` / `"error: redis unreachable"`
- `admin.py:720`: change to `"account_id": os.getenv("AWS_ACCOUNT_ID", "")` and remove ECS detail strings
