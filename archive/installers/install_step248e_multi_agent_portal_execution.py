from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
TEST = ROOT / "test_step248e_multi_agent_portal_execution.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for file in [CLIENT_PAGE, ADMIN_PAGE, TEST]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step248e_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

client = CLIENT_PAGE.read_text(encoding="utf-8")
admin = ADMIN_PAGE.read_text(encoding="utf-8")

# ---------------- CLIENT PORTAL ----------------
client = client.replace(
    'const [selectedAgent, setSelectedAgent] = useState("");',
    'const [selectedAgent, setSelectedAgent] = useState("");\n  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);'
)

client = client.replace(
    '''          if (data.account.active_agents?.length > 0) {
            setSelectedAgent(data.account.active_agents[0]);
          }''',
    '''          if (data.account.active_agents?.length > 0) {
            setSelectedAgent(data.account.active_agents[0]);
            setSelectedAgents([data.account.active_agents[0]]);
          }'''
)

client = client.replace(
    '''  async function runAgent() {
    if (!selectedAgent || !task.trim()) {
      setError("Select an agent and enter a task.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`/api/run-agent`, {
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

      const data = await response.json();

      setResult(data);

      if (!response.ok || data?.success === false) {
        setError(
          data?.message ||
            data?.reason ||
            "Execution blocked or failed."
        );
      }
    } catch {
      setError("Execution failed.");
    } finally {
      setLoading(false);
    }
  }''',
    '''  function toggleClientAgent(agentId: string) {
    setSelectedAgents((current) => {
      if (current.includes(agentId)) {
        const next = current.filter((item) => item !== agentId);
        setSelectedAgent(next[0] || "");
        return next;
      }

      const next = [...current, agentId];
      setSelectedAgent(next[0] || agentId);
      return next;
    });
  }

  async function runAgent() {
    if (selectedAgents.length === 0 || !task.trim()) {
      setError("Select at least one active paid agent and enter a task.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const results = [];

      for (const agentId of selectedAgents) {
        const response = await fetch(`/api/run-agent`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            requested_agent: agentId,
            task,
          }),
        });

        const data = await response.json();

        results.push({
          agent_id: agentId,
          agent_label: SAFE_AGENT_LABELS[agentId] || agentId,
          http_status: response.status,
          result: data,
        });
      }

      const allSucceeded = results.every((item) => item.result?.success === true);

      const combinedResult = {
        success: allSucceeded,
        status: allSucceeded ? "multi_agent_execution_completed" : "multi_agent_execution_partially_blocked",
        selected_agent_count: selectedAgents.length,
        results,
      };

      setResult(combinedResult);

      if (!allSucceeded) {
        setError("One or more selected agents were blocked or failed.");
      }
    } catch {
      setError("Execution failed.");
    } finally {
      setLoading(false);
    }
  }'''
)

client = client.replace(
    '''              <select
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
                style={{
                  width: "100%",
                  padding: 14,
                  borderRadius: 14,
                  border: "1px solid rgba(148,163,184,.18)",
                  background: "#020617",
                  color: "#fff",
                }}
              >
                {(account?.active_agents || []).map((agent) => (
                  <option key={agent} value={agent}>
                    {SAFE_AGENT_LABELS[agent] || agent}
                  </option>
                ))}
              </select>''',
    '''              <div
                style={{
                  display: "grid",
                  gap: 10,
                  maxHeight: 260,
                  overflow: "auto",
                  border: "1px solid rgba(148,163,184,.18)",
                  borderRadius: 16,
                  padding: 12,
                  background: "#020617",
                }}
              >
                {(account?.active_agents || []).map((agent) => (
                  <label
                    key={agent}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      padding: 10,
                      borderRadius: 12,
                      background: selectedAgents.includes(agent)
                        ? "rgba(37,99,235,.22)"
                        : "rgba(15,23,42,.8)",
                      cursor: "pointer",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedAgents.includes(agent)}
                      onChange={() => toggleClientAgent(agent)}
                    />
                    <span>{SAFE_AGENT_LABELS[agent] || agent}</span>
                  </label>
                ))}
              </div>

              <div style={{ color: "#94a3b8", fontSize: 12, marginTop: 8 }}>
                Selected agents: {selectedAgents.length}. Only active paid agents are shown.
              </div>'''
)

client = client.replace(
    '''{loading ? "Running..." : "Run Agent"}''',
    '''{loading ? "Running..." : selectedAgents.length > 1 ? "Run Selected Agents" : "Run Agent"}'''
)

CLIENT_PAGE.write_text(client, encoding="utf-8")

# ---------------- ADMIN PORTAL ----------------
admin = admin.replace(
    '''  const [agent, setAgent] = useState("product_copywriting_agent");''',
    '''  const [agent, setAgent] = useState("product_copywriting_agent");
  const [selectedAdminAgents, setSelectedAdminAgents] = useState<string[]>(["product_copywriting_agent"]);'''
)

admin = admin.replace(
    '''  async function runAdminAgent() {
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
  }''',
    '''  function toggleAdminAgent(agentId: string) {
    setSelectedAdminAgents((current) => {
      if (current.includes(agentId)) {
        const next = current.filter((item) => item !== agentId);
        setAgent(next[0] || "");
        return next;
      }

      const next = [...current, agentId];
      setAgent(next[0] || agentId);
      return next;
    });
  }

  async function runAdminAgent() {
    setRunning(true);
    setRunResult(null);

    try {
      const results = [];

      for (const agentId of selectedAdminAgents) {
        const response = await fetch("/api/run-agent", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
          },
          body: JSON.stringify({
            tenant_id: "owner_admin",
            requested_agent: agentId,
            workflow_stage: "admin_internal_execution",
            action_type: "product_copy_generation",
            actor_role: "owner",
            owner_approved: true,
            task,
          }),
        });

        const data = await response.json();

        results.push({
          agent_id: agentId,
          http_status: response.status,
          result: data,
        });
      }

      const allSucceeded = results.every((item) => item.result?.success === true);

      setRunResult({
        success: allSucceeded,
        status: allSucceeded ? "admin_multi_agent_execution_completed" : "admin_multi_agent_execution_partially_blocked",
        selected_agent_count: selectedAdminAgents.length,
        results,
      });
    } catch {
      setRunResult({ success: false, message: "Admin execution failed." });
    } finally {
      setRunning(false);
    }
  }'''
)

admin = admin.replace(
    '''                <select
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
                </select>''',
    '''                <div
                  style={{
                    display: "grid",
                    gap: 10,
                    border: "1px solid rgba(148,163,184,.22)",
                    borderRadius: 16,
                    padding: 12,
                    background: "#020617",
                  }}
                >
                  {[
                    ["product_copywriting_agent", "Product Copywriting Agent"],
                    ["ugc_creative_agent", "UGC Creative Agent"],
                    ["analytics_optimisation_agent", "Analytics Optimisation Agent"],
                    ["influencer_collaboration_agent", "Influencer Collaboration Agent"],
                    ["product_image_direction_agent", "Product Image Direction Agent"],
                  ].map(([agentId, label]) => (
                    <label
                      key={agentId}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        padding: 10,
                        borderRadius: 12,
                        background: selectedAdminAgents.includes(agentId)
                          ? "rgba(37,99,235,.22)"
                          : "rgba(15,23,42,.8)",
                        cursor: "pointer",
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={selectedAdminAgents.includes(agentId)}
                        onChange={() => toggleAdminAgent(agentId)}
                      />
                      <span>{label}</span>
                    </label>
                  ))}
                </div>

                <div style={{ color: "#94a3b8", fontSize: 12 }}>
                  Selected agents: {selectedAdminAgents.length}. Owner/admin can run one agent or multiple agents for internal operations.
                </div>'''
)

admin = admin.replace(
    '''{running ? "Running..." : "Run Agent"}''',
    '''{running ? "Running..." : selectedAdminAgents.length > 1 ? "Run Selected Agents" : "Run Agent"}'''
)

ADMIN_PAGE.write_text(admin, encoding="utf-8")

TEST.write_text(r'''
from pathlib import Path
import subprocess

ROOT = Path.cwd()
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"

client = client_page.read_text(encoding="utf-8", errors="ignore").lower()
admin = admin_page.read_text(encoding="utf-8", errors="ignore").lower()

checks = {
    "client_multi_agent_state_present": "selectedagents" in client,
    "client_toggle_function_present": "toggleclientagent" in client,
    "client_paid_agent_copy_present": "only active paid agents are shown" in client,
    "client_multi_run_status_present": "multi_agent_execution" in client,
    "admin_multi_agent_state_present": "selectedadminagents" in admin,
    "admin_toggle_function_present": "toggleadminagent" in admin,
    "admin_multi_run_status_present": "admin_multi_agent_execution" in admin,
    "admin_owner_copy_present": "owner/admin can run one agent or multiple agents" in admin,
    "admin_owner_headers_present": '"x-actor-role": "owner"' in admin,
}

print("STEP_248E_MULTI_AGENT_PORTAL_EXECUTION_RESULTS")
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

print("STEP_248E_MULTI_AGENT_PORTAL_EXECUTION_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_248E_MULTI_AGENT_PORTAL_EXECUTION_INSTALLED")
print(f"Updated: {CLIENT_PAGE}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Created/updated: {TEST}")
print("STEP_248E_OK")