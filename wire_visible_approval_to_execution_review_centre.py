from pathlib import Path
from datetime import datetime
import shutil

p = Path("frontend/src/app/admin/page.tsx")
backup = Path("backups") / f"visible_approval_execution_review_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "page.tsx")

s = p.read_text(encoding="utf-8")

s = s.replace(
    "const [runResult, setRunResult] = useState<any>(null);",
    """const [runResult, setRunResult] = useState<any>(null);
  const [implementationPlans, setImplementationPlans] = useState<any[]>([]);
  const [latestImplementationPlan, setLatestImplementationPlan] = useState<any>(null);"""
)

anchor = '  const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Orchestration", "Recovery", "Billing"];'

fn = r'''
  async function approveOutcomeAndCreatePlan(item: any) {
    const outcomeText =
      item?.output ||
      item?.generated_output ||
      item?.response ||
      item?.provider_output ||
      item?.message ||
      "";

    if (!outcomeText.trim()) {
      showToast("No outcome available to convert into an implementation plan.");
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
          tenant_id: "owner_admin",
          project_id: "admin_outcome_approval",
          owner_approved: true,
        }),
      });

      const wrapper = await response.json();
      const plan = wrapper?.data || wrapper;

      if (!plan?.success) {
        showToast("Approval saved, but implementation plan creation failed.");
        return;
      }

      setLatestImplementationPlan(plan);
      setImplementationPlans((prev) => [plan, ...prev].slice(0, 20));
      showToast(`Approved. ${plan.action_count || 0} implementation action packet(s) created.`);
    } catch {
      showToast("Approval failed before creating implementation action plan.");
    }
  }

'''

if fn.strip() not in s:
    if anchor not in s:
        raise SystemExit("navItems anchor not found.")
    s = s.replace(anchor, fn + "\n" + anchor)

s = s.replace(
    '<button onClick={() => showToast("Outcome approved by admin.")}>Approve</button>',
    '<button onClick={() => approveOutcomeAndCreatePlan(item)}>Approve + create plan</button>'
)

s = s.replace(
    '<button onClick={() => createOutcomeActionPlan(item, "approved")}>Approve + create action plan</button>',
    '<button onClick={() => approveOutcomeAndCreatePlan(item)}>Approve + create plan</button>'
)

s = s.replace(
'''                              <div className="executionTimeline">
                                <span>Generated</span>
                                <span>Review ready</span>
                                <span>{item?.success ? "Awaiting approval" : "Needs amendment"}</span>
                              </div>''',
'''                              <div className="executionTimeline">
                                <span>Generated</span>
                                <span>Review ready</span>
                                <span>{latestImplementationPlan ? "Implementation planned" : item?.success ? "Awaiting approval" : "Needs amendment"}</span>
                              </div>

                              {latestImplementationPlan ? (
                                <div className="implementationPlanBox">
                                  <strong>Implementation Action Plan</strong>
                                  <p>{latestImplementationPlan.action_count || 0} action packet(s) created from approved outcome.</p>
                                  {(latestImplementationPlan.action_packets || []).slice(0, 6).map((packet: any) => (
                                    <div className="implementationPacket" key={packet.packet_id}>
                                      <b>{String(packet.recommended_agent || "agent").replaceAll("_", " ")}</b>
                                      <span>{packet.title}</span>
                                      <em>{packet.execution_status}</em>
                                    </div>
                                  ))}
                                </div>
                              ) : null}'''
)

if ".implementationPlanBox" not in s:
    s = s.replace(
'''        .executionTimeline span {''',
'''        .implementationPlanBox {
          margin-top: 14px;
          padding: 14px;
          border-radius: 18px;
          background: rgba(20, 184, 166, .09);
          border: 1px solid rgba(20, 184, 166, .32);
        }
        .implementationPlanBox strong {
          display: block;
          color: #5eead4;
          text-transform: uppercase;
          letter-spacing: .08em;
          font-size: 12px;
          margin-bottom: 8px;
        }
        .implementationPlanBox p {
          margin: 0 0 10px;
          color: #cbd5e1;
        }
        .implementationPacket {
          display: grid;
          grid-template-columns: 170px 1fr 170px;
          gap: 10px;
          align-items: start;
          padding: 10px;
          margin-top: 8px;
          border-radius: 14px;
          background: rgba(2, 6, 23, .56);
          border: 1px solid rgba(148, 163, 184, .18);
        }
        .implementationPacket b {
          color: #bfdbfe;
          font-size: 12px;
        }
        .implementationPacket span {
          color: #e5e7eb;
          font-size: 13px;
          line-height: 1.35;
        }
        .implementationPacket em {
          color: #facc15;
          font-style: normal;
          font-size: 12px;
          font-weight: 800;
        }
        .executionTimeline span {'''
    )

# Patch execution review centre counts if those labels exist.
s = s.replace(
'''["Live provider outputs", 0],
                ["Dead-letter items", 0],
                ["Manual review items", 0],''',
'''["Live provider outputs", implementationPlans.length],
                ["Implementation packets", latestImplementationPlan?.action_count || 0],
                ["Manual review items", latestImplementationPlan?.approval_summary?.approval_required_count || 0],'''
)

s = s.replace(
'''No Pending Manual Reviews''',
'''{implementationPlans.length ? "Implementation Plan Ready" : "No Pending Manual Reviews"}'''
)

s = s.replace(
'''Dead-letter/manual-review runtime is ready''',
'''{implementationPlans.length ? `${latestImplementationPlan?.action_count || 0} action packets created from approved outcome.` : "Dead-letter/manual-review runtime is ready"}'''
)

s = s.replace(
'''Items requiring owner/admin decisions will appear here.''',
'''{implementationPlans.length ? "Review generated action packets and continue to implementation queue." : "Items requiring owner/admin decisions will appear here."}'''
)

p.write_text(s, encoding="utf-8")

print("VISIBLE_APPROVAL_TO_EXECUTION_REVIEW_CENTRE_WIRED")
print(f"Backup: {backup}")
print(f"Updated: {p}")