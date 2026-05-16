from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
TEST = ROOT / "test_step251_admin_deployment_controls_ui.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"admin_page_before_step251_{timestamp}.tsx"
backup.write_text(ADMIN_PAGE.read_text(encoding="utf-8"), encoding="utf-8")

text = ADMIN_PAGE.read_text(encoding="utf-8")

text = text.replace(
    '''  const [running, setRunning] = useState(false);''',
    '''  const [running, setRunning] = useState(false);
  const [deployCompany, setDeployCompany] = useState("Manual Deploy Client");
  const [deployEmail, setDeployEmail] = useState("manual-client@example.com");
  const [deployTenant, setDeployTenant] = useState("client_manual_admin");
  const [deploymentResult, setDeploymentResult] = useState<any>(null);'''
)

insert_function = '''
  async function callDeploymentControl(path: string, payload: any) {
    try {
      const response = await fetch(`http://127.0.0.1:8000${path}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-actor-role": "owner",
          "x-tenant-id": "owner",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      setDeploymentResult(data);
    } catch {
      setDeploymentResult({ success: false, message: "Deployment control action failed." });
    }
  }

'''

text = text.replace(
    '''  const runtimeStatus = useMemo(() => runtime?.runtime?.platform_status || "offline", [runtime]);''',
    insert_function + '''  const runtimeStatus = useMemo(() => runtime?.runtime?.platform_status || "offline", [runtime]);'''
)

panel = '''
              <Panel title="Deploy / Suspend / Cancel Client System">
                <p style={{ color: "#94a3b8", lineHeight: 1.7 }}>
                  Owner/admin controls to manually deploy a client system with unlimited credits, suspend access, cancel access, or reactivate a system.
                </p>

                <div style={{ display: "grid", gap: 12 }}>
                  <input
                    value={deployTenant}
                    onChange={(event) => setDeployTenant(event.target.value)}
                    placeholder="Tenant ID"
                    style={{
                      padding: 14,
                      borderRadius: 14,
                      background: "#020617",
                      color: "#fff",
                      border: "1px solid rgba(148,163,184,.22)",
                    }}
                  />

                  <input
                    value={deployCompany}
                    onChange={(event) => setDeployCompany(event.target.value)}
                    placeholder="Company name"
                    style={{
                      padding: 14,
                      borderRadius: 14,
                      background: "#020617",
                      color: "#fff",
                      border: "1px solid rgba(148,163,184,.22)",
                    }}
                  />

                  <input
                    value={deployEmail}
                    onChange={(event) => setDeployEmail(event.target.value)}
                    placeholder="Client email"
                    style={{
                      padding: 14,
                      borderRadius: 14,
                      background: "#020617",
                      color: "#fff",
                      border: "1px solid rgba(148,163,184,.22)",
                    }}
                  />

                  <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                    <button
                      onClick={() => callDeploymentControl("/admin/deployment-control/manual-deploy", {
                        tenant_id: deployTenant,
                        company_name: deployCompany,
                        contact_email: deployEmail,
                        package: "Manual Unlimited",
                        active_agents: selectedAdminAgents,
                        unlimited_credits: true,
                      })}
                      style={{
                        padding: "12px 16px",
                        borderRadius: 12,
                        border: "none",
                        background: "#22c55e",
                        color: "#052e16",
                        fontWeight: 900,
                        cursor: "pointer",
                      }}
                    >
                      Deploy With Unlimited Credits
                    </button>

                    <button
                      onClick={() => callDeploymentControl("/admin/deployment-control/suspend", {
                        tenant_id: deployTenant,
                        reason: "Suspended from admin portal.",
                      })}
                      style={{
                        padding: "12px 16px",
                        borderRadius: 12,
                        border: "none",
                        background: "#f97316",
                        color: "#fff7ed",
                        fontWeight: 900,
                        cursor: "pointer",
                      }}
                    >
                      Suspend System
                    </button>

                    <button
                      onClick={() => callDeploymentControl("/admin/deployment-control/reactivate", {
                        tenant_id: deployTenant,
                        reason: "Reactivated from admin portal.",
                      })}
                      style={{
                        padding: "12px 16px",
                        borderRadius: 12,
                        border: "none",
                        background: "#0ea5e9",
                        color: "#eff6ff",
                        fontWeight: 900,
                        cursor: "pointer",
                      }}
                    >
                      Reactivate System
                    </button>

                    <button
                      onClick={() => callDeploymentControl("/admin/deployment-control/cancel", {
                        tenant_id: deployTenant,
                        reason: "Cancelled from admin portal.",
                      })}
                      style={{
                        padding: "12px 16px",
                        borderRadius: 12,
                        border: "none",
                        background: "#ef4444",
                        color: "#fef2f2",
                        fontWeight: 900,
                        cursor: "pointer",
                      }}
                    >
                      Cancel System
                    </button>
                  </div>

                  {deploymentResult ? (
                    <div style={{
                      padding: 16,
                      borderRadius: 16,
                      background: deploymentResult.success ? "rgba(34,197,94,.12)" : "rgba(239,68,68,.12)",
                      border: deploymentResult.success ? "1px solid rgba(34,197,94,.24)" : "1px solid rgba(239,68,68,.24)",
                      color: deploymentResult.success ? "#bbf7d0" : "#fecaca",
                      lineHeight: 1.6,
                    }}>
                      <strong>{deploymentResult.success ? "Action completed" : "Action failed"}</strong>
                      <div>{deploymentResult.status || deploymentResult.message || deploymentResult.error || "Result received."}</div>
                      {deploymentResult.tenant?.activation_link ? (
                        <div>Activation link: {deploymentResult.tenant.activation_link}</div>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              </Panel>

'''

anchor = '''              <Panel title="Runtime Health">'''
text = text.replace(anchor, panel + anchor)

ADMIN_PAGE.write_text(text, encoding="utf-8")

TEST.write_text(r'''
from pathlib import Path
import subprocess

ROOT = Path.cwd()
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
text = admin_page.read_text(encoding="utf-8", errors="ignore").lower()

checks = {
    "admin_page_exists": admin_page.exists(),
    "deployment_panel_present": "deploy / suspend / cancel client system" in text,
    "manual_deploy_route_present": "/admin/deployment-control/manual-deploy" in text,
    "suspend_route_present": "/admin/deployment-control/suspend" in text,
    "cancel_route_present": "/admin/deployment-control/cancel" in text,
    "reactivate_route_present": "/admin/deployment-control/reactivate" in text,
    "unlimited_credits_present": "unlimited_credits: true" in text,
    "activation_link_present": "activation_link" in text,
}

print("STEP_251_ADMIN_DEPLOYMENT_CONTROLS_UI_RESULTS")
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

print("STEP_251_ADMIN_DEPLOYMENT_CONTROLS_UI_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_251_ADMIN_DEPLOYMENT_CONTROLS_UI_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Created/updated: {TEST}")
print("STEP_251_OK")