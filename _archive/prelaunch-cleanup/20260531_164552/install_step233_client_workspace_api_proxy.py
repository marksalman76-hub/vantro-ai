from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
FRONTEND = ROOT / "frontend"
APP = FRONTEND / "src" / "app"
CLIENT_PAGE = APP / "client" / "page.tsx"
API_DIR = APP / "api"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

client_me_route = API_DIR / "client-me" / "route.ts"
run_agent_route = API_DIR / "run-agent" / "route.ts"

for file in [CLIENT_PAGE, client_me_route, run_agent_route]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step233_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

(client_me_route.parent).mkdir(parents=True, exist_ok=True)
(run_agent_route.parent).mkdir(parents=True, exist_ok=True)

client_me_route.write_text(r'''
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://ecommerce-ai-agent-platform-1.onrender.com";

export async function GET() {
  const cookieStore = await cookies();
  const sessionToken = cookieStore.get("client_session")?.value;

  if (!sessionToken) {
    return NextResponse.json(
      {
        success: false,
        error: "client_session_missing",
      },
      { status: 401 }
    );
  }

  const response = await fetch(
    `${BACKEND_URL}/client/me?session_token=${encodeURIComponent(sessionToken)}`,
    {
      method: "GET",
      cache: "no-store",
    }
  );

  const data = await response.json().catch(() => ({
    success: false,
    error: "invalid_backend_response",
  }));

  return NextResponse.json(data, { status: response.status });
}
'''.lstrip(), encoding="utf-8")

run_agent_route.write_text(r'''
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://ecommerce-ai-agent-platform-1.onrender.com";

function scrubClientVisiblePayload(value: unknown): unknown {
  const raw = JSON.stringify(value ?? {});
  const scrubbed = raw
    .replace(/client_[a-zA-Z0-9_-]+/g, "[protected]")
    .replace(/tenant_[a-zA-Z0-9_-]+/g, "[protected]")
    .replace(/sk_live_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/sk_test_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/whsec_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/postgresql:\/\/[^"]+/g, "[protected]");

  try {
    return JSON.parse(scrubbed);
  } catch {
    return {
      success: false,
      message: "Unable to render response safely.",
    };
  }
}

export async function POST(request: NextRequest) {
  const cookieStore = await cookies();
  const sessionToken = cookieStore.get("client_session")?.value;

  if (!sessionToken) {
    return NextResponse.json(
      {
        success: false,
        message: "Please log in again before running an agent.",
      },
      { status: 401 }
    );
  }

  const body = await request.json();

  const meResponse = await fetch(
    `${BACKEND_URL}/client/me?session_token=${encodeURIComponent(sessionToken)}`,
    {
      method: "GET",
      cache: "no-store",
    }
  );

  const meData = await meResponse.json().catch(() => null);

  if (!meResponse.ok || !meData?.success || !meData?.account) {
    return NextResponse.json(
      {
        success: false,
        message: "Client account could not be verified.",
      },
      { status: 401 }
    );
  }

  const account = meData.account;
  const activeAgents: string[] = Array.isArray(account.active_agents)
    ? account.active_agents
    : [];

  const requestedAgent = String(body.requested_agent || "");

  if (!activeAgents.includes(requestedAgent)) {
    return NextResponse.json(
      {
        success: false,
        message: "This agent is not active on your account.",
      },
      { status: 403 }
    );
  }

  const backendPayload = {
    tenant_id: account.tenant_id,
    requested_agent: requestedAgent,
    workflow_stage: "store_creation",
    action_type: "product_copy_generation",
    actor_role: "customer",
    owner_approved: false,
    task: String(body.task || ""),
    region: body.region || "Global",
    language: body.language || "English",
    currency: body.currency || "USD",
  };

  const response = await fetch(`${BACKEND_URL}/run-agent`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-tenant-id": account.tenant_id,
      "x-actor-role": "customer",
    },
    body: JSON.stringify(backendPayload),
  });

  const data = await response.json().catch(() => ({
    success: false,
    message: "Backend returned an invalid response.",
  }));

  const safeData = scrubClientVisiblePayload(data);

  return NextResponse.json(safeData, { status: response.status });
}
'''.lstrip(), encoding="utf-8")

page = CLIENT_PAGE.read_text(encoding="utf-8")

page = page.replace(
    '''const API_BASE =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://ecommerce-ai-agent-platform-1.onrender.com";
''',
    '''const API_BASE = "";
'''
)

page = page.replace(
    '''      const me = await fetch(`${API_BASE}/client/me`, {
        credentials: "include",
        cache: "no-store",
      });
''',
    '''      const me = await fetch(`/api/client-me`, {
        credentials: "include",
        cache: "no-store",
      });
'''
)

page = page.replace(
    '''      const response = await fetch(`${API_BASE}/run-agent`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-tenant-id": account?.tenant_id || "client_portal",
          "x-actor-role": "customer",
        },
        body: JSON.stringify({
          tenant_id: account?.tenant_id || "client_portal",
          requested_agent: selectedAgent,
          workflow_stage: "client_execution",
          action_type: "product_copy_generation",
          actor_role: "customer",
          owner_approved: false,
          task,
        }),
      });
''',
    '''      const response = await fetch(`/api/run-agent`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          requested_agent: selectedAgent,
          task,
        }),
      });
'''
)

CLIENT_PAGE.write_text(page, encoding="utf-8")

py_compile.compile(str(ROOT / "install_step233_client_workspace_api_proxy.py"), doraise=True)

print("STEP_233_CLIENT_WORKSPACE_API_PROXY_INSTALLED")
print(f"Created/updated: {client_me_route}")
print(f"Created/updated: {run_agent_route}")
print(f"Updated: {CLIENT_PAGE}")
print("STEP_233_OK")