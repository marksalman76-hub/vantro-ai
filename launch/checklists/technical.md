# Vantro.ai Technical Launch Checklist

## 1. Database

- [ ] Alembic at head: `cd backend && alembic current` outputs `021_team_runs (head)`
- [ ] Production RDS migrated: `alembic upgrade head`
- [ ] pgvector extension installed on RDS: `CREATE EXTENSION IF NOT EXISTS vector;`
- [ ] Connection pooling configured (pool_size, max_overflow set in `backend/app/database.py`)
- [ ] DATABASE_REPLICA_URL set for read replica (used by `get_read_db()` on GET endpoints)
- [ ] RDS max_connections ≥ ECS task count × connection pool size (check parameter group)
- [ ] workspace_id indexes applied: confirm migration `017_indexes_features_webhooks.py` applied and in chain
- [ ] No orphaned Workspaces: `SELECT w.id, ca.id FROM workspaces w LEFT JOIN credits_accounts ca ON ca.workspace_id = w.id WHERE ca.id IS NULL` returns zero rows
- [ ] Fernet encryption key (INTEGRATION_ENCRYPTION_KEY) was NOT rotated without re-encrypting existing `encrypted_value` rows

## 2. Backend / FastAPI

- [ ] ENVIRONMENT=production set in ECS task definition (disables /docs and /redoc)
- [ ] SECRET_KEY: minimum 32 chars, loaded from AWS Secrets Manager (not .env file)
- [ ] ANTHROPIC_API_KEY loaded from Secrets Manager (never in .env in production)
- [ ] INTEGRATION_ENCRYPTION_KEY explicitly set in Secrets Manager (fallback to SECRET_KEY derivation confirmed acceptable, or set explicitly)
- [ ] OPENAI_API_KEY set (required for pgvector skill RAG embeddings; silent-skip if absent means RAG is disabled)
- [ ] OpenAPI docs disabled: `curl https://api.vantro.ai/docs` → 404; `curl https://api.vantro.ai/redoc` → 404
- [ ] Health endpoint live: `curl https://api.vantro.ai/health` → 200
- [ ] ECS task runs as non-root user (check Dockerfile USER directive)
- [ ] uvicorn launched with `--workers 1` per ECS task (or gunicorn + uvicorn worker class)
- [ ] TESTING env var NOT set in ECS task definition (would disable agent worker loop in conftest)
- [ ] No `.env` file present in ECS container image (verify Dockerfile .dockerignore)

## 3. Frontend / Next.js

- [ ] `cd frontend && npm run build` exits 0 with zero errors
- [ ] `cd frontend && npm run lint` exits 0 with zero warnings/errors
- [ ] No backend URLs in frontend source: `grep -r "localhost:8000\|api\.vantro\|fastapi" frontend/app/` returns nothing
- [ ] No model/provider names exposed: `grep -r "claude\|gpt-4\|anthropic\|haiku\|sonnet\|opus" frontend/app/` returns nothing
- [ ] NEXT_PUBLIC_ environment variables contain no secrets (audit all NEXT_PUBLIC_ vars)
- [ ] All API calls proxy through Next.js route handlers (no direct backend URL in client bundles)
- [ ] Build output per-page size reasonable (< 10 MB per route chunk)
- [ ] NEXT_PUBLIC_API_URL (if any) points to internal Next.js route, not bare backend

## 4. Security

- [ ] Server header absent: `curl -I https://vantro.ai | grep -i server` returns no Server line
- [ ] SecurityHeadersMiddleware active in `backend/app/main.py` (strips Server header on every response)
- [ ] INJECTION_GUARD block present in every assembled system prompt (verify in `backend/app/agents/agent_executor.py`)
- [ ] FINANCIAL_CONSTRAINT_BLOCK prepended to every agent execution (verify in `backend/app/agents/agent_executor.py`)
- [ ] `scan_for_financial_actions()` called on every agent output before transitioning job to `completed`
- [ ] Suspicious path blocking active: `curl https://api.vantro.ai/.env` → 403; `curl https://api.vantro.ai/wp-admin` → 403
- [ ] `SUSPICIOUS_PATH_MARKERS` list in `app/core/security_hardening_runtime.py` includes `/.env`, `/wp-admin`, `/phpmyadmin`, `/information_schema`, `<script`, `../`
- [ ] Auth rate limit enforced: AUTH_RATE_LIMIT_MAX_REQUESTS=40 per 60s per IP on all auth routes
- [ ] General rate limit: RATE_LIMIT_MAX_REQUESTS=180; admin rate limit: ADMIN_RATE_LIMIT_MAX_REQUESTS=90
- [ ] WorkspaceIntegration encrypted_value never in any API response: `GET /api/integrations` returns only `redacted_meta()` shape (`{present, length, redacted, prefix}`)
- [ ] HITL-3 approval events written to audit_logs table (verify at least one row per approval action)
- [ ] CSRF protection enabled if cookie-based auth is in use

## 5. Agent System

- [ ] Catalogue count correct: `cd backend && python -c "from app.agents.agent_registry import AGENT_CATALOGUE; assert len(AGENT_CATALOGUE) == 27, f'Got {len(AGENT_CATALOGUE)}'; print('OK: 27 agents')"` prints `OK: 27 agents`
- [ ] All 27 agents have `min_package` set (starter/growth/business/enterprise) — no None values
- [ ] AGENT_ALIASES in `agent_registry.py` cover all legacy IDs for backward compatibility
- [ ] HITL-3 flow verified end-to-end: `POST /api/agents/head_agent/run` → AgentJob.status == `pending_approval` → admin approves → status → `approved` → worker executes → `completed`
- [ ] HITL-0 agents use Haiku model: confirm HITL_MODEL_MAP in `backend/app/agents/agent_executor.py` maps 0 → Haiku
- [ ] HITL-1/2 agents use Sonnet model: confirm HITL_MODEL_MAP maps 1 and 2 → Sonnet
- [ ] Financial scanner test: synthesize agent output containing "I will purchase" → job routes to `pending_financial_review` and admin email sent
- [ ] AGENTS_MAY_NOT_SPEND=True, AGENTS_MAY_NOT_SCALE_PAID=True, AGENTS_MAY_NOT_SIGN_AGREEMENTS=True in executor
- [ ] Agent worker loop starts on FastAPI startup (verify `lifespan` context manager in `backend/app/main.py` spawns worker)
- [ ] MAX_CONCURRENT_JOBS=3 enforced in `backend/app/agents/agent_worker.py`
- [ ] POLL_INTERVAL_SECONDS=5 acceptable under expected production load (increase if CPU spikes observed)
- [ ] CloudWatch metric emission confirmed: "Vantro/AgentJobs" namespace has data points in CloudWatch console
- [ ] Skill RAG auto-index runs every 6h in background: confirm `_reindex_new_skills()` scheduled in worker
- [ ] Skill RAG manual trigger works: `POST /api/admin/skills/index` returns 200

## 6. Credits System

- [ ] TOKENS_PER_CREDIT = 1000 constant set in `backend/app/agents/agent_executor.py`
- [ ] Credit deduction runs AFTER job completion (not pre-deducted before LLM call)
- [ ] `credits_used` column populated on every completed AgentJob row (spot-check with: `SELECT id, credits_used FROM agent_jobs WHERE status='completed' AND credits_used IS NULL`)
- [ ] Package tier gates enforced: starter workspace cannot invoke business-tier or enterprise-tier agents (verify 403 returned)
- [ ] CreditsAccount.balance never goes negative: DB constraint or application-level guard in place
- [ ] End-to-end credits test: run HITL-0 agent → confirm `credits_used > 0` on AgentJob and `CreditsAccount.balance` decremented by same amount

## 7. Full Test Suite

- [ ] `cd backend && TESTING=1 PYTHONPATH=. pytest tests/ -q` — all tests pass, exit 0
- [ ] Zero skipped tests without an explicit `@pytest.mark.skip(reason="...")` annotation
- [ ] No hardcoded credentials, API keys, or secrets in any test file (`grep -r "sk-\|AKIA\|password123" backend/tests/`)
