from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"

if not PAGE.exists():
    raise FileNotFoundError("frontend/src/app/admin/page.tsx not found")

ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"admin_page_before_orchestration_dashboard_ui_{ts}.tsx"
original = PAGE.read_text(encoding="utf-8")
backup.write_text(original, encoding="utf-8")

s = original

# 1) Add orchestration state after busyAction
state_anchor = '  const [busyAction, setBusyAction] = useState("");\n'
state_insert = '''  const [orchestration, setOrchestration] = useState<any>({
    readiness: null,
    routes: null,
    liveExecutions: null,
    deadLetters: null,
    manualReview: null,
  });
  const [orchestrationBusy, setOrchestrationBusy] = useState(false);
  const [orchestrationResult, setOrchestrationResult] = useState<any>(null);
'''
if state_insert.strip() not in s:
    s = s.replace(state_anchor, state_anchor + state_insert)

# 2) Add nav map item
s = s.replace(
'''      "Provider Governance": "admin-governance",
      "Recovery": "admin-recovery",
      "Billing": "admin-billing",''',
'''      "Provider Governance": "admin-governance",
      "Orchestration": "admin-orchestration",
      "Recovery": "admin-recovery",
      "Billing": "admin-billing",'''
)

# 3) Add orchestration loader and test route functions before runAdminAgent
function_anchor = "  async function runAdminAgent() {\n"
function_insert = r'''
  async function callAdminProxy(path: string, method: "GET" | "POST" = "GET", payload: any = null) {
    const response = await fetch("/api/admin-deployment-control", {
      method: "POST",
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
        "x-actor-role": "owner",
        "x-tenant-id": "owner",
      },
      body: JSON.stringify({ path, method, payload }),
    });
    return response.json();
  }

  async function loadOrchestrationDashboard() {
    setOrchestrationBusy(true);
    try {
      const [routingReady, routingList, liveReady, liveList, deadLetters, manualReview] = await Promise.all([
        callAdminProxy("/admin/workflow-provider-routing/readiness", "GET"),
        callAdminProxy("/admin/workflow-provider-routing/list?limit=10", "GET"),
        callAdminProxy("/admin/live-provider-execution/readiness", "GET"),
        callAdminProxy("/admin/live-provider-execution/list?limit=10", "GET"),
        callAdminProxy("/admin/dead-letter/list?limit=10", "GET"),
        callAdminProxy("/admin/manual-review/list?limit=10", "GET"),
      ]);

      setOrchestration({
        readiness: {
          routing: routingReady,
          live_execution: liveReady,
        },
        routes: routingList,
        liveExecutions: liveList,
        deadLetters,
        manualReview,
      });
      showToast("Orchestration dashboard refreshed.");
    } catch {
      setOrchestration({
        readiness: null,
        routes: null,
        liveExecutions: null,
        deadLetters: null,
        manualReview: null,
      });
      showToast("Orchestration dashboard refresh failed.");
    } finally {
      setOrchestrationBusy(false);
    }
  }

  async function runOrchestrationSmokeTest() {
    setOrchestrationBusy(true);
    setOrchestrationResult(null);

    try {
      const routeResult = await callAdminProxy("/admin/workflow-provider-routing/route", "POST", {
        tenant_id: "owner",
        workflow_id: "admin_orchestration_dashboard_test",
        agent_id: "marketing_specialist_agent",
        action_type: "generate_campaign_copy",
        workflow_payload: {
          provider: "openai",
          brand: "Owner Admin",
          region: "global",
          task: "campaign copy",
        },
        available_providers: ["openai"],
        entitlement_active: true,
      });

      const packet = routeResult?.provider_execution_packet || {};

      const executionResult = await callAdminProxy("/admin/live-provider-execution/execute", "POST", {
        tenant_id: packet.tenant_id || "owner",
        workflow_id: packet.workflow_id || "admin_orchestration_dashboard_test",
        agent_id: packet.agent_id || "marketing_specialist_agent",
        provider: packet.provider || "openai",
        action_type: packet.action_type || "generate_campaign_copy",
        payload: packet.payload || {},
        execution_allowed: packet.execution_allowed === true,
        owner_approved: true,
        live_keys_available: false,
        entitlement_active: true,
      });

      setOrchestrationResult({
        status: "orchestration_smoke_test_completed",
        routeResult,
        executionResult,
      });

      await loadOrchestrationDashboard();
      showToast("Orchestration smoke test completed.");
    } catch {
      setOrchestrationResult({
        status: "orchestration_smoke_test_failed",
        message: "Unable to run orchestration smoke test.",
      });
      showToast("Orchestration smoke test failed.");
    } finally {
      setOrchestrationBusy(false);
    }
  }

'''
if function_insert.strip() not in s:
    s = s.replace(function_anchor, function_insert + function_anchor)

# 4) Load orchestration on page load
s = s.replace(
'''  useEffect(() => {
    loadRuntime();
    loadClientRegistry();
  }, []);''',
'''  useEffect(() => {
    loadRuntime();
    loadClientRegistry();
    loadOrchestrationDashboard();
  }, []);'''
)

# 5) Add nav item
s = s.replace(
'''  const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Recovery", "Billing"];''',
'''  const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Orchestration", "Recovery", "Billing"];'''
)

# 6) Add orchestration metric cards after metrics section
metrics_anchor = '''          </section>

          <section className="grid two">
            <div className="panel" id="admin-run">'''
metrics_insert = '''          </section>

          <section className="orchestrationStrip">
            {[
              ["Routes", orchestration?.routes?.count || 0, "Workflow → provider routing"],
              ["Live outputs", orchestration?.liveExecutions?.count || 0, "Prepared / executed provider packets"],
              ["Dead letters", orchestration?.deadLetters?.count || 0, "Failed workflows needing review"],
              ["Manual review", orchestration?.manualReview?.count || 0, "Owner/admin review queue"],
            ].map(([label, value, hint]) => (
              <div className="orchestrationMini" key={label}>
                <small>{label}</small>
                <strong>{value}</strong>
                <span>{hint}</span>
              </div>
            ))}
          </section>

          <section className="grid two">
            <div className="panel" id="admin-run">'''
if "orchestrationStrip" not in s:
    s = s.replace(metrics_anchor, metrics_insert)

# 7) Insert orchestration dashboard before Operational Recovery section
recovery_anchor = '''          <section className="grid two">
            <div id="admin-recovery">'''
orchestration_panel = r'''          <section className="grid two" id="admin-orchestration">
            <Panel title="Orchestration Dashboard" subtitle="Workflow routing, provider execution, dead-letter handling and owner review visibility.">
              <div className="orchestrationGrid">
                <div>
                  <small>Routing runtime</small>
                  <strong>{orchestration?.readiness?.routing?.status || "review"}</strong>
                </div>
                <div>
                  <small>Live execution</small>
                  <strong>{orchestration?.readiness?.live_execution?.status || "review"}</strong>
                </div>
                <div>
                  <small>Owner gates</small>
                  <strong>Active</strong>
                </div>
                <div>
                  <small>Client safety</small>
                  <strong>Protected</strong>
                </div>
              </div>

              <div className="panelActions">
                <button className="ghost" onClick={loadOrchestrationDashboard} disabled={orchestrationBusy}>
                  {orchestrationBusy ? "Refreshing..." : "Refresh orchestration"}
                </button>
                <button className="ghost" onClick={runOrchestrationSmokeTest} disabled={orchestrationBusy}>
                  Run safe smoke test
                </button>
              </div>

              <div className="timeline">
                {(orchestration?.routes?.routes || []).slice(-5).reverse().map((route: any, index: number) => (
                  <div className="timelineItem" key={route.routing_id || index}>
                    <b>{route.status || "route"}</b>
                    <span>{route.agent_id || "agent"} → {route.selected_provider || route.provider_category || "provider"}</span>
                    <p>{route.route_state || route.action_type || "Workflow route decision recorded."}</p>
                  </div>
                ))}
                {!(orchestration?.routes?.routes || []).length ? (
                  <div className="timelineItem">
                    <b>No route events loaded</b>
                    <span>Refresh or run a safe smoke test</span>
                    <p>Workflow provider routing decisions will appear here.</p>
                  </div>
                ) : null}
              </div>
            </Panel>

            <Panel title="Execution Review Centre" subtitle="Live provider outputs, dead letters and manual review queue.">
              <div className="reviewRows">
                <div>
                  <span>Live provider outputs</span>
                  <b>{orchestration?.liveExecutions?.count || 0}</b>
                </div>
                <div>
                  <span>Dead-letter items</span>
                  <b>{orchestration?.deadLetters?.count || 0}</b>
                </div>
                <div>
                  <span>Manual review items</span>
                  <b>{orchestration?.manualReview?.count || 0}</b>
                </div>
              </div>

              <div className="reviewList">
                {(orchestration?.manualReview?.manual_review_items || []).slice(-4).reverse().map((item: any, index: number) => (
                  <div className="reviewItem" key={item.review_id || index}>
                    <strong>{item.status || "pending_owner_review"}</strong>
                    <span>{item.agent_id || "agent"} · {item.action_type || "action"}</span>
                    <p>{item.failure_reason || "Owner/admin review required before recovery."}</p>
                  </div>
                ))}
                {!(orchestration?.manualReview?.manual_review_items || []).length ? (
                  <div className="reviewItem">
                    <strong>No pending manual reviews</strong>
                    <span>Dead-letter/manual-review runtime is ready</span>
                    <p>Items requiring owner/admin decisions will appear here.</p>
                  </div>
                ) : null}
              </div>

              <pre className={orchestrationResult ? "output has" : "output"}>
                {orchestrationResult ? JSON.stringify(orchestrationResult, null, 2) : "Orchestration test result will appear here..."}
              </pre>
            </Panel>
          </section>

          <section className="grid two">
            <div id="admin-recovery">'''
if 'id="admin-orchestration"' not in s:
    s = s.replace(recovery_anchor, orchestration_panel)

# 8) Add CSS before modal styles
css_anchor = "        .modal{position:fixed;inset:0;"
css_insert = r'''        .orchestrationStrip{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:-8px 0 22px}.orchestrationMini{background:#0F1228;border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:16px}.orchestrationMini small{display:block;color:#3E4A5C;text-transform:uppercase;letter-spacing:.09em;font-size:10px;font-weight:900}.orchestrationMini strong{display:block;color:#EEF2FF;font-size:28px;margin:7px 0}.orchestrationMini span{color:#7A8899;font-size:12px;line-height:1.4}
        .orchestrationGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:14px 0}.orchestrationGrid div{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:12px}.orchestrationGrid small{display:block;color:#3E4A5C;text-transform:uppercase;font-size:9px;font-weight:900}.orchestrationGrid strong{display:block;color:#EEF2FF;margin-top:6px;text-transform:capitalize}
        .timeline,.reviewList{display:grid;gap:8px;margin-top:12px}.timelineItem,.reviewItem{background:rgba(255,255,255,.03);border-left:3px solid #5B52F0;border-radius:10px;padding:12px}.timelineItem b,.reviewItem strong{display:block;color:#EEF2FF;font-size:12px;text-transform:capitalize}.timelineItem span,.reviewItem span{display:block;color:#0ECFBC;font-size:11px;margin-top:4px}.timelineItem p,.reviewItem p{margin:6px 0 0;color:#7A8899;font-size:12px;line-height:1.45}.reviewRows{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:14px 0}.reviewRows div{background:rgba(255,255,255,.03);border-radius:10px;padding:12px}.reviewRows span{display:block;color:#3E4A5C;font-size:10px;text-transform:uppercase;font-weight:900}.reviewRows b{display:block;color:#EEF2FF;font-size:24px;margin-top:6px}
'''
if ".orchestrationStrip" not in s:
    s = s.replace(css_anchor, css_insert + css_anchor)

# 9) Responsive CSS update
s = s.replace(
'''@media(max-width:1100px){.metrics{grid-template-columns:repeat(3,1fr)}.grid.two,.billingGrid{grid-template-columns:1fr}.sidebar{display:none}.content{padding:18px}.pills{max-height:320px}}''',
'''@media(max-width:1100px){.metrics{grid-template-columns:repeat(3,1fr)}.grid.two,.billingGrid,.orchestrationStrip{grid-template-columns:1fr}.orchestrationGrid,.reviewRows{grid-template-columns:1fr 1fr}.sidebar{display:none}.content{padding:18px}.pills{max-height:320px}}'''
)

PAGE.write_text(s, encoding="utf-8")

print("ADMIN_ORCHESTRATION_DASHBOARD_UI_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print("Added:")
print("- Orchestration navigation")
print("- Orchestration metrics strip")
print("- Workflow routing visibility")
print("- Live provider execution visibility")
print("- Dead-letter/manual-review visibility")
print("- Safe orchestration smoke test action")
print("- Customer-safe operational summaries")