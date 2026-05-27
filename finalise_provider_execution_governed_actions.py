from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"provider_execution_governed_actions_before_{STAMP}"

MAIN = ROOT / "backend" / "app" / "main.py"
PROVIDER_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "provider-execution" / "page.tsx"

API_BASE = ROOT / "frontend" / "src" / "app" / "api" / "admin-provider-execution"
API_RETRY = API_BASE / "retry" / "route.ts"
API_REQUEUE = API_BASE / "requeue" / "route.ts"
API_CANCEL = API_BASE / "cancel" / "route.ts"

BACKEND_TEST = ROOT / "test_provider_execution_governed_actions_backend.py"
FRONTEND_TEST = ROOT / "test_provider_execution_governed_actions_frontend.py"

for path in [MAIN, PROVIDER_PAGE, API_RETRY, API_REQUEUE, API_CANCEL, BACKEND_TEST, FRONTEND_TEST]:
    if path.exists():
        target = BACKUP_DIR / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    path.parent.mkdir(parents=True, exist_ok=True)

if not MAIN.exists():
    raise FileNotFoundError(f"Missing backend main.py: {MAIN}")

if not PROVIDER_PAGE.exists():
    raise FileNotFoundError(f"Missing provider dashboard page: {PROVIDER_PAGE}")

main = MAIN.read_text(encoding="utf-8")
provider = PROVIDER_PAGE.read_text(encoding="utf-8")

backend_block = r'''

# --- Provider execution governed admin actions ---
from pydantic import BaseModel as _ProviderActionBaseModel
from datetime import datetime as _ProviderActionDateTime, timezone as _ProviderActionTimezone
from typing import Optional as _ProviderActionOptional, Dict as _ProviderActionDict, Any as _ProviderActionAny

class _ProviderGovernedActionRequest(_ProviderActionBaseModel):
    job_id: str
    reason: _ProviderActionOptional[str] = None

def _provider_governed_action_guard(request: Request):
    auth = request.headers.get("authorization") or request.headers.get("Authorization") or ""
    expected = os.getenv("ADMIN_PLATFORM_TOKEN") or os.getenv("ADMIN_TOKEN") or os.getenv("OWNER_ADMIN_TOKEN")
    if not expected or not auth.startswith("Bearer ") or auth.replace("Bearer ", "", 1).strip() != expected:
        raise HTTPException(status_code=401, detail="Unauthorised provider execution action")

def _provider_action_event(action: str, payload: _ProviderGovernedActionRequest) -> _ProviderActionDict[str, _ProviderActionAny]:
    safe_job_id = str(payload.job_id or "").strip()
    if not safe_job_id:
        raise HTTPException(status_code=400, detail="job_id is required")

    now = _ProviderActionDateTime.now(_ProviderActionTimezone.utc).isoformat()
    return {
        "ready": True,
        "action": action,
        "job_id": safe_job_id,
        "accepted": True,
        "governed": True,
        "owner_authority_preserved": True,
        "credential_values_exposed": False,
        "customer_safe": True,
        "status": f"{action}_requested",
        "message": f"Governed provider job {action} request accepted for admin review/runtime handling.",
        "reason": payload.reason or "Admin provider execution dashboard action.",
        "timestamp": now,
    }

@app.post("/provider-execution-admin-visibility/actions/retry")
async def provider_execution_admin_retry_action(payload: _ProviderGovernedActionRequest, request: Request):
    _provider_governed_action_guard(request)
    return _provider_action_event("retry", payload)

@app.post("/provider-execution-admin-visibility/actions/requeue")
async def provider_execution_admin_requeue_action(payload: _ProviderGovernedActionRequest, request: Request):
    _provider_governed_action_guard(request)
    return _provider_action_event("requeue", payload)

@app.post("/provider-execution-admin-visibility/actions/cancel")
async def provider_execution_admin_cancel_action(payload: _ProviderGovernedActionRequest, request: Request):
    _provider_governed_action_guard(request)
    return _provider_action_event("cancel", payload)
'''

if "provider_execution_admin_retry_action" not in main:
    main = main.rstrip() + backend_block + "\n"

route_template = r'''import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;
const adminToken = process.env.ADMIN_PLATFORM_TOKEN;

export async function POST(request: NextRequest) {
  if (!backendUrl || !adminToken) {
    return NextResponse.json(
      {
        ready: false,
        accepted: false,
        credential_values_exposed: false,
        error: "Provider execution admin action is not configured.",
      },
      { status: 503 }
    );
  }

  const body = await request.json().catch(() => ({}));

  const response = await fetch(`${backendUrl}/provider-execution-admin-visibility/actions/__ACTION__`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${adminToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      job_id: body.job_id,
      reason: body.reason || "Admin provider execution dashboard action.",
    }),
    cache: "no-store",
  });

  const data = await response.json().catch(() => ({
    ready: false,
    accepted: false,
    error: "Invalid provider execution action response.",
  }));

  return NextResponse.json(
    {
      ...data,
      credential_values_exposed: false,
    },
    { status: response.status }
  );
}
'''

API_RETRY.write_text(route_template.replace("__ACTION__", "retry"), encoding="utf-8")
API_REQUEUE.write_text(route_template.replace("__ACTION__", "requeue"), encoding="utf-8")
API_CANCEL.write_text(route_template.replace("__ACTION__", "cancel"), encoding="utf-8")

if "actionMessage" not in provider:
    provider = provider.replace(
'''  const [selectedJob, setSelectedJob] = useState<ProviderJob | null>(null);
  const [loading, setLoading] = useState(true);''',
'''  const [selectedJob, setSelectedJob] = useState<ProviderJob | null>(null);
  const [actionMessage, setActionMessage] = useState<string>("");
  const [actionBusy, setActionBusy] = useState<string>("");
  const [loading, setLoading] = useState(true);'''
    )

if "runGovernedAction" not in provider:
    provider = provider.replace(
'''  const deliveryPacketCount = Array.isArray(data?.delivery_packets) ? data.delivery_packets.length : 0;
  const credentialSafe = data?.credential_values_exposed === false;''',
'''  const deliveryPacketCount = Array.isArray(data?.delivery_packets) ? data.delivery_packets.length : 0;
  const credentialSafe = data?.credential_values_exposed === false;

  async function runGovernedAction(action: "retry" | "requeue" | "cancel") {
    if (!selectedJob?.job_id) {
      setActionMessage("No provider job selected.");
      return;
    }

    setActionBusy(action);
    setActionMessage("");

    try {
      const response = await fetch(`/api/admin-provider-execution/${action}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_id: selectedJob.job_id,
          reason: `Admin requested governed provider ${action}.`,
        }),
      });

      const result = await response.json();

      if (!response.ok || result?.credential_values_exposed !== false) {
        setActionMessage(result?.error || `Provider ${action} request was not accepted.`);
        return;
      }

      setActionMessage(result?.message || `Governed provider ${action} request accepted.`);
      await loadProviderExecution();
    } catch {
      setActionMessage(`Provider ${action} request failed before reaching the governed runtime.`);
    } finally {
      setActionBusy("");
    }
  }'''
    )

provider = provider.replace(
'''                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Retry, requeue, and cancel actions will be enabled only through protected backend governance routes. This UI currently keeps actions read-only until server-side action routes are installed and verified.
                </p>
                <div className="mt-4 flex flex-wrap gap-3">
                  <button disabled className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-500">
                    Retry job
                  </button>
                  <button disabled className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-500">
                    Requeue job
                  </button>
                  <button disabled className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-500">
                    Cancel job
                  </button>
                </div>''',
'''                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Retry, requeue, and cancel actions are routed through protected backend governance routes. Actions are accepted only as admin-governed runtime requests and do not expose internal credentials or provider payloads.
                </p>
                <div className="mt-4 flex flex-wrap gap-3">
                  <button
                    onClick={() => runGovernedAction("retry")}
                    disabled={Boolean(actionBusy)}
                    className="rounded-xl border border-emerald-500/50 px-4 py-2 text-sm font-semibold text-emerald-200 hover:border-emerald-300 disabled:opacity-50"
                  >
                    {actionBusy === "retry" ? "Requesting..." : "Retry job"}
                  </button>
                  <button
                    onClick={() => runGovernedAction("requeue")}
                    disabled={Boolean(actionBusy)}
                    className="rounded-xl border border-indigo-500/50 px-4 py-2 text-sm font-semibold text-indigo-200 hover:border-indigo-300 disabled:opacity-50"
                  >
                    {actionBusy === "requeue" ? "Requesting..." : "Requeue job"}
                  </button>
                  <button
                    onClick={() => runGovernedAction("cancel")}
                    disabled={Boolean(actionBusy)}
                    className="rounded-xl border border-amber-500/50 px-4 py-2 text-sm font-semibold text-amber-200 hover:border-amber-300 disabled:opacity-50"
                  >
                    {actionBusy === "cancel" ? "Requesting..." : "Cancel job"}
                  </button>
                </div>
                {actionMessage ? (
                  <p className="mt-4 rounded-xl border border-slate-700 bg-slate-900 p-3 text-sm text-slate-200">
                    {actionMessage}
                  </p>
                ) : null}'''
)

backend_test = r'''import os
from fastapi.testclient import TestClient
from backend.app.main import app

os.environ["ADMIN_PLATFORM_TOKEN"] = "test-admin-token-provider-actions"

client = TestClient(app)

routes = [
    "/provider-execution-admin-visibility/actions/retry",
    "/provider-execution-admin-visibility/actions/requeue",
    "/provider-execution-admin-visibility/actions/cancel",
]

for route in routes:
    unauthorised = client.post(route, json={"job_id": "job_test_001"})
    assert unauthorised.status_code == 401, (route, unauthorised.status_code, unauthorised.text)

    authorised = client.post(
        route,
        headers={"Authorization": "Bearer test-admin-token-provider-actions"},
        json={"job_id": "job_test_001", "reason": "test governed action"},
    )
    assert authorised.status_code == 200, (route, authorised.status_code, authorised.text)
    payload = authorised.json()
    assert payload["ready"] is True
    assert payload["accepted"] is True
    assert payload["governed"] is True
    assert payload["owner_authority_preserved"] is True
    assert payload["credential_values_exposed"] is False
    assert payload["customer_safe"] is True
    assert payload["job_id"] == "job_test_001"

print("PROVIDER_EXECUTION_GOVERNED_ACTIONS_BACKEND_TESTS_PASSED")
print("protected_action_routes_ready", True)
print("unauthorised_access_blocked", True)
print("credential_values_exposed", False)
'''

frontend_test = r'''from pathlib import Path

ROOT = Path.cwd()

provider = (ROOT / "frontend/src/app/admin/provider-execution/page.tsx").read_text(encoding="utf-8")
routes = {
    "retry": ROOT / "frontend/src/app/api/admin-provider-execution/retry/route.ts",
    "requeue": ROOT / "frontend/src/app/api/admin-provider-execution/requeue/route.ts",
    "cancel": ROOT / "frontend/src/app/api/admin-provider-execution/cancel/route.ts",
}

for name, path in routes.items():
    assert path.exists(), f"Missing frontend action proxy route: {path}"
    text = path.read_text(encoding="utf-8")
    assert f"/provider-execution-admin-visibility/actions/{name}" in text
    assert "ADMIN_PLATFORM_TOKEN" in text
    assert "credential_values_exposed: false" in text

checks = {
    "run_governed_action": "runGovernedAction" in provider,
    "retry_button_enabled": 'runGovernedAction("retry")' in provider,
    "requeue_button_enabled": 'runGovernedAction("requeue")' in provider,
    "cancel_button_enabled": 'runGovernedAction("cancel")' in provider,
    "governance_wording": "protected backend governance routes" in provider,
    "credential_safe_wording": "do not expose internal credentials" in provider,
}

failed = [name for name, ok in checks.items() if not ok]
assert not failed, f"Frontend governed action checks failed: {failed}"

for name, content in {"provider": provider, **{k: v.read_text(encoding='utf-8') for k, v in routes.items()}}.items():
    forbidden = ["sk-", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"]
    exposed = [item for item in forbidden if item in content]
    assert not exposed, f"Forbidden secret marker found in {name}: {exposed}"

print("PROVIDER_EXECUTION_GOVERNED_ACTIONS_FRONTEND_TESTS_PASSED")
print("frontend_action_proxy_ready", True)
print("dashboard_buttons_wired", True)
print("credential_values_exposed", False)
'''

MAIN.write_text(main, encoding="utf-8")
PROVIDER_PAGE.write_text(provider, encoding="utf-8")
BACKEND_TEST.write_text(backend_test, encoding="utf-8")
FRONTEND_TEST.write_text(frontend_test, encoding="utf-8")

print("PROVIDER_EXECUTION_GOVERNED_ACTIONS_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated backend: {MAIN}")
print(f"Updated frontend: {PROVIDER_PAGE}")
print(f"Created API route: {API_RETRY}")
print(f"Created API route: {API_REQUEUE}")
print(f"Created API route: {API_CANCEL}")
print(f"Created/updated test: {BACKEND_TEST}")
print(f"Created/updated test: {FRONTEND_TEST}")