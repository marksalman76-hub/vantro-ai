from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
api_dir = ROOT / "frontend" / "src" / "app" / "api" / "outcome-action-plan"
api_file = api_dir / "route.ts"

backup = ROOT / "backups" / f"outcome_action_plan_frontend_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(admin_page, backup / "admin_page.tsx")

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

  const response = await fetch(`${BACKEND_URL}/admin/outcome-action-plan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-admin-token": ADMIN_TOKEN,
      "x-actor-role": "owner_admin",
      "x-tenant-id": "owner_admin",
      "x-csrf-token": "outcome-action-plan",
      origin: process.env.NEXT_PUBLIC_FRONTEND_URL || "https://trance-formation.com.au",
    },
    body: JSON.stringify({
      outcome_text: body.outcome_text || "",
      source_agent: body.source_agent || "unknown_agent",
      tenant_id: body.tenant_id || "owner_admin",
      project_id: body.project_id || "frontend_outcome_action_plan",
      owner_approved: body.owner_approved === true,
    }),
    cache: "no-store",
  });

  const data = await response.json();

  return NextResponse.json({
    success: response.ok && data?.success === true,
    backend_status: response.status,
    data,
  });
}
'''.lstrip(), encoding="utf-8")

s = admin_page.read_text(encoding="utf-8")

insert_after = '''  function cancelClient() {
    setCancelOpen(false);
    callDeploymentControl(
      "/admin/deployment-control/cancel",
      {
        account_reference: deployTenant,
        reason: "Cancelled from admin portal.",
      },
      "Cancel"
    );
  }
'''

add_function = '''
  async function createOutcomeActionPlan(item: any, decision: "approved" | "amendment_requested" | "rejected") {
    const outcomeText =
      item?.output ||
      item?.generated_output ||
      item?.response ||
      item?.provider_output ||
      item?.message ||
      "";

    if (!outcomeText.trim()) {
      showToast("No outcome text available to convert into an action plan.");
      return;
    }

    if (decision === "rejected") {
      showToast("Outcome rejected. No implementation action plan created.");
      return;
    }

    if (decision === "amendment_requested") {
      showToast("Amendment requested. Add revision notes to the task and rerun before implementation.");
      return;
    }

    try {
      const response = await fetch("/api/outcome-action-plan", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          outcome_text: outcomeText,
          source_agent: item?.agent_id || "unknown_agent",
          owner_approved: true,
          tenant_id: "owner_admin",
          project_id: "admin_visible_outcome_approval",
        }),
      });

      const wrapper = await response.json();
      const plan = wrapper?.data || wrapper;

      const packetCount = plan?.action_count || 0;
      const approvalCount = plan?.approval_summary?.approval_required_count || 0;
      const safeCount = plan?.approval_summary?.safe_auto_ready_count || 0;

      showToast(`Approved. Implementation plan created: ${packetCount} action packets, ${approvalCount} approval-gated, ${safeCount} safe-ready.`);
    } catch {
      showToast("Approval saved, but implementation action plan creation failed.");
    }
  }

'''

if add_function.strip() not in s:
    if insert_after not in s:
        raise SystemExit("Function insertion anchor not found.")
    s = s.replace(insert_after, insert_after + add_function)

s = s.replace(
'''                                <button onClick={() => showToast("Outcome approved by admin.")}>Approve</button>
                                <button onClick={() => showToast("Amendment requested. Add revision notes in the task box and rerun.")}>Request amendment</button>
                                <button onClick={() => showToast("Outcome rejected by admin.")}>Reject</button>''',
'''                                <button onClick={() => createOutcomeActionPlan(item, "approved")}>Approve + create action plan</button>
                                <button onClick={() => createOutcomeActionPlan(item, "amendment_requested")}>Request amendment</button>
                                <button onClick={() => createOutcomeActionPlan(item, "rejected")}>Reject</button>'''
)

admin_page.write_text(s, encoding="utf-8")

print("OUTCOME_ACTION_PLAN_FRONTEND_WIRED")
print(f"Backup: {backup}")
print(f"Updated: {admin_page}")
print(f"Created/updated: {api_file}")