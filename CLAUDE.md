# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Backend
cd backend
$env:PYTHONPATH = "."; pytest tests/ -q                          # full suite
$env:PYTHONPATH = "."; pytest tests/test_research_agent.py -q    # single file
$env:PYTHONPATH = "."; pytest tests/ -k "test_credit" -q         # filter by name
python -m uvicorn app.main:app --reload --port 8000              # dev server
python scripts/index_skills.py                                   # re-index skill RAG

# Migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Frontend
cd frontend
npm run dev      # Next.js dev server (port 3000)
npm run build
npm run lint
```

Run tests with `TESTING=1` set to prevent the worker loop from starting in conftest.

## Architecture

### Multi-tenant isolation
`Organization` → `Workspace` → `CreditsAccount`. Every API call resolves to a workspace. All DB queries must filter by `workspace_id`. `WorkspaceIntegration` stores encrypted third-party credentials (Fernet, `app/services/encryption_service.py`) — the decrypted value is **never** returned in any API response, log, or error.

### 22-agent catalogue (`app/agents/`)
`agent_registry.py` is the single source of truth: 22 client-facing agents with package-tier gates (starter → growth → business → enterprise), HITL levels, and credit estimates. Aliases in `AGENT_ALIASES` preserve backward compatibility with legacy IDs. Assert `len(AGENT_CATALOGUE) == 22` must not change without deliberate approval.

**Job lifecycle:** `POST /api/agents/{id}/run` → `AgentJob` row written (status=`pending`) → `agent_worker.py` background loop picks up → `agent_executor.py` calls LLM → status transitions to `completed`, `pending_financial_review`, or `failed`.

### HITL (Human-in-the-Loop) model tiering
| Level | Model | Trigger |
|-------|-------|---------|
| HITL-0 | Haiku | Low-stakes, high-volume |
| HITL-1/2 | Sonnet | Standard agents |
| HITL-3 | Opus | Spend/scale approval required — job held `pending_approval` |

HITL-3 jobs must be manually approved by owner before the worker executes them.

### Agent execution pipeline
`agent_worker._process_job()` enriches context before executor call:
1. Workspace `business_context` injected
2. pgvector RAG (`skill_retriever`) retrieves top-3 relevant skill chunks from indexed `~/.claude/skills/`
3. Few-shot examples (`example_retriever`) for quality reference
4. Composio credentials for live tool access (if workspace has connected apps)

`agent_executor.execute_agent()` assembles system prompt as: **FINANCIAL_CONSTRAINT_BLOCK → INJECTION_GUARD → few-shot → skill context → agent core**. Tool-use loop activates if any tools available (analytics tools for `research_analytics_agent` + Composio tools for any agent with key).

### Financial governance (hard rules — cannot be bypassed)
- `AGENTS_MAY_NOT_SPEND = True`, `AGENTS_MAY_NOT_SCALE_PAID = True`, `AGENTS_MAY_NOT_SIGN_AGREEMENTS = True`
- `FINANCIAL_CONSTRAINT_BLOCK` is prepended to every system prompt
- Output scanner (`scan_for_financial_actions`) checks every response — any matched phrase routes job to `pending_financial_review` and emails admin
- Admin portal is unrestricted (no credit/package limits). Client portal is fully gated.

### Credential security rules
- Raw credential values: encrypted on receipt, never returned in any response, decrypted only during `/test` integration calls
- API responses about credentials use `redacted_meta()` only: `{present, length, redacted, prefix}`
- `WorkspaceIntegration` table: `encrypted_value` column, Fernet AES-128-CBC + HMAC-SHA256
- `INTEGRATION_ENCRYPTION_KEY` env var is the master key; derives from `SECRET_KEY` as fallback

### Skill RAG auto-indexing
Skills installed via `claude plugin install` to `~/.claude/skills/*/SKILL.md` are auto-indexed on server startup and every 6h by `agent_worker._reindex_new_skills()`. Requires `OPENAI_API_KEY` for embeddings (silent skip if missing). Manual trigger: `POST /api/admin/skills/index`.

### Database
PostgreSQL via SQLAlchemy. Primary + optional read replica (`DATABASE_REPLICA_URL`). Migrations in `alembic/versions/` — revision chain: 001→...→012. `get_db()` for writes, `get_read_db()` for read-heavy GET endpoints.

### Frontend
Next.js 14 App Router. All API calls proxy through Next.js to avoid exposing the backend URL. No backend URL, model names, or provider names are referenced in frontend code or responses.

## Security constraints — non-negotiable

**Tech stack opacity:** Clients must never learn what LLM providers, frameworks, or infrastructure this platform uses. Never expose provider model names (`claude-*`, `gpt-*`) in API responses, error messages, logs visible to clients, or frontend code. Generic error messages only to clients.

**OpenAPI docs disabled in production.** `ENVIRONMENT=production` must set `docs_url=None, redoc_url=None`. Never re-enable in production.

**Server header suppressed.** `SecurityHeadersMiddleware` in `main.py` must strip the `Server` header on every response.

**Injection guard:** `INJECTION_GUARD` block in every system prompt prevents prompt injection from client task inputs. Never remove it.

**Rate limits:** All auth routes: 10/min. Agent execution: enforced per workspace. Do not increase limits without reviewing the cost implications.

**Suspicious path detection** (`app/core/security_hardening_runtime.py`): scanner blocks `.env`, `wp-admin`, `phpmyadmin`, `information_schema`, `<script`, path traversal (`../`). Add new patterns here, not inline.

**AWS Option A production target:** ECS/Fargate + SQS + RDS + S3 + Secrets Manager + CloudWatch. AWS route cutover is flag-gated — stays disabled until all gates satisfied. All spend/scaling requires HITL-3 (owner/admin) approval.
