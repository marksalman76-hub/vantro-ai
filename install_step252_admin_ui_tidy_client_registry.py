from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
TEST = ROOT / "test_step252_admin_ui_tidy_client_registry.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"admin_page_before_step252_{timestamp}.tsx"
backup.write_text(ADMIN_PAGE.read_text(encoding="utf-8"), encoding="utf-8")

text = ADMIN_PAGE.read_text(encoding="utf-8")

text = text.replace(
    '''  const [deploymentResult, setDeploymentResult] = useState<any>(null);''',
    '''  const [deploymentResult, setDeploymentResult] = useState<any>(null);
  const [clientRegistry, setClientRegistry] = useState<any[]>([]);
  const [clientRegistrySummary, setClientRegistrySummary] = useState<any>(null);'''
)

text = text.replace(
    '''      setRuntime(data);''',
    '''      setRuntime(data);
      await loadClientRegistry();'''
)

insert_function = '''
  async function loadClientRegistry() {
    try {
      const response = await fetch("http://127.0.0.1:8000/admin/deployment-control/list?limit=25", {
        headers: {
          "x-actor-role": "owner",
          "x-tenant-id": "owner",
        },
        cache: "no-store",
      });

      const data = await response.json();
      setClientRegistry(data.tenants || []);
    } catch {
      setClientRegistry([]);
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/admin/deployment-control/summary", {
        headers: {
          "x-actor-role": "owner",
          "x-tenant-id": "owner",
        },
        cache: "no-store",
      });

      const data = await response.json();
      setClientRegistrySummary(data);
    } catch {
      setClientRegistrySummary(null);
    }
  }

'''

text = text.replace(
    '''  async function callDeploymentControl(path: string, payload: any) {''',
    insert_function + '''  async function callDeploymentControl(path: string, payload: any) {'''
)

text = text.replace(
    '''      const data = await response.json();
      setDeploymentResult(data);''',
    '''      const data = await response.json();
      setDeploymentResult(data);
      await loadClientRegistry();'''
)

# Replace long Run Agent panel header/copy with compact styling and shorter list area
text = text.replace(
    '''<p style={{ color: "#94a3b8", lineHeight: 1.7 }}>
                  Owner/admin can run one agent or multiple agents for internal operations, demos, and testing. Client credit limits do not apply here, but governance and approval controls remain active.
                </p>''',
    '''<p style={{ color: "#94a3b8", lineHeight: 1.7 }}>
                  Select one or more agents, enter a task, and run an owner/admin execution.
                </p>'''
)

text = text.replace(
    '''display: "grid",
                  gap: 10,
                  border: "1px solid rgba(148,163,184,.22)",
                  borderRadius: 16,
                  padding: 12,
                  background: "#020617",''',
    '''display: "grid",
                  gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))",
                  gap: 8,
                  maxHeight: 260,
                  overflow: "auto",
                  border: "1px solid rgba(148,163,184,.22)",
                  borderRadius: 16,
                  padding: 12,
                  background: "#020617",'''
)

client_registry_panel = '''
              <Panel title="Client Registry">
                <p style={{ color: "#94a3b8", lineHeight: 1.7 }}>
                  Track active, suspended, cancelled, and previously deployed client systems.
                </p>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(160px,1fr))", gap: 12 }}>
                  <Card title="Total Clients" value={clientRegistrySummary?.tenant_count || clientRegistry.length || 0} />
                  <Card title="Active" value={clientRegistrySummary?.active_count || 0} />
                  <Card title="Suspended" value={clientRegistrySummary?.suspended_count || 0} />
                  <Card title="Cancelled" value={clientRegistrySummary?.cancelled_count || 0} />
                </div>

                <div style={{
                  marginTop: 16,
                  display: "grid",
                  gap: 10,
                  maxHeight: 360,
                  overflow: "auto",
                }}>
                  {clientRegistry.length === 0 ? (
                    <div style={{ color: "#94a3b8" }}>No deployed clients found yet.</div>
                  ) : clientRegistry.map((client) => (
                    <div
                      key={client.tenant_id}
                      style={{
                        padding: 14,
                        borderRadius: 16,
                        background: "#020617",
                        border: "1px solid rgba(148,163,184,.16)",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                        <strong>{client.company_name || "Client"}</strong>
                        <span style={{
                          padding: "6px 10px",
                          borderRadius: 999,
                          background:
                            client.access_status === "active"
                              ? "rgba(34,197,94,.14)"
                              : client.access_status === "suspended"
                                ? "rgba(249,115,22,.14)"
                                : "rgba(239,68,68,.14)",
                          color:
                            client.access_status === "active"
                              ? "#bbf7d0"
                              : client.access_status === "suspended"
                                ? "#fed7aa"
                                : "#fecaca",
                          fontSize: 12,
                          fontWeight: 800,
                        }}>
                          {client.access_status || client.status || "unknown"}
                        </span>
                      </div>

                      <div style={{ color: "#94a3b8", fontSize: 13, marginTop: 8 }}>
                        {client.contact_email || "No email"} · {client.package || "No package"} · Agents: {(client.active_agents || []).length}
                      </div>

                      <div style={{ color: "#94a3b8", fontSize: 12, marginTop: 6 }}>
                        Credits: {client.unlimited_credits ? "Unlimited" : client.credit_state?.credits_remaining || "Limited"}
                      </div>
                    </div>
                  ))}
                </div>
              </Panel>

'''

anchor = '''              <Panel title="Billing & Deployment">'''
text = text.replace(anchor, client_registry_panel + anchor)

ADMIN_PAGE.write_text(text, encoding="utf-8")

TEST.write_text(r'''
from pathlib import Path
import subprocess

ROOT = Path.cwd()
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
text = admin_page.read_text(encoding="utf-8", errors="ignore").lower()

checks = {
    "admin_page_exists": admin_page.exists(),
    "client_registry_panel_present": "client registry" in text,
    "client_registry_state_present": "clientregistry" in text,
    "client_registry_summary_present": "clientregistrysummary" in text,
    "deployment_list_route_present": "/admin/deployment-control/list" in text,
    "deployment_summary_route_present": "/admin/deployment-control/summary" in text,
    "compact_run_agent_copy_present": "select one or more agents" in text,
    "run_agent_list_max_height_present": "maxheight: 260" in text,
    "client_status_tracking_present": "suspended" in text and "cancelled" in text and "active" in text,
}

print("STEP_252_ADMIN_UI_TIDY_CLIENT_REGISTRY_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

print("RUNNING_FRONTEND_BUILD")
build = subprocess.run(["npm.cmd", "run", "build"], cwd=str(ROOT / "frontend"), text=True)
print("frontend_build_exit_code", build.returncode)

if build.returncode != 0:
    failed.append("frontend_build")

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_252_ADMIN_UI_TIDY_CLIENT_REGISTRY_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_252_ADMIN_UI_TIDY_CLIENT_REGISTRY_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Created/updated: {TEST}")
print("STEP_252_OK")