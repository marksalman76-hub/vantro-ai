# Sentry Configuration — Vantro.ai

Multi-tenant AI agent SaaS. Solo founder setup. All errors captured, noisy expected errors filtered.

---

## 1. Backend Sentry Setup (FastAPI / Python)

### Install

```bash
pip install "sentry-sdk[fastapi,sqlalchemy,httpx]"
```

Add to `backend/requirements.txt`:
```
sentry-sdk[fastapi,sqlalchemy,httpx]>=2.14.0
```

### `app/main.py` — `sentry_sdk.init()` call

Add this block **before** the FastAPI app is created (top of `main.py`, after imports):

```python
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging


def _sentry_before_send(event: dict, hint: dict) -> dict | None:
    """
    Filter hook called before every event is sent to Sentry.

    Rules:
      - DROP:  OpenAI 401 errors from skill RAG indexing (expected when
               OPENAI_API_KEY is missing; not actionable).
      - ALWAYS SEND: financial_scanner events and HITL-3 failures,
               even if they would otherwise be sampled out.
    """
    exc_info = hint.get("exc_info")

    if exc_info:
        exc_type, exc_value, _ = exc_info
        exc_str = str(exc_value)
        exc_name = exc_type.__name__ if exc_type else ""

        # --- DROP: OpenAI 401 / SkillIndexingError ---
        # These fire when OPENAI_API_KEY is absent. Expected in dev/staging.
        is_skill_indexing_error = exc_name in (
            "SkillIndexingError",
            "OpenAIAuthenticationError",
        )
        is_openai_401 = (
            "api.openai.com" in exc_str and "401" in exc_str
        ) or (
            "openai" in exc_str.lower() and "authentication" in exc_str.lower()
        )

        # Also catch httpx / requests 401 to openai
        if not is_skill_indexing_error and not is_openai_401:
            # Check chained exceptions
            cause = getattr(exc_value, "__cause__", None) or getattr(
                exc_value, "__context__", None
            )
            if cause:
                cause_str = str(cause)
                if "api.openai.com" in cause_str and "401" in cause_str:
                    is_openai_401 = True

        if is_skill_indexing_error or is_openai_401:
            return None  # drop — do not send

    # --- ALWAYS SEND: financial scanner events ---
    tags = event.get("tags", {})
    extra = event.get("extra", {})
    message = event.get("message", "") or ""

    is_financial_scanner = (
        tags.get("financial_scanner") == "triggered"
        or "financial_scanner" in message
        or extra.get("financial_scanner_triggered")
    )

    is_hitl3_failure = (
        tags.get("hitl_level") == "3"
        and tags.get("agent_job_status") == "failed"
    )

    if is_financial_scanner or is_hitl3_failure:
        # Force-send: override any sampling that may have dropped this
        event.setdefault("tags", {})["force_capture"] = "true"
        return event

    return event


SENTRY_DSN = os.getenv("SENTRY_DSN")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=os.getenv("ENVIRONMENT", "development"),
        release=os.getenv("APP_VERSION", "unknown"),

        # 10% of transactions sampled for performance monitoring.
        # Errors are always captured (traces_sample_rate only affects
        # performance transactions, not error events).
        traces_sample_rate=0.1,

        # Capture 100% of errors (default; explicit for clarity).
        # Error sampling is controlled via before_send, not here.
        # Set to 1.0 to ensure all exceptions reach before_send.
        sample_rate=1.0,

        before_send=_sentry_before_send,

        integrations=[
            # Order matters: Starlette must come before FastAPI
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            LoggingIntegration(
                level=logging.WARNING,       # Breadcrumb level
                event_level=logging.ERROR,   # Capture as Sentry event
            ),
        ],

        # Scrub these from payloads before sending
        send_default_pii=False,

        # Extra context attached to every event
        # (workspace_id / job_id are added per-request via middleware below)
    )
```

### Middleware — tag every request with `workspace_id`, `agent_id`, `job_id`

Add this middleware class in `app/main.py` (or `app/middleware/sentry_context.py`) and register it:

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import sentry_sdk


class SentryContextMiddleware(BaseHTTPMiddleware):
    """
    Attaches workspace/agent/job context to the Sentry scope on every
    request so all events and transactions carry these tags.

    Reads from:
      - Path params: /api/agents/{agent_id}/run  → agent_id
      - Request state: set by auth/workspace resolution middleware
        (workspace_id, job_id added after job creation)
    """

    async def dispatch(self, request: Request, call_next):
        with sentry_sdk.new_scope() as scope:
            # workspace_id is resolved by the auth middleware and stored on
            # request.state.  Fall back to None if not yet resolved.
            workspace_id = getattr(request.state, "workspace_id", None)
            agent_id = request.path_params.get("agent_id") or request.path_params.get("id")
            job_id = getattr(request.state, "job_id", None)

            if workspace_id:
                scope.set_tag("workspace_id", str(workspace_id))
                scope.set_user({"id": str(workspace_id)})  # GDPR-safe: no email

            if agent_id:
                scope.set_tag("agent_id", str(agent_id))

            if job_id:
                scope.set_tag("job_id", str(job_id))

            response = await call_next(request)
            return response


# Register after auth middleware, before route handlers:
# app.add_middleware(SentryContextMiddleware)
```

Register order in `app/main.py`:

```python
# Middleware registration (order: last-added = first-executed)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SentryContextMiddleware)   # ← add this
# ... other middleware
```

### Update job scope after job creation

In `agent_worker.py` or wherever `AgentJob` is created, update the Sentry scope:

```python
import sentry_sdk

def _tag_job_scope(job: AgentJob) -> None:
    """Call immediately after AgentJob row is created."""
    with sentry_sdk.new_scope():
        sentry_sdk.set_tag("job_id", str(job.id))
        sentry_sdk.set_tag("agent_job_status", job.status)
        sentry_sdk.set_tag("hitl_level", str(job.hitl_level))
```

### Manually capture financial scanner triggers

In `app/agents/agent_executor.py` (or wherever `scan_for_financial_actions()` is called):

```python
import sentry_sdk


def _capture_financial_scanner_event(
    job_id: str,
    agent_id: str,
    workspace_id: str,
    matched_phrase: str,
    response_excerpt: str,
) -> None:
    """
    Capture a high-priority Sentry event when the financial scanner fires.
    Always sent — never filtered or sampled out (enforced in before_send).
    """
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("financial_scanner", "triggered")
        scope.set_tag("agent_job_status", "pending_financial_review")
        scope.set_tag("agent_id", agent_id)
        scope.set_tag("job_id", job_id)
        scope.set_tag("workspace_id", workspace_id)
        scope.set_level("error")

        scope.set_extra("matched_phrase", matched_phrase)
        # Truncate to avoid leaking full LLM output into Sentry
        scope.set_extra("response_excerpt", response_excerpt[:500])

        sentry_sdk.capture_message(
            f"financial_scanner triggered on job {job_id} — phrase: {matched_phrase!r}",
            level="error",
            scope=scope,
        )


# Usage in agent_executor.py:
#
# financial_hits = scan_for_financial_actions(agent_response)
# if financial_hits:
#     job.status = "pending_financial_review"
#     db.commit()
#     _capture_financial_scanner_event(
#         job_id=str(job.id),
#         agent_id=str(job.agent_id),
#         workspace_id=str(job.workspace_id),
#         matched_phrase=financial_hits[0],
#         response_excerpt=agent_response[:500],
#     )
#     send_admin_email(...)
```

### Capture HITL-3 failures

In `agent_worker.py`, in the exception handler for job processing:

```python
import sentry_sdk


def _capture_hitl3_failure(job: AgentJob, exc: Exception) -> None:
    """Always capture HITL-3 (Opus-level) job failures to Sentry."""
    if job.hitl_level != 3:
        return

    with sentry_sdk.new_scope() as scope:
        scope.set_tag("hitl_level", "3")
        scope.set_tag("agent_job_status", "failed")
        scope.set_tag("agent_id", str(job.agent_id))
        scope.set_tag("job_id", str(job.id))
        scope.set_tag("workspace_id", str(job.workspace_id))
        scope.set_level("error")
        sentry_sdk.capture_exception(exc, scope=scope)


# Usage in _process_job():
#
# except Exception as exc:
#     job.status = "failed"
#     db.commit()
#     _capture_hitl3_failure(job, exc)
#     raise
```

---

## 2. Frontend Sentry Setup (Next.js 16 / @sentry/nextjs)

### Install

```bash
cd frontend
npm install @sentry/nextjs
```

### `frontend/sentry.client.config.ts`

```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT ?? "development",
  release: process.env.NEXT_PUBLIC_APP_VERSION,

  // 10% of frontend performance transactions
  tracesSampleRate: 0.1,

  // Capture 100% of errors
  sampleRate: 1.0,

  // Do not send errors in development unless explicitly opted in
  enabled: process.env.NODE_ENV === "production",

  beforeBreadcrumb(breadcrumb) {
    /**
     * Tech stack opacity rule: strip any breadcrumb that contains
     * LLM provider or model names. Clients must never see these in
     * Sentry sessions, replays, or bug reports they share.
     */
    const PROVIDER_PATTERN = /claude|anthropic|openai|gpt|sonnet|haiku|opus/i;

    const data = breadcrumb.data;
    const message = breadcrumb.message ?? "";
    const category = breadcrumb.category ?? "";

    // Scrub URL breadcrumbs (XHR, fetch) that reference provider APIs
    if (data?.url && PROVIDER_PATTERN.test(String(data.url))) {
      return null; // drop
    }

    // Scrub console/log breadcrumbs containing provider names
    if (PROVIDER_PATTERN.test(message)) {
      return null; // drop
    }

    // Scrub navigation breadcrumbs (shouldn't leak provider names but guard anyway)
    if (category === "navigation" && PROVIDER_PATTERN.test(data?.to ?? "")) {
      return null;
    }

    return breadcrumb;
  },

  beforeSend(event) {
    // Strip any exception values that contain provider names
    const PROVIDER_PATTERN = /claude|anthropic|openai|gpt|sonnet|haiku|opus/i;

    if (event.exception?.values) {
      for (const ex of event.exception.values) {
        if (ex.value && PROVIDER_PATTERN.test(ex.value)) {
          ex.value = "[internal service error]";
        }
      }
    }

    return event;
  },
});
```

### `frontend/sentry.server.config.ts`

```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.SENTRY_DSN ?? process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.ENVIRONMENT ?? "development",
  release: process.env.APP_VERSION,

  // Server-side: capture all errors, 10% of transactions
  tracesSampleRate: 0.1,
  sampleRate: 1.0,

  enabled: process.env.NODE_ENV === "production",

  beforeBreadcrumb(breadcrumb) {
    const PROVIDER_PATTERN = /claude|anthropic|openai|gpt|sonnet|haiku|opus/i;
    const message = breadcrumb.message ?? "";
    const url = breadcrumb.data?.url ?? "";

    if (PROVIDER_PATTERN.test(message) || PROVIDER_PATTERN.test(url)) {
      return null;
    }
    return breadcrumb;
  },
});
```

### `frontend/sentry.edge.config.ts`

```typescript
import * as Sentry from "@sentry/nextjs";

// Edge runtime (middleware.ts). Minimal config — edge has limited APIs.
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT ?? "development",

  // Very low sample rate for edge middleware — high volume, low signal
  tracesSampleRate: 0.01,
  sampleRate: 1.0,

  enabled: process.env.NODE_ENV === "production",
});
```

### `frontend/next.config.js` — `withSentryConfig` wrapper

```javascript
// @ts-check
const { withSentryConfig } = require("@sentry/nextjs");

/** @type {import('next').NextConfig} */
const nextConfig = {
  // ... your existing Next.js config
};

module.exports = withSentryConfig(nextConfig, {
  // Sentry webpack plugin options (used at build time)
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
  authToken: process.env.SENTRY_AUTH_TOKEN,

  // Upload source maps but do NOT serve them publicly.
  // Maps are uploaded to Sentry, then deleted from the build output.
  hideSourceMaps: true,

  // Suppress noisy Sentry build output
  silent: true,

  // Automatically instrument Server Components and Route Handlers
  autoInstrumentServerFunctions: true,
  autoInstrumentMiddleware: true,

  // Suppress the Sentry tunnel route (not needed for basic setup)
  // tunnelRoute: "/monitoring",

  // Disable tree shaking of Sentry debug code in production
  disableLogger: true,
});
```

### Capturing a frontend error with workspace context (GDPR-safe)

```typescript
// Use this pattern anywhere in the frontend to manually capture errors.
// Pass workspace_id only — never email, name, or PII.

import * as Sentry from "@sentry/nextjs";

export function captureWorkspaceError(
  error: unknown,
  workspaceId: string,
  context?: Record<string, string>
): void {
  Sentry.withScope((scope) => {
    // GDPR-safe user identifier: workspace ID only, no email
    scope.setUser({ id: workspaceId });
    scope.setTag("workspace_id", workspaceId);

    if (context) {
      for (const [key, value] of Object.entries(context)) {
        scope.setExtra(key, value);
      }
    }

    Sentry.captureException(error);
  });
}

// Example usage in an agent job polling hook:
//
// try {
//   const result = await pollJobStatus(jobId);
// } catch (err) {
//   captureWorkspaceError(err, currentWorkspaceId, {
//     job_id: jobId,
//     agent_id: agentId,
//   });
//   throw err;
// }
```

---

## 3. Sentry Alert Rules (UI Configuration)

Configure these in **Sentry → Alerts → Create Alert Rule** for project `vantro-backend` and `vantro-frontend`.

### 3.1 New Issue → Immediate Email

| Field | Value |
|---|---|
| **Alert type** | Issue alert |
| **Trigger** | A new issue is created |
| **Action** | Send email to `mark.salman76@gmail.com` |
| **Priority** | High |
| **Name** | `New issue — immediate` |

### 3.2 Financial Scanner Triggered → Immediate + High Priority

| Field | Value |
|---|---|
| **Alert type** | Issue alert |
| **Trigger** | An event occurs with tag `financial_scanner = triggered` |
| **Conditions** | `The event's tags match: financial_scanner equals triggered` |
| **Action** | Send email to `mark.salman76@gmail.com` |
| **Action** | Create Sentry issue with priority **Critical** |
| **Name** | `Financial scanner triggered — critical` |
| **Note** | Set **resolve threshold** to manual only — never auto-resolve |

### 3.3 HITL-3 Job Failed → Immediate

| Field | Value |
|---|---|
| **Alert type** | Issue alert |
| **Conditions** | Tag `hitl_level equals 3` AND tag `agent_job_status equals failed` |
| **Trigger** | An event occurs matching the above tags |
| **Action** | Send email to `mark.salman76@gmail.com` |
| **Priority** | High |
| **Name** | `HITL-3 job failure` |

### 3.4 Performance — Agent Run P95 > 10s

| Field | Value |
|---|---|
| **Alert type** | Performance / Metric alert |
| **Metric** | `p95(transaction.duration)` |
| **Filter** | `transaction = POST /api/agents/{id}/run` |
| **Threshold** | Greater than `10000ms` for 5 minutes |
| **Action** | Send email to `mark.salman76@gmail.com` |
| **Name** | `Agent run P95 > 10s` |

> In Sentry's filter field for transaction, use the pattern `*agents*run` if wildcard matching is needed for the `{id}` path param.

### 3.5 Weekly Digest

| Field | Value |
|---|---|
| **Alert type** | Issue alert |
| **Trigger** | Weekly digest |
| **Recipients** | `mark.salman76@gmail.com` |
| **Name** | `Weekly issues digest` |

Configure in **Settings → Notifications → Weekly Reports** and enable for the `vantro` Sentry org.

---

## 4. Environment Variables

### Backend (`backend/.env` / ECS task definition secrets)

```env
# Required
SENTRY_DSN=https://<key>@o<org_id>.ingest.sentry.io/<project_id>

# Used by sentry_sdk.init()
ENVIRONMENT=production          # or staging / development
APP_VERSION=1.0.0               # set by CI from git tag
```

### Frontend (`frontend/.env.local` / Vercel environment variables)

```env
# Public — intentionally exposed to the browser. Contains no secrets.
# The DSN is safe to expose: it only allows event ingestion, not read access.
NEXT_PUBLIC_SENTRY_DSN=https://<key>@o<org_id>.ingest.sentry.io/<project_id>
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_APP_VERSION=1.0.0

# Build-time only — for source map upload. Never exposed to browser.
# Set in CI environment (GitHub Actions secret, Vercel env var marked "Build").
SENTRY_AUTH_TOKEN=<token-from-sentry-settings-auth-tokens>
SENTRY_ORG=vantro               # Your Sentry org slug
SENTRY_PROJECT=vantro-frontend  # Your Sentry project slug
```

> **Why `NEXT_PUBLIC_SENTRY_DSN` is safe:** Sentry DSNs only allow writing events to your project. They cannot be used to read data. The Sentry Auth Token (`SENTRY_AUTH_TOKEN`) is secret — it allows source map uploads and API access. Never set it as `NEXT_PUBLIC_`.

---

## 5. Testing the Integration

### 5.1 Backend — verify errors reach Sentry

Add a **temporary** test route to `app/main.py` (remove before production deploy or gate behind `ENVIRONMENT != production`):

```python
@app.get("/api/internal/sentry-test", include_in_schema=False)
async def sentry_test():
    """Smoke test: raises an exception that should appear in Sentry within 30s."""
    import os
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(status_code=404, detail="Not found")
    raise ValueError("Sentry integration test — Vantro backend")
```

Trigger with curl:

```bash
curl -X GET http://localhost:8000/api/internal/sentry-test
# Expected: 500 response
# Expected in Sentry within ~30s: new issue "ValueError: Sentry integration test"
```

Verify the financial scanner capture path:

```bash
# In a Python shell with the app loaded:
python - <<'EOF'
import sentry_sdk
sentry_sdk.init(dsn="<your-dsn>")  # or load from env
with sentry_sdk.new_scope() as scope:
    scope.set_tag("financial_scanner", "triggered")
    sentry_sdk.capture_message(
        "financial_scanner triggered on job test-001 — phrase: 'authorize payment'",
        level="error",
        scope=scope,
    )
print("Event sent — check Sentry dashboard")
EOF
```

### 5.2 Frontend — trigger a test error

Add a **dev-only** button to any page component:

```typescript
// components/dev/SentryTestButton.tsx
// Only render in non-production environments

"use client";
import * as Sentry from "@sentry/nextjs";

export function SentryTestButton() {
  if (process.env.NODE_ENV === "production") return null;

  return (
    <button
      onClick={() => {
        Sentry.captureException(
          new Error("Sentry frontend integration test — Vantro")
        );
        // Also test the workspace context helper:
        // captureWorkspaceError(new Error("test"), "ws_test_001");
      }}
      style={{ position: "fixed", bottom: 16, right: 16, zIndex: 9999 }}
    >
      Test Sentry
    </button>
  );
}
```

Check Sentry dashboard → Issues within 30 seconds of clicking.

### 5.3 Verify filtered events are NOT sent

```bash
# Simulate an OpenAI 401 that should be dropped by before_send:
python - <<'EOF'
import sentry_sdk

events_sent = []

def mock_transport(event):
    events_sent.append(event)

sentry_sdk.init(
    dsn="<your-dsn>",
    before_send=_sentry_before_send,  # import from app/main.py
    transport=mock_transport,
)

class FakeOpenAI401(Exception):
    pass

try:
    raise FakeOpenAI401(
        "api.openai.com returned 401 authentication failed"
    )
except FakeOpenAI401:
    sentry_sdk.capture_exception()

print(f"Events sent: {len(events_sent)}")  # Expected: 0
assert len(events_sent) == 0, "OpenAI 401 should be filtered!"
print("PASS — OpenAI 401 correctly filtered")
EOF
```
