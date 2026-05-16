from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
TEST = ROOT / "test_step248d_admin_run_agent_panel.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"admin_page_before_step248d_{timestamp}.tsx"
backup.write_text(ADMIN_PAGE.read_text(encoding="utf-8"), encoding="utf-8")

text = ADMIN_PAGE.read_text(encoding="utf-8")

text = text.replace(
    'const [loading, setLoading] = useState(true);',
    '''const [loading, setLoading] = useState(true);
  const [agent, setAgent] = useState("product_copywriting_agent");
  const [task, setTask] = useState("Create a premium Shopify product page for a high-converting ecommerce product.");
  const [runResult, setRunResult] = useState<any>(null);
  const [running, setRunning] = useState(false);'''
)

insert_function = '''
  async function runAdminAgent() {
    setRunning(true);
    setRunResult(null);

    try {
      const response = await fetch("/api/run-agent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-actor-role": "owner",
          "x-tenant-id": "owner",
        },
        body: JSON.stringify({
          tenant_id: "owner_admin",
          requested_agent: agent,
          workflow_stage: "admin_internal_execution",
          action_type: "product_copy_generation",
          actor_role: "owner",
          owner_approved: true,
          task,
        }),
      });

      const data = await response.json();
      setRunResult(data);
    } catch {
      setRunResult({ success: false, message: "Admin execution failed." });
    } finally {
      setRunning(false);
    }
  }

'''

text = text.replace(
    '  const provider = runtime?.provider_governance || {};',
    insert_function + '  const provider = runtime?.provider_governance || {};'
)

panel = '''
            <Panel title="Run Agent">
              <p style={{ color: "#94a3b8", lineHeight: 1.7 }}>
                Owner/admin execution area for internal testing, demos, and operations. Client credit limits do not apply here, but governance and approval controls remain active.
              </p>

              <div style={{ display: "grid", gap: 14 }}>
                <select
                  value={agent}
                  onChange={(event) => setAgent(event.target.value)}
                  style={{
                    width: "100%",
                    padding: 14,
                    borderRadius: 14,
                    background: "#020617",
                    color: "#fff",
                    border: "1px solid rgba(148,163,184,.22)",
                  }}
                >
                  <option value="product_copywriting_agent">Product Copywriting Agent</option>
                  <option value="ugc_creative_agent">UGC Creative Agent</option>
                  <option value="analytics_optimisation_agent">Analytics Optimisation Agent</option>
                  <option value="influencer_collaboration_agent">Influencer Collaboration Agent</option>
                  <option value="product_image_direction_agent">Product Image Direction Agent</option>
                </select>

                <textarea
                  value={task}
                  onChange={(event) => setTask(event.target.value)}
                  rows={6}
                  style={{
                    width: "100%",
                    padding: 14,
                    borderRadius: 14,
                    background: "#020617",
                    color: "#fff",
                    border: "1px solid rgba(148,163,184,.22)",
                    resize: "vertical",
                  }}
                />

                <button
                  onClick={runAdminAgent}
                  disabled={running}
                  style={{
                    padding: "14px 18px",
                    borderRadius: 14,
                    border: "none",
                    background: "linear-gradient(135deg,#2563eb 0%,#06b6d4 100%)",
                    color: "#fff",
                    fontWeight: 800,
                    cursor: "pointer",
                  }}
                >
                  {running ? "Running..." : "Run Agent"}
                </button>

                {runResult ? (
                  <div style={{
                    padding: 16,
                    borderRadius: 16,
                    background: runResult.success ? "rgba(34,197,94,.12)" : "rgba(239,68,68,.12)",
                    border: runResult.success ? "1px solid rgba(34,197,94,.24)" : "1px solid rgba(239,68,68,.24)",
                    color: runResult.success ? "#bbf7d0" : "#fecaca",
                    lineHeight: 1.6,
                  }}>
                    <strong>{runResult.success ? "Execution prepared" : "Execution blocked"}</strong>
                    <div>{runResult.status || runResult.message || "Result received."}</div>
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
    "run_agent_panel_present": "run agent" in text,
    "run_admin_agent_function_present": "runadminagent" in text,
    "owner_actor_role_present": '"x-actor-role": "owner"' in text,
    "owner_approved_present": "owner_approved: true" in text,
    "client_credit_bypass_copy_present": "client credit limits do not apply here" in text,
    "no_json_block_component": "jsonblock" not in text,
}

print("STEP_248D_ADMIN_RUN_AGENT_PANEL_RESULTS")
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

print("STEP_248D_ADMIN_RUN_AGENT_PANEL_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_248D_ADMIN_RUN_AGENT_PANEL_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Created/updated: {TEST}")
print("STEP_248D_OK")