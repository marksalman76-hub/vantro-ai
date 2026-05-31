from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
api_dir = ROOT / "frontend" / "src" / "app" / "api" / "delegated-workforce-execution"
api_file = api_dir / "route.ts"

backup = ROOT / "backups" / f"delegated_workforce_admin_bridge_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(admin_page, backup / "page.tsx")

api_dir.mkdir(parents=True, exist_ok=True)

api_file.write_text(r'''
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  "";

export async function POST(req: NextRequest) {
  const body = await req.json();

  if (!ADMIN_TOKEN) {
    return NextResponse.json(
      { success: false, error: "admin_token_not_configured" },
      { status: 500 }
    );
  }

  const response = await fetch(`${BACKEND_URL}/delegated-workforce-execution`, {
    method: "POST",
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      "x-admin-token": ADMIN_TOKEN,
      "x-actor-role": "owner_admin",
      "x-tenant-id": "owner_admin",
      "x-csrf-token": "delegated-workforce-execution",
      origin: process.env.NEXT_PUBLIC_FRONTEND_URL || "https://app.trance-formation.com.au",
    },
    body: JSON.stringify({
      implementation_plan: body.implementation_plan || { action_packets: [] },
      owner_approved: body.owner_approved === true,
      client_owned_agents: body.client_owned_agents || [],
      package_tier: body.package_tier || "enterprise",
    }),
  });

  const data = await response.json().catch(() => ({
    success: false,
    error: "backend_response_not_json",
  }));

  return NextResponse.json(
    {
      success: response.ok && data?.success === true,
      backend_status: response.status,
      data,
    },
    { status: response.ok ? 200 : response.status }
  );
}

export async function GET() {
  return NextResponse.json({
    success: true,
    route: "delegated-workforce-execution",
    methods: ["POST"],
    status: "ready",
  });
}
'''.lstrip(), encoding="utf-8")

s = admin_page.read_text(encoding="utf-8")

s = s.replace(
    "const [completedImplementationRuns, setCompletedImplementationRuns] = useState<any[]>([]);",
    """const [completedImplementationRuns, setCompletedImplementationRuns] = useState<any[]>([]);
  const [delegatedWorkforceResults, setDelegatedWorkforceResults] = useState<any[]>([]);"""
)

anchor = '  const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Orchestration", "Recovery", "Billing"];'

fn = r'''
  async function runDelegatedWorkforcePlan() {
    if (!latestImplementationPlan?.action_packets?.length) {
      showToast("No implementation plan available for delegated workforce execution.");
      return;
    }

    try {
      showToast("Running delegated workforce execution...");

      const response = await fetch("/api/delegated-workforce-execution", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          implementation_plan: latestImplementationPlan,
          owner_approved: true,
          client_owned_agents: ADMIN_AGENT_OPTIONS.map(([id]) => id),
          package_tier: "enterprise",
        }),
      });

      const wrapper = await response.json();
      const result = wrapper?.data || wrapper;

      if (!result?.success) {
        showToast("Delegated workforce execution needs review.");
        return;
      }

      setDelegatedWorkforceResults((prev) => [result, ...prev].slice(0, 10));
      showToast(`Delegated workforce completed ${result.completed_count || 0} packet(s), blocked ${result.blocked_count || 0}.`);
    } catch {
      showToast("Delegated workforce execution failed before reaching backend.");
    }
  }

'''

if fn.strip() not in s:
    if anchor not in s:
      raise SystemExit("navItems anchor not found.")
    s = s.replace(anchor, fn + "\n" + anchor)

s = s.replace(
'''<p>{latestImplementationPlan.action_count || 0} action packet(s) created from approved outcome.</p>''',
'''<p>{latestImplementationPlan.action_count || 0} action packet(s) created from approved outcome.</p>
                                  <div className="packetActions" style={{ marginBottom: 12 }}>
                                    <button onClick={runDelegatedWorkforcePlan}>Run delegated workforce</button>
                                  </div>'''
)

s = s.replace(
'''["Completed packet runs", completedImplementationRuns.length],
                ["Manual review items", latestImplementationPlan?.approval_summary?.approval_required_count || 0],''',
'''["Completed packet runs", completedImplementationRuns.length],
                ["Delegated workforce runs", delegatedWorkforceResults.length],
                ["Manual review items", latestImplementationPlan?.approval_summary?.approval_required_count || 0],'''
)

s = s.replace(
'''{completedImplementationRuns.length ? (
                <div className="implementationPlanBox">
                  <strong>Completed Implementation Runs</strong>''',
'''{delegatedWorkforceResults.length ? (
                <div className="implementationPlanBox">
                  <strong>Delegated Workforce Results</strong>
                  <p>{delegatedWorkforceResults.length} delegated workforce execution(s) completed.</p>
                  {delegatedWorkforceResults.slice(0, 4).map((result: any) => (
                    <div key={result.execution_id} style={{ display: "grid", gap: 10 }}>
                      {(result.completed_results || []).slice(0, 8).map((run: any) => (
                        <div className="implementationPacket" key={run.packet_id + run.created_at_ms}>
                          <div>
                            <small>Specialist agent</small>
                            <b>{String(run.assigned_agent || "agent").replaceAll("_", " ")}</b>
                          </div>
                          <div>
                            <small>Completed deliverable</small>
                            <span>{run.completed_output || "Delegated execution completed."}</span>
                          </div>
                          <div>
                            <small>Status</small>
                            <em>{run.execution_status} · {run.deliverable_type}</em>
                          </div>
                          <div className="packetActions">
                            <button onClick={() => navigator.clipboard.writeText(run.completed_output || "")}>Copy</button>
                          </div>
                        </div>
                      ))}
                      {(result.blocked_results || []).slice(0, 6).map((run: any) => (
                        <div className="implementationPacket locked" key={run.packet_id + run.created_at_ms}>
                          <div>
                            <small>Recommended specialist agent</small>
                            <b>{String(run.assigned_agent || "agent").replaceAll("_", " ")}</b>
                          </div>
                          <div>
                            <small>Why recommended</small>
                            <span>This specialist agent could unlock additional implementation capacity for this outcome.</span>
                          </div>
                          <div>
                            <small>Package status</small>
                            <em>Upgrade required · task hidden</em>
                          </div>
                          <div className="packetActions">
                            <button onClick={() => showToast("Upgrade recommendation saved.")}>Recommend upgrade</button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              ) : null}

              {completedImplementationRuns.length ? (
                <div className="implementationPlanBox">
                  <strong>Completed Implementation Runs</strong>'''
)

admin_page.write_text(s, encoding="utf-8")

print("DELEGATED_WORKFORCE_EXECUTION_ADMIN_BRIDGE_WIRED")
print(f"Backup: {backup}")
print(f"Updated: {admin_page}")
print(f"Created/updated: {api_file}")